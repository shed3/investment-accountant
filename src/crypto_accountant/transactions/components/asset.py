"""
An Asset represents the info about a coin that makes up part
of a transaction. Currently it is used as a base coin, 
quote coin, or fee coin in a tx.
"""
from ...utils import set_precision

stable_coins = [
    'USDC',
    'USDT',
    'UST',
    'BUSD',
    'GUSD',
    'HUSD',
    'TUSD',
    'PAX',
    'DAI',
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
        self.usd_value = set_precision(self.quantity * self.usd_price, 2)
        self.is_fiat = self.symbol == "USD"
        self.is_stable = self.is_fiat or self.symbol in stable_coins

    @property
    def quantity(self):
        return self._quantity

    @property
    def usd_price(self):
        return self._usd_price

    @quantity.setter
    def quantity(self, val):
        self._quantity = set_precision(val, 18)

    @usd_price.setter
    def usd_price(self, val):
        self._usd_price = set_precision(val, 18)

    def to_dict(self):
        val = self.__dict__.copy()
        val['usd_price'] = val['_usd_price']
        val['quantity'] = val['_quantity']
        del val['_usd_price']
        del val['_quantity']

        return val
