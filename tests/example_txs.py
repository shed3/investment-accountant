import uuid
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation

import pandas as pd
from src.crypto_accountant.position import Position
from src.crypto_accountant.transactions.buy import Buy
from src.crypto_accountant.transactions.deposit import Deposit
from src.crypto_accountant.transactions.receive import Receive
from src.crypto_accountant.transactions.sell import Sell
from src.crypto_accountant.transactions.send import Send
from src.crypto_accountant.transactions.swap import Swap
from src.crypto_accountant.transactions.withdrawal import Withdrawal
from src.crypto_accountant.utils import check_type


def no_fee_no_positions():

    # Deposit 10,000 USD
    deposit_initial = {
        'type': 'deposit',
        'timestamp': datetime(year=2018, month=1, day=1),
        'id': uuid.uuid4(),
        'base_currency': 'usd',
        'base_quantity': Decimal(10000.00),
        'base_usd_price': Decimal(1.00)
    }

    # Buy 9,000 USDC
    buy_usdc = {
        'type': 'buy',
        'timestamp': datetime(year=2018, month=1, day=2),
        'id': uuid.uuid4(),
        'base_currency': 'usdc',
        'base_quantity': Decimal(9000.000000),
        'base_usd_price': Decimal(1.00),
        'quote_currency': 'usd',
        'quote_quantity': Decimal(9000.00),
        'quote_usd_price': Decimal(1.00),
    }

    # Buy $500 of bitcoin with USD
    buy_btc = {
        'type': 'buy',
        'timestamp': datetime(year=2018, month=1, day=3),
        'id': uuid.uuid4(),
        'base_currency': 'btc',
        'base_quantity': Decimal(1.00000000),
        'base_usd_price': Decimal(500.00),
        'quote_currency': 'usd',
        'quote_quantity': Decimal(500.00),
        'quote_usd_price': Decimal(1.00),
    }

    # Swap $1000 of bitcoin with USDC
    swap_btc_usdc = {
        'type': 'swap',
        'timestamp': datetime(year=2018, month=1, day=4),
        'id': uuid.uuid4(),
        'base_currency': 'btc',
        'base_quantity': Decimal(2.00000000),
        'base_usd_price': Decimal(500.00),
        'quote_currency': 'usdc',
        'quote_quantity': Decimal(1000.000000),
        'quote_usd_price': Decimal(1.00),
    }

    # Reward $20 USD
    reward_usd = {
        'type': 'reward',
        'timestamp': datetime(year=2018, month=2, day=1),
        'id': uuid.uuid4(),
        'base_currency': 'usd',
        'base_quantity': Decimal(25.00),
        'base_usd_price': Decimal(1.00),
    } 

    # Reward $20 USDC
    reward_usdc = {
        'type': 'reward',
        'timestamp': datetime(year=2018, month=2, day=1),
        'id': uuid.uuid4(),
        'base_currency': 'usdc',
        'base_quantity': Decimal(20.00),
        'base_usd_price': Decimal(1.00),
    }
    # Reward $20 BTC
    reward_btc = {
        'type': 'reward',
        'timestamp': datetime(year=2018, month=2, day=1),
        'id': uuid.uuid4(),
        'base_currency': 'btc',
        'base_quantity': Decimal(0.00100000),
        'base_usd_price': Decimal(750.00),
    }

    # Receive $20 USD
    receive_usd = {
        'type': 'receive',
        'timestamp': datetime(year=2018, month=3, day=1),
        'id': uuid.uuid4(),
        'base_currency': 'usd',
        'base_quantity': Decimal(20.00),
        'base_usd_price': Decimal(1.00),
    } # Producing a cryptocurrency entry instead of cash.

    # Receive $20 USDC
    receive_usdc = {
        'type': 'receive',
        'timestamp': datetime(year=2018, month=3, day=1),
        'id': uuid.uuid4(),
        'base_currency': 'usdc',
        'base_quantity': Decimal(20.00),
        'base_usd_price': Decimal(1.00),
    }
    # Receive $20 BTC
    receive_btc = {
        'type': 'receive',
        'timestamp': datetime(year=2018, month=3, day=1),
        'id': uuid.uuid4(),
        'base_currency': 'btc',
        'base_quantity': Decimal(0.00100000),
        'base_usd_price': Decimal(750.00),
    }

    return [deposit_initial, buy_usdc, buy_btc, swap_btc_usdc, reward_usd, reward_usdc, reward_btc, receive_usd, receive_usdc, receive_btc]


