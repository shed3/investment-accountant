import pytz
import pandas as pd
from datetime import datetime, tzinfo
from decimal import Decimal

from .transactions.base import BaseTx
from .transactions.components.entry import Entry
from .ledger import Ledger
from .position import Position
from .transactions.entry_config import CRYPTO_FAIR_VALUE_ADJ, UNREALIZED_GAIN_LOSS
from .utils import check_type, create_tx

utc = pytz.UTC

# adjust to market and accrue unrealized gains.
adj_fair_value = {'side': "debit", 'type': 'adjust', 'quantity': 0, **CRYPTO_FAIR_VALUE_ADJ}
adj_unrealized_gains = {'side': "credit", 'type': 'adjust', 'quantity': 0, **UNREALIZED_GAIN_LOSS}
adj_to_fair_value_entries = [adj_fair_value, adj_unrealized_gains]

class BookKeeper:
    def __init__(self, freq="D", interval="1") -> None:
        self.positions = {'usd': Position('usd')}
        self.ledger = Ledger()
        self.tax_rates = {'long': check_type(.25), 'short': check_type(.4)}
        self.freq = freq
        self.interval = interval
        self.periods = []
        self.current_period_index = 0
        self.historical_data = None
        self.historical_data_change = None

    def detect_type(self, tx):
        # if auto detect is allowed and the tx arg isnt already some form of BaseTx
        # create an instance of the correct tx class based on tx data
        if not isinstance(tx, BaseTx):
            tx = create_tx(**tx)
        return tx

    def add_historical_data(self, data):
        """Set bookkeeper's historical data frame
        *Will require specifically formatted dataframe

        Args:
            data ([type]): [description]
        """
        data.index = data.index.tz_localize(tz='UTC').ceil(self.interval + self.freq)
        self.historical_data = data
        self.historical_data_change = data.diff()

    def _add_prechecks(self, tx):
        # create position from base_currency if needed
        if tx.assets['base'].symbol not in self.positions:
            self.positions[tx.assets['base'].symbol] = Position(
                tx.assets['base'].symbol)

         # create position from quote_currency if needed
        if 'quote' in tx.assets and tx.assets['quote'].symbol not in self.positions:
            self.positions[tx.assets['quote'].symbol] = Position(
                tx.assets['quote'].symbol)

        if len(self.periods) < 1:
            start=tx.timestamp
            end=pd.Timestamp.now(tz=utc)
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
        return self.historical_data.at[timestamp.ceil(self.interval + self.freq), symbol]

    def get_price_change(self, timestamp, symbol):
        """Get change in price of an asset since end of previous period at specified timestamp

        Args:
            timestamp ([type]): [description]
            symbol ([type]): [description]

        Returns:
            [type]: [description]
        """
        return self.historical_data_change.at[timestamp.round(self.interval + self.freq), symbol]
    

    def create_closing_entries(self):
        all_entries = []
        # get all open tax lots for each symbol
        for symbol, position in self.positions.items():
            symbol = symbol.upper()
            # get price change and multiple by lot quantity to get value.
            timestamp = self.periods[self.current_period_index]
            curr_price = self.get_price(timestamp, symbol)
            change_price = self.get_price_change(timestamp, symbol)
            for tax_lot in position.open_tax_lots:
                change_val = tax_lot['qty'] * change_price
                # print(symbol, change_val, tax_lot['qty'], curr_price, change_price)
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
                    all_entries.append(Entry(**adj_config))
        return all_entries

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
            period_entries = self.create_closing_entries()
            closing_entries += period_entries
            self.current_period_index += 1
        if len(closing_entries) > 0:
            for entry in closing_entries:
                self.ledger.add_entry(entry.to_dict())


    def add_txs(self, txs, auto_detect=True):
        transactions = sorted(txs, key=lambda x: dict(x).get('timestamp'))
        for tx in transactions:
            self.add_tx(tx, auto_detect)

    def add_tx(self, tx, auto_detect=True):
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

        affected_positions = tx.get_affected_balances()
        for symbol, qty in affected_positions.items():
            if qty > 0:
                # add tx to debit assets to positions
                asset = list([item for item in tx.assets.values()
                             if item.symbol == symbol])[0]
                self.positions[symbol].add(
                    tx.id, asset.usd_price, tx.timestamp, asset.quantity)

        entry_dicts = list([x.to_dict() for x in entries])
        entry_check = self.validate_entry_set(entry_dicts)
        if not entry_check['valid']:
            print(entry_check)

        # add new tx's entries to ledger
        for entry in entries:
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

    def process_taxable(self, tx):

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

                position.close(tx.id, tx.assets[taxable_asset].usd_price, tx.timestamp, tax_lot_usage)

                closing_entries = tx.generate_credit_entries(
                    taxable_asset, lot_price, fillable_qty, type=tx_type)

                entries += closing_entries
                filled_qty += fillable_qty
                del lots[0]

        return entries
