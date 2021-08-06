from datetime import datetime
from .account import Account
from .ledger import Ledger
from .utils import query_df
from .config import account_configs
from decimal import Decimal
import logging
import dateutil.parser

log = logging.getLogger(__name__)

class BookKeeper:

    def __init__(self, config=account_configs) -> None:
        self.config = config
        self.book = Ledger()
        self.accounts = {}


    @property
    def incomplete_accounts(self):
        incomplete_accts = []
        for tx_type, acct in self.accounts.items():
            if acct.requires_adjustment:
                incomplete_accts.append(tx_type)
        return incomplete_accts


    def add_account(self, tx_type):
        for config in self.config[tx_type]:
            new_acct = Account(config['account'], config['sub_account'])
            if tx_type in self.accounts:
                self.accounts[tx_type].append(new_acct)
            else:
                self.accounts[tx_type] = [new_acct]


    def add_accounts(self, tx_types):
        for tx_type in tx_types:
            self.add_account(tx_type)
    
    def add_tx(self, tx):
        # add tx to all affected accounts
        if tx.tx_type not in self.accounts:
            self.add_account(tx.tx_type)

        if tx.taxable:
            tx = self.process_taxable(tx)

        entries =[]
        for affected_acct in self.accounts[tx.tx_type]:
            entries += affected_acct.add_tx(tx)

        for entry in entries:
            self.book.add_entry(entry)

    def add_txs(self, txs):
        for tx in txs:
            self.add_tx(tx)

   
    def process_taxable(self, tx):
        # Responsible for handling taxable transactions correctly. 
        # check if any entries since tx.timestamp, ensure we use all available if so and reprocess after.

        # get open positions for symbol
        # get entries

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

                confs = account_configs[tx_copy['tx_type']]
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