### MAIN ACCOUNTS ###
assets = {'account': 'Assets'}
equities = {'account': 'Equities'}
liabilities = {'account': 'Liabilities'}

### SUB ACCOUNTS ###
cash = {**assets, 'sub_account': 'Cash'}
crypto = {**assets, 'sub_account': 'Cryptocurrencies'}

invested_capital = {**equities, 'sub_account': 'Invested Capital'}
withdrawn_capital = {**equities, 'sub_account': 'Invested Capital'}

transfers_in = {**equities, 'sub_account': 'Transfers In'}
transfers_out = {**equities, 'sub_account': 'Transfers Out'}

interest_earned_account = {**equities, 'sub_account': 'Interest Earned Account'}
interest_earned_stake = {**equities, 'sub_account': 'Interest Earned Stake'}

rewards = {**equities, 'sub_account': 'Rewards'}
realized_gain_loss = {**equities, 'sub_account': 'Realized Gains / Losses'}

fees_paid = {**liabilities, 'sub_account': 'Fees Paid'}


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
buy = create_general_schema('buy', crypto, crypto, c_kwargs={'mkt': 'quote'})

sell_open = {'type': 'sell', 'side': "debit", 'mkt': 'quote', 'taxable': True, **crypto}
sell_close = {'type': 'sell', 'side': "credit", 'taxable': True, **crypto}
realized_gain = {'type': 'sell', 'side': "credit", 'taxable': True, **realized_gain_loss}

sell = [
    sell_open,
    sell_close,
    realized_gain
]

tx_configs = {
    'fee': fee,
    'deposit': deposit,
    'withdrawal': withdrawal,
    'buy': buy,
    'sell': sell,
    'send': send,
    'receive': receive,
    'reward': reward,
    'interest-in-stake': interest_in_stake,
    'interest-in-account': interest_in_account,
}
