### MAIN ACCOUNTS ###
ASSETS = {'account_type': 'assets'}
LIABILITIES = {'account_type': 'liabilities'}
EQUITIES = {'account_type': 'equities'}
# equity accounts are used for income statements


# Current Assets (Assets)
CURRENT_ASSETS = {**ASSETS, 'account': 'current_assets'}
CASH = {**CURRENT_ASSETS, 'sub_account': 'cash'}
CRYPTO = {**CURRENT_ASSETS, 'sub_account': 'cryptocurrencies'}
CRYPTO_FAIR_VALUE_ADJ = {**CURRENT_ASSETS, 'sub_account': 'adj_fair_value'}

# Receivables (Assets)
RECEIVABLES = {**ASSETS, 'account': 'receivables'}
INTEREST_ACCRUED_ACCOUNT = {**RECEIVABLES, 'sub_account': 'interest_accrued_account'}
INTEREST_ACCRUED_STAKE = {**RECEIVABLES, 'sub_account': 'interest_accrued_stake'}
REWARDS_ACCRUED = {**RECEIVABLES, 'sub_account': 'rewards_accrued'}

# Payables (Liabilites)
PAYABLES = {**LIABILITIES, 'account': 'payables'}
INCOME_TAX_PAYABLE = {**PAYABLES, 'sub_account': 'income_tax_payable'}
INTEREST_PAYABLE = {**PAYABLES, 'sub_account': 'interest_payable'}

# Revenues
REVENUES = {**EQUITIES, 'account': 'revenues'}
INTEREST_EARNED_ACCOUNT = {**REVENUES, 'sub_account': 'interest_earned_account'}
INTEREST_EARNED_STAKE = {**REVENUES, 'sub_account': 'interest_earned_stake'}
REWARDS = {**REVENUES, 'sub_account': 'rewards'}
REALIZED_GAIN_LOSS = {**REVENUES, 'sub_account': 'realized_gains_losses'}
UNREALIZED_GAIN_LOSS = {**REVENUES, 'sub_account': 'unrealized_gains_losses'}

# Expenses
EXPENSES = {**EQUITIES, 'account': 'expenses'}
FEES_PAID = {**EXPENSES, 'sub_account': 'fee_expense'}
TAXES_PAID = {**EXPENSES, 'sub_account': 'income_tax_expense'}

# Owner activities
INVESTED_CAPITAL = {**EQUITIES, 'account': 'invested_capital'}
DEPOSITS = {**INVESTED_CAPITAL, 'sub_account': 'usd_deposits'}
WITHDRAWALS = {**INVESTED_CAPITAL, 'sub_account': 'usd_withdrawals'}
TRANSFERS_IN = {**INVESTED_CAPITAL, 'sub_account': 'transfers_in'}
TRANSFERS_OUT = {**INVESTED_CAPITAL, 'sub_account': 'transfers_out'}