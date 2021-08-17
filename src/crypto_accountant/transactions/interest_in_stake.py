from .base import BaseTx
from .entry_config import CASH, CRYPTO, INTEREST_EARNED_STAKE

debit_crypto_base_entry = {'side': "debit", **CRYPTO}
debit_cash_base_entry = {'side': "debit", **CASH}
credit_base_entry = {'side': "credit",  **INTEREST_EARNED_STAKE}
entry_template = {
    'credit': credit_base_entry,
    'debit': debit_crypto_base_entry
}
class InterestInStake(BaseTx):

    def __init__(self, **kwargs) -> None:
        kwargs['type'] = 'interest-in-stake'
        super().__init__(entry_template=entry_template.copy(), **kwargs)
        if self.assets['base'].is_fiat:
            self.entry_template['debit'] = debit_cash_base_entry
    
    def get_affected_balances(self):
        base = self.assets['base']
        affected_balances = {}
        affected_balances[base.symbol] = base.quantity
        if 'fee' in self.assets:
            fee = self.assets['fee']
            affected_balances[fee.symbol] = -fee.quantity
        return affected_balances
