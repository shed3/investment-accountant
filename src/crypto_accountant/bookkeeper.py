import logging
import re
from datetime import datetime
from decimal import Decimal

import pandas as pd
import pytz

from .ledger import Ledger
from .position import Position
from .transactions.base import BaseTx
from .transactions.buy import Buy
from .transactions.components.entry import Entry
from .transactions.deposit import Deposit
from .transactions.entry_config import (CRYPTO_FAIR_VALUE_ADJ,
                                        UNREALIZED_GAIN_LOSS)
from .transactions.interest_in_account import InterestInAccount
from .transactions.interest_in_stake import InterestInStake
from .transactions.receive import Receive
from .transactions.reward import Reward
from .transactions.sell import Sell
from .transactions.send import Send
from .transactions.swap import Swap
from .transactions.withdrawal import Withdrawal
from .utils import set_precision

log = logging.getLogger(__name__)
utc = pytz.UTC


class BookKeeper:
    def __init__(self, freq="D", interval="1") -> None:
        self.positions = {}
        self.ledger = Ledger()
        self.tax_rates = {
            'long': set_precision(.25, 2), 'short': set_precision(.4, 2)}
        self.freq = freq
        self.interval = interval
        self.period = interval + freq
        self.periods = []
        self.current_period_index = 0
        self.historical_data = None

    def set_historical_data(self, data, tz='UTC', ceil=True):
        """Set bookkeeper's historical data frame. 
        
        WILL OVERWRITE EXISTING DATA

        Args:
            data (DataFrame): Must have index timestamp and columns symbols.
        """
        if ceil:
            data.index = data.index.ceil(self.interval + self.freq)
        if tz:
            data.index = data.index.tz_localize(tz=tz)

        self.historical_data = data

    def add_historical_data(self, data, df=False, tz='UTC', ceil=False):
        """Add data to bookkeeper's historical data frame. Will not overwrite.

        Args:
            data (DataFrame): Must have index timestamp and columns symbols.
        """
        if df:
            if ceil:
                data.index = data.index.ceil(self.interval + self.freq)
            if tz:
                data.index = data.index.tz_localize(tz=tz)
        else:
            for timestamp, value in data.items():
                new_data = []
                if ceil:
                    timestamp = timestamp.ceil(self.interval + self.freq)
                if tz:
                    timestamp = timestamp.tz_localize(tz=tz)
                new_data.append({timestamp: value})
            data = new_data
        self.historical_data = pd.concat(self.historical_data, data)

    def get_price(self, timestamp, symbol):
        """Get price of an asset at specified timestamp from historical_data

        Args:
            timestamp (Timestamp): timestamp to retrieve
            symbol (str): symbol, uppercase, to retrieve

        Returns:
            Decimal: price of the symbol at provided timestamp
        """
        return set_precision(self.historical_data.at[timestamp, symbol], 18)

    def add_tx(self, tx, auto_detect=True):
        """Add a transaction to the ledger
        
        This is the main interface for interacting with transactions. It is responsible for getting entries, updating positions, and adding entries to ledger as well as calling any follow up functions.

        Updates self.ledger, self.historical_data, and self.positions

        Args:
            tx (BaseTx | dict): Needs to be a subclass of BaseTx. If autodetect=True, may be a dictionary of arguments to create a transaction object
            auto_detect (bool, optional): If True, check type and create instance of correlating subclass of BaseTx. Defaults to True.
        """
        if auto_detect:
            tx = self.detect_type(tx)

        # checks that positions are initialized and periods have been created
        self._add_prechecks(tx)

        # tx occured after current period close date -> close periods
        if tx.timestamp > self.periods[self.current_period_index]:
            self.close_periods(tx.timestamp)
        if tx.taxable:
            entries = self.process_taxable(tx)
        else:
            entries = tx.get_entries()
            # need to close non taxable positions here?

        affected_positions = tx.get_affected_balances()
        for symbol, qty in affected_positions.items():
            position, asset = list([[key, val] for key, val in tx.assets.items()
                                    if val.symbol == symbol])[0]
            if qty > 0:
                # add tx to debit assets to positions
                self.positions[symbol].add(
                    tx.id, asset.usd_price, tx.timestamp, asset.quantity)
            elif getattr(tx, 'taxable_assets', False):
                if position not in tx.taxable_assets.keys():
                    self.positions[symbol].close(
                        tx.id, asset.usd_price, tx.timestamp, fill_quantity=-qty)

        # Entry validation checks
        # entry_dicts = list([x.to_dict() for x in entries])
        # entry_check = self.validate_entry_set(entry_dicts)
        # if not entry_check['valid']:
        #     log.debug(entry_check)

        # add new tx's entries to ledger
        for entry in entries:
            self.ledger.add_entry(entry.to_dict())

    def add_txs(self, txs, auto_detect=True):
        """Helper for adding bulk transactions. 

        Calls add_tx() for each transaction, passing auto_detect.

        Args:
            txs ([BaseTx | dict]): Needs to be a list of objects that are instances of a subclass of BaseTx. If autodetect=True, may be a list of dictionaries containing arguments to create a transaction object
            auto_detect (bool, optional): If True, check type and create instance of correlating subclass of BaseTx. Defaults to True.
        """
        if auto_detect:
            transactions = sorted(txs, key=lambda x: dict(x).get('timestamp'))
        else:
            transactions = sorted(txs, key=lambda x: x.timestamp)
        for tx in transactions:
            self.add_tx(tx, auto_detect)

    def _add_prechecks(self, tx):
        """Creates and updates positions if necessary. Creates periods on first run

        Checks all tx assets and creates and updates positions. If initial transaction, creates periods.

        Updates self.positions and self.periods.

        Args:
            tx (BaseTx): An instance of a subclass of BaseTx
        """
        # create position from base_currency if needed
        if tx.assets['base'].symbol not in self.positions:
            self.positions[tx.assets['base'].symbol] = Position(
                tx.assets['base'].symbol)

        # create position from quote_currency if needed
        if 'quote' in tx.assets and tx.assets['quote'].symbol not in self.positions:
            self.positions[tx.assets['quote'].symbol] = Position(
                tx.assets['quote'].symbol)

        # create position from fee_currency if needed
        if 'fee' in tx.assets and tx.assets['fee'].symbol not in self.positions:
            self.positions[tx.assets['fee'].symbol] = Position(
                tx.assets['fee'].symbol)

        # adjust positions to mkt price from tx assets
        prices = [{symbol: asset.usd_price} for symbol, asset in tx.assets.items()]
        self.add_historical_data({tx.timestamp: prices})

        #TODO Not sure we need the below
        for symbol, price in prices():
            self.positions[symbol].adjust_to_mtk(
                price, tx.timestamp)

        if len(self.periods) < 1:
            start = tx.timestamp
            end = pd.Timestamp.now(tz=utc)
            freq = self.interval + self.freq
            tz = pytz.UTC
            period_df = pd.date_range(
                start=start, end=end, freq=freq, tz=tz, normalize=True)
            self.periods = period_df

    def process_taxable(self, tx):
        """Processes taxable transactions.

        Uses positions and historical data to create adjust and close entries for taxable transactions. 

        Args:
            tx (BaseTx): Subclass of BaseTx. Currently only Sell, Send, Swap.

        Returns:
            [Entry]: All required entries as Entry objects.
        """

        # check if tx has fee and isnt taxable
        if 'fee' not in tx.taxable_assets.keys() and len(tx.taxable_assets.keys()) > 0:
            # fee isnt in taxable assets so just overwrite entry config
            entries = tx.get_entries(
                config={'debit': tx.entry_template['debit']})
        elif len(tx.taxable_assets.keys()) == 1:
            # the fee is the only taxable asset
            entries = tx.get_entries()
        else:
            # base or quote as well as fee are in taxable assets so just get debit entries
            entries = tx.generate_debit_entry()

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

                position.close(
                    tx.id, tx.assets[taxable_asset].usd_price, tx.timestamp, tax_lot_usage)

                closing_entries = tx.generate_credit_entries(
                    taxable_asset, lot_price, fillable_qty, type=tx_type)

                entries += closing_entries
                filled_qty += fillable_qty
                del lots[0]

        return entries

    def get_period_entries(self):
        """Returns closing entries for end of period.

        This will eventually be responsible for more. Currently only handles adjusting fair value entries for all positions at the end of the period.

        Returns:
            [Entry]: All required entries as Entry objects.
        """
        all_entries = []
        # get all open tax lots for each symbol
        for symbol in self.positions.keys():
            # get price change and multiple by lot quantity to get value.
            timestamp = self.periods[self.current_period_index]
            curr_price = self.get_price(timestamp, symbol)
            all_entries += self.create_adjusting_entries(
                symbol, curr_price, timestamp)
        return all_entries

    def create_adjusting_entries(self, symbol, curr_price, timestamp):
        adj_entries = []
        position = self.positions[symbol]
        change_price = curr_price - position.mkt_price
        self.positions[symbol].adjust_to_mtk(curr_price, timestamp)
        for tax_lot in position.open_tax_lots:
            change_val = tax_lot['qty'] * change_price
            if change_val != 0:
                for entry in adj_to_fair_value_entries:
                    adj_config = {
                        **entry,
                        # Quote price is original position entry. Value is change in market value of quantity.
                        'id': tax_lot['id'],
                        'timestamp': timestamp,
                        'symbol': symbol,
                        'quote': tax_lot['price'],
                        'value': change_val,
                        'close_quote': curr_price,
                    }
                    adj_entries.append(Entry(**adj_config))
        return adj_entries

    def close_periods(self, timestamp):
        # determine number of periods to close between tx timestamp and last entry
        # create closing entries for each period
        # run trial balance on each period being closed
        # add number of closing periods to current period index

        # move below to place calling this function
        period_timedelta = timestamp - self.periods[self.current_period_index]
        if self.freq == "H":
            num_periods = period_timedelta.hours
        elif self.freq == "D":
            num_periods = period_timedelta.days
        elif self.freq == "W":
            num_periods = period_timedelta.weeks

        closing_entries = []
        # close all past periods
        for x in range(num_periods + 1):
            period_entries = self.get_period_entries()
            closing_entries += period_entries
            self.current_period_index += 1
        if len(closing_entries) > 0:
            for entry in closing_entries:
                self.ledger.add_entry(entry.to_dict())

    def detect_type(self, tx):
        # if auto detect is allowed and the tx arg isnt already some form of BaseTx
        # create an instance of the correct tx class based on tx data
        if not isinstance(tx, BaseTx):
            type = tx.get('type', 'other')
            args = {}
            for key, value in tx.items():
                key = key.replace('-', '_')
                key = key.replace(' ', '_')
                key_pieces = re.findall('[A-Za-z][^A-Z]*', key)
                key = '_'.join(key_pieces)
                key = key.replace('__', '_')
                key = key.lower()
                if key in ['tx_type', 'txn_type', 'type', 'trans_type', 'transaction_type']:
                    tx_type = value
                    args['type'] = tx_type
                elif key in ['timestamp', 'time', 'date', 'time_stamp']:
                    args['timestamp'] = value
                else:
                    args[key] = value

            if 'type' in args.keys():
                type = args['type']
                if type == 'deposit':
                    return Deposit(**args)
                elif type == 'withdrawal':
                    return Withdrawal(**args)
                elif type == 'buy':
                    return Buy(**args)
                elif type == 'sell':
                    return Sell(**args)
                elif type == 'swap':
                    return Swap(**args)
                elif type == 'send':
                    return Send(**args)
                elif type == 'receive':
                    return Receive(**args)
                elif type == 'reward':
                    return Reward(**args)
                elif type == 'interest-in-stake':
                    return InterestInStake(**args)
                elif type == 'interest-in-account':
                    return InterestInAccount(**args)
                # elif type == 'interest_in':
                    # return InterestInAccount(**args)
                else:
                    raise Exception('TYPE {} NOT CREATED'.format(type))

        return tx


