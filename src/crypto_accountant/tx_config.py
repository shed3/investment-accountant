### MAIN ACCOUNTS ###
assets = {'account': 'assets'}
equities = {'account': 'equities'}
liabilities = {'account': 'liabilities'}

### SUB ACCOUNTS ###
cash = {**assets, 'sub_account': 'cash'}
crypto = {**assets, 'sub_account': 'cryptocurrencies'}

invested_capital = {**equities, 'sub_account': 'invested_capital'}
withdrawn_capital = {**equities, 'sub_account': 'invested_capital'}

transfers_in = {**equities, 'sub_account': 'transfers_in'}
transfers_out = {**equities, 'sub_account': 'transfers_out'}

interest_earned_account = {**equities, 'sub_account': 'interest_earned_account'}
interest_earned_stake = {**equities, 'sub_account': 'interest_earned_stake'}

rewards = {**equities, 'sub_account': 'rewards'}
realized_gain_loss = {**equities, 'sub_account': 'realized_gains_losses'}

fees_paid = {**liabilities, 'sub_account': 'fees_paid'}


### TX DEFAULT ENTRY SCHEMA

def create_general_schema(tx_type, d, c, d_kwargs={}, c_kwargs={}):
   return [
   {'type': tx_type, 'side': "debit", **d, **d_kwargs},
   {'type': tx_type, 'side': "credit", **c, **c_kwargs},
]

deposit = create_general_schema('deposit', cash, invested_capital)
withdrawal = create_general_schema('withdrawal', withdrawn_capital, cash)

send = create_general_schema('send', transfers_out, crypto)
receive = create_general_schema('receive', crypto, transfers_in)

interest_in_account = create_general_schema('interest-in-account', crypto, interest_earned_account)
interest_in_stake = create_general_schema('interest-in-stake', crypto, interest_earned_stake)

reward = create_general_schema('reward', crypto, rewards)
fee = create_general_schema('fee', fees_paid, cash)
buy = create_general_schema('buy', crypto, cash, c_kwargs={'mkt': 'quote'})

sell = create_general_schema('sell', cash, crypto, d_kwargs={'mkt': 'quote'}, c_kwargs={'taxable': True})

# swap assumes exchanging quote_currency for base_currency
swap = create_general_schema('swap', crypto, crypto, d_kwargs={'taxable': False}, c_kwargs={'mkt': 'quote', 'taxable': True})

realized_gain = {'side': "credit", 'taxable': True, **realized_gain_loss}
realized_gain_sell = {'type': 'sell', **realized_gain}
realized_gain_swap = {'type': 'swap', 'mkt': 'quote', **realized_gain}
# sell_open = {'type': 'sell', 'side': "debit", 'mkt': 'quote', 'taxable': True, **crypto}
# sell_close = {'type': 'sell', 'side': "credit", 'taxable': True, **crypto}

# realized_gain = {'type': 'sell', 'side': "credit", 'taxable': True, **realized_gain_loss}
invested_capital_buy = {'type': 'buy', 'side': "debit", 'mkt': 'quote', **invested_capital}

tx_configs = {
    'fee': fee,
    'deposit': deposit,
    'withdrawal': withdrawal,
    'buy': buy + [invested_capital_buy],
    # 'buy': buy,
    'sell': sell + [realized_gain_sell],
    'swap': swap + [realized_gain_swap],
    'send': send,
    'receive': receive,
    'reward': reward,
    'interest-in-stake': interest_in_stake,
    'interest-in-account': interest_in_account,
}
