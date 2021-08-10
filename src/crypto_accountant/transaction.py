"""
This Module handles cleaning transactions via the Transaction object.

Transaction Object used to represent a transaction and set its values in accordance with the confinguration.

Example:
"""

from .tx_config import tx_configs
from .utils import set_decimal

# ALL VALUES MUST BE DECIMALS
class Transaction:

    def __init__(
        self,
        **kwargs
    ) -> None:
        self.timestamp = kwargs.get("timestamp", None)
        self.type = kwargs.get("type", None)
        self.id = kwargs.get("id", None)
        self.base_currency = kwargs.get("base_currency", None)
        self.base_quantity = set_decimal(kwargs.get("base_quantity", None))
        self.base_usd_price = set_decimal(kwargs.get("base_usd_price", None))
        self.fee_currency = kwargs.get("fee_currency", None)
        self.fee_quantity = set_decimal(kwargs.get("fee_quantity", None))
        self.fee_usd_price = set_decimal(kwargs.get("fee_usd_price", None))
        self.fee_total = set_decimal(kwargs.get("fee_total", None))
        self.quote_currency = kwargs.get("quote_currency", None)
        self.quote_quantity = set_decimal(kwargs.get("quote_quantity", None))
        self.quote_usd_price = set_decimal(kwargs.get("quote_usd_price", None))
        self.sub_total = set_decimal(kwargs.get("sub_total", None))
        self.taxable = kwargs.get("taxable", False)


    @property
    def to_dict(self):
        val = self.__dict__
        return val

    @property
    def print(self):
        val = list('{}: {}'.format(key, val) + '\n' for key, val in self.to_dict.items())
        string = ''
        for n in val:
            string += (n)
        return string
        
    def get_entries(self, **kwargs):
        entry_configs = kwargs.get("config", tx_configs[self.type]) 
        fee_configs = kwargs.get("fee_config", tx_configs['fee']) 
        
        entries = list([self.create_entry(**config) for config in entry_configs])
        if self.fee_quantity > 0:
            # add fee entries to list of tx entries
            fee_entries = list([self.create_entry(**config) for config in fee_configs])
            entries += fee_entries

        self.entries = entries
        return entries

    def create_entry(self, **kwargs):
        side = kwargs.get("side", 'credit')
        mkt = kwargs.get("mkt", 'base')
        tx_type = kwargs.get("type", self.type)
        default_value = self.sub_total
        default_quantity = getattr(self, '{}_quantity'.format(mkt))
        if tx_type == "fee":
            default_value = self.fee_total
            default_quantity = self.fee_quantity
        entry = {
            'id': kwargs.get("id", self.id),
            'account': kwargs.get("account", None),
            'sub_account': kwargs.get("sub_account", None),
            'type': tx_type,
            'timestamp': kwargs.get("timestamp", self.timestamp),
            'taxable': kwargs.get("taxable", self.taxable),
            'symbol': kwargs.get("symbol", getattr(self, '{}_currency'.format(mkt))),
            'quote': kwargs.get("quote", getattr(self, '{}_usd_price'.format(mkt))),
            '{}_value'.format(side): kwargs.get("value", default_value),
            '{}_quantity'.format(side): kwargs.get('quantity', default_quantity),
        }
        return entry