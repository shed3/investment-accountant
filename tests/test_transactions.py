import pytest


@pytest.mark.usefixtures("local_txs")
class TestTransactions:

    def test_fetch_local_txns(self, local_txs):
        txns = local_txs
        length = len(txns)
        print(length)
        print(txns)
        print(txns[0])
        assert False
    
    def test_txn_entries(self, local_txs):
        pass

    def test_txn_entries_by_type(self, local_txs):
        # might need more (one for each type)
        pass