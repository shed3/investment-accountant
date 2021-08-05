
from datetime import datetime, time

class Position:

    def __init__(self, symbol) -> None:
        self.symbol = symbol
        self._opens = {}
        self._closes = {}
        self.stats = {}
        self.mkt_price = 0

    @property
    def available_quantity(self):
        # sum opens available qtys
        return [lambda x: x['available_qty'], self._opens.values()].sum()

    @property
    def tax_lots(self):
        # sum opens available qtys
        return self._opens

    @property
    def open_tax_lots(self):
        # sum opens available qtys
        lots = list([lot for lot in self._opens if lot['available_qty'] > 0])
        for lot in lots:
            lot['qty'] = lot['available_qty']
            del lot['available_qty']
        return lots

    @property
    def days_open(self):
        return (self.stats['open']['first_timestamp'] - self.self.stats['close']['last_timestamp']).days

    @property
    def realized_gain(self):
        return [lambda x: x['realized_gain'], self._closes.values()].sum()

    @property
    def unrealized_gain(self):
        return [lambda x: x['unrealized_gain'], self._opens.values()].sum()

    def adjust_to_mtk(self, price, timestamp):
        self.mkt_price = price
        self.mkt_timestamp = timestamp
        for id in self._opens.keys():
            self._opens[id]['unrealized_gain'] = self._opens[id]['available_quantity'] * price
            if (timestamp  - self._opens[id]['timestamp']).days > 365:
                self._opens[id]['term'] = 'long'

    def _update_stats(self, name, price, timestamp):
        entries = self._opens.values() if name == 'open' else self._closes.values()
        self.stats[name]['avg'] = [lambda x: x['price'], entries].mean()
        if price > self.stats[name].get('highest', 0):
            self.stats[name]['highest'] = price
        if price < self.stats[name].get('lowest', 999999999):
            self.stats[name]['lowest'] = price
        if timestamp < self.stats[name].get('first_timestamp', datetime(year=3000)):
            self.stats[name]['first_timestamp'] = timestamp
            self.stats[name]['first'] = price
        if timestamp > self.stats[name].get('last_timestamp', datetime(year=1000)):
            self.stats[name]['last_timestamp'] = timestamp
            self.stats[name]['last'] = price
            self._update_unrealized_gain(price)

    def add(self, id, price, timestamp, qty):
        # add entry to opens and update open_stats
        self._opens[id] = {
            'timestamp': timestamp,
            'price': price,
            'available_qty': qty,
            'unrealized_gain': 0,
            'term': 'short'
        }
        self.update_stats('open', price, timestamp)

    def close(self, id, price, timestamp, config):
        # add entry to closes and update close_stats
        qty = config.values().sum()
        self._closes[id] = {
            'timestamp': timestamp,
            'price': price,
            'qty': qty,
            'realized_gain': 0
        }

        # update available quantities
        # config = {id1: qty1, id2: qty2}
        for config_id, config_qty in config.items():
            entry = self._opens.get(config_id, None)
            if entry:
                close_qty = config_qty
                if entry['available_qty'] >= config_qty:
                    self._opens[config_id]['available_qty'] -= config_qty
                else:
                    self._opens[config_id]['available_qty'] = 0
                    close_qty = self._opens[config_id]['available_qty']

                self._closes[id]['realized_gain'] += close_qty * price
            else:
                raise Exception('No matching entry found for', id)
        
        self.update_stats('close', price, timestamp)
        

