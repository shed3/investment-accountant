from base import BaseTx
from entry_config import CRYPTO, REALIZED_GAIN_LOSS, UNREALIZED_GAIN_LOSS, CRYPTO_FAIR_VALUE_ADJ

# first, adjust to market and accrue unrealized gains.
adj_fair_value = {'side': "debit", 'type': 'adjust', 'quantity': 0, **CRYPTO_FAIR_VALUE_ADJ}
adj_unrealized_gains = {'side': "credit", 'type': 'adjust', 'quantity': 0, **UNREALIZED_GAIN_LOSS}
adj_to_fair_value_entries = [adj_fair_value, adj_unrealized_gains]


# close crypto (init), adj(change), and open new cash/crypto (total) -- last out of scope of base taxable
close_crypto = {'side': "credit", **CRYPTO}
close_fair_value = {'side': "credit", **CRYPTO_FAIR_VALUE_ADJ}
close_credit_entries = [close_crypto, close_fair_value]
# open depends on type and should be implemented there via the debit transaction.

# move gains from unrealized to realized (change)
close_unrealized_gains = {'side': "debit", **UNREALIZED_GAIN_LOSS}
close_realized_gains = {'side': "credit", **REALIZED_GAIN_LOSS}
close_gain_entries = [close_unrealized_gains, close_realized_gains]

credit_fee_entry = {'side': "credit", 'type': 'fee', 'mkt': 'fee', **CRYPTO}
# I think this single fee entry is suspicious, could be causing a good amount of imbalance if not taken into account properly elsewhere.


class TaxableTx(BaseTx):
    # Each taxable transaction entry should have the correct open quote, close quote, and current quote added. This will allow us to automatically derive gains, tax and (I think) equity curve

    def __init__(self, adj_entries=adj_to_fair_value_entries, close_entries=close_credit_entries, gain_entries=close_gain_entries, **kwargs) -> None:
        super().__init__(**kwargs)
        self.taxable_assets = {}
        self.adj_entries = adj_entries
        self.close_entries = close_entries
        self.gain_entries = gain_entries
        if 'fee' in self.assets.keys():
            if not self.assets['fee'].is_fiat:
                #  add fee to taxable assets and set credit entry to use crypto account
                fee_entries = {
                    **self.fee_entry_template,
                    'credit': credit_fee_entry
                    # this fee entry is also suspicious when I changed it, kayne
                }
                self.fee_entry_template = fee_entries.copy()  # set credit entry to use crypto account
            if not self.assets['fee'].is_stable:
                self.add_taxable_asset('fee', fee_entries.copy())

    def add_taxable_asset(self, name, entry_template):
        # name of assets position in tx -> can be any of [base, quote, fee]
        self.taxable_assets[name] = entry_template
        self.taxable = True

    def generate_debit_entry(self):
        entries = [self.create_entry(**self.entry_template['debit'])]
        if 'fee' in self.taxable_assets.keys():
            entries.append(self.create_entry(**self.fee_entry_template['debit']))
        return entries

    def generate_credit_entries(self, asset, open_price, qty, **kwargs):

        # 1. adjust to market entries
        tx_asset = self.assets[asset]
        closing_val = tx_asset.usd_price * qty
        open_val = open_price * qty
        change_val = closing_val - open_val
        all_entries = []
        # entries are the same otherwise, so for loop
        for entry in self.adj_entries:
            adj_config = {
                **entry,
                'mkt': asset,
                'quote': tx_asset.usd_price,
                'value': change_val,
            }

            all_entries.append(self.create_entry(**adj_config))

        close_cost_basis_entry = self.close_entries[0]
        close_fair_value_entry = self.close_entries[1]
        # 2. close crypto and fair value
        close_base_config = {
            'mkt': asset,
            'type': kwargs.get('type', self.type),
            'quote': open_price,
            'close_quote': tx_asset.usd_price,
        }
        close_cost_basis_entry = {
            **close_cost_basis_entry,
            **close_base_config,
            'quantity': qty,  # intentionally 0, if overwritten will affect quantity which is not wanted
            'value': open_val,
        }
        close_fair_value_entry = {
            **close_fair_value_entry,
            **close_base_config,
            'quantity': 0,  # intentionally 0, if overwritten will affect quantity which is not wanted
            'value': change_val,
        }
        all_entries.append(self.create_entry(**close_cost_basis_entry))
        all_entries.append(self.create_entry(**close_fair_value_entry))
        # 3. Move gains (use same value as fair value entry uses)
        for entry in self.gain_entries:
            adj_config = {
                **entry,
                'mkt': asset,
                'type': kwargs.get('type', self.type),
                'quantity': 0,  # intentionally 0, if overwritten will affect quantity which is not wanted
                'quote': open_price,
                'close_quote': tx_asset.usd_price,
                'value': change_val,
            }
            all_entries.append(self.create_entry(**adj_config))

        return all_entries
