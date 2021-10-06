from .taxable import TaxableTx
from .entry_config import CRYPTO, TRANSFERS_OUT

# debit_base_entry = {'side': "debit", **TRANSFERS_OUT}
# credit_quote_entry = {'side': "credit",  **CRYPTO}
# entry_template = {
#     'debit': debit_base_entry,
#     'credit': credit_quote_entry
# }

class Send(TaxableTx):

    def __init__(self, **kwargs) -> None:
        kwargs['type'] = 'send'
        super().__init__(**kwargs)
        # set entry templates
        self.entry_templates["base"] = [
            {'side': "debit", **TRANSFERS_OUT},
            {'side': "credit",  **CRYPTO}
        ]
    
    def affected_balances(self):
        affected_balances = {}
        base = self.assets['base']
        affected_balances[base.symbol] = -base.quantity
        if 'fee' in self.assets:
            fee = self.assets['fee']
            affected_balances[fee.symbol] = -fee.quantity
        return affected_balances
