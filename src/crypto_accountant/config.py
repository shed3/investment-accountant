id = '-id'
connection_id = '-connectionId'
tx_type = '-tx_type'
timestamp = '-timestamp'
value = '-subTotal'

asset_account = 'Assets'
equity_account = 'Equities'
liabilities = 'Liabilities'
crypto_account = 'Cryptocurrencies'
cash_account = 'Cash'


def entry_config_factory(acct, sub_acct, side, **kwargs):
    mkt = kwargs.get("mkt", "base")
    base_config = {
        'id': kwargs.get("id", id),
        'account': acct,
        'sub_account': sub_acct,
        'tx_type': kwargs.get("tx_type", tx_type),
        'timestamp': kwargs.get("timestamp", timestamp),
        'taxable': kwargs.get("taxable", False),
        'symbol': kwargs.get("symbol", '-{}Currency'.format(mkt)),
        'position': kwargs.get("position", '-{}UsdPrice'.format(mkt)),
        '{}_value'.format(side): kwargs.get("value", '{}'.format(value)),
        '{}_quantity'.format(side): kwargs.get('quantity', '-{}Quantity'.format(mkt)),
    }
    return base_config


deposit = [
    entry_config_factory(asset_account, cash_account, "debit"),
    entry_config_factory(equity_account, 'Invested Capital', "credit"),
]

withdrawal = [
    entry_config_factory(equity_account, 'Withdrawn Capital', "debit"),
    entry_config_factory(asset_account, cash_account, "credit"),
]

fee = [
    entry_config_factory(liabilities, 'Fees Paid', "debit", mkt="fee", tx_type="fees"),
    entry_config_factory(asset_account, crypto_account, "credit", mkt="fee", tx_type="fees"),
]

buy = [
    entry_config_factory(asset_account, crypto_account, "debit"),
    entry_config_factory(asset_account, crypto_account, "credit", mkt="quote"),
]

sell = [
    entry_config_factory(asset_account, crypto_account, "debit", mkt="quote",
                         value="-closeTotal", quantity="-closeQuoteQuantity", taxable=True),
    entry_config_factory(asset_account, crypto_account, "credit", position="-closePosition",
                         value="-closeValue", quantity="-closeQuantity", taxable=True),
]

realized_gains = [
    entry_config_factory(equity_account, "Realized Gains / Losses", "credit",
                         position="-closePosition", value="-closeGain", quantity="-closeQuantity", taxable=True)
]

send = [
    entry_config_factory(equity_account, 'Transfers Out', "debit"),
    entry_config_factory(asset_account, crypto_account, "credit"),
]

receive = [
    entry_config_factory(asset_account, crypto_account, "debit"),
    entry_config_factory(equity_account, 'Transfers In', "credit"),
]

reward = [
    entry_config_factory(asset_account, crypto_account, "debit"),
    entry_config_factory(equity_account, 'Rewards', "credit"),
]

interest_in_account = [
    entry_config_factory(asset_account, crypto_account, "debit"),
    entry_config_factory(equity_account, 'Interest Earned Account', "credit"),
]

interest_in_stake = [
    entry_config_factory(asset_account, crypto_account, "debit"),
    entry_config_factory(equity_account, 'Interest Earned Stake', "credit"),
]

account_configs = {
    'fees': fee,
    'deposit': deposit,
    'withdrawal': withdrawal,
    'buy': buy,
    'sell': sell + realized_gains,
    'send': send,
    'receive': receive,
    'reward': reward,
    'interest-in-stake': interest_in_stake,
    'interest-in-account': interest_in_account,
}