def usd_fee_no_positions():
    """
    NOT TAXABLE TXS (currently not configured to have taxable fees. Works with USD fees as shown below, but will probably never exist in the wild.)
    * receive
    * reward
    * interest-in-account
    * interest-in-stake
    """
    # Deposit 10,000 USD, 2 USD Fee (unrealistic sometimes)
    deposit_initial = {
        'type': 'deposit',
        'timestamp': datetime(year=2018, month=1, day=1),
        'id': uuid.uuid4(),
        'base_currency': 'usd',
        'base_quantity': Decimal(10000.00),
        'base_usd_price': Decimal(1.00),
        'fee_currency': 'usd',
        'fee_quantity': Decimal(2),
        'fee_usd_price': Decimal(1.00),
    }

    # Buy 9,000 USDC, 2 USD Fee (unrealistic sometimes)
    buy_usdc = {
        'type': 'buy',
        'timestamp': datetime(year=2018, month=1, day=2),
        'id': uuid.uuid4(),
        'base_currency': 'usdc',
        'base_quantity': Decimal(9000.000000),
        'base_usd_price': Decimal(1.00),
        'quote_currency': 'usd',
        'quote_quantity': Decimal(9000.00),
        'quote_usd_price': Decimal(1.00),
        'fee_currency': 'usd',
        'fee_quantity': Decimal(2),
        'fee_usd_price': Decimal(1.00),
    }

    # Buy $500 of bitcoin with USD, 2 USD Fee (unrealistic sometimes)
    buy_btc = {
        'type': 'buy',
        'timestamp': datetime(year=2018, month=1, day=3),
        'id': uuid.uuid4(),
        'base_currency': 'btc',
        'base_quantity': Decimal(1.00000000),
        'base_usd_price': Decimal(500.00),
        'quote_currency': 'usd',
        'quote_quantity': Decimal(500.00),
        'quote_usd_price': Decimal(1.00),
        'fee_currency': 'usd',
        'fee_quantity': Decimal(2),
        'fee_usd_price': Decimal(1.00),
    }

    # Swap $1000 of bitcoin with USDC, 2 USD Fee (unrealistic sometimes)
    swap_btc_usdc = {
        'type': 'swap',
        'timestamp': datetime(year=2018, month=1, day=4),
        'id': uuid.uuid4(),
        'base_currency': 'btc',
        'base_quantity': Decimal(1.00000000),
        'base_usd_price': Decimal(500.00),
        'quote_currency': 'usdc',
        'quote_quantity': Decimal(500.000000),
        'quote_usd_price': Decimal(1.00),
        'fee_currency': 'usd',
        'fee_quantity': Decimal(2),
        'fee_usd_price': Decimal(1.00),
    }

    # Reward $20 USD, 2 USD Fee (unrealistic sometimes)
    reward_usd = {
        'type': 'reward',
        'timestamp': datetime(year=2018, month=2, day=1),
        'id': uuid.uuid4(),
        'base_currency': 'usd',
        'base_quantity': Decimal(20.00),
        'base_usd_price': Decimal(1.00),
        'fee_currency': 'usd',
        'fee_quantity': Decimal(2),
        'fee_usd_price': Decimal(1.00),
    }

    # Reward $20 USDC, 2 USD Fee (unrealistic sometimes)
    reward_usdc = {
        'type': 'reward',
        'timestamp': datetime(year=2018, month=2, day=1),
        'id': uuid.uuid4(),
        'base_currency': 'usdc',
        'base_quantity': Decimal(20.00),
        'base_usd_price': Decimal(1.00),
        'fee_currency': 'usd',
        'fee_quantity': Decimal(2),
        'fee_usd_price': Decimal(1.00),
    }
    # Reward $20 BTC, 2 USD Fee (unrealistic sometimes)
    reward_btc = {
        'type': 'reward',
        'timestamp': datetime(year=2018, month=2, day=1),
        'id': uuid.uuid4(),
        'base_currency': 'btc',
        'base_quantity': Decimal(0.00100000),
        'base_usd_price': Decimal(750.00),
        'fee_currency': 'usd',
        'fee_quantity': Decimal(2),
        'fee_usd_price': Decimal(1.00),
    }

    # Receive $20 USD, 2 USD Fee (unrealistic sometimes)
    receive_usd = {
        'type': 'receive',
        'timestamp': datetime(year=2018, month=3, day=1),
        'id': uuid.uuid4(),
        'base_currency': 'usd',
        'base_quantity': Decimal(20.00),
        'base_usd_price': Decimal(1.00),
        'fee_currency': 'usd',
        'fee_quantity': Decimal(2),
        'fee_usd_price': Decimal(1.00),
    }

    # Receive $20 USDC, 2 USD Fee (unrealistic sometimes)
    receive_usdc = {
        'type': 'receive',
        'timestamp': datetime(year=2018, month=3, day=1),
        'id': uuid.uuid4(),
        'base_currency': 'usdc',
        'base_quantity': Decimal(20.00),
        'base_usd_price': Decimal(1.00),
        'fee_currency': 'usd',
        'fee_quantity': Decimal(2),
        'fee_usd_price': Decimal(1.00),
    }
    # Receive $20 BTC, 2 USD Fee (unrealistic sometimes)
    receive_btc = {
        'type': 'receive',
        'timestamp': datetime(year=2018, month=3, day=1),
        'id': uuid.uuid4(),
        'base_currency': 'btc',
        'base_quantity': Decimal(0.00100000),
        'base_usd_price': Decimal(750.00),
        'fee_currency': 'usd',
        'fee_quantity': Decimal(2),
        'fee_usd_price': Decimal(1.00),
    }    


    return [deposit_initial, buy_usdc, buy_btc, swap_btc_usdc, reward_usd, reward_usdc, reward_btc, receive_usd, receive_usdc, receive_btc]

