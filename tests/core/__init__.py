from datetime import datetime
import pytz


def make_datetime(dt):
    "For convenience."
    return datetime.strptime(dt, "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.utc)


