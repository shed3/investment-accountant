"""
Accountable TXs

The premise of an accountable transaction flips the responsibilty of knowledge regarding
how a tx affects accounts from the book keeper to the txs themselves. This means that
txs MUST understand how it would affect an account and be able to provide entries describing
it's effect. It is also important that txs recognize which assets involved in the tx were
incoming/outgoing and provide a simple interface for describing the credits and debits.
This allows for tracking higher level positions outside the scope of a tx.
"""

from components.asset import Asset
from components.entry import Entry
from entry_config import FEES_PAID, CASH, CRYPTO

debit_fee_entry = {'side': "debit", 'mkt': 'fee', **FEES_PAID}
credit_fee_entry = {'side': "credit", 'type': 'fee', 'mkt': 'fee', **CASH}
fee_config = {
    'debit': debit_fee_entry.copy(),
    'credit': credit_fee_entry.copy()
}
stable_credit_fee_entry = {'side': "credit", 'type': 'fee', 'mkt': 'fee', **CRYPTO}

# ALL VALUES MUST BE DECIMALS


class BaseTx:

    def __init__(
        self,
        entry_template={},
        fee_entry_template=fee_config.copy(),
        **kwargs
    ) -> None:
        self.entry_template = entry_template
        self.fee_entry_template = fee_entry_template
        self.id = kwargs.get("id", None)
        self.type = kwargs.get("type", None)
        self.taxable = kwargs.get("taxable", False)
        self.timestamp = kwargs.get("timestamp", None)
        self.assets = {}
        self.add_asset("base", **kwargs)
        self.add_asset("quote", **kwargs)
        self.sub_total = self.assets['base'].usd_value
        self.total = self.sub_total

        # if fee exists create fee asset and add to assets
        fee_qty = kwargs.get("fee_quantity", 0)
        if fee_qty > 0:
            if kwargs['fee_currency'] == kwargs['base_currency']:
                kwargs['fee_usd_price'] = kwargs['base_usd_price']
            elif 'quote_currency' in kwargs and kwargs['fee_currency'] == kwargs['quote_currency']:
                kwargs['fee_usd_price'] = kwargs['quote_usd_price']
            self.add_asset("fee", **kwargs)
            if self.assets['fee'].is_stable and not self.assets['fee'].is_fiat:
                self.fee_entry_template['credit'] = stable_credit_fee_entry.copy()
            self.total += self.assets['fee'].usd_value

    def get_affected_balances(self):
        print('Implementation Error: must define get_affected_balances for {} tx'.format(self.type))
        return {}

    def to_dict(self):
        dict_val = self.__dict__.copy()
        dict_val['base'] = self.assets['base'].to_dict()
        dict_val['quote'] = self.assets['quote'].to_dict()
        if 'fee' in self.assets:
            dict_val['fee'] = self.assets['fee'].to_dict()
        del dict_val['assets']
        return dict_val

    def add_asset(self, position, **kwargs):
        # position refers to asset's position within tx -> base, quote, fee
        new_asset = Asset(
            kwargs.get("{}_currency".format(position), ""),
            kwargs.get("{}_quantity".format(position), 0),
            kwargs.get("{}_usd_price".format(position), 0),
        )
        self.assets[position] = new_asset

    def create_entry(self, **kwargs):
        mkt = kwargs.get("mkt", 'base')
        expected_entry_kwargs = {
            'id': kwargs.get("id", self.id),
            'account_type': kwargs.get("account_type", None),
            'account': kwargs.get("account", None),
            'sub_account': kwargs.get("sub_account", None),
            'timestamp': kwargs.get("timestamp", self.timestamp),
            'symbol': kwargs.get("symbol", self.assets[mkt].symbol),
            'side': kwargs.get("side", ''),
            'type': kwargs.get("type", self.type),
            'quote': kwargs.get("quote", self.assets[mkt].usd_price),
            'close_quote': kwargs.get("close_quote", self.assets[mkt].usd_price),
            'value': kwargs.get("value", self.assets[mkt].usd_value),
            'quantity': kwargs.get('quantity', self.assets[mkt].quantity),
        }
        entry_kwargs = {
            **kwargs,
            **expected_entry_kwargs
        }
        entry = Entry(**entry_kwargs)
        return entry

    def create_entries(self, entry_configs, fee_configs):
        entries = list([self.create_entry(**config) for config in list(entry_configs.values())])
        if 'fee' in self.assets and self.assets['fee'].quantity > 0:
            if self.assets['fee'].is_fiat:
                # add fee entries to list of tx entries
                fee_entries = list([self.create_entry(**config) for config in list(fee_configs.values())])
                entries += fee_entries
            else:
                entries.append(self.create_entry(**self.fee_entry_template['debit']))

        self.entries = entries
        return entries

    def get_entries(self, **kwargs):
        entry_configs = kwargs.get("config", self.entry_template)
        fee_configs = kwargs.get("fee_config", self.fee_entry_template)
        return self.create_entries(entry_configs, fee_configs)
