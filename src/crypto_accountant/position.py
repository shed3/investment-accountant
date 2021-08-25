
from datetime import datetime
from .utils import check_type
import pytz
utc=pytz.UTC
class Position:

    def __init__(self, symbol) -> None:
        self.symbol = symbol
        self._opens = {}
        self._closes = {}
        self.stats = {'open': {}, 'close': {}}
        self.mkt_price = 0
        self.mkt_timestamp = None

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
                new_lot['qty'] = new_lot['available_qty']
                del new_lot['available_qty']
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


    def adjust_to_mtk(self, price, timestamp):
        self.mkt_price = price
        self.mkt_timestamp = timestamp
        for id in self._opens.keys():
            self._opens[id]['unrealized_gain'] = self._opens[id]['available_qty'] * check_type(price)
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

    def add(self, id, price, timestamp, qty):
        # add entry to opens and update open_stats
        timestamp = timestamp.replace(tzinfo=utc)
        price = check_type(price)
        qty = check_type(qty)
        self._opens[id] = {
            'timestamp': timestamp,
            'price': check_type(price),
            'qty': check_type(qty),
            'available_qty': check_type(qty),
            'unrealized_gain': check_type(0),
            'term': 'short'
        }
        self._update_stats('open', price, timestamp)

    def close(self, id, price, timestamp, config):
        # add entry to closes and update close_stats
        timestamp = timestamp.replace(tzinfo=utc)
        price = check_type(price)
        qty =  sum(list([check_type(x) for x in list(config.values())]))
        self._closes[id] = {
            'timestamp': timestamp,
            'price': price,
            'qty': qty,
            'realized_gain': check_type(0)
        }

        # update available quantities
        # config = {id1: qty1, id2: qty2}
        for config_id, config_qty in config.items():
            entry = self._opens.get(config_id, None)
            if entry:
                close_qty = check_type(config_qty)
                if entry['available_qty'] >= config_qty:
                    self._opens[config_id]['available_qty'] -= close_qty
                else:
                    self._opens[config_id]['available_qty'] = check_type(0)
                    close_qty = self._opens[config_id]['available_qty']

                self._closes[id]['realized_gain'] += close_qty * price
            else:
                raise Exception('No matching entry found for', id)
        
        self._update_stats('close', price, timestamp)
        

