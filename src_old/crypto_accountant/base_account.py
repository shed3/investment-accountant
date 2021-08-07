import pandas as pd

from .utils import set_decimal, query_df
from .transaction import Transaction
from .ledger import Ledger
from .config import cpa_config


class BaseAccount:

    def __init__(self, account_type, category, name, transactions=[]) -> None:
        self.type = account_type
        self.category = category
        self.name = name
        self.requires_adjustment = False
        self.journal = Ledger()
        self.fee_config = cpa_config['fees']
        self._transactions = []
        self.add_txs(transactions)

    @property
    def transactions(self):
        return self._transactions

    @property
    def incomplete_txs(self):
        return list([x[1] for x in query_df(self.journal.ledger,'incomplete', True).index.tolist()])

    @property
    def taxable_txs(self):
        return list([x[1] for x in query_df(self.journal.ledger,'taxable', True).index.tolist()])
    # The balance is a property that is equal to the summarization of the account ledgers debits and credits.
    @property
    def credit_balance(self):
        balance_value = self.journal.credit_value_sum - self.journal.debit_value_sum
        balance_quantity = self.journal.credit_quantity_sum - \
            self.journal.debit_quantity_sum
        return {'value': balance_value, 'quantity': balance_quantity}

    # The balance is a property that is equal to the summarization of the account ledgers debits and credits.
    @property
    def debit_balance(self):
        balance_value = self.journal.debit_value_sum - self.journal.credit_value_sum
        balance_quantity = self.journal.debit_quantity_sum - \
            self.journal.credit_quantity_sum
        return {'value': balance_value, 'quantity': balance_quantity}

    @property
    def balance(self):
        debit_balance = self.debit_balance
        credit_balance = self.credit_balance
        if self.type == 'Asset':
            balance_value = debit_balance['value'] - credit_balance['value']
            balance_quantity = debit_balance['quantity'] - \
                credit_balance['quantity']
        else:
            balance_value = credit_balance['value'] - debit_balance['value']
            balance_quantity = credit_balance['quantity'] - \
                debit_balance['quantity']
        return {'value': balance_value, 'quantity': balance_quantity}

    def _tx_mapper(self, tx, mapping):
        values = {}
        for key in mapping:
            values[key] = mapping[key]
            if callable(values[key]):
                pass
            elif type(values[key]) == bool:
                pass
            elif values[key].startswith('-'):
                if mapping[key][1:] in tx:
                    k = values[key][1:]
                    values[key] = set_decimal(tx[k])
            elif not mapping[key].startswith('-'):
                values[key] = mapping[key]
        # log.debug(
            # 'Got the following mapped values:\n {}\n'.format(values))
        return values

    def add_txs(self, txs):
        all_entries = []
        current_tx_ids = list([item.id for item in self._transactions])
        txs = list([tx for tx in txs if tx.id not in current_tx_ids])
        self._transactions += txs   # add new txs to list of txs
        for tx in txs:
            entry_configs = cpa_config[tx.tx_type]
            entries = list([self._tx_mapper(tx.to_dict, config)
                           for config in entry_configs])

            if tx.feeQuantity > 0:
                # add fee entries to list of tx entries
                fee_entries = list([self._tx_mapper(tx.to_dict, config)
                                   for config in self.fee_config])
                entries += fee_entries

            # add tx entries to list of all tx entries
            all_entries += entries
        for entry in all_entries:
            self.journal.add_entry(entry)

    def adjust_tx(self, id, adjusting_entries): 
        for entry in self.journal.entries:
            if entry.id == id:
                entry['adjusted'] = True
        for entry in adjusting_entries:
            self.journal.add_entry(entry)


    # replace values
    # if len val > 1, create new entries
    # 
