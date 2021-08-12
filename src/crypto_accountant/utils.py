from datetime import date, datetime, time
import logging
from os import replace
from google.api_core.datetime_helpers import DatetimeWithNanoseconds
from decimal import Decimal, InvalidOperation
import pandas as pd
from src.crypto_accountant.transactions.interest_in_account import InterestInAccount
from src.crypto_accountant.transactions.interest_in_stake import InterestInStake
from src.crypto_accountant.transactions.reward import Reward
from src.crypto_accountant.transactions.buy import Buy
from src.crypto_accountant.transactions.deposit import Deposit
from src.crypto_accountant.transactions.receive import Receive
from src.crypto_accountant.transactions.sell import Sell
from src.crypto_accountant.transactions.send import Send
from src.crypto_accountant.transactions.swap import Swap
from src.crypto_accountant.transactions.withdrawal import Withdrawal
import re
import pytz

utc=pytz.UTC

log = logging.getLogger(__name__)

def check_type(val, check_string=False, types=[Decimal]):
    original_type = type(val)
    if isinstance(val, (int, float)):
        val = Decimal(str(val))
    if isinstance(val, (datetime, DatetimeWithNanoseconds, date, time)):
        val = pd.Timestamp(val).replace(tzinfo=utc)
    if type(val) == DatetimeWithNanoseconds:
        val = pd.Timestamp(val).replace(tzinfo=utc)
    if check_string:
        if isinstance(val, str):
            for t in types:
                try:
                    val = t(val)
                except:
                    pass        
    return val

def create_tx(**kwargs):
    type = kwargs.get('type', 'other')
    args = {}
    for key, value in kwargs.items():
        key = key.replace('-','_')
        key = key.replace(' ','_')
        key_pieces = re.findall('[A-Za-z][^A-Z]*', key)
        key = '_'.join(key_pieces)
        key = key.replace('__','_')
        key = key.lower()
        if key in ['tx_type', 'txn_type', 'type', 'trans_type', 'transaction_type']:
            tx_type = value
            args['type'] = tx_type
        elif key in ['timestamp', 'time', 'date', 'time_stamp']:
            args['timestamp'] = check_type(value, check_string=True, types=[pd.Timestamp])
        else:
            args[key] = check_type(value)

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
        elif type == 'interest_in_stake':
            return InterestInStake(**args)  
        elif type == 'interest_in_account':
            return InterestInAccount(**args)       
        elif type == 'interest_in':
            return InterestInAccount(**args)                                
        else:
            return False
            # raise Exception('TYPE {} NOT CREATED'.format(type))
    else:
        return False  
        # raise Exception('NO TYPE INCLUDED')


    # if tx['type'] == 'reward':
    #     return Deposit(tx)  
    # if tx['type'] == 'interest_earned_account':
    #     return Deposit(tx)  
    # if tx['type'] == 'interest_earned_stake':
    #     return Deposit(tx)     


def query_df(df, col, val):
    return df.loc[df[col] == val]
    
    
