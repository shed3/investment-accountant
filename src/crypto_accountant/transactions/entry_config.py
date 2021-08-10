### MAIN ACCOUNTS ###
ASSETS = {'account': 'assets'}
EQUITIES = {'account': 'equities'}
LIABILITIES = {'account': 'liabilities'}

### SUB ACCOUNTS ###
CASH = {**ASSETS, 'sub_account': 'cash'}
CRYPTO = {**ASSETS, 'sub_account': 'cryptocurrencies'}

INVESTED_CAPITAL = {**EQUITIES, 'sub_account': 'invested_capital'}
WITHDRAWN_CAPITAL = {**EQUITIES, 'sub_account': 'invested_capital'}

TRANSFERS_IN = {**EQUITIES, 'sub_account': 'transfers_in'}
TRANSFERS_OUT = {**EQUITIES, 'sub_account': 'transfers_out'}

INTEREST_EARNED_ACCOUNT = {**EQUITIES, 'sub_account': 'interest_earned_account'}
INTEREST_EARNED_STAKE = {**EQUITIES, 'sub_account': 'interest_earned_stake'}

REWARDS = {**EQUITIES, 'sub_account': 'rewards'}
REALIZED_GAIN_LOSS = {**EQUITIES, 'sub_account': 'realized_gains_losses'}

FEES_PAID = {**LIABILITIES, 'sub_account': 'fees_paid'}
