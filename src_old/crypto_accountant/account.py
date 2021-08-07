import pandas as pd

from .utils import set_decimal, query_df
from .config import account_configs
from .position import Position


class Account:

    def __init__(self, account_type, category) -> None:
        self.type = account_type
        self.category = category
        self.txs_untaxable = {}
        self.txs_taxable = {}
        self.entries = {}
        self.positions = {}
        self.requires_adjustment = False

    @property
    def all_txs(self):
        return {**self.txs_untaxable, **self.txs_taxable}

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

    def add_tx(self, tx):
        if tx.id not in self.all_txs.keys():
            entry_configs = account_configs[tx.tx_type]
            entries = list([self._tx_mapper(tx.to_dict, config)
                           for config in entry_configs])

            if tx.feeQuantity > 0:
                # add fee entries to list of tx entries
                fee_entries = list([self._tx_mapper(tx.to_dict, config)
                                   for config in account_configs['fees']])
                entries += fee_entries
            # add tx entries to list of all tx entries
            self.entries[tx.id] = entries
            if tx.taxable:
                self.requires_adjustment = True
                self.txs_taxable[tx.id] = tx
            else:
                self.txs_untaxable[tx.id] = tx
            return entries

        if tx.baseCurrency not in self.positions:
            self.positions[tx.baseCurrency] = Position(tx.baseCurrency)
        self.positions[tx.baseCurrency].add(tx.id, tx.baseUsdPrice, tx.timestamp, tx.baseQuantity)

    def add_txs(self, txs):
        for tx in txs:
            self.add_tx(tx)
