from base import BaseTx
from entry_config import CASH, WITHDRAWALS

debit_base_entry = {'side': "debit", **WITHDRAWALS}
credit_base_entry = {'side': "credit",  **CASH}
entry_template = {
    'debit': debit_base_entry,
    'credit': credit_base_entry
}

class Withdrawal(BaseTx):

    def __init__(self, **kwargs) -> None:
        kwargs['type'] = 'withdrawal'
        super().__init__(entry_template=entry_template.copy(), **kwargs)
    
    def get_affected_balances(self):
        affected_balances = {}
        base = self.assets['base']
        affected_balances[base.symbol] = -base.quantity
        if 'fee' in self.assets:
            fee = self.assets['fee']
            affected_balances[fee.symbol] = -fee.quantity
        return affected_balances
