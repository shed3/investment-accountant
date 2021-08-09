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
class TaxableTx(BaseTx):

    def __init__(self, taxable_asset, **kwargs) -> None:
        super().__init__(**kwargs)
        # which assets should be taxed -> can be any of [base, quote, fee]
        self.taxable_assets = taxable_asset

        
    def generate_closing_entries(self, close_config, realized_gain_config):
        close_entry = self.create_entry(**close_config)
        realized_gain = self.create_entry(**realized_gain_config)
        return [close_entry, realized_gain]
