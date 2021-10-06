
from datetime import datetime
from .utils import set_precision
import pytz
utc=pytz.UTC
class Position:

    def __init__(self, symbol, **kwargs) -> None:
        self.symbol = symbol
        self._opens = {}
        self._closes = {}
        self.stats = {'open': {}, 'close': {}}
        self.mkt_price = 0
        self.mkt_timestamp = None
        self.tax_rates = {
            'long': set_precision(kwargs.get('tax_rate_long', .25), 2),
            'short': set_precision(kwargs.get('tax_rate_short', .4), 2)
        }

    ####### PROPERTIES #######

    @property
    def balance(self):
        # sum opens available qtys
        debit_sum = sum(list([x['qty'] for x in self._opens.values()]))
        credit_sum = sum(list([x['qty'] for x in self._closes.values()]))
        return debit_sum - credit_sum

    @property
    def available_quantity(self):
        # sum opens available qtys
        return sum(list([x['available_qty'] for x in self._opens.values()]))

    @property
    def tax_lots(self):
        # sum opens available qtys
        return self._opens

    @property
    def open_tax_lots(self):
        # TODO make this a function that can accept a date range so that we can derive values from periods
        # sum opens available qtys
        lots = self._opens.copy()
        open_lots = []
        for id, lot in lots.items():
            if lot['available_qty'] > 0:
                new_lot = {**lot}
                new_lot['id'] = id
                # new_lot['qty'] = new_lot['available_qty']
                # del new_lot['available_qty']
                open_lots.append(new_lot)
        return open_lots

    @property
    def days_open(self):
        return (self.stats['open']['first_timestamp'] - self.self.stats['close']['last_timestamp']).days

    @property
    def realized_gain(self):
        return sum(list([(lambda x: x['realized_gain'])(x) for x in list(self._closes.values())]))

    @property
    def unrealized_gain(self):
        return sum(list([(lambda x: x['unrealized_gain'])(x) for x in list(self._opens.values())]))


    ####### INTERFACE METHODS #######

    def open(self, id, price, timestamp, qty):
        # add entry to opens and update open_stats
        timestamp = timestamp.replace(tzinfo=utc)
        self._opens[id] = {
            'timestamp': timestamp,
            'price': price,
            'qty': qty,
            'available_qty': qty,
            'unrealized_gain': set_precision(0, 18),
            'term': 'short'
        }
        self._update_stats('open', price, timestamp)

    def close(self, id, price, timestamp, qty):
        # record close event
        self._closes[id] = {
            'timestamp': timestamp.replace(tzinfo=utc),
            'price': price,
            'qty': qty,
            'realized_gain': set_precision(0, 18)
        }

        open_lots = self.open_tax_lots.copy()
        for lot in open_lots:
            lot['tax_liability'] = lot['unrealized_gain'] * self.tax_rates[lot['term']]
        lots = sorted(open_lots, key=lambda x: x['tax_liability'], reverse=True)

        # Loop through open tax lots (sorted by tax liability) until filled
        # At each tax lot, use fillable qty => all available qty or qty needed to fill order
        # Create credit entries from tx
        filled_qty = 0  # tracks qty filled from open tax lots
        tax_lot_usage = []
        while filled_qty < qty and len(lots) > 0:
            current_lot = lots[0]
            lot_available_qty = current_lot['available_qty']
            lot_price = current_lot['price']

            unfilled_qty = qty - filled_qty
            fillable_qty = unfilled_qty if lot_available_qty > unfilled_qty else lot_available_qty

            # partially or fully close position's available_qty
            self._opens[current_lot['id']]['available_qty'] -= fillable_qty

            # increment close event's realized gain
            self._closes[id]['realized_gain'] += fillable_qty * price

            # update lot usage and filled qty before removing current tax lot from list
            tax_lot_usage.append((lot_price, fillable_qty))
            filled_qty += fillable_qty
            del lots[0]

        self._update_stats('close', price, timestamp)
        return tax_lot_usage

    ####### HELPER METHODS #######

    def adjust_to_mtk(self, price, timestamp):
        self.mkt_price = price
        self.mkt_timestamp = timestamp
        for id in self._opens.keys():
            self._opens[id]['unrealized_gain'] = self._opens[id]['available_qty'] * price
            if (timestamp  - self._opens[id]['timestamp']).days > 365:
                self._opens[id]['term'] = 'long'

    def _update_stats(self, name, price, timestamp):
        timestamp = timestamp.replace(tzinfo=utc)
        entries = self._opens.values() if name == 'open' else self._closes.values()
        entries = list(entries)
        prices = list([(lambda x: x['price'])(x) for x in entries])
        self.stats[name]['avg'] = sum(prices) / len(entries)
        highest = self.stats[name].get('highest', 0)
        lowest = self.stats[name].get('lowest', 999999999)
        first = self.stats[name].get('first_timestamp', datetime(year=3000, month=1, day=1, tzinfo=utc))
        last =self.stats[name].get('last_timestamp', datetime(year=1000, month=1, day=1, tzinfo=utc))
        if price > highest:
            self.stats[name]['highest'] = price
        if price < lowest:
            self.stats[name]['lowest'] = price
        if timestamp < first:
            self.stats[name]['first_timestamp'] = timestamp
            self.stats[name]['first'] = price
        if timestamp > last:
            self.stats[name]['last_timestamp'] = timestamp
            self.stats[name]['last'] = price
        self.adjust_to_mtk(price, timestamp)

    

        

