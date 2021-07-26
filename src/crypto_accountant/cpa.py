from .ledger import Ledger


class CPA:

    def __init__(self, book, config) -> None:
        self.book = book
        self.config = config

    # create balance sheet from book

    def balance_sheet(self, format):
        pass

    # create income statement from book
    def income_statement(self, format):
        pass

     # create cash flows from book
    def cash_flows(self, format):
        pass

     # create tax report from book
    def tax_report(self, format):
        pass

    # Does a performance report on the CPA's performance
    def internal_audit(self):
        pass
