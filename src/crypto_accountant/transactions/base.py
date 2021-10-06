"""
Accountable TXs

The premise of an accountable transaction flips the responsibilty of knowledge regarding
how a tx affects accounts from the book keeper to the txs themselves. This means that
txs MUST understand how it would affect an account and be able to provide entries describing
it's effect. It is also important that txs recognize which assets involved in the tx were
incoming/outgoing and provide a simple interface for describing the credits and debits.
This allows for tracking higher level positions outside the scope of a tx.
"""

import logging
from pprint import pformat

import pandas as pd
import pytz

from .components.asset import Asset
from .components.entry import Entry
from .entry_config import CASH, CRYPTO, FEES_PAID

utc = pytz.UTC
log = logging.getLogger(__name__)


fee_debit_entry = {'side': "debit", 'mkt': 'fee', **FEES_PAID}
fee_credit_fiat_entry = {'side': "credit", 'type': 'fee', 'mkt': 'fee', **CASH}
fee_credit_crypto_entry = {'side': "credit", 'type': 'fee', 'mkt': 'fee', **CRYPTO}

class BaseTx:

    def __init__(
        self,
        **kwargs
    ) -> None:
        self.id = kwargs.get("id", None)
        self.type = kwargs.get("type", None)
        self.timestamp = pd.Timestamp(kwargs.get("timestamp", None)).replace(tzinfo=pytz.UTC)
        
        self.assets = {}
        self.entry_templates = {}

        self.add_asset("base", **kwargs)
        if 'quote_currency' in kwargs:
            self.add_asset("quote", **kwargs)
        
        self.sub_total = self.assets['base'].usd_value
        self.total = self.sub_total

        # if fee exists create fee asset and add to assets
        if kwargs.get("fee_quantity", 0) > 0:
            # attempt to set fee usd price if not provided
            if not kwargs.get('fee_usd_price', False):
                if kwargs['fee_currency'] == kwargs['base_currency']:
                    kwargs['fee_usd_price'] = kwargs['base_usd_price']
                elif 'quote_currency' in kwargs and kwargs['fee_currency'] == kwargs['quote_currency']:
                    kwargs['fee_usd_price'] = kwargs['quote_usd_price']

            # add fee to assets and "fees paid" entry template
            self.add_asset("fee", **kwargs)
            self.entry_templates["fee"].append(fee_debit_entry)

            # add crypto/cash credit entry template
            if self.assets['fee'].is_stable:
                if self.assets['fee'].is_fiat:
                    self.entry_templates["fee"].append(fee_credit_fiat_entry)
                else:
                    self.entry_templates["fee"].append(fee_credit_crypto_entry)

            # add value of fee to tx's total value
            self.total += self.assets['fee'].usd_value
        
        # log.debug('Tx initialized of type {}:\n{}\n\n'.format(self.type, pformat(self.to_dict())))
        

    ####### INTERFACE METHODS #######

    def affected_balances(self):
        print('Implementation Error: must define affected_balances for {} tx'.format(
            self.type))
        return {}

    def entries(self):
        # return all entries known by tx - excluded taxable/closing and adjusting extries
        # should be able to determine which entries can be created from affected assets
        entries = []
        for entry_templates in self.entry_templates.values():
            # entry templates can have 1 or many templates
            if type(entry_templates) is list:
                entries += list([self.create_entry(**template) for template in entry_templates])
            else:
                entries.append(self.create_entry(**entry_templates))
        return entries


    ####### HELPER METHODS #######

    def add_asset(self, position, **kwargs):
        # position refers to asset's position within tx -> base, quote, fee
        new_asset = Asset(
            kwargs.get("{}_currency".format(position), ""),
            kwargs.get("{}_quantity".format(position), 0),
            kwargs.get("{}_usd_price".format(position), 0),
        )
        self.assets[position] = new_asset
        self.entry_templates[position] = []


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

    def to_dict(self):
        dict_val = self.__dict__.copy()
        dict_val['base'] = self.assets['base'].to_dict()
        if 'quote' in self.assets:
            dict_val['quote'] = self.assets['quote'].to_dict() 
        if 'fee' in self.assets:
            dict_val['fee'] = self.assets['fee'].to_dict()
        del dict_val['assets']
        return dict_val

