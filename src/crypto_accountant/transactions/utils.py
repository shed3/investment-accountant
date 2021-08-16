from decimal import Decimal


def set_precision(val, precision):
    fmt_str = ':.{}f'.format(precision)
    fmt_str = '{' + fmt_str + '}'
    val = fmt_str.format(val)
    return Decimal(val)
