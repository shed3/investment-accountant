"""
The Bookkeeper manages the process of converting real word transactions to entries on the general ledger.

This means that the Bookkeeper must implements and enforce the interfaces between Transactions, Entries,
Positions, and the Ledger

Things to keep in mind:
 * Who/What is the source of truth and for what?
 * What pieces of data do classes ACTUALLY need to know to carry out their functions?

--- Entry ---

    - Required fields:
        * id
        * account_type
        * account
        * sub_account
        * timestamp
        * symbol
        * side
        * type
        * quantity
        * value
        * quote
        * close_quote
 
    - Created by: Transactions or Bookkeeper (for adjusting)
    - Verified by: Bookkeeper and Ledger (really should be one or the other)
    - Used by: Ledger

    * The decimal precision for quantity, value, quote, and close_quote

--- Transaction ---
    The Transaction interface is two fold - dict and class instance

    ## Dict ##
        - Required fields:
        * id
        * timestamp
        * type
        * base_currency
        * base_quantity
        * base_usd_price

        - Supported fields:
        * quote_currency
        * quote_quantity
        * quote_usd_price
        * fee_currency
        * fee_quantity
        * fee_usd_price

        * This schema is needed for transaction type detection
        * Additional fields may require class implementation

    ## Tx Class ##
        - affected_balances()
        * (Return) quantity gained or lost of each asset in transaction. Format: {symbol: +/- qty}
        * (Interface) This is how a transaction can plainly communicate its effect on asset positions

        - entries()
        * By default uses entry_template values to create set of entries detailing tx's effect on accounts
        * Can be overwritten or passed templates args to create a non standard entry set
        * Needs a way to know
        * (Return) all entries except those that will be generated from process_taxable
        * (Interface) This is how a transaction can communicate its effect on the general ledger

        - closing_entries({asset_position: [(price, qty)]})
        * Applies to taxable transacions ONLY
        * (Accept) Dict of asset_positions (base, quote or fee) to close, each with a list of price and quantity tuples. Format: {asset_position: [(price, qty), ...]}
        * (Return) List of Entry instances that comply with Entry interface
        * (Interface) This is how a taxable transaction works with positions to communicate its tax implications

--- Position ---
    A position is responsible for maintaining tax lot availability for a certain asset. 
    
    (Source of Truth)
    - Current market price of asset 
    - Current tax lot availability
    * Note current refers to the timestamp of the entry most recently added to the ledger

    - open(id, price, timestamp, qty)
    * create new tax lot with data from args

    - close(price, timestamp, qty)
    * record position closing event with data from args
    * Iterate through list of open tax lots sorted by tax liability decreasing lots' available qty and increasing close event's realized gains (repeat until filled)
    * (Return) List of tuples containing (price, qty) info of lots closed out off. Format: [(price, qty), ...]

--- Ledger ---
    A ledger is responsible for type checking/acceping entries.

    (Source of Truth)
    - Historical account balances (qty & usd value)

    - add(entry)
    * Validate that entry implements Entry interface then add to entry set (or reject)

--- Bookkeeper ----
    A Bookkeeper can
     * accept transaction -> update assets' position -> gets entries from tx -> create adjusting entries for affected positions -> record tx and adjusting entries on ledger
     * accept new price -> update assets' position -> create adjusting entries for asset positions -> record adjusting entries on ledger

     - import_prices(prices)
     * load in historical asset prices (EOD)
     * (Accept) df of df formatted dict of asset prices. Format: Dataframe or {symbol: []}


     - record_price(price, timestamp, symbol)
     * create adjusting entries for asset positions and update historical prices

     - import_txs(txs)
     * load in historical transacations and add them to ledger
     * generally requires historical data to function properly
     * (Accept) List of class instances or dicts that implement the Transaction interface

     - record_tx(tx)
     * gets entries from tx and adds them to ledger
     * calls record_price() for asset prices
     * (Accept) Class instances or dict that implement the Transaction interface
     * (Interface) Responsible for acccepting/rejecting txs based on proper Tx interface implementation and Tx's Entry interfaces implementation

"""

import logging
import re
import pytz
import pandas as pd
from datetime import datetime
from decimal import Decimal

from .transactions.base import BaseTx
from .transactions.interest_in_account import InterestInAccount
from .transactions.interest_in_stake import InterestInStake
from .transactions.reward import Reward
from .transactions.buy import Buy
from .transactions.deposit import Deposit
from .transactions.receive import Receive
from .transactions.sell import Sell
from .transactions.send import Send
from .transactions.swap import Swap
from .transactions.withdrawal import Withdrawal
from .transactions.components.entry import Entry
from .ledger import Ledger
from .position import Position
from .transactions.entry_config import CRYPTO_FAIR_VALUE_ADJ, UNREALIZED_GAIN_LOSS
from .utils import set_precision

log = logging.getLogger(__name__)

utc = pytz.UTC

# adjust to market and accrue unrealized gains.
adj_fair_value = {'side': "debit", 'type': 'adjust', 'quantity': 0, **CRYPTO_FAIR_VALUE_ADJ}
adj_unrealized_gains = {'side': "credit", 'type': 'adjust', 'quantity': 0, **UNREALIZED_GAIN_LOSS}
adj_to_fair_value_entries = [adj_fair_value, adj_unrealized_gains]


