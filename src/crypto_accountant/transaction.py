"""
This Module handles cleaning transactions via the Transaction object.

Transaction Object used to represent a transaction and set its values in accordance with the confinguration.

Example:
"""


import json
import logging
from datetime import datetime

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
        self.tx_type = kwargs.get("tx_type", None)
        self.id = kwargs.get("id", None)
        self.baseCurrency = kwargs.get("baseCurrency", None)
        self.baseQuantity = set_decimal(kwargs.get("baseQuantity", None))
        self.baseUsdPrice = set_decimal(kwargs.get("baseUsdPrice", None))
        self.feeCurrency = kwargs.get("feeCurrency", None)
        self.feeQuantity = set_decimal(kwargs.get("feeQuantity", None))
        self.feeUsdPrice = set_decimal(kwargs.get("feeUsdPrice", None))
        self.feeTotal = set_decimal(kwargs.get("feeTotal", None))
        self.quoteCurrency = kwargs.get("quoteCurrency", None)
        self.quoteQuantity = set_decimal(kwargs.get("quoteQuantity", None))
        self.quoteUsdPrice = set_decimal(kwargs.get("quoteUsdPrice", None))
        self.subTotal = set_decimal(kwargs.get("subTotal", None))
        self.taxable = kwargs.get("taxable", False)

    @property
    def to_dict(self):
        """Base ledger entries associated with the transaction. Does not account for taxable transactions or gains.

        Returns:
            Ledger Object containing relevant entries.
        """
        val = self.__dict__
        return val

# seed_config = {
#     "timestamp": datetime(),
#     "tx_type": "seed",
#     "id": 0,
#     "baseCurrency": "",
#     "baseQuantity": 0,
#     "baseUsdPrice": 0,
#     "feeCurrency": "",
#     "feeQuantity": 0,
#     "feeUsdPrice": 0,
#     "feeTotal": 0,
#     "subTotal": 0,
# }
# SeedTransaction = Transaction(**seed_config)