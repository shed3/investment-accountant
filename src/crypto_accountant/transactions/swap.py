from .taxable import TaxableTx
from .entry_config import CRYPTO

# debit_base_entry = {'side': "debit", 'mkt': 'base', **CRYPTO}
# credit_quote_entry = {'side': "credit", 'mkt': 'quote', **CRYPTO}
# entry_template = {
#     'debit': debit_base_entry,
#     'credit': credit_quote_entry
# }

class Swap(TaxableTx):

    def __init__(self, **kwargs) -> None:
        kwargs['type'] = 'swap'
        super().__init__(**kwargs)
        # set entry templates
        self.entry_templates["base"] = {'side': "debit", **CRYPTO}
        self.entry_templates["quote"] = {'side': "credit", 'mkt': 'quote', **CRYPTO}

        # DO NOT OVERWRITE: must append to prevent possibly losing taxable fee
        self.taxable_assets.append("quote")

    def affected_balances(self):
        affected_balances = {}
        base = self.assets['base']
        quote = self.assets['quote']
        affected_balances[base.symbol] = base.quantity
        affected_balances[quote.symbol] = -quote.quantity
        if 'fee' in self.assets:
            fee = self.assets['fee']
            affected_balances[fee.symbol] = -fee.quantity
        return affected_balances
