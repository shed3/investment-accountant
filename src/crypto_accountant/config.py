cpa_config = {
    'fees': {
        'credits': [
            {
                'ID': '-id',
                'Account': 'Assets',
                'Sub Account': 'Cryptocurrencies',
                'Connection ID': '-connectionId',
                'Type': 'Fee',
                'Symbol': '-feeCurrency',
                'Timestamp': '-timestamp',
                'Position': '-feePrice',
                'Value': '-feeTotal',
                'Quantity': '-feeQuantity',
            }
        ],
        'debits': [
            {
                'ID': '-id',
                'Account': 'Liabilities',
                'Sub Account': 'Fees Paid',
                'Connection ID': '-connectionId',
                'Type': '-type',
                'Symbol': '-feeCurrency',
                'Timestamp': '-timestamp',
                'Position': '-feePrice',
                'Value': '-feeTotal',
                'Quantity': '-feeQuantity',
            }
        ]
    },
    'deposit': {
        'credits': [
            {
                'ID': '-id',
                'Account': 'Equities',
                'Sub Account': 'Invested Capital',
                'Connection ID': '-connectionId',
                'Type': '-type',
                'Symbol': '-baseCurrency',
                'Timestamp': '-timestamp',
                'Value': '-subTotal',
                'Quantity': '-baseQuantity',
            }
        ],
        'debits': [
            {
                'ID': '-id',
                'Account': 'Assets',
                'Sub Account': 'Cash',
                'Connection ID': '-connectionId',
                'Type': '-type',
                'Symbol': '-baseCurrency',
                'Timestamp': '-timestamp',
                'Value': '-subTotal',
                'Quantity': '-baseQuantity',
            }
        ]
    },
    'withdrawal': {
        'credits': [
            {
                'ID': '-id',
                'Account': 'Assets',
                'Sub Account': 'Cash',
                'Connection ID': '-connectionId',
                'Type': '-type',
                'Symbol': '-baseCurrency',
                'Timestamp': '-timestamp',
                'Value': '-subTotal',
                'Quantity': '-baseQuantity',
            }
        ],
        'debits': [
            {
                'ID': '-id',
                'Account': 'Equities',
                'Sub Account': 'Withdrawn Capital',
                'Connection ID': '-connectionId',
                'Type': '-type',
                'Symbol': '-baseCurrency',
                'Timestamp': '-timestamp',
                'Value': '-subTotal',
                'Quantity': '-baseQuantity',
            }
        ]
    },
    'buy': {
        'credits': [
            {
                'ID': '-id',
                'Account': 'Assets',
                'Sub Account': 'Cryptocurrencies',
                'Connection ID': '-connectionId',
                'Type': '-type',
                'Symbol': '-quoteCurrency',
                'Timestamp': '-timestamp',
                'Position': '-quoteUsdPrice',
                'Value': '-subTotal',
                'Quantity': '-quoteQuantity'
                # 'Taxable' : False, Need to think about this, it is taxable unless the payment is made in USD. That is, we will recognize a gain or loss on any other quote currency.
            }
        ],
        'debits': [
            {
                'ID': '-id',
                'Account': 'Assets',
                'Sub Account': 'Cryptocurrencies',
                'Connection ID': '-connectionId',
                'Type': '-type',
                'Symbol': '-baseCurrency',
                'Timestamp': '-timestamp',
                'Position': '-baseUsdPrice',
                'Value': '-subTotal',
                'Quantity': '-baseQuantity'
                # 'Taxable' : False, Need to think about this, it is taxable unless the payment is made in USD. That is, we will recognize a gain or loss on any other quote currency.
            }
        ]
    },
    'sell': {
        'credits': [
            {
                'ID': '-id',
                'Account': 'Assets',
                'Sub Account': 'Cryptocurrencies',
                'Connection ID': '-connectionId',
                'Type': '-type',
                'Symbol': '-baseCurrency',
                'Timestamp': '-timestamp',
                'Position': '-closePosition',
                'Value': '-closeValue',
                'Quantity': '-closeQuantity',
                'Taxable': True,
            },
            {
                'Account': 'Equities',
                'Sub Account': 'Realized Gains / Losses',
                'Connection ID': '-connectionId',
                'Type': '-type',
                'Symbol': '-baseCurrency',
                'Timestamp': '-timestamp',
                'Position': '-closePosition',
                'Value': '-closeGain',
                'Quantity': '-closeQuantity',
                'Taxable': True,
            }
        ],
        'debits': [
            {
                'ID': '-id',
                'Account': 'Assets',
                'Sub Account': 'Cryptocurrencies',
                'Connection ID': '-connectionId',
                'Type': '-type',
                'Symbol': '-quoteCurrency',
                'Timestamp': '-timestamp',
                'Position': '-quoteUsdPrice',
                'Value': '-closeTotal',
                'Quantity': '-closeQuoteQuantity',
                'Taxable': True,
            }            
        ]
    },
    'send': {
        'credits': [
            {
                'ID': '-id',
                'Account': 'Assets',
                'Sub Account': 'Cryptocurrencies',
                'Connection ID': '-connectionId',
                'Type': '-type',
                'Symbol': '-baseCurrency',
                'Timestamp': '-timestamp',
                'Position': '-baseUsdPrice',
                'Value': '-subTotal',
                'Quantity': '-baseQuantity',
            }
        ],
        'debits': [
            {
                'ID': '-id',
                'Account': 'Equities',
                'Sub Account': 'Transfers Out',
                'Connection ID': '-connectionId',
                'Type': '-type',
                'Symbol': '-baseCurrency',
                'Timestamp': '-timestamp',
                'Position': '-baseUsdPrice',
                'Value': '-subTotal',
                'Quantity': '-baseQuantity',
            }
        ]
    },
    'receive': {
        'credits': [
            {
                'ID': '-id',
                'Account': 'Equities',
                'Sub Account': 'Transfers In',
                'Connection ID': '-connectionId',
                'Type': '-type',
                'Symbol': '-baseCurrency',
                'Timestamp': '-timestamp',
                'Position': '-baseUsdPrice',
                'Value': '-subTotal',
                'Quantity': '-baseQuantity',
            }
        ],
        'debits': [
            {
                'ID': '-id',
                'Account': 'Assets',
                'Sub Account': 'Cryptocurrencies',
                'Connection ID': '-connectionId',
                'Type': '-type',
                'Symbol': '-baseCurrency',
                'Timestamp': '-timestamp',
                'Position': '-baseUsdPrice',
                'Value': '-subTotal',
                'Quantity': '-baseQuantity',
            }
        ]
    },
    'reward': {
        'credits': [
            {
                'ID': '-id',
                'Account': 'Equities',
                'Sub Account': 'Rewards',
                'Connection ID': '-connectionId',
                'Type': '-type',
                'Symbol': '-baseCurrency',
                'Timestamp': '-timestamp',
                'Position': '-baseUsdPrice',
                'Value': '-subTotal',
                'Quantity': '-baseQuantity'
                # 'Taxable' : False, This could be true if we report it as taxable income.
            }
        ],
        'debits': [
            {
                'ID': '-id',
                'Account': 'Assets',
                'Sub Account': 'Cryptocurrencies',
                'Connection ID': '-connectionId',
                'Type': '-type',
                'Symbol': '-baseCurrency',
                'Timestamp': '-timestamp',
                'Position': '-baseUsdPrice',
                'Value': '-subTotal',
                'Quantity': '-baseQuantity'
                # 'Taxable' : False, This could be true if we report it as taxable income.
            }
        ]
    },
    'interest-in-stake': {
        'credits': [
            {
                'ID': '-id',
                'Account': 'Equities',
                'Sub Account': 'Interest Earned - Staking',
                'Connection ID': '-connectionId',
                'Type': '-type',
                'Symbol': '-baseCurrency',
                'Timestamp': '-timestamp',
                'Position': '-baseUsdPrice',
                'Value': '-subTotal',
                'Quantity': '-baseQuantity'
                # 'Taxable' : False, This could be true if we report it as taxable income.
            }
        ],
        'debits': [
            {
                'ID': '-id',
                'Account': 'Assets',
                'Sub Account': 'Cryptocurrencies',
                'Connection ID': '-connectionId',
                'Type': '-type',
                'Symbol': '-baseCurrency',
                'Timestamp': '-timestamp',
                'Position': '-baseUsdPrice',
                'Value': '-subTotal',
                'Quantity': '-baseQuantity'
                # 'Taxable' : False, This could be true if we report it as taxable income.
            }
        ]
    },
    'interest-in-account': {
        'credits': [
            {
                'ID': '-id',
                'Account': 'Equities',
                'Sub Account': 'Interest Earned',
                'Connection ID': '-connectionId',
                'Type': '-type',
                'Symbol': '-baseCurrency',
                'Timestamp': '-timestamp',
                'Position': '-baseUsdPrice',
                'Value': '-subTotal',
                'Quantity': '-baseQuantity'
                # 'Taxable' : False, This could be true if we report it as taxable income.
            }
        ],
        'debits': [
            {
                'ID': '-id',
                'Account': 'Assets',
                'Sub Account': 'Cryptocurrencies',
                'Connection ID': '-connectionId',
                'Type': '-type',
                'Symbol': '-baseCurrency',
                'Timestamp': '-timestamp',
                'Position': '-baseUsdPrice',
                'Value': '-subTotal',
                'Quantity': '-baseQuantity'
                # 'Taxable' : False, This could be true if we report it as taxable income.
            }
        ]
    },
    'interest-in': {
        'credits': [
            {
                'ID': '-id',
                'Account': 'Equities',
                'Sub Account': 'Interest Earned',
                'Connection ID': '-connectionId',
                'Type': '-type',
                'Symbol': '-baseCurrency',
                'Timestamp': '-timestamp',
                'Position': '-baseUsdPrice',
                'Value': '-subTotal',
                'Quantity': '-baseQuantity'
                # 'Taxable' : False, This could be true if we report it as taxable income.
            }
        ],
        'debits': [
            {
                'ID': '-id',
                'Account': 'Assets',
                'Sub Account': 'Cryptocurrencies',
                'Connection ID': '-connectionId',
                'Type': '-type',
                'Symbol': '-baseCurrency',
                'Timestamp': '-timestamp',
                'Position': '-baseUsdPrice',
                'Value': '-subTotal',
                'Quantity': '-baseQuantity'
                # 'Taxable' : False, This could be true if we report it as taxable income.
            }
        ]
    }
}

