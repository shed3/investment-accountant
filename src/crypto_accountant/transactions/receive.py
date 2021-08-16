from .base import BaseTx
from .entry_config import CRYPTO, TRANSFERS_IN

debit_base_entry = {'side': "debit", **CRYPTO}
credit_base_entry = {'side': "credit",  **TRANSFERS_IN}
entry_template = {
    'debit': debit_base_entry,
    'credit': credit_base_entry
}

class Receive(BaseTx):

    def __init__(self, **kwargs) -> None:
        kwargs['type'] = 'receive'
        super().__init__(entry_template=entry_template.copy(), **kwargs)
    
    def get_affected_balances(self):
        affected_balances = {}
        base = self.assets['base']
        affected_balances[base.symbol] = base.quantity
        if 'fee' in self.assets:
            fee = self.assets['fee']
            affected_balances[fee.symbol] = -fee.quantity
        return affected_balances
