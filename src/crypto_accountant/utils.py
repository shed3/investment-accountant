from datetime import date, datetime, time
import logging
from os import replace
from google.api_core.datetime_helpers import DatetimeWithNanoseconds
from decimal import Decimal
import pandas as pd
import pytz

utc = pytz.UTC
log = logging.getLogger(__name__)

def check_type(val, check_string=False, types=[Decimal]):
    original_type = type(val)
    if isinstance(val, (int, float)):
        val = Decimal(str(val))
    if isinstance(val, (datetime, DatetimeWithNanoseconds, date, time)):
        val = pd.Timestamp(val).replace(tzinfo=utc)
    if type(val) == DatetimeWithNanoseconds:
        val = pd.Timestamp(val).replace(tzinfo=utc)
    if check_string:
        if isinstance(val, str):
            for t in types:
                try:
                    val = t(val)
                except:
                    pass
    return val


def query_df(df, col, val):
    return df.loc[df[col] == val]


def dict_to_string(d, indent=0):
    pval = ''
    for key, value in d.items():
        val1 = ('\t' * indent + str(key))
        pval += val1
        pval += '\n'
        if isinstance(value, str):
            val2 = ('\t' * (indent+1) + str(value))
        elif isinstance(value, dict):
            val2 = dict_to_string(value, indent+1)            
        else:
            val2 = dict_to_string(value.__dict__, indent+1)
        pval += val2
        return pval


def set_precision(val, precision):
    fmt_str = ':.{}f'.format(precision)
    fmt_str = '{' + fmt_str + '}'
    val = fmt_str.format(val)
    return Decimal(val)
