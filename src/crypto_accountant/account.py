from .ledger import Ledger


class Account:

    def __init__(self, account_type, category, transactions) -> None:
        self.type = account_type
        self.category = category
        self.transactions = transactions
        self.requires_adjustment = False

    # The balance is a property that is equal to the summarization of the account ledgers debits and credits.
    @property
    def balance(self):
        ledger = self.journal.summarize_ledger()
        if self.type == 'Asset':
            ledger['Balance'] = ledger['Debits'] - ledger['Credits']
            ledger['Quant - Balance'] = ledger['Debits - Quantity'] - \
                ledger['Credits - Quantity']
            return ledger
        else:
            ledger['Balance'] = ledger['Credits'] - ledger['Debits']
            ledger['Quant - Balance'] = ledger['Credits - Quantity'] - \
                ledger['Debits - Quantity']
            return ledger

    # Adds all the ledger entries to the ledger (skips value of taxble txs)
    @property
    def journal(self):
        ledger = Ledger()
        ledger['Account Type'] = self.account_type
        ledger['Account Category'] = self.category
        for trans in self.transactions:
            ledger.merge(trans['entries'])
        return ledger

    @property
    def positions(self):
        return