def in_kind_fee_no_positions():
    """
    NOT TAXABLE TXS (currently not configured to have taxable fees. Works with USD fees, but will probably never exist in the wild.)
    * receive
    * reward
    * interest-in-account
    * interest-in-stake

    Returns:
        [type]: [description]
    """
    # Deposit 10,000 USD, 2 USD Fee (unrealistic sometimes)
    deposit_initial = {
        'type': 'deposit',
        'timestamp': datetime(year=2018, month=1, day=1),
        'id': uuid.uuid4(),
        'base_currency': 'usd',
        'base_quantity': Decimal(10000.00),
        'base_usd_price': Decimal(1.00),
        'fee_currency': 'usd',
        'fee_quantity': Decimal(2),
        'fee_usd_price': Decimal(1.00),
    }

    # Buy 9,000 USDC, 2 usdc Fee (unrealistic sometimes)
    buy_usdc = {
        'type': 'buy',
        'timestamp': datetime(year=2018, month=1, day=2),
        'id': uuid.uuid4(),
        'base_currency': 'usdc',
        'base_quantity': Decimal(9000.000000),
        'base_usd_price': Decimal(1.00),
        'quote_currency': 'usd',
        'quote_quantity': Decimal(9000.00),
        'quote_usd_price': Decimal(1.00),
        'fee_currency': 'usd',
        'fee_quantity': Decimal(2),
        'fee_usd_price': Decimal(1.00),
    } # Does not currently credit current assets crypto. Need a USDC position.

    # Buy $500 of bitcoin with USD, $2 btc Fee (unrealistic sometimes)
    buy_btc = {
        'type': 'buy',
        'timestamp': datetime(year=2018, month=1, day=3),
        'id': uuid.uuid4(),
        'base_currency': 'btc',
        'base_quantity': Decimal(1.00000000),
        'base_usd_price': Decimal(500.00),
        'quote_currency': 'usd',
        'quote_quantity': Decimal(500.00),
        'quote_usd_price': Decimal(1.00),
        'fee_currency': 'usd',
        'fee_quantity': Decimal(2),
        'fee_usd_price': Decimal(1.00),
    } # Does not currently credit current assets crypto. Need a btc position.

    # Swap $1000 of bitcoin with USDC, $2 btc Fee (unrealistic sometimes)
    swap_btc_usdc = {
        'type': 'swap',
        'timestamp': datetime(year=2018, month=1, day=4),
        'id': uuid.uuid4(),
        'base_currency': 'btc',
        'base_quantity': Decimal(1.00000000),
        'base_usd_price': Decimal(500.00),
        'quote_currency': 'usdc',
        'quote_quantity': Decimal(500.000000),
        'quote_usd_price': Decimal(1.00),
        'fee_currency': 'btc',
        'fee_quantity': Decimal(.004),
        'fee_usd_price': Decimal(500.00),
    }

    # Swap $1000 of bitcoin with USDC, $2 usdc Fee (unrealistic sometimes)
    swap_btc_usdc_fee = {
        'type': 'swap',
        'timestamp': datetime(year=2018, month=1, day=4),
        'id': uuid.uuid4(),
        'base_currency': 'btc',
        'base_quantity': Decimal(1.00000000),
        'base_usd_price': Decimal(500.00),
        'quote_currency': 'usdc',
        'quote_quantity': Decimal(500.000000),
        'quote_usd_price': Decimal(1.00),
        'fee_currency': 'usdc',
        'fee_quantity': Decimal(2),
        'fee_usd_price': Decimal(1.00),
    }

    return [deposit_initial, buy_usdc, buy_btc, swap_btc_usdc, swap_btc_usdc_fee]

