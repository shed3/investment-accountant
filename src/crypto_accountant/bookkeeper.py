from .ledger import Ledger
from .account import Account


class BookKeeper:

    def __init__(self, transactions, config) -> None:
        self.book = Ledger()
        self.config = config
        self.transactions = transactions
        self.accounts = []

    # create accounts from txs, will require filtering transactions for each acct
    def create_accounts(self):
        # take all transactions, group them by account in entries. Transactions may affect multiple accounts. Result is
        # {account type: {account category : [transactions]}}
        temp_accts = {}
        for trans in self.transactions:
            for entry in trans.entries.ledger:
                if (entry['Account'], entry['Sub Account']) not in temp_accts:
                    temp_accts[(entry['Account'], entry['Sub Account'])] = []
                temp_accts[(entry['Account'], entry['Sub Account'])].append(entry)

        for key, val in temp_accts:
            self.accounts.append(Account(key[0], key[1], val))
        print(self.accounts)

    # create main ledger from accounts ledgers
    def create_book(self):
        pass

    # make sure debits = credits
    def trial_balance(self):
        pass

    # close taxable positions (with no value) and realizing gains
    def close_positions(self):
        pass
