import datetime as dt
from jinja2 import Environment
import pytz


def datetimefilter(value):
    format = "%d.%m.%Y, %H:%M"
    ru_tz = pytz.timezone("Europe/Moscow")
    local_dt = value.astimezone(ru_tz)
    return local_dt.strftime(format)


env = Environment()
env.filters['datetimefilter'] = datetimefilter
