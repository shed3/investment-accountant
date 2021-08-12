from pandas.core.algorithms import isin
from pandas.core.dtypes.missing import isna
from src.crypto_accountant.transactions.interest_in_account import InterestInAccount
from src.crypto_accountant.transactions.interest_in_stake import InterestInStake
from src.crypto_accountant.transactions.reward import Reward
from src.crypto_accountant.transactions.buy import Buy
from src.crypto_accountant.transactions.deposit import Deposit
from src.crypto_accountant.transactions.receive import Receive
from src.crypto_accountant.transactions.sell import Sell
from src.crypto_accountant.transactions.send import Send
from src.crypto_accountant.transactions.swap import Swap
from src.crypto_accountant.transactions.withdrawal import Withdrawal
from .ledger import Ledger
from .position import Position
from .utils import check_type, create_tx


class BookKeeper:
    def __init__(self) -> None:
        self.positions = {'usd': Position('usd')}
        self.ledger = Ledger()
        self.tax_rates = {'long': check_type(.25), 'short': check_type(.4)}

    def add_txs(self, txs, auto_detect=True):
        transactions = []
        for tx in txs:
            if auto_detect:
                tx = create_tx(**tx)
            if type(tx) in [Buy, Sell, Deposit, Withdrawal, Send, Receive, Swap, Reward, InterestInAccount, InterestInStake]:
                transactions.append(tx)
        # transactions = sorted(transactions, key=lambda x: x.timestamp)
        for tx in transactions:
            self.add_tx(tx)

    def add_tx(self, tx):
        # create position from base_currency if needed
        if tx.assets['base'].symbol not in self.positions:
            self.positions[tx.assets['base'].symbol] = Position(
                tx.assets['base'].symbol)

         # create position from quote_currency if needed
        if 'quote' in tx.assets and tx.assets['quote'].symbol not in self.positions:
            self.positions[tx.assets['quote'].symbol] = Position(
                tx.assets['quote'].symbol)

        if tx.taxable:
            entries = self.process_taxable(tx)
        else:
            entries = tx.get_entries()

        affected_positions = tx.get_affected_balances()
        for symbol, qty in affected_positions.items():
            if qty > 0:
                # add tx to debit assets to positions
                asset = list([item for item in tx.assets.values()
                             if item.symbol == symbol])[0]
                self.positions[symbol].add(
                    tx.id, asset.usd_price, tx.timestamp, asset.quantity)

        # add new tx's entries to ledger
        for entry in entries:
            self.ledger.add_entry(entry)

    def process_taxable(self, tx):
        # add opening sell entry to entries list
        entries = tx.generate_debit_entry()

        # check if tx has fee and isnt taxable
        if 'fee' not in tx.taxable_assets.keys():
            # overwrite entries w/ tx entries using debit and inherited fee templates
            entries = tx.get_entries(
                config={'debit': tx.entry_template['debit']})

        for taxable_asset in tx.taxable_assets.keys():
            # sort all open tax lots for tx's base currency position
            position = self.positions[tx.assets[taxable_asset].symbol]
            open_lots = position.open_tax_lots.copy()

            for lot in open_lots:
                lot['tax_liability'] = lot['unrealized_gain'] * \
                    self.tax_rates[lot['term']]
            lots = sorted(
                open_lots, key=lambda x: x['tax_liability'], reverse=True)

            tx_type = tx.type if taxable_asset != 'fee' else 'fee'
            # Loop through open tax lots (sorted by tax liability) until filled
            # At each tax lot, use fillable qty => all available qty or qty needed to fill order
            # Create credit entries from tx
            qty = tx.assets[taxable_asset].quantity
            filled_qty = 0  # tracks qty filled from open tax lots
            tax_lot_usage = {}

            while filled_qty < qty and len(lots) > 0:
                current_lot = lots[0]
                lot_available_qty = current_lot['qty']
                lot_price = current_lot['price']

                unfilled_qty = qty - filled_qty
                fillable_qty = unfilled_qty if lot_available_qty > unfilled_qty else lot_available_qty

                # partially or fully close position
                tax_lot_usage = {}
                tax_lot_usage[current_lot['id']] = fillable_qty
                position.close(tx.id, lot_price, tx.timestamp, tax_lot_usage)

                closing_entries = tx.generate_credit_entries(
                    taxable_asset, lot_price, fillable_qty, type=tx_type)

                entries += closing_entries
                filled_qty += fillable_qty
                del lots[0]

        return entries
