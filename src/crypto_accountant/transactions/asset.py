"""
An Asset represents the info about a coin that makes up part
of a transaction. Currently it is used as a base coin, 
quote coin, or fee coin in a tx.
"""

from ..utils import set_decimal

class Asset:

    def __init__(
        self,
        symbol,
        qty,
        price,
    ) -> None:
        self.symbol = symbol
        self.quantity = set_decimal(qty)
        self.usd_price = set_decimal(price)
        self.usd_value = self.quantity * self.usd_price

    @property
    def to_dict(self):
        val = self.__dict__
        return val
        