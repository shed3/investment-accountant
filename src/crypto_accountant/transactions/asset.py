"""
An Asset represents the info about a coin that makes up part
of a transaction. Currently it is used as a base coin, 
quote coin, or fee coin in a tx.
"""


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
        self.symbol = symbol.lower()
        self.quantity = qty
        self.usd_price = price
        self.usd_value = self.quantity * self.usd_price
        self.is_fiat = self.symbol == "usd"
        self.is_stable = self.is_fiat or self.symbol in stable_coins

    @property
    def to_dict(self):
        val = self.__dict__
        return val
        