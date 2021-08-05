from .transaction import Transaction
from .ledger import Ledger
import pandas as pd


class Account:

    def __init__(self, account_type, category, transactions) -> None:
        self.type = account_type
        self.category = category
        self.transactions = transactions

    @property
    def transactions(self):
        return self._transactions

    @transactions.setter
    def transactions(self, txns):
        trans = []
        for t in txns:
            trans.append(Transaction(**t))
        self._transactions = trans

    @property
    def test(self):
        return True

    # The balance is a property that is equal to the summarization of the account ledgers debits and credits.
    @property
    def balance(self):
        if self.type == 'Asset':
            balance_value = self.journal.debit_value_sum - self.journal.credit_value_sum
            balance_quantity = self.journal.debit_quantity_sum - self.journal.credit_quantity_sum
        else:
            balance_value = self.journal.credit_value_sum - self.journal.debit_value_sum
            balance_quantity = self.journal.credit_quantity_sum - self.journal.debit_quantity_sum
            return {'value' : balance_value, 'quantity' : balance_quantity}

    # Adds all the ledger entries to the ledger (skips value of taxble txs)
    @property
    def journal(self):
        ledger = Ledger()
        # ledger['Account Type'] = self.type
        # ledger['Account Category'] = self.category
        entries = []
        for trans in self.transactions:
            entries.append(trans.entries)
        ledger.merge(entries)
        return ledger




    @property
    def positions(self):
        return
