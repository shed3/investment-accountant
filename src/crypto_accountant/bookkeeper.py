from .ledger import Ledger
from .position import Position
from .utils import set_decimal
from .tx_config import tx_configs, realized_gain_sell, realized_gain_swap

realized_gain = {
    'sell': realized_gain_sell,
    'swap': realized_gain_swap,
}

class BookKeeper:
    def __init__(self) -> None:
        self.positions = {'usd': Position('usd')}
        self.ledger = Ledger()
        self.tax_rates = {'long': set_decimal(.25), 'short': set_decimal(.4)}

    def add_tx(self, tx):
        # create position from base_currency if needed
        if tx.base_currency not in self.positions:
            self.positions[tx.base_currency] = Position(tx.base_currency)

         # create position from quote_currency if needed
        if tx.quote_currency and tx.quote_currency not in self.positions:
            self.positions[tx.quote_currency] = Position(tx.quote_currency)

        if tx.taxable:
            if tx.type == 'sell':
                # get sell entries
                processed_tx = self.process_taxable(tx, tx.base_currency, tx.base_quantity, tx.base_usd_price)
                entries = processed_tx['entries']

                # close tx from base symbol's current position
                self.positions[tx.base_currency].close(tx.id, tx.base_usd_price, tx.timestamp, processed_tx['tax_lot_usage'])
                # add tx to quote symbol's current position
                self.positions[tx.quote_currency].add(tx.id, tx.quote_usd_price, tx.timestamp, tx.quote_quantity)
                
            elif tx.type == 'swap':
                # get swap entries
                processed_tx = self.process_taxable(tx, tx.quote_currency, tx.quote_quantity, tx.quote_usd_price)
                entries = processed_tx['entries']

                # close tx from quote symbol's current position
                self.positions[tx.quote_currency].close(tx.id, tx.quote_usd_price, tx.timestamp, processed_tx['tax_lot_usage'])
                # add tx to base symbol's current position
                self.positions[tx.base_currency].add(tx.id, tx.base_usd_price, tx.timestamp, tx.base_quantity)
                
        else:
            # TODO need to handle how other tx types affect positions
            entries = tx.get_entries() 
            self.positions[tx.base_currency].add(tx.id, tx.base_usd_price, tx.timestamp, tx.base_quantity)

        # add new tx's entries to ledger
        for entry in entries:
            self.ledger.add_entry(entry)

    def add_txs(self, txs):
        txs = sorted(txs, key=lambda x: x.timestamp)
        for tx in txs:
            self.add_tx(tx)

    def process_taxable(self, tx, symbol, qty, price):
        # add opening sell entry to entries list
        entry_config = tx_configs[tx.type]
        opening_entry = entry_config[0]
        closinging_entry = entry_config[1]
        entries = [tx.create_entry(**opening_entry)]

        # add fee entries if tx has fee
        if tx.fee_quantity > 0:
            # TODO need to handle tabable fees
            for fee_config in tx_configs['fee']:
                entries.append(tx.create_entry(**fee_config))

        # sort all open tax lots for tx's base currency position
        position = self.positions[symbol]
        open_lots = position.open_tax_lots.copy()

        for lot in open_lots:
            lot['tax_liability'] = lot['unrealized_gain'] * \
                self.tax_rates[lot['term']]
        lots = sorted(
            open_lots, key=lambda x: x['tax_liability'], reverse=True)

        # Loop through open tax lots (sorted by tax liability) until filled
        # At each tax lot, use fillable qty => all available qty or qty needed to fill order
        # Create 2 entries to reflect
        # - selling fillable qty from tax lot at current price
        # - realizing gain/loss from profit of sale
        # Add new entries to entries list
        # * THIS ONLY WORKS FOR SELL AND SWAP
        filled_qty = 0  # tracks qty filled from open tax lots
        tax_lot_usage = {}
        while filled_qty < qty and len(lots) > 0:
            current_lot = lots[0]
            unfilled_qty = qty - filled_qty
            fillable_qty = unfilled_qty if current_lot['qty'] > unfilled_qty else current_lot['qty']
            tax_lot_usage[current_lot['id']] = fillable_qty
            close_config = {
                **closinging_entry,
                'quantity': fillable_qty,
                'quote': current_lot['price'],
                'value': current_lot['price'] * fillable_qty,
            }
            close_entry = tx.create_entry(**close_config)
            realized_gain_config = {
                **realized_gain[tx.type],
                'quantity': fillable_qty,
                'quote': current_lot['price'],
                'value': (price - current_lot['price']) * fillable_qty,
            }
            realized_gain_entry = tx.create_entry(**realized_gain_config)

            entries += [close_entry, realized_gain_entry]
            filled_qty += fillable_qty
            del lots[0]

        # close symbol's position (partial or fully) with tx's data and sellof data
        return {
            'entries': entries,
            'tax_lot_usage': tax_lot_usage
        }
