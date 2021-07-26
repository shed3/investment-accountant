import copy
import pytest
import pandas as pd
from src.crypto_accountant.ledger import Ledger


@pytest.fixture(scope="class")
def ledger_local_transactions(local_txs):
    ledger_trans = []
    asset = copy.deepcopy(local_txs[0])
    asset['Account'] = 'asset'
    asset['Sub Account'] = 'asset sub'
    asset['Timestamp'] = asset['timestamp']
    asset['Symbol'] = asset['baseCurrency']
    asset['Quantity'] = asset['baseQuantity']
    asset['Value'] = asset['subTotal']
    asset['ID'] = asset['id']
    del asset['timestamp']
    del asset['baseCurrency']
    del asset['baseQuantity']
    del asset['subTotal']
    del asset['id']
    ledger_trans.append(asset)
    liability = copy.deepcopy(local_txs[0])
    liability['Account'] = 'Liability'
    liability['Sub Account'] = 'Liability sub'
    liability['Timestamp'] = liability['timestamp']
    liability['Symbol'] = liability['baseCurrency']
    liability['Quantity'] = liability['baseQuantity']
    liability['Value'] = liability['subTotal']
    liability['ID'] = liability['id']
    del liability['timestamp']
    del liability['baseCurrency']
    del liability['baseQuantity']
    del liability['subTotal']
    del liability['id']
    ledger_trans.append(liability)
    return ledger_trans


@pytest.fixture(scope="class")
def ledger_with_entries(ledger_local_transactions):
    ledger = Ledger()
    ledger.credit(ledger_local_transactions[0])
    ledger.debit(ledger_local_transactions[1])
    return ledger


@pytest.mark.usefixtures("ledger_local_transactions", "ledger_with_entries")
class TestLedger:
    """All tests for Ledger class.

    Need to add tests for dataframe renaming, currently the fixture does not have correct mapping to enable this.
    """

    def test_debit_ledger(self, ledger_local_transactions):
        ledger = Ledger()
        ledger.debit(ledger_local_transactions[0])
        assert len(ledger.debits) == 1
        assert len(ledger.debits_df) == 1
        assert len(ledger.credits) == 0
        assert type(ledger.debits_df) == pd.DataFrame
        assert len(ledger.raw_ledger) == 1
        assert type(ledger.raw_ledger) == pd.DataFrame

    def test_credit_ledger(self, ledger_local_transactions):
        ledger = Ledger()
        ledger.credit(ledger_local_transactions[0])
        assert len(ledger.credits) == 1
        assert len(ledger.credits_df) == 1
        assert len(ledger.debits) == 0
        assert type(ledger.credits_df) == pd.DataFrame
        assert len(ledger.raw_ledger) == 1
        assert type(ledger.raw_ledger) == pd.DataFrame

    def test_full_ledger(self, ledger_local_transactions):
        ledger = Ledger()
        ledger.credit(ledger_local_transactions[0])
        ledger.debit(ledger_local_transactions[1])
        assert len(ledger.credits) == 1
        assert len(ledger.credits_df) == 1
        assert type(ledger.credits_df) == pd.DataFrame
        assert len(ledger.debits) == 1
        assert len(ledger.debits_df) == 1
        assert type(ledger.debits_df) == pd.DataFrame
        print('current ledger', ledger.raw_ledger)
        assert len(ledger.raw_ledger) == 2
        assert type(ledger.raw_ledger) == pd.DataFrame

    def test_set_ledger_index(self, ledger_with_entries):
        ledger = ledger_with_entries.set_ledger_index()
        assert ledger.index.names == ['Timestamp', 'ID']
        assert len(ledger) == 2
        assert type(ledger) == pd.DataFrame
        assert ledger.index.is_monotonic_increasing

    def test_summarize_ledger(self, ledger_with_entries):
        # Eventual params - columns, indexes
        # Need to verify the sums are actually correct ... maybe the data types and shit too. This works for now.
        ledger = ledger_with_entries.summarize_ledger()
        assert ledger.index.names == ['Account', 'Sub Account', 'Symbol']
        assert list(ledger.columns) == ['Quant - Bal', 'Val - Bal', 'Debits', 'Credits']
        assert len(ledger) == 2
        assert type(ledger) == pd.DataFrame
        assert ledger.index.is_monotonic_increasing

    def test_ledger_properties(self, ledger_with_entries):
        pass

    def test_find_ledger_entries(self, ledger_with_entries):
        pass
