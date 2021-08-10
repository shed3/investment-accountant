import pandas as pd
import numpy as np
from datetime import datetime
import uuid
import random
from randomtimestamp import randomtimestamp
from src.crypto_accountant.utils import set_decimal
from src.crypto_accountant.transaction import Transaction
from src.crypto_accountant.position import Position


class TxnFactory:
    def __init__(self):
        self.positions = {
            'usd': Position('usd'),
            'btc': Position('btc'),
            'eth': Position('eth'),
            'link': Position('link'),
            'usdc': Position('usdc'),
            'grt': Position('grt'),
            'ada': Position('ada'),
        }
        self.data_factory = HistoricalDataFactory()
        self.date_range = self.data_factory.date_range
        self.eod_data = self.data_factory.data
        for symbol in self.positions.keys():
            self.positions[symbol].mkt_price = set_decimal(
                self.eod_data[symbol].iloc[0]['close'])
            self.positions[symbol].mkt_timestamp = set_decimal(self.eod_data[symbol].index[0])                
        self.transactions = []

    def deposit_factory(self, base_quantity=set_decimal(random.randint(0, 10000)), fee=False, **kwargs):
        args = {
            'base_currency': 'usd',
            'base_usd_price': set_decimal(1),
            'base_quantity': base_quantity}
        if fee:
            # move this to a new function called add fee
            fee_total_q = base_quantity * \
                set_decimal(random.randint(0, 7)) * .01
            args['fee_quantity'] = fee_total_q
            args['fee_usd_price'] = args['base_usd_price']
            args['fee_currency'] = args['base_currency']
        tx = self.txn_factory('deposit', **args)
        self.positions['usd'].add(tx.id, set_decimal(
            1), tx.timestamp, tx.base_quantity)
        self.transactions.append(tx)


    def receive_factory(self, quantity=set_decimal(random.randint(0, 100)), fee=False, **kwargs):
        available_assets = list(
            [x for x in self.positions.keys()])
        base_currency = kwargs.get(
            "base_currency", available_assets[random.randint(0, len(available_assets) - 1)])        
        base_quantity = quantity
        timestamp = kwargs.get("timestamp", randomtimestamp(
            start_year=2018, text=False))
        base_usd_price = self.data_factory.get_price(base_currency, timestamp)
        args = {
            'base_currency': base_currency,
            'base_usd_price': base_usd_price,
            'base_quantity': base_quantity}
        if fee:
            fee_total_q = base_quantity * \
                set_decimal(random.randint(0, 7)) * set_decimal(.01)
            args['fee_quantity'] = fee_total_q
            args['fee_usd_price'] = args['base_usd_price']
            args['fee_currency'] = args['base_currency']
        tx = self.txn_factory('deposit', **args)
        self.positions[base_currency].add(
            tx.id, tx.base_usd_price, tx.timestamp, tx.base_quantity)
        self.transactions.append(tx)

    def buy_factory(self, **kwargs):
        available_assets = list(
            [x for x in self.positions.keys() if x != 'usd'])
        base_currency = kwargs.get(
            "base_currency", available_assets[random.randint(0, len(available_assets) - 1)])
        quote_quantity = set_decimal(
            random.randint(0, self.positions['usd'].balance))
        timestamp = randomtimestamp(start=self.positions['usd'].mkt_timestamp, text=False)
        base_usd_price = self.data_factory.get_price(base_currency, timestamp)
        base_quantity = quote_quantity / base_usd_price
        args = {
            'base_currency': base_currency,
            'base_usd_price': base_usd_price,
            'base_quantity': base_quantity,
            'quote_currency': 'usd',
            'quote_usd_price': set_decimal(1),
            'quote_quantity': quote_quantity,
            'timestamp': timestamp
        }
        if set_decimal(random.random()) > .5:
            fee_total_q = base_quantity * \
                set_decimal(random.randint(0, 7) * .01)
            args['fee_quantity'] = fee_total_q
            args['fee_usd_price'] = args['base_usd_price']
            args['fee_currency'] = args['base_currency']

        tx = self.txn_factory('buy', **args)
        self.positions[base_currency].add(
            tx.id, tx.base_usd_price, tx.timestamp, tx.base_quantity)
        self.positions['usd']._closes[tx.id] = {
            'timestamp': tx.timestamp,
            'price': set_decimal(1),
            'qty': quote_quantity,
            'realized_gain': 0
        }
        # self.positions['usd'].close(tx.id, set_decimal(1), tx.timestamp, {self.positions['usd'].open_tax_lots})
        self.transactions.append(tx)

    def swap_factory(self, **kwargs):
        available_assets = list(
            [x for x in self.positions.keys() if x != 'usd'])
        available_assets = list(
            [x for x in available_assets if self.positions[x].balance > 0])
        base_currency = kwargs.get(
            "base_currency", available_assets[random.randint(0, len(available_assets) - 1)])     
        available_assets = list(
            [x for x in available_assets if x != base_currency])
        quote_currency = kwargs.get(
            "quote_currency", available_assets[random.randint(0, len(available_assets) - 1)])
        base_position = self.positions[base_currency]
        quote_position = self.positions[quote_currency]
        print(quote_position, quote_position.balance)
        quote_quantity = set_decimal(random.uniform(0, .1))
        quote_quantity = set_decimal(quote_quantity* quote_position.balance)
        timestamp = kwargs.get("timestamp", randomtimestamp(
            start=quote_position.mkt_timestamp, text=False))
        base_usd_price = self.data_factory.get_price(base_currency, timestamp)
        quote_usd_price = self.data_factory.get_price(
            quote_currency, timestamp)
        base_quantity = quote_usd_price * quote_quantity / base_usd_price
        args = {
            'base_currency': base_currency,
            'base_usd_price': base_usd_price,
            'base_quantity': base_quantity,
            'quote_currency': quote_currency,
            'quote_usd_price': quote_usd_price,
            'quote_quantity': quote_quantity,
            'timestamp': timestamp
        }
        if set_decimal(random.random()) > .5:
            fee_total_q = base_usd_price * \
                base_quantity * set_decimal(random.randint(0, 7) * .01)
            args['fee_quantity'] = fee_total_q
            args['fee_usd_price'] = args['quote_usd_price']
            args['fee_currency'] = args['quote_currency']

        tx = self.txn_factory('swap', **args)
        self.positions[base_currency].add(
            tx.id, tx.base_usd_price, tx.timestamp, tx.base_quantity)
        self.positions[quote_currency]._closes[tx.id] = {
            'timestamp': tx.timestamp,
            'price': quote_usd_price,
            'qty': quote_quantity,
            'realized_gain': 0
        }
        self.transactions.append(tx)

    def sell_factory(self, **kwargs):
        available_assets = list(x for x in self.positions.keys())
        quote_currency = 'usd'
        available_assets = list(
            [x for x in available_assets if x != quote_currency and self.positions[x].balance > 0])
        base_currency = kwargs.get(
            "base_currency", available_assets[random.randint(0, len(available_assets) - 1)])
        base_position = self.positions[base_currency]
        quote_position = self.positions[quote_currency]
        base_quantity = set_decimal(
            random.randint(0, int(base_position.balance)))

        timestamp = kwargs.get("timestamp", randomtimestamp(start=base_position.mkt_timestamp, text=False))
        base_usd_price = self.data_factory.get_price(base_currency, timestamp)
        quote_usd_price = set_decimal(1)
        quote_quantity = base_usd_price * base_quantity / quote_usd_price
        args = {
            'base_currency': base_currency,
            'base_usd_price': base_usd_price,
            'base_quantity': base_quantity,
            'quote_currency': quote_currency,
            'quote_usd_price': quote_usd_price,
            'quote_quantity': quote_quantity,
            'timestamp': timestamp
        }
        if set_decimal(random.random()) > .5:
            fee_total_q = base_usd_price * \
                base_quantity * \
                set_decimal(random.randint(0, 7)) * set_decimal(.01)
            args['fee_quantity'] = fee_total_q
            args['fee_usd_price'] = args['quote_usd_price']
            args['fee_currency'] = args['quote_currency']
        tx = self.txn_factory('sell', **args)
        self.positions['usd'].add(tx.id, set_decimal(
            1), tx.timestamp, tx.base_quantity)
        self.positions[base_currency]._closes[tx.id] = {
            'timestamp': tx.timestamp,
            'price': base_usd_price,
            'qty': base_quantity,
            'realized_gain': 0
        }
        self.transactions.append(tx)

    def txn_factory(self, tx_type, **kwargs):
        available_assets = list(
            [x for x in self.positions.keys() if x != 'usd'])
        base_currency = kwargs.get(
            "base_currency", available_assets[random.randint(0, len(available_assets) - 1)])
        base_usd_price = kwargs.get(
            "base_usd_price", set_decimal(random.random()) * 100)
        base_quantity = kwargs.get(
            "base_quantity", set_decimal(random.random()) * 10)

        fee_price = kwargs['quote_usd_price'] if 'quote_usd_price' in kwargs else base_usd_price
        fee_usd_price = kwargs.get("fee_usd_price", fee_price)
        fee_quantity = kwargs.get(
            "fee_quantity", set_decimal(random.random()) * 10)
        fee_total = fee_usd_price * fee_quantity
        sub_total = base_usd_price * base_quantity

        txn = {
            'type': tx_type,
            'timestamp': kwargs.get("timestamp", randomtimestamp(start_year=2018, text=False)),
            'id': kwargs.get("id", uuid.uuid4()),
            'base_currency': base_currency,
            'base_quantity': base_quantity,
            'base_usd_price': base_usd_price,
            'fee_currency': kwargs.get("fee_currency", base_currency),
            'fee_quantity': fee_quantity,
            'fee_usd_price': kwargs.get("fee_usd_price", None),
            'fee_total': fee_total,
            'sub_total': sub_total,
            'total': sub_total + fee_total,
            'taxable': kwargs.get("taxable", False)
        }
        if tx_type == "buy" or tx_type == "sell" or tx_type == "swap":
            available_assets = list(
                [x for x in self.positions.keys() if x != base_currency])
            quote_currency = kwargs.get(
                "quote_currency", available_assets[random.randint(0, len(available_assets) - 1)])
            quote_price = kwargs.get(
                "quote_price", set_decimal(random.random()) * 10)
            quote_usd_price = kwargs.get(
                "quote_usd_price", set_decimal(random.random()) * 100)
            quote_quantity = kwargs.get(
                "quote_quantity", (quote_usd_price / base_usd_price) * base_quantity)
            txn['quote_currency'] = quote_currency
            txn['quote_price'] = quote_price
            txn['quote_usd_price'] = quote_usd_price
            txn['quote_quantity'] = quote_quantity
        tx = Transaction(**txn)
        return tx