class BookKeeper:
    def __init__(self, freq="D", interval="1") -> None:
        self.positions = {'USD': Position('USD')}
        self.ledger = Ledger()
        self.tax_rates = {'long': set_precision(.25, 2), 'short': set_precision(.4, 2)}
        self.freq = freq
        self.interval = interval
        self.periods = []
        self.current_period_index = 0
        self.historical_prices = None

    ####### INTERFACE METHODS #######

    def import_prices(self, prices):
        """Set bookkeeper's historical data frame
        *Will require specifically formatted dataframe

        Args:
            prices (pd.Dataframe): Historical prices data
        """
        prices.index = prices.index.tz_localize(tz='UTC').ceil(self.interval + self.freq)
        self.historical_prices = prices

    def record_price(self, timestamp, symbol, price):
        pass
    
    def import_txs(self, txs, auto_detect=True):
        if auto_detect:
            transactions = sorted(txs, key=lambda x: dict(x).get('timestamp'))
        else:
            transactions = sorted(txs, key=lambda x: x.timestamp)
        for tx in transactions:
            self.record_tx(tx, auto_detect)

    def record_tx(self, tx, auto_detect):

        # attempted to instanciate transaction class from tx dict
        if auto_detect:
            tx = self.detect_type(tx)
        
        # set period date list
        if len(self.periods) < 1:
            self.interpolate_date_range((tx))

        # tx occured after current period close date -> close periods
        if tx.timestamp > self.periods[self.current_period_index]:
            self.close_periods(tx.timestamp)

        # checks that positions are initialized and market prices are updated
        self.update_positions(tx)

        # adjust positions of affected assets
        affected_positions = tx.affected_balances()
        for symbol, qty in affected_positions.items():
            position, asset = list([[key, val] for key, val in tx.assets.items() if val.symbol == symbol])[0]
            if qty > 0:
                # open a new position with asset info
                self.positions[symbol].open(tx.id, asset.usd_price, tx.timestamp, qty)
            elif hasattr(tx, 'taxable_assets') and position not in tx.taxable_assets:
                # close out position the affected amount
                self.positions[symbol].close(tx.id, asset.usd_price, tx.timestamp, qty)

        # get base entries
        entries = tx.entries()

        # create closing entries for
        if hasattr(tx, 'taxable_assets'):
            closing_templates = {}
            for taxable_asset in tx.taxable_assets:
                # sort all open tax lots for tx's base currency position
                asset = tx.assets[taxable_asset]
                symbol = asset.symbol
                position = self.positions[symbol]
                closing_templates[taxable_asset] = position.close(tx.id, asset.usd_price, tx.timestamp, asset.quantity)
            entries += tx.closing_entries(closing_templates)

        # Entry validation checks
        entry_dicts = list([x.to_dict() for x in entries])
        entry_check = self.validate_entry_set(entry_dicts)
        if not entry_check['valid']:
            log.debug(entry_check)

        # add new tx's entries to ledger
        for entry in entries:
            self.ledger.add_entry(entry.to_dict())


    ####### HELPER METHODS #######

    

    def update_positions(self, tx):
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
        for asset in tx.assets.values():
            self.positions[asset.symbol].adjust_to_mtk(asset.usd_price, tx.timestamp)

    def interpolate_date_range(self, tx):
        # create list of dates that represent start and end times of periods
        if len(self.periods) < 1:
            start = tx.timestamp
            end = pd.Timestamp.now(tz=utc)
            freq = self.interval + self.freq
            tz = pytz.UTC
            period_df = pd.date_range(start=start, end=end, freq=freq, tz=tz, normalize=True)
            self.periods = period_df

    def get_price(self, timestamp, symbol):
        """Get price of an asset at specified timestamp

        Args:
            timestamp ([type]): [description]
            symbol ([type]): [description]

        Returns:
            [type]: [description]
        """
        return set_precision(self.historical_prices.at[timestamp.ceil(self.interval + self.freq), symbol], 18)

    def get_period_entries(self):
        """Returns entries that close out current period

        Args:
            price ([type]): [description]
            timestamp ([type]): [description]

        Returns:
            [type]: [description]
        """
        all_entries = []
        # get all open tax lots for each symbol
        for symbol in self.positions.keys():
            # get price change and multiple by lot quantity to get value.
            timestamp = self.periods[self.current_period_index]
            curr_price = self.get_price(timestamp, symbol)
            all_entries += self.create_adjusting_entries(symbol, curr_price, timestamp)
            self.positions[symbol].adjust_to_mtk(curr_price, timestamp)
        return all_entries

    def create_adjusting_entries(self, symbol, curr_price, timestamp):
        adj_entries = []
        position = self.positions[symbol]
        change_price = curr_price - position.mkt_price
        for tax_lot in position.open_tax_lots:
            change_val = tax_lot['available_qty'] * change_price
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
        elif self.freq == "M":
            num_periods = period_timedelta.months
        elif self.freq == "Y":
            num_periods = period_timedelta.months

        closing_entries = []
        # close all past periods
        for x in range(num_periods):
            period_entries = self.get_period_entries()
            closing_entries += period_entries
            self.current_period_index += 1
        if len(closing_entries) > 0:
            for entry in closing_entries:
                self.ledger.add_entry(entry.to_dict())

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

