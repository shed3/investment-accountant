import re
from google.api_core.datetime_helpers import DatetimeWithNanoseconds
from decimal import Decimal

import logging
log = logging.getLogger(__name__)


def set_decimal(val):
    if isinstance(val, int) or isinstance(val, float):
        res = Decimal(str(val))
        return res
    elif not isinstance(val, str) and type(val) != DatetimeWithNanoseconds:
        log.debug('Unrecognized type: {}'.format(type(val)))
    return val

def is_row_valid(row, invalid_pattern='(^-\w+)', result_col="incomplete"):
    # check whether row is valid. Valid mean no invalid_pattern matches are found
    cols = row.keys()
    invalid_cols = {}
    for col in cols:
        if isinstance(row[col], str):
            invalid_match = re.match(invalid_pattern, row[col]) 
            if bool(invalid_match):
                return False
    return True
    
def query_df(df, col, val):
    return df.loc[df[col] == val]
    
    
