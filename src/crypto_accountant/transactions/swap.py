from .taxable import TaxableTx
from .entry_config import CRYPTO, CASH

debit_base_entry = {'side': "debit", **CRYPTO}
credit_quote_entry = {'side': "credit", **CRYPTO}
entry_template = {
    'debit': debit_base_entry,
    'credit': credit_quote_entry
}

class Swap(TaxableTx):

    def __init__(self, **kwargs) -> None:
        super().__init__(entry_template=entry_template.copy(), **kwargs)
        # if base asset isnt stable add to taxable assets
        if not self.assets['quote'].is_stable:
            self.add_taxable_asset('quote', entry_template)

    def get_affected_balances(self):
        affected_balances = {}
        base = self.assets['base']
        quote = self.assets['quote']
        affected_balances[base.symbol] = base.quantity
        affected_balances[quote.symbol] = -quote.quantity
        if 'fee' in self.assets:
            fee = self.assets['fee']
            affected_balances[fee.symbol] = -fee.quantity
        return affected_balances