def no_fee_with_positions():
    og_txs = no_fee_no_positions()
    new_txs = no_fee_no_positions().copy()
    for tx in new_txs:
        tx['timestamp'] = tx['timestamp'].replace(year=tx['timestamp'].year + 1)

    interest_in_account_usd = {
        'type': 'interest-in-account',
        'timestamp': datetime(year=2019, month=2, day=1),
        'id': uuid.uuid4(),
        'base_currency': 'usd',
        'base_quantity': Decimal(25.00),
        'base_usd_price': Decimal(1.00),
    } 

    # Reward $20 USDC
    interest_in_account_usdc = {
        'type': 'interest-in-account',
        'timestamp': datetime(year=2019, month=2, day=2),
        'id': uuid.uuid4(),
        'base_currency': 'usdc',
        'base_quantity': Decimal(20.00),
        'base_usd_price': Decimal(1.00),
    }
    # Reward $20 BTC
    interest_in_account_btc = {
        'type': 'interest-in-account',
        'timestamp': datetime(year=2019, month=2, day=3),
        'id': uuid.uuid4(),
        'base_currency': 'btc',
        'base_quantity': Decimal(0.00100000),
        'base_usd_price': Decimal(2500.00),
    }

    interest_in_stake_usd = {
        'type': 'interest-in-stake',
        'timestamp': datetime(year=2019, month=3, day=1),
        'id': uuid.uuid4(),
        'base_currency': 'usd',
        'base_quantity': Decimal(25.00),
        'base_usd_price': Decimal(1.00),
    } 

    # Reward $20 USDC
    interest_in_stake_usdc = {
        'type': 'interest-in-stake',
        'timestamp': datetime(year=2019, month=3, day=2),
        'id': uuid.uuid4(),
        'base_currency': 'usdc',
        'base_quantity': Decimal(20.00),
        'base_usd_price': Decimal(1.00),
    }
    # Reward $20 BTC
    interest_in_stake_btc = {
        'type': 'interest-in-stake',
        'timestamp': datetime(year=2019, month=3, day=3),
        'id': uuid.uuid4(),
        'base_currency': 'btc',
        'base_quantity': Decimal(0.00100000),
        'base_usd_price': Decimal(2750.00),
    }
    return og_txs + new_txs + [interest_in_account_usd, interest_in_account_usdc, interest_in_account_btc, interest_in_stake_usd, interest_in_stake_usdc, interest_in_stake_btc]

