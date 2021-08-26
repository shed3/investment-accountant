from pandas.core.tools.datetimes import to_datetime
import pytz
import pandas as pd
from randomtimestamp import randomtimestamp


def generate_timestamp(**kwargs):
    start = kwargs.get('start', None)
    if start and type(start) == pd.Timestamp:
        start = pd.to_datetime(start)

    date = randomtimestamp(
        start=start,
        start_year=kwargs.get('start_year', None),
        text=False
    )
    return pd.Timestamp(date, tz=pytz.UTC)
