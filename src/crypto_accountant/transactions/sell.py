"""
Accountable TXs

The premise of an accountable transaction flips the responsibilty of knowledge regarding
how a tx affects accounts from the book keeper to the txs themselves. This means that
txs MUST understand how it would affect an account and be able to provide entries describing
it's effect. It is also important that txs recognize which assets involved in the tx were
incoming/outgoing and provide a simple interface for describing the credits and debits.
This allows for tracking higher level positions outside the scope of a tx.
"""

from .base import BaseTx
from .config import tx_configs

# ALL VALUES MUST BE DECIMALS
class Sell(BaseTx):

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        
    def get_entries(self):
        super.get_entries()
        return self.create_entries(tx_configs['sell'], tx_configs['fee'])

    def get_affected_balances(self):
        affected_balances = {}
        base = self.assets['base']
        quote = self.assets['quote']
        affected_balances[base.symbol] = -base.quantity
        affected_balances[quote.symbol] = quote.quantity
        if 'fee' in self.assets:
            fee = self.assets['fee']
            affected_balances[fee.symbol] = -fee.quantity
        return affected_balances
