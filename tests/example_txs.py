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
        'base_quantity': Decimal(1.00000000),
        'base_usd_price': Decimal(500.00),
        'quote_currency': 'usdc',
        'quote_quantity': Decimal(500.000000),
        'quote_usd_price': Decimal(1.00),
    }

    # Reward $20 USD
    reward_usd = {
        'type': 'reward',
        'timestamp': datetime(year=2018, month=2, day=1),
        'id': uuid.uuid4(),
        'base_currency': 'usd',
        'base_quantity': Decimal(20.00),
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
    }

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
        'base_quantity': Decimal(1.00000000),
        'base_usd_price': Decimal(500.00),
        'quote_currency': 'usdc',
        'quote_quantity': Decimal(500.000000),
        'quote_usd_price': Decimal(1.00),
    }

    # Reward $20 USD
    reward_usd = {
        'type': 'reward',
        'timestamp': datetime(year=2018, month=2, day=1),
        'id': uuid.uuid4(),
        'base_currency': 'usd',
        'base_quantity': Decimal(20.00),
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
    }

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
    # Deposit 10,000 USD, .99 USD Fee
    # Buy 9,000 USDC, .99 USD Fee
    # Buy $500 of bitcoin with USD, .99 USD Fee
    # Buy $1000 of bitcoin with USDC, .99 USD Fee
    # Reward $20 USD , .99 USD Fee
    # Reward $20 USDC , .99 USD Fee
    # Reward $20 BTC , .99 USD Fee
    # Receive $20 USD , .99 USD Fee
    # Receive $20 USDC , .99 USD Fee
    # Receive $20 BTC , .99 USD Fee

    return


def in_kind_fee_no_positions():
    # This scenario will need to deduct the fee from the new position it is opening, since it can not close it out. These are only receive type transactions with no previous transactions.

    # Deposit 10,000 USD, .99 USD Fee
    # Buy 9,000 USDC, .99 USDC Fee
    # Buy $500 of bitcoin with USD, .99 USD Fee
    # Buy $1000 of bitcoin with USDC, .99 USDC Fee
    # Reward $20 USD , .99 USD Fee
    # Reward $20 USDC , .99 USDC Fee
    # Reward $20 BTC , .99 BTC Fee
    # Receive $20 USD , .99 USD Fee
    # Receive $20 USDC , .99 USDC Fee
    # Receive $20 BTC , .99 BTC Fee

    return


def no_fee_with_positions():
    # Deposit 10,000 USD
    # Buy 9,000 USDC
    # Buy $500 of bitcoin with USD
    # Buy $1000 of bitcoin with USDC
    # Reward $20 USD
    # Reward $20 USDC
    # Reward $20 BTC
    # Receive $20 USD
    # Receive $20 USDC
    # Receive $20 BTC
    # Interest Account $0.50 BTC x 10 @ different prices
    # Interest Stake $2.00 BTC x 5 at different prices
    # Interest Account $5.00 USDC x 10 @ different prices
    # Interest Stake $20.00 USDC x 5 at different prices

    # Swap $200 BTC for USDC - short term
    # Sell $500 BTC for USD - short term
    # Sell $250 BTC for ETH - short term
    # Swap $200 BTC for USDC - long term
    # Sell $500 BTC for USD - long term
    # Sell $250 BTC for ETH - long term

    return

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
        'base_quantity': check_type(1.000000000000),
        'base_usd_price': check_type(2000.00),
        # 'fee_currency': 'usd',
        # 'fee_quantity': check_type(2.99),
        # 'fee_usd_price': check_type(1.00),
        'quote_currency': 'usd',
        'quote_quantity': check_type(1.000000000000) * check_type(2000.00),
        'quote_usd_price': check_type(1.00),
    })
    txs.append(short_term_btc_sell_gain)

    date = date.__add__(timedelta(days=365))
    # long term gain. sell 1 btc at 4000 per coin for 3000 gain.
    long_term_btc_sell_gain = Sell(**{
        'type': 'sell',
        'timestamp': date,
        'id': uuid.uuid4(),
        'base_currency': 'btc',
        'base_quantity': check_type(1.000000000000),
        'base_usd_price': check_type(4000.00),
        'fee_currency': 'usd',
        'fee_quantity': check_type(2.99),
        'fee_usd_price': check_type(1.00),
        'quote_currency': 'usd',
        'quote_quantity': check_type(1.000000000000) * check_type(4000.00),
        'quote_usd_price': check_type(1.00),
    })
    txs.append(long_term_btc_sell_gain)

    date = date.__add__(timedelta(days=1))
    # long term loss. swap 1 btc at 500 per coin for 500 loss. get 10 eth for 50 per eth. no fee
    long_term_btc_swap_loss = Swap(**{
        'type': 'swap',
        'timestamp': date,
        'id': uuid.uuid4(),
        'base_currency': 'eth',
        'base_quantity': check_type(10.000000000000),
        'base_usd_price': check_type(50.00),
        'fee_currency': 'btc',
        'fee_quantity': check_type(.001),
        'fee_usd_price': check_type(500.00),
        'quote_currency': 'btc',
        'quote_quantity': check_type(1.000000000000),
        'quote_usd_price': check_type(500.00),
    })
    txs.append(long_term_btc_swap_loss)

    return txs
