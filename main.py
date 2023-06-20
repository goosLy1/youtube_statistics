import json
from fastapi import Depends, FastAPI, Request
from sqlalchemy import distinct, func, select, exists, inspect
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates

from utils import get_service, Youtube
from configurator import core_configurator as config


from models import Base, Channel, ChannelStatistics, Video, VideoStatistics
from database import engine, SessionLocal
from datetime import datetime

app = FastAPI()
Base.metadata.create_all(bind=engine)
ids = config.ids


@app.on_event("startup")
def startup():
    with SessionLocal() as db:
        channel_models = Youtube().get_channels_statistics(ids)
        db.add_all(channel_models)
        db.commit()
        video_models = list()
        for id in ids:
            video_ids = Youtube().get_video_ids_by_channel(id)
            video_models.extend(Youtube().get_videos_statistics(video_ids))
        for model in video_models:
            db.add(model)
            db.commit()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


templates = Jinja2Templates(directory='templates')


# username:str = config.cp2_user
# password:str = config.cp2_password


@app.get('/')
def get_statistics(request: Request, db: Session = Depends(get_db)):

    # print(stat)
    # count = db.execute(select(func.count(Channel.id))).scalar()
    stmt_desc = select(Channel, ChannelStatistics).join(Channel.statistics).distinct(Channel.id).order_by(Channel.id,
                                                                                                          ChannelStatistics.fetch_date.desc())
    # print(stmt_desc)
    # result_last = db.execute("SELECT DISTINCT ON (channels.id) channels.id, channels.title, channel_statistics.view_count, channel_statistics.subscriber_count, channel_statistics.video_count, channel_statistics.fetch_date \
    #                          FROM channels JOIN channel_statistics ON channels.id = channel_statistics.channel_id \
    #                          ORDER BY channels.id, channel_statistics.fetch_date DESC")
    # print(result_last.fetchall())
    result_last = db.execute(stmt_desc).fetchall()
    # print(len(result_last))
    # datalist = list()
    # for id in ids:
    #     stmt = select(Channel, ChannelStatistics).join(Channel.statistics).where(Channel.id == id).order_by(
    #         ChannelStatistics.fetch_date.desc()).limit(2)
    #     datalist.extend(db.execute(stmt).all())
    # # r1 = result.fetchall()
    # # print(datalist)
    # final_list = list()
    # for i in range(0, len(datalist), 2):
    #     stonks = datalist[i].ChannelStatistics.view_count - \
    #         datalist[i+1].ChannelStatistics.view_count
    #     final_tuple = (*datalist[i], stonks)
    #     final_list.append(final_tuple)
    # print(final_list)

    # print(stmt_desc)

    # print(result_last)
    # result_first = db.execute(stmt_asc)
    # r1 = result_last.fetchall()
    # print(r1)
    # r2 = result_first.fetchall()
    # for i in range(0, len(r1)):
    #     print(r1[i].Channel.id, '---', r2[i].Channel.id)
    # result = db.scalars(stmt)
    # print(final_list[0][0].__dict__)

    query = db.execute("WITH first_vc as ( \
                        SELECT DISTINCT ON (channel_statistics.channel_id) channel_statistics.channel_id, channel_statistics.view_count, channel_statistics.fetch_date \
                        FROM channel_statistics \
                        ORDER BY channel_statistics.channel_id, channel_statistics.fetch_date), \
                        last_vc as ( \
                        SELECT DISTINCT ON (channel_statistics.channel_id) channel_statistics.channel_id, channel_statistics.view_count, channel_statistics.fetch_date \
                        FROM channel_statistics \
                        ORDER BY channel_statistics.channel_id, channel_statistics.fetch_date DESC) \
                        select last_vc.channel_id, (last_vc.view_count - first_vc.view_count) as stonks \
                        from last_vc join first_vc on last_vc.channel_id = first_vc.channel_id")
    stonks = query.fetchall()
    # print(stonks)
    # for res in result_last:
    #     for i in range(len(stonks)):
    #         if res.Channel.id == stonks[i][0]:
    #             res.Channel['stonks'] = stonks[i][1]

    return templates.TemplateResponse('index.html', {'request': request, 'data': result_last, 'stonks': stonks})
    # return {"message": "ok"}


@app.get('/channel/{id}')
def get_videos_stat(request: Request, id: str, db: Session = Depends(get_db)):

    stmt_desc = select(Video, VideoStatistics).join(Video.statistics).where(Video.channel_id == id).distinct(Video.id).order_by(Video.id,
                                                                                                                                VideoStatistics.fetch_date.desc())
    result_last = db.execute(stmt_desc).fetchall()

    return templates.TemplateResponse('video.html', {'request': request, 'data': result_last})
    # return {"message": "ok"}


@app.get('/channel/chart/{id}')
def get_channel_chart(request: Request, id: str, db: Session = Depends(get_db)):
    stmt = select(ChannelStatistics).where(ChannelStatistics.channel_id == id).distinct(
        ChannelStatistics.view_count).order_by(ChannelStatistics.view_count, ChannelStatistics.fetch_date)
    result = db.execute(stmt).scalars().all()
    view_count = []
    subscriber_count = []
    video_count = []
    fetch_date = []
    for res in result:
        view_count.append(res.view_count)
        subscriber_count.append(res.subscriber_count)
        video_count.append(res.video_count)
        fetch_date.append(res.fetch_date)
    data = dict()
    data['view_count'] = view_count
    data['subscriber_count'] = subscriber_count
    data['video_count'] = video_count
    data['fetch_date'] = fetch_date

    def custom_serializer(obj):
        if isinstance(obj, datetime):
            serial = obj.isoformat("#", "seconds")
            return serial

    dataJSON = json.dumps(data, default=custom_serializer)
    context = {'request': request, 'data': dataJSON}
    return templates.TemplateResponse('chart.html', context)
    # return {"message": "ok"}
# SELECT  *
# FROM (
# SELECT  channels.*, channel_statistics.*, row_number() OVER (PARTITION BY channels.id) rn
# FROM channels JOIN channel_statistics ON channels.id = channel_statistics.channel_id
# ORDER BY channels.id, channel_statistics.fetch_date DESC
# ) AS foo
# WHERE rn = 1
