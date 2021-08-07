import logging
from google.api_core.datetime_helpers import DatetimeWithNanoseconds
from decimal import Decimal

log = logging.getLogger(__name__)

def set_decimal(val):
    if isinstance(val, int) or isinstance(val, float):
        res = Decimal(str(val))
        return res
    elif not isinstance(val, str) and type(val) != DatetimeWithNanoseconds:
        log.debug('Unrecognized type: {}'.format(type(val)))
    return val

def query_df(df, col, val):
    return df.loc[df[col] == val]
    
    
