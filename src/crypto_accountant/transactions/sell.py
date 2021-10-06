from .taxable import TaxableTx
from .entry_config import CRYPTO, CASH

# debit_quote_entry = {'side': "debit", 'mkt': 'quote', **CASH}
# credit_base_entry = {'side': "credit", 'mkt': 'base', **CRYPTO}

# entry_template = {
#     'debit': debit_quote_entry,
#     'credit': credit_base_entry
# }

class Sell(TaxableTx):

    def __init__(self, **kwargs) -> None:
        kwargs['type'] = 'sell'
        super().__init__(**kwargs)

        # set entry templates
        self.entry_templates["base"] = {'side': "credit", **CRYPTO}
        self.entry_templates["quote"] = {'side': "debit", 'mkt': 'quote', **CASH}

        # DO NOT OVERWRITE: must append to prevent possibly losing taxable fee
        self.taxable_assets.append("base")
        
    def affected_balances(self):
        affected_balances = {}
        base = self.assets['base']
        quote = self.assets['quote']
        affected_balances[base.symbol] = -base.quantity
        affected_balances[quote.symbol] = quote.quantity
        if 'fee' in self.assets:
            fee = self.assets['fee']
            affected_balances[fee.symbol] = -fee.quantity
        return affected_balances
