from .ledger import Ledger
from .position import Position
from .utils import set_decimal
from .tx_config import tx_configs, sell_open, sell_close, realized_gain

class BookKeeper:
    def __init__(self) -> None:
        self.positions = {}
        self.ledger = Ledger()
        self.tax_rates = {'long': set_decimal(.25), 'short': set_decimal(.4)}

    def add_tx(self, tx):
        # if position for tx base currency doesn't exist -> create one
        if tx.base_currency not in self.positions:
            self.positions[tx.base_currency] = Position(tx.base_currency)

        # get entries from tx
        if tx.taxable:
            # get entries by closing positions
            entries = self.process_taxable(tx)
        else:
            # get tx's default entries & add tx to symbol's current position
            entries = tx.get_entries()
            self.positions[tx.base_currency].add(tx.id, tx.base_usd_price, tx.timestamp, tx.base_quantity)

        # add new tx's entries to ledger
        for entry in entries:
            self.ledger.add_entry(entry)

    def add_txs(self, txs):
        txs = sorted(txs, key=lambda x: x.timestamp)
        for tx in txs:
            self.add_tx(tx)

    def process_taxable(self, tx):
        # add opening sell entry to entries list
        entries = [tx.create_entry(**sell_open, quantity=tx.quote_quantity)]

        # add fee entries if tx has fee
        if tx.fee_quantity > 0:
            for fee_config in tx_configs['fee']:
                entries.append(tx.create_entry(**fee_config))

        # sort all open tax lots for tx's base currency position
        position = self.positions[tx.base_currency]
        open_lots = position.open_tax_lots.copy()
        for lot in open_lots:
            lot['tax_liability'] = lot['unrealized_gain'] * self.tax_rates[lot['term']]
        lots = sorted(open_lots, key=lambda x: x['tax_liability'], reverse=True)

        # Loop through open tax lots (sorted by tax liability) until filled
        # At each tax lot, use fillable qty => all available qty or qty needed to fill order
        # Create 2 entries to reflect 
        # - selling fillable qty from tax lot at current price
        # - realizing gain/loss from profit of sale
        # Add new entries to entries list
        filled_qty = 0  # tracks qty filled from open tax lots
        close_config = {} 
        while filled_qty < tx.base_quantity and len(lots) > 0:
            current_lot = lots[0]
            unfilled_qty = tx.base_quantity - filled_qty
            fillable_qty = unfilled_qty if current_lot['qty'] > unfilled_qty else current_lot['qty']
            close_config[current_lot['id']] = fillable_qty
            sell_close_config = {
                **sell_close,
                'quantity': fillable_qty,
                'quote': current_lot['price'],
                'value': current_lot['price'] * fillable_qty,
            }
            sell_close_entry = tx.create_entry(**sell_close_config)
            realized_gain_config = {
                **realized_gain,
                'quantity': fillable_qty,
                'quote': current_lot['price'],
                'value': (tx.base_usd_price - current_lot['price']) * fillable_qty,
            }
            realized_gain_entry = tx.create_entry(**realized_gain_config)
            
            entries += [sell_close_entry, realized_gain_entry]
            filled_qty += fillable_qty
            del lots[0]

        # close symbol's position (partial or fully) with tx's data and sellof data
        self.positions[tx.base_currency].close(tx.id, tx.base_usd_price, tx.timestamp, close_config)
        return entries
