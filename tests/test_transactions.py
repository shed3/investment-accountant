import pytest


@pytest.mark.usefixtures("local_txs")
class TestTransactions:

    def test_fetch_local_transactions(self, local_txs):
        pass
