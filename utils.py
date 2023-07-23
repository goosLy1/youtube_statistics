from typing import Dict, List
import googleapiclient.discovery
from sqlalchemy import select
from sqlalchemy.orm import Session
from models import Channel, ChannelStatistics, Video, VideoStatistics
from configurator import core_configurator as config
from database import SessionLocal
from typing import Type


def get_service():
    service = googleapiclient.discovery.build(
        'youtube', 'v3', developerKey=config.API_KEY)
    return service


class Youtube:
    ids = config.ids
    bad_ids = None

    def get_existing_or_new_channel(self, channel: Dict[str, str] | List[str]) -> Type[Channel]:
        with SessionLocal() as db:
            if isinstance(channel, Dict):
                db_channel = Channel(
                    id=channel['id'],
                    title=channel['snippet']['title']
                )
            else:
                db_channel = Channel(
                    id=channel,
                    title='This channel was deleted'.upper()
                )
            db_channel_merged = db.merge(db_channel)
            return db_channel_merged

    def get_existing_or_new_video(self, video: Dict[str, str]) -> Type[Video]:
        with SessionLocal() as db:
            channel_from_db = db.query(Channel).filter(
                Channel.id == video['snippet']['channelId']).first()
            # db_channel_merged = db.merge(channel_from_db)
            db_video = Video(
                id=video['id'],
                title=video['snippet']['title'],
                pub_date=video['snippet']['publishedAt'],
                channel=channel_from_db
            )
            db.expunge_all()
            db_video_merged = db.merge(db_video)

            return db_video_merged

    def get_channels_statistics(self) -> List[ChannelStatistics]:
        yt_api_response = get_service().channels().list(
            id=self.ids, part='snippet, statistics').execute()
        channel_statistics = yt_api_response.get('items')
        # print(channel_statistics[0].get("id"))
        channel_statistics_models = list()
        good_ids = list()
        for channel in channel_statistics:
            good_ids.append(channel['id'])
            db_channel_merged = self.get_existing_or_new_channel(channel)

            db_channel_stat = ChannelStatistics(
                view_count=channel['statistics']['viewCount'],
                subscriber_count=channel['statistics']['subscriberCount'],
                video_count=channel['statistics']['videoCount'],
                channel=db_channel_merged
            )
            # channel_statistics_models.append(db_channel)
            channel_statistics_models.append(db_channel_stat)
        print(good_ids)
        self.bad_ids = list(set(self.ids) ^ set(good_ids))
        self.ids = good_ids
        print(self.bad_ids)
        print(self.ids)
        return channel_statistics_models

    def get_video_ids_by_channel(self) -> List[str]:
        for id in self.ids:
            uploads_playlist_id = id.replace('UC', 'UU')
            video_ids = list()
            next_page_token = ''

            while next_page_token is not None:
                result = get_service().playlistItems().list(
                    part="contentDetails",
                    playlistId=uploads_playlist_id,
                    maxResults=50,
                    pageToken=next_page_token
                ).execute()
                next_page_token = result.get('nextPageToken')
                items = result.get('items')

                for item in items:
                    video_ids.append(item['contentDetails']['videoId'])
        return video_ids

    def get_videos_statistics(self, video_ids: List[str]) -> List[VideoStatistics]:
        video_statistics = list()
        while video_ids:
            portion_of_video_ids = list()

            while video_ids and len(portion_of_video_ids) != 50:
                portion_of_video_ids.append(video_ids.pop(0))

            yt_api_response = get_service().videos().list(
                part="snippet,contentDetails,statistics, status",
                id=portion_of_video_ids
            ).execute()

            video_statistics.extend(yt_api_response.get('items'))
        video_statistics_models = list()
        print(len(video_statistics))
        for video in video_statistics:
            db_video_merged = self.get_existing_or_new_video(video)
            db_video_stat = VideoStatistics(
                view_count=video['statistics']['viewCount'] if 'viewCount' in video['statistics'] else 0,
                like_count=video['statistics']['likeCount'] if 'likeCount' in video['statistics'] else 0,
                comment_count=video['statistics']['commentCount'] if 'commentCount' in video['statistics'] else 0,
                privacy_status=video['status']['privacyStatus'],
                yt_rating=video['contentDetails']['contentRating']['ytRating'] if 'ytRating' in video['contentDetails']['contentRating'] else '',
                video=db_video_merged
            )
            video_statistics_models.append(db_video_stat)
        return video_statistics_models

    def handle_deleted_channels(self) -> List[ChannelStatistics]:
        bad_channel_statistics_models = list()
        for id in self.bad_ids:
            db_channel_merged = self.get_existing_or_new_channel(id)

            db_channel_stat = ChannelStatistics(
                view_count=-1,
                subscriber_count=-1,
                video_count=-1,
                channel=db_channel_merged
            )
            # channel_statistics_models.append(db_channel)
            bad_channel_statistics_models.append(db_channel_stat)
        return bad_channel_statistics_models

# def add_channel_statistics_in_db(db: Session, models: List[ChannelStatistics]):
#     db.add_all(models)
#     db.commit()


# def add_video_statistics_in_db(db: Session, models: List[VideoStatistics]):
#     db.add_all(models)
#     db.commit()