def no_fee_with_positions_taxable():

    # Sell $100 BTC short term
    sell_btc_short_gain = {
            'type': 'sell',
            'timestamp': datetime(year=2018, month=1, day=6),
            'id': uuid.uuid4(),
            'base_currency': 'btc',
            'base_quantity': Decimal(0.2),
            'base_usd_price': Decimal(600.00),
            'quote_currency': 'usd',
            'quote_quantity': Decimal(120.00),
            'quote_usd_price': Decimal(1.00),
    }    

    # Sell $100 BTC long term
    sell_btc_long = {
            'type': 'sell',
            'timestamp': datetime(year=2020, month=1, day=6),
            'id': uuid.uuid4(),
            'base_currency': 'btc',
            'base_quantity': Decimal(0.01),
            'base_usd_price': Decimal(10000.00),
            'quote_currency': 'usd',
            'quote_quantity': Decimal(100.00),
            'quote_usd_price': Decimal(1.00),
    }

    # Swap $400 of bitcoin with eth short term
    swap_btc_eth_short = {
            'type': 'swap',
            'timestamp': datetime(year=2018, month=1, day=8),
            'id': uuid.uuid4(),
            'base_currency': 'eth',
            'base_quantity': Decimal(2),
            'base_usd_price': Decimal(200.00),
            'quote_currency': 'btc',
            'quote_quantity': Decimal(0.8),
            'quote_usd_price': Decimal(500.00),
    }    

    # Swap $400 of bitcoin with eth
    swap_btc_eth_long = {
            'type': 'swap',
            'timestamp': datetime(year=2020, month=1, day=8),
            'id': uuid.uuid4(),
            'base_currency': 'eth',
            'base_quantity': Decimal(2),
            'base_usd_price': Decimal(200.00),
            'quote_currency': 'btc',
            'quote_quantity': Decimal(0.04),
            'quote_usd_price': Decimal(10000.00),
    }

    # Sell $100 BTC short term
    send_btc_short = {
            'type': 'send',
            'timestamp': datetime(year=2018, month=1, day=9),
            'id': uuid.uuid4(),
            'base_currency': 'btc',
            'base_quantity': Decimal(0.2),
            'base_usd_price': Decimal(500.00),
            'quote_currency': 'usd',
            'quote_quantity': Decimal(100.00),
            'quote_usd_price': Decimal(1.00),
    }    

    # Sell $100 BTC long term
    send_btc_long = {
            'type': 'send',
            'timestamp': datetime(year=2020, month=1, day=9),
            'id': uuid.uuid4(),
            'base_currency': 'btc',
            'base_quantity': Decimal(0.01),
            'base_usd_price': Decimal(10000.00),
            'quote_currency': 'usd',
            'quote_quantity': Decimal(100.00),
            'quote_usd_price': Decimal(1.00),
    }
    

    return no_fee_no_positions() + [sell_btc_short_gain, sell_btc_long, swap_btc_eth_short, swap_btc_eth_long, send_btc_short, send_btc_long]


    # Swap $200 BTC for USDC - short term
    # Sell $500 BTC for USD - short term
    # Sell $250 BTC for ETH - short term
    # Swap $200 BTC for USDC - long term
    # Sell $500 BTC for USD - long term
    # Sell $250 BTC for ETH - long term


    # initial 10,000 deposit. Cash 10,000, Invested Capital 10,000
    date = datetime(year=2018, month=1, day=1)
    txs = []
    deposit_initial = {
        'type': 'deposit',
        'timestamp': datetime(year=2018, month=1, day=1),
        'id': uuid.uuid4(),
        'base_currency': 'usd',
        'base_quantity': Decimal(10000.00),
        'base_usd_price': Decimal(1.00)
    }
    txs.append(Deposit(**deposit_initial))
    date = date.__add__(timedelta(days=2))
    # initial 5 BTC buy at 1000 per btc for 5000 USD. Cash 5000, Crypto 5000 qty 5. No fee.
    buy_btc_simple = Buy(**{
        'type': 'buy',
        'timestamp': datetime(year=2018, month=1, day=2),
        'id': uuid.uuid4(),
        'base_currency': 'btc',
        'base_quantity': Decimal(5.000000000000),
        'base_usd_price': Decimal(1000.00),
        'quote_currency': 'usd',
        'quote_quantity': Decimal(5.000000000000) * Decimal(1000.00),
        'quote_usd_price': Decimal(1.00),
    })
    txs.append(buy_btc_simple)

    date = date.__add__(timedelta(days=180))
    # short term gain. sell 1 btc at 2000 per coin for 1000 gain. No fee
    short_term_btc_sell_gain = Sell(**{
        'type': 'sell',
        'timestamp': date,
        'id': uuid.uuid4(),
        'base_currency': 'btc',
        'base_quantity': Decimal(1.000000000000),
        'base_usd_price': Decimal(2000.00),
        # 'fee_currency': 'usd',
        # 'fee_quantity': Decimal(2.99),
        # 'fee_usd_price': Decimal(1.00),
        'quote_currency': 'usd',
        'quote_quantity': Decimal(1.000000000000) * Decimal(2000.00),
        'quote_usd_price': Decimal(1.00),
    })
    txs.append(short_term_btc_sell_gain)

    date = date.__add__(timedelta(days=365))
    # long term gain. sell 1 btc at 4000 per coin for 3000 gain.
    long_term_btc_sell_gain = Sell(**{
        'type': 'sell',
        'timestamp': date,
        'id': uuid.uuid4(),
        'base_currency': 'btc',
        'base_quantity': Decimal(1.000000000000),
        'base_usd_price': Decimal(4000.00),
        'fee_currency': 'usd',
        'fee_quantity': Decimal(2.99),
        'fee_usd_price': Decimal(1.00),
        'quote_currency': 'usd',
        'quote_quantity': Decimal(1.000000000000) * Decimal(4000.00),
        'quote_usd_price': Decimal(1.00),
    })
    txs.append(long_term_btc_sell_gain)

    date = date.__add__(timedelta(days=1))
    # long term loss. swap 1 btc at 500 per coin for 500 loss. get 10 eth for 50 per eth. no fee
    long_term_btc_swap_loss = Swap(**{
        'type': 'swap',
        'timestamp': date,
        'id': uuid.uuid4(),
        'base_currency': 'eth',
        'base_quantity': Decimal(10.000000000000),
        'base_usd_price': Decimal(50.00),
        'fee_currency': 'btc',
        'fee_quantity': Decimal(.001),
        'fee_usd_price': Decimal(500.00),
        'quote_currency': 'btc',
        'quote_quantity': Decimal(1.000000000000),
        'quote_usd_price': Decimal(500.00),
    })
    txs.append(long_term_btc_swap_loss)

    return txs
