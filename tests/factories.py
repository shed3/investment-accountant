from decimal import Decimal
import uuid
import random
from datetime import datetime
from dateutil.relativedelta import relativedelta
from randomtimestamp import randomtimestamp

from src.crypto_accountant.transaction import Transaction

# random symbols
symbols = [
    'btc',
    'eth',
    'xrp',
    'xlm',
    'link',
    'usdc',
    'grt',
    'ada',
    'cel',
    'cro',
]

def txn_factory(tx_type, **kwargs):
    baseCurrency = kwargs.get("baseCurrency", symbols[random.randint(0, len(symbols) - 1)])
    baseUsdPrice = kwargs.get("baseUsdPrice", random.random() * 100)
    baseQuantity = kwargs.get("baseQuantity", random.random() * 10)
    
    feePrice = kwargs['quoteUsdPrice'] if 'quoteUsdPrice' in kwargs else baseUsdPrice
    feeUsdPrice = kwargs.get("feeUsdPrice", feePrice)
    feeQuantity = kwargs.get("feeQuantity", random.random() * 10)
    feeTotal = feeUsdPrice * feeQuantity
    subTotal = baseUsdPrice * baseQuantity

    txn = {
        'tx_type' : tx_type,
        'timestamp' : kwargs.get("timestamp", randomtimestamp(start_year=2018, text=False)),
        'id' : kwargs.get("id",uuid.uuid4()),
        'baseCurrency' : baseCurrency,
        'baseQuantity' : baseQuantity,
        'baseUsdPrice' : baseUsdPrice,
        'feeCurrency' : kwargs.get("feeCurrency", baseCurrency),
        'feeQuantity' : feeQuantity,
        'feeUsdPrice' : kwargs.get("feeUsdPrice", None),
        'feeTotal': feeTotal,
        'subTotal' : subTotal,
        'total' : subTotal + feeTotal
    }
    if tx_type == "buy" or tx_type == "sell":
        quotePrice = kwargs.get("quotePrice", random.random() * 10)
        quoteUsdPrice = kwargs.get("quoteUsdPrice", random.random() * 100)
        quoteQuantity = quoteUsdPrice / baseUsdPrice * baseQuantity
        quoteCurrency = kwargs.get("quoteCurrency", symbols[random.randint(0, len(symbols) - 1)])

        txn['quoteCurrency'] = quoteCurrency
        txn['quotePrice'] = quotePrice
        txn['quoteUsdPrice'] = quoteUsdPrice
        txn['quoteQuantity'] = quoteQuantity

        if 'feeCurrency' not in kwargs:
            feeTotal = quoteUsdPrice * feeQuantity
            txn['feeCurrency'] =  quoteCurrency
            txn['feeUsdPrice'] = quoteUsdPrice
            txn['feeTotal'] = feeTotal
            txn['total'] = subTotal + feeTotal

    tx = Transaction(**txn)
    return tx