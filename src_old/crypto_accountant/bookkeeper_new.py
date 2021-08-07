from datetime import date, datetime, timedelta
from typing import ByteString
from .base_account import BaseAccount
from .transaction import Transaction
from .ledger import Ledger
from .utils import query_df
from .config import cpa_config
from decimal import Decimal
import logging
import dateutil.parser

log = logging.getLogger(__name__)

class BookKeeper(BaseAccount):

    def __init__(self, transactions=[], config=cpa_config) -> None:
        super().__init__( 'Book', 'All', 'Main Book', transactions)
        self.config = config
        self.accounts = []
        self.create_accounts()


    # Main function. Creates accounts, processes transactions, performs trial balance, and produces a final ledger.

    def create_accounts(self):
        for type, tx_configs in cpa_config.items():
            for tx_config in tx_configs:
                account_txs = list([tx for tx in self._transactions if tx.tx_type == type])
                if len(account_txs) > 0:
                    self.accounts.append(BaseAccount(tx_config['account'], tx_config['sub_account'], tx_config['sub_account'], account_txs))
        

    def get_balance_sheet(self, date='now'):
        pass

    def get_income_statement(self, period='this month'):
        pass

    def add_transactions(self, transactions):
        # For each transaction: add to self.transactions (check for duplicates), pass to relevant accounts (accts responsible for adding to their journal)
        # Then process transactions
        pass


    def process_transactions(self):
        # Responsible for handling taxable transactions correctly. 
        # Updates balances after
        pass

    def trial_balance(self):
    # makes sure everything looks good
        pass


    def close_positions(self):
        # grab transaction ids where incomplete not equal to none (or taxable equal to true?)
        # find all positions for asset in question
        # create closing entries
        # send adjusting transactions to affected accounts
        # update the incomplete somehow
        pass
    
    def get_open_positions(self, tx):
        symbol = tx.baseCurrency
        positions = self.journal.raw_ledger
        positions = positions.loc[positions['timestamp'] < tx.timestamp]
        current_positions = query_df(positions, 'symbol', symbol)
        current_positions = query_df(current_positions, 'taxable', False)
        current_positions = current_positions.fillna({'credit_value': 0, 'debit_value': 0,'credit_quantity': 0, 'debit_quantity': 0})
        current_positions = current_positions.groupby('timestamp').sum(numeric_only=False)
        current_positions['balance'] = current_positions['debit_value'] - current_positions['credit_value']

        # log.debug('All Positions found:\n{}\n'.format(
        #     current_positions[['credit_value', 'debit_value', 'balance']]))
        # Mark open positions and filter for only open positions.
        current_positions['open'] = current_positions['balance'] > 0
        open_positions = query_df(current_positions, 'open', True)
        open_positions = open_positions.reset_index().set_index(['account', 'sub_account', 'timestamp', 'position', 'tx_type']).sort_index()
        return open_positions

    def get_best_position(self, tx, tax_rate_short=Decimal(str(.35)), tax_rate_long=Decimal(str(.2))):
        current_positions = self.test_open_positions(tx)
        if current_positions.empty:
            return
        else:
            positions = current_positions.reset_index()
            # Convert tx timestamp to datetime object
            # convert convert position df timestamp column to datetime object
            # Create row in df for timedifference in seconds
            # Base calculations off seconds column
            log.debug('Getting best positions out of found positions:\n{}'.format(positions))
            positions['change_usd'] = Decimal(str(tx.baseUsdPrice)) - positions['position'] 
            positions['change_timestamp'] = tx.timestamp - positions['timestamp']
            positions['change_seconds'] = positions['change_timestamp'].apply(lambda x: x.seconds)
            positions['change_days'] = positions['change_timestamp'].apply(lambda x: x.days)
            positions['short_term'] = positions['change_days'] < 365
            positions['tax_rate'] = positions['short_term'].apply(lambda x: tax_rate_short if x == True else tax_rate_long)
            # Check for short or long term tax liability based on original timestamp and transaction timestamp
            positions['tax_liability_price'] = positions['change_usd'] * positions['tax_rate']

            positions = positions.reset_index().set_index(['account', 'symbol', 'tax_liability_price','position'])
            positions.sort_index(inplace=True)
            position_balances = positions['debit_value', 'debit_quantity', 'credit_value', 'credit_quantity'].apply(lambda x: x.sum())
            positions.groupby(level=[0, 1, 2, 3]).sum()
            return positions.iloc[[0]].reset_index().to_dict(orient='records')[0]
        
    def get_first_position(self, current_positions):
        current_positions.sort_index(inplace=True)
        return current_positions.groupby(level=[0, 1, 3]).sum()

    def get_last_opened(self, current_positions):
        current_positions.sort_index(ascending=False, inplace=True)
        return current_positions.groupby(level=[0, 1, 3]).sum()

    def get_highest_open(self, current_positions):
        positions = current_positions.reset_index().set_index(['account', 'symbol', 'position'])
        positions.sort_index(ascending=False, inplace=True)
        return positions.groupby(level=[0, 1, 2]).sum()

    def get_lowest_open(self, current_positions):
        positions = current_positions.reset_index().set_index(['account', 'symbol', 'position'])
        positions.sort_index(inplace=True)
        return positions.groupby(level=[0, 1, 2]).sum()

    def generate_closing_entries(self, tx,):
        remainder = tx.baseQuantity
        tx_copy = tx.to_dict
        i = 0
        all_entries = []
        while remainder > 0:
            position = self.get_best_position(tx)
            if position:
                log.debug('Current Position:\n{}\n'.format(position))
                available_quantity = position['balance'] 

                r = remainder - available_quantity
                log.debug('Remainder: {}\n'.format(r))
                close_quantity = 0
                if r < 0:
                    close_quantity = remainder
                    # determine short term and long term and calc taxes here
                else:
                    close_quantity = available_quantity
                
                close_value = close_quantity * position['position']
                # piece of total that we are crediting in this transaction.
                close_total = tx.baseUsdPrice * close_quantity
                close_quote_quantity = close_total / tx.quoteUsdPrice
                close_gain = close_total - close_value  # usd gain of position closed

                tx_copy['closePosition'] = position['position']
                tx_copy['closeQuantity'] = close_quantity
                tx_copy['closeQuoteQuantity'] = close_quote_quantity
                if 'quoteUsdPrice' in position:  # why do we need this?
                    tx_copy['quoteUsdPrice'] = position['quoteUsdPrice']
                tx_copy['closeValue'] = close_value
                tx_copy['closeGain'] = close_gain
                tx_copy['closeTotal'] = close_total

                confs = cpa_config[tx_copy['tx_type']]
                new_entries = list([self._tx_mapper(tx_copy, conf) for conf in confs])
                all_entries += new_entries
            else:
                break
            i += 1
            remainder -= close_quantity
        return all_entries

    def close_positions(self):
        incomplete_txs_full = list([tx for tx in self._transactions if tx.id in self.incomplete_txs])
        for tx in incomplete_txs_full:
            entries = self.generate_closing_entries(tx)


        return incomplete_txs_full
    # get all incomplete transactions 
    #     for incomplete transactions 
    #       while remainding qty > 0
    #           grab best position
    #           create entries 
    #           add to all entries list
    #       calling adjust tx with id and entries