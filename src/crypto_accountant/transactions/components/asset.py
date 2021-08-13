"""
An Asset represents the info about a coin that makes up part
of a transaction. Currently it is used as a base coin, 
quote coin, or fee coin in a tx.
"""
from decimal import Decimal


stable_coins = [
    'usd',
    'usdc',
    'usdt',
    'busd',
    'husd',
    'tusd',
    'pax',
    'dai',
]

class Asset:

    def __init__(
        self,
        symbol,
        qty,
        price,
    ) -> None:
        self.symbol = symbol.upper()
        self.quantity = qty
        self.usd_price = price
        self.usd_value = self.quantity * self.usd_price
        self.is_fiat = self.symbol == "usd"
        self.is_stable = self.is_fiat or self.symbol in stable_coins

    @property
    def quantity(self):
        return self._quantity

    @property
    def usd_price(self):
        return self._usd_price

    @quantity.setter
    def quantity(self, val):
        self._quantity = val if isinstance(val, Decimal) else Decimal(val)
    
    @usd_price.setter
    def usd_price(self, val):
        self._usd_price = val if isinstance(val, Decimal) else Decimal(val)

    def to_dict(self):
        val = self.__dict__
        return val
        