def validate_entry_set(self, entries):
    
    """
    1. Check required fields are present and all fields have correct data type
        Required:
        * timestamp -> datetime
        * account_type -> str
        * account -> str
        * symbol -> str
        * side -> str ("debit" or "credit")
        * type -> str
        * quantity -> Decimal
        * value -> Decimal
        * quote -> Decimal
        Optional:
        * sub_account -> str
        * close_quote -> Decimal

    2. Check that sum of all entries debits and credits balance
        Passing Check
        *  sum debit values - sum credit values = 0
        *  (???) sum debit qty - sum credit qty = 0
    """
    debits = 0
    credits = 0
    required_fields = ['timestamp', 'account_type', 'account',
                       'symbol', 'side', 'type', 'quantity', 'value', 'quote']
    for entry in entries:
        if not all(field in entry for field in required_fields):
            return {
                'valid': False,
                'reason': "Entry missing required field. Make sure all entries contain fields: 'timestamp', 'account_type', 'account', 'symbol', 'side', 'type', 'quantity', 'value', 'quote'"
            }
        if not isinstance(entry['timestamp'], datetime):
            return {
                'valid': False,
                'reason': 'Incorrect timestamp format. Must be datetime instance'
            }
        if not isinstance(entry['account_type'],  str):
            return {
                'valid': False,
                'reason': 'Incorrect account_type format. Must be string'
            }
        if not isinstance(entry['account'],  str):
            return {
                'valid': False,
                'reason': 'Incorrect account format. Must be string'
            }
        if not isinstance(entry['symbol'],  str):
            return {
                'valid': False,
                'reason': 'Incorrect symbol format. Must be string'
            }
        if entry['side'] != 'credit' and entry['side'] != 'debit':
            return {
                'valid': False,
                'reason': 'Incorrect side format. Must be credit or debit'
            }
        if not isinstance(entry['type'],  str):
            return {
                'valid': False,
                'reason': 'Incorrect type format. Must be string'
            }
        if not isinstance(entry['quantity'],  Decimal):
            return {
                'valid': False,
                'reason': 'Incorrect quantity format. Must be Decimal'
            }
        if not isinstance(entry['value'],  Decimal):
            return {
                'valid': False,
                'reason': 'Incorrect value format. Must be Decimal'
            }
        if not isinstance(entry['quote'],  Decimal):
            return {
                'valid': False,
                'reason': 'Incorrect quote format. Must be Decimal'
            }
        if 'sub_account' in entry and not isinstance(entry['sub_account'],  str):
            return {
                'valid': False,
                'reason': 'Incorrect sub_account format. Must be Decimal'
            }
        if 'close_quote' in entry and not isinstance(entry['close_quote'],  Decimal):
            return {
                'valid': False,
                'reason': 'Incorrect close_quote format. Must be Decimal'
            }

        # if you have made it this far you have passed the entry formatting checks!

        if entry['side'] == 'credit':
            credits += entry['value']
        else:
            debits += entry['value']

    if credits - debits != 0:
        return {
            'valid': False,
            'reason': 'Credit and debit entries do not balance. Diff = ' + str(credits - debits)
        }

    return {'valid': True}
