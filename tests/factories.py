import uuid
import random
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
    base_currency = kwargs.get("base_currency", symbols[random.randint(0, len(symbols) - 1)])
    base_usd_price = kwargs.get("base_usd_price", random.random() * 100)
    base_quantity = kwargs.get("base_quantity", random.random() * 10)
    
    fee_price = kwargs['quote_usd_price'] if 'quote_usd_price' in kwargs else base_usd_price
    fee_usd_price = kwargs.get("fee_usd_price", fee_price)
    fee_quantity = kwargs.get("fee_quantity", random.random() * 10)
    fee_total = fee_usd_price * fee_quantity
    sub_total = base_usd_price * base_quantity

    txn = {
        'type' : tx_type,
        'timestamp' : kwargs.get("timestamp", randomtimestamp(start_year=2018, text=False)),
        'id' : kwargs.get("id",uuid.uuid4()),
        'base_currency' : base_currency,
        'base_quantity' : base_quantity,
        'base_usd_price' : base_usd_price,
        'fee_currency' : kwargs.get("fee_currency", base_currency),
        'fee_quantity' : fee_quantity,
        'fee_usd_price' : kwargs.get("fee_usd_price", None),
        'fee_total': fee_total,
        'sub_total' : sub_total,
        'total' : sub_total + fee_total,
        'taxable': kwargs.get("taxable", False)
    }
    if tx_type == "buy" or tx_type == "sell":
        quote_price = kwargs.get("quote_price", random.random() * 10)
        quote_usd_price = kwargs.get("quote_usd_price", random.random() * 100)
        quote_quantity = kwargs.get("quote_quantity", (quote_usd_price / base_usd_price) * base_quantity)
        quote_currency = kwargs.get("quote_currency", symbols[random.randint(0, len(symbols) - 1)])

        txn['quote_currency'] = quote_currency
        txn['quote_price'] = quote_price
        txn['quote_usd_price'] = quote_usd_price
        txn['quote_quantity'] = quote_quantity

        if 'fee_currency' not in kwargs:
            fee_total = quote_usd_price * fee_quantity
            txn['fee_currency'] =  quote_currency
            txn['fee_usd_price'] = quote_usd_price
            txn['fee_total'] = fee_total
            txn['total'] = sub_total + fee_total

    tx = Transaction(**txn)
    return tx