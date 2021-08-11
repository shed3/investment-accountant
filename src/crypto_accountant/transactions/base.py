"""
Accountable TXs

The premise of an accountable transaction flips the responsibilty of knowledge regarding
how a tx affects accounts from the book keeper to the txs themselves. This means that
txs MUST understand how it would affect an account and be able to provide entries describing
it's effect. It is also important that txs recognize which assets involved in the tx were
incoming/outgoing and provide a simple interface for describing the credits and debits.
This allows for tracking higher level positions outside the scope of a tx.
"""

from .asset import Asset
from .entry_config import FEES_PAID, CASH

debit_fee_entry = {'side': "debit", 'mkt': 'fee', **FEES_PAID}
credit_fee_entry =  {'side': "credit", 'type': 'fee', 'mkt': 'fee', **CASH}
fee_config = {
    'debit': debit_fee_entry,
    'credit': credit_fee_entry
}

# ALL VALUES MUST BE DECIMALS
class BaseTx:

    def __init__(
        self,
        entry_template={},
        fee_entry_template=fee_config,
        **kwargs
    ) -> None:
        self.entry_template = entry_template
        self.fee_entry_template = fee_entry_template.copy()
        self.id = kwargs.get("id", None)
        self.type = kwargs.get("type", None)
        self.taxable = kwargs.get("taxable", False)
        self.timestamp = kwargs.get("timestamp", None)
        self.assets = {
            'base': Asset(
                kwargs.get("base_currency", ""),
                kwargs.get("base_quantity", 0),
                kwargs.get("base_usd_price", 0),
            ),
            'quote': Asset(
                kwargs.get("quote_currency", ""),
                kwargs.get("quote_quantity", 0),
                kwargs.get("quote_usd_price", 0),
            ),
        }
        self.sub_total = self.assets['base'].usd_value + self.assets['quote'].usd_value
        self.total = self.sub_total

        # if fee exists create fee asset and add to assets
        fee_qty = kwargs.get("fee_quantity", 0)
        if fee_qty > 0:
            self.assets['fee'] = Asset(
                kwargs.get("fee_currency", ""),
                kwargs.get("fee_quantity", 0),
                kwargs.get("fee_usd_price", 0),
            )
            self.total += self.assets['fee'].usd_value


    def get_affected_balances(self):
        print('Implementation Error: must define get_affected_balances for {} tx'.format(self.type))
        return {}

    @property
    def to_dict(self):
        dict_val = self.__dict__.copy()
        dict_val['base'] = self.assets['base'].to_dict
        dict_val['quote'] = self.assets['quote'].to_dict
        if 'fee' in self.assets:
            dict_val['fee'] = self.assets['fee'].to_dict
        del dict_val['assets']
        return dict_val
    
    def get_entries(self, **kwargs):
        entry_configs = kwargs.get("config", self.entry_template)
        fee_configs = kwargs.get("fee_config", self.fee_entry_template)
        return self.create_entries(entry_configs, fee_configs)

    def create_entries(self, entry_configs, fee_configs):
        entries = list([self.create_entry(**config) for config in list(entry_configs.values())])
        if 'fee' in self.assets and self.assets['fee'].quantity > 0:
            if self.assets['fee'].is_fiat:
            # add fee entries to list of tx entries
                fee_entries = list([self.create_entry(**config) for config in list(fee_configs.values())])
                entries += fee_entries
        self.entries = entries
        return entries

    def create_entry(self, **kwargs):
        side = kwargs.get("side", 'credit')
        mkt = kwargs.get("mkt", 'base')
        tx_type = kwargs.get("type", self.type)
        default_value = self.assets[mkt].usd_value
        default_quantity = self.assets[mkt].quantity
        entry = {
            'id': kwargs.get("id", self.id),
            'account': kwargs.get("account", None),
            'sub_account': kwargs.get("sub_account", None),
            'type': tx_type,
            'timestamp': kwargs.get("timestamp", self.timestamp),
            'taxable': kwargs.get("taxable", self.taxable),
            'symbol': kwargs.get("symbol", self.assets[mkt].symbol),
            'quote': kwargs.get("quote", self.assets[mkt].usd_price),
            'close_quote': kwargs.get("close_quote", self.assets[mkt].usd_price),
            '{}_value'.format(side): kwargs.get("value", default_value),
            '{}_quantity'.format(side): kwargs.get('quantity', default_quantity),
        }
        return entry
