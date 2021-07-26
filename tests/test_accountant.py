import pytest
import numpy as np
from src.crypto_accountant.config import cpa_config
from src.crypto_accountant.accountant import Accountant


class TestCPA:

    def test_process(self, local_txs):
        # Transform to include running once for each transaction and setting the processed flag. Also check for different ledger before and after.
        pass

    def test_process_transaction(self, local_txs):
        # Test checking for the type from config
        # test checking for fee
        # test sending to journal ? Might be integration idk.
        # test for no trans type and for trans type unknown.

        cpa = Accountant()
        cpa.process(local_txs)
        # assert len(cpa.symbols) == 1
        print('Current account ledger for testing credits and debits:\n{}', format(
            cpa.ledger.positions_ledger.loc[:, ['Credits', 'Debits']]))
        # Currently not working because there are no Credits, need to look later.
        # assert cpa.accounts_balance.sum()['Credits'] == cpa.accounts_balance.sum()['Debits']
        if len(local_txs) > 1:
            debits = []
            credits = []
            accounts = []
            fees = 0
            for t in local_txs:
                keys = cpa_config[t['type']]
                debits.append(len(keys['debits']))
                credits.append(len(keys['credits']))

                if t['feeQuantity'] > 0:
                    fees += 2
                for credit in keys['credits']:
                    accounts.append(credit['Sub Account'])
            assert len(cpa.ledger.ledger) == np.sum(
                debits) + np.sum(credits) + fees
            for acct in accounts:
                assert acct in cpa.ledger.accounts_ledger.index.get_level_values(
                    'Sub Account')

        elif len(local_txs) == 1:
            keys = cpa_config[local_txs[0]['type']]
            debits = len(keys['debits'])
            credits = len(keys['credits'])
            assert len(cpa.transactions_ledger) == debits + credits

            accounts = []
            for debit in keys['debits']:
                accounts.append(debit['Sub Account'])
            for credit in keys['credits']:
                accounts.append(credit['Sub Account'])
            for acct in accounts:
                assert acct in cpa.accounts_ledger.index.get_level_values(
                    'Sub Account')

    # Import a credit and a debit
    # Credit only, make sure credits, creditsdf, and ledger are right
    # Debit only, make sure debits, debitsdf, and ledger are right
    # Debitand credit, make sure debits, credits, debitsdf, creditsdf and ledger are right
    def test_process(self, local_txs):
        # Transform to include running once for each transaction and setting the processed flag. Also check for different ledger before and after.
        pass

    def test_process_transaction(self, local_txs):
        # Test checking for the type from config
        # test checking for fee
        # test sending to journal ? Might be integration idk.
        # test for no trans type and for trans type unknown.
        pass

    def test_check_fees(self, local_txs):
        pass

    def test_process_fees(self, local_txs):
        pass

    def test_check_taxable(self, local_txs):
        pass

    def test_close_positions(self, local_txs):
        # This currently does the role of every position related thing, will be broken down further. This should simply determine if it needs to be closed, fetch the correct position, and debit it, repeating until closed.
        pass

    def test_get_current_positions(self, local_txs):
        pass

    def test_get_position_with_method(self, local_txs):
        pass
    # Use params for different methods above

    def test_set_ledger_values(self, local_txs):
        # Should get everything from config and change trans values for varialbes.
        pass

    def test_journal_transaction(self, local_txs):
        # make sure run for each debit and credit
        # Check taxable check
        # Test sending to set ledger values ?
        # Test debit and credit ledger ?
        pass

    def test_balance_sheet(self, local_txs):
        pass

    def test_income_statement(self, local_txs):
        pass

    def test_cash_flow_statement(self, local_txs):
        pass

    def test_save_timeseries(self, local_txs):
        pass

    def test_save_summary(self, local_txs):
        pass

    def test_save_pdf_report(seself, local_txs):
        pass
