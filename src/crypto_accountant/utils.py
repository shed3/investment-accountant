from google.api_core.datetime_helpers import DatetimeWithNanoseconds
from decimal import Decimal

import logging
log = logging.getLogger(__name__)


def set_decimal(val):
    if isinstance(val, int) or isinstance(val, float):
        res = Decimal(str(val))
        return res
    elif not isinstance(val, str) and type(val) != DatetimeWithNanoseconds:
        log.warning('Unrecognized type: {}'.format(type(val)))
    return val
