from .base import BaseTx
from .entry_config import CASH, DEPOSITS

# debit_base_entry = {'side': "debit", **CASH}
# credit_base_entry = {'side': "credit",  **DEPOSITS}
# entry_template = {
#     'debit': debit_base_entry,
#     'credit': credit_base_entry
# }

class Deposit(BaseTx):

    def __init__(self, **kwargs) -> None:
        kwargs['type'] = 'deposit'
        super().__init__(**kwargs)
        # set entry templates
        self.entry_templates["base"] = [
            {'side': "debit", **CASH},
            {'side': "credit",  **DEPOSITS}
        ]

    def affected_balances(self):
        affected_balances = {}
        base = self.assets['base']
        affected_balances[base.symbol] = base.quantity
        if 'fee' in self.assets:
            fee = self.assets['fee']
            affected_balances[fee.symbol] = -fee.quantity
        return affected_balances
