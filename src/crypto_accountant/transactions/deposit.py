from .base import BaseTx
from .entry_config import CASH, INVESTED_CAPITAL

debit_base_entry = {'side': "debit", **CASH}
credit_quote_entry = {'side': "credit",  **INVESTED_CAPITAL}
entry_template = {
    'debit': debit_base_entry,
    'credit': credit_quote_entry
}

class Deposit(BaseTx):

    def __init__(self, **kwargs) -> None:
        super().__init__(entry_template=entry_template, **kwargs)
    
    def get_affected_balances(self):
        affected_balances = {}
        base = self.assets['base']
        affected_balances[base.symbol] = base.quantity
        if 'fee' in self.assets:
            fee = self.assets['fee']
            affected_balances[fee.symbol] = -fee.quantity
        return affected_balances
