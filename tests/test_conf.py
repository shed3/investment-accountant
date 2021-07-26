import pytest
from decimal import Decimal
from .fixtures import Fixes


@pytest.fixture(scope="class")
def local_txs():
    return Fixes.local_txs()
