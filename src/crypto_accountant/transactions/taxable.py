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
from .entry_config import CRYPTO, CASH, REALIZED_GAIN_LOSS

debit_base_entry = {'side': "debit", **CRYPTO}
credit_quote_entry = {'side': "credit", 'taxable': True, **CRYPTO}

realized_gain = {'side': "credit", 'taxable': True, **REALIZED_GAIN_LOSS}
credit_fee_entry = {'side': "credit", 'type': 'fee', 'mkt': 'fee', **CRYPTO}

entry_template = {
    'debit': debit_base_entry,
    'credit': credit_quote_entry
}

class TaxableTx(BaseTx):

    def __init__(self, realized_gain=realized_gain, **kwargs) -> None:
        super().__init__(**kwargs)
        self.taxable_assets = {}
        self.realized_gain = realized_gain
        if 'fee' in self.assets.keys():
            if not self.assets['fee'].is_fiat and not self.assets['fee'].is_stable:
                #  add fee to taxable assets and set credit entry to use crypto account
                fee_entries = {
                    **self.fee_entry_template,
                    'credit': credit_fee_entry
                }
                self.add_taxable_asset('fee', fee_entries)
                self.fee_entry_template = fee_entries  # set credit entry to use crypto account

    def add_taxable_asset(self, name, entry_template):
        # name of assets position in tx -> can be any of [base, quote, fee]
        self.taxable_assets[name] = entry_template
        self.taxable = True

    def generate_debit_entry(self):
        return self.create_entry(**self.entry_template['debit'])
    
    def generate_credit_entries(self, asset, current_price, qty, **kwargs):
        if asset in self.taxable_assets.keys() and 'credit' in self.taxable_assets[asset].keys():
            tx_asset =  self.assets[asset]
            credit_config = {
                **self.taxable_assets[asset]['credit'],
                'quantity': qty,
                'quote': current_price,
                'value': current_price * qty,
                'symbol': tx_asset.symbol
            }
            credit_entry = self.create_entry(**credit_config)
            realized_gain_config = {
                **self.realized_gain,
                'quantity': qty,
                'quote': current_price,
                'value': (tx_asset.usd_price - current_price) * qty,
                'symbol': tx_asset.symbol
            }
            realized_gain_entry = self.create_entry(**realized_gain_config)
            return [credit_entry, realized_gain_entry]
        raise Exception('{} (TaxableTx) Implementation Error: must define a closing entry for instance of TaxableTx'.format(self.type))
