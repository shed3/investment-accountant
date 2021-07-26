"""
This Module handles cleaning transactions via the Transaction object.

Transaction Object used to represent a transaction and set its values in accordance with the confinguration.

Example:
"""


import json
import logging

from .config import cpa_config
from .utils import set_decimal
from .ledger import Ledger

log = logging.getLogger(__name__)


# ALL VALUES MUST BE DECIMALS
class Transaction:

    def __init__(
        self,
        **kwargs
    ) -> None:
        self.timestamp = kwargs.get("timestamp", None)
        self.tx_type = kwargs.get("type", None)
        self.id = kwargs.get("id", None)
        self.uid = kwargs.get("uid", None)
        self.connnectionId = kwargs.get("connnectionId", None)
        self.baseCurrency = kwargs.get("baseCurrency", None)
        self.baseQuantity = set_decimal(kwargs.get("baseQuantity", None))
        self.baseUsdPrice = set_decimal(kwargs.get("baseUsdPrice", None))
        self.feeCurrency = kwargs.get("feeCurrency", None)
        self.feeQuantity = set_decimal(kwargs.get("feeQuantity", None))
        self.feeUsdPrice = set_decimal(kwargs.get("feeUsdPrice", None))
        self.quoteCurrency = kwargs.get("quoteCurrency", None)
        self.quoteQuantity = set_decimal(kwargs.get("quoteQuantity", None))
        self.quoteUsdPrice = set_decimal(kwargs.get("quoteUsdPrice", None))
        self.config = cpa_config[self.tx_type]
        self.fee_config = cpa_config['fees']

    @property
    def to_dict(self):
        """Base ledger entries associated with the transaction. Does not account for taxable transactions or gains.

        Returns:
            Ledger Object containing relevant entries.
        """
        val = self.__dict__
        return val

    @property
    def entries(self):
        """Base ledger entries associated with the transaction. Does not account for taxable transactions or gains.

        Returns:
            Ledger Object containing relevant entries.
        """
        log.debug('Getting entries for transaction: {}\n'.format(self))
        if self.tx_type:
            if self.config:
                return self._get_entries()
            else:
                log.warning('No config for transaction type: {}\n'.format(
                    self.tx_type))
        else:
            log.warning('No type for transaction: {}\n'.format(self.id))

    # TODO | Return object with credit & debit keys that contain entries list (basically combine it with journal transaction & the previous function).
    # TODO | Can then proper column names for credits and debits.
    def _map_txn_values(self, mapping):
        log.debug('Setting values for transaction {} with mapping:\n {}\n'.format(
            self.id, self.config))
        values = {}
        for key in mapping:
            values[key] = mapping[key]
            if callable(values[key]):
                pass
            elif type(values[key]) == bool:
                pass
            elif values[key].startswith('-'):
                if mapping[key][1:] in self.to_dict:
                    k = values[key][1:]
                    values[key] = set_decimal(self.to_dict[k])
            elif not mapping[key].startswith('-'):
                values[key] = mapping[key]
        log.debug(
            'Sending the following values back to be added to ledger:\n {}\n'.format(values))

        return values

    def _get_entries(self):
        log.debug('Creating entries.')
        # Need to update this to make fees not in USD taxable transactions.
        entries_ledger = Ledger()

        if self.feeQuantity > 0:
            log.debug('Journaling fee for transaction: {}\n'.format(
                self.id))
            for debit in self.fee_config['debits']:
                res = self._map_txn_values(debit)
                entries_ledger.debit(res)
            for credit in self.fee_config['credits']:
                res = self._map_txn_values(credit)
                entries_ledger.credit(res)

        for debit in self.config['debits']:
            res = self._map_txn_values(debit)
            entries_ledger.debit(**res)
        for credit in self.config['credits']:
            res = self._map_txn_values(credit)
            entries_ledger.credit(res)
        print(entries_ledger.ledger)
        return entries_ledger