class HistoricalDataFactory:
    def __init__(self, start='1/1/2018', end=datetime.now(), freq='D'):
        self.date_range = pd.date_range(start=start, end=end, freq=freq)
        self.data = {
            'usd': pd.DataFrame(index=self.date_range, columns=['close']),
            'btc': pd.DataFrame(index=self.date_range, columns=['close']),
            'eth': pd.DataFrame(index=self.date_range, columns=['close']),
            'link': pd.DataFrame(index=self.date_range, columns=['close']),
            'usdc': pd.DataFrame(index=self.date_range, columns=['close']),
            'grt': pd.DataFrame(index=self.date_range, columns=['close']),
            'ada': pd.DataFrame(index=self.date_range, columns=['close']),
        }
        for d in range(self.date_range.size):
            if d == 0:
                self.data['btc'].iloc[d]['close'] = set_decimal(6000)
                self.data['eth'].iloc[d]['close'] = set_decimal(150)
                self.data['link'].iloc[d]['close'] = set_decimal(2)
                self.data['grt'].iloc[d]['close'] = set_decimal(.05)
                self.data['ada'].iloc[d]['close'] = set_decimal(.50)
            else:
                self.data['btc'].iloc[d]['close'] = set_decimal(self.data['btc'].iloc[d -
                                                                          1]['close'] * set_decimal(1 + random.uniform(-2, 2.5) / 100))
                self.data['eth'].iloc[d]['close'] = set_decimal(self.data['eth'].iloc[d -
                                                                          1]['close'] * set_decimal(1 + random.uniform(-3, 3.5) / 100))
                self.data['link'].iloc[d]['close'] = set_decimal(self.data['link'].iloc[d -
                                                                            1]['close'] * set_decimal(1 + random.uniform(-1, 1.5) / 100))
                self.data['grt'].iloc[d]['close'] = set_decimal(self.data['grt'].iloc[d -
                                                                          1]['close'] * set_decimal(1 + random.uniform(-1, 1.5) / 100))
                self.data['ada'].iloc[d]['close'] = set_decimal(self.data['ada'].iloc[d -
                                                                          1]['close'] * set_decimal(1 + random.uniform(-1, 1.5) / 100))
        self.data['usd']['close'] = set_decimal(1)
        self.data['usdc']['close'] = set_decimal(1)

    def get_price(self, symbol, timestamp):
        date = datetime(year=timestamp.year, month=timestamp.month, day=timestamp.day)
        return self.data[symbol].loc[date]['close']
