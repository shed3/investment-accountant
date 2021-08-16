from decimal import Decimal


class Entry:

    def __init__(self, **kwargs) -> None:
        self.id = kwargs.get('id', '')
        self.account_type = kwargs.get('account_type', '')
        self.account = kwargs.get('account', '')
        self.sub_account = kwargs.get('sub_account', '')
        self.timestamp = kwargs.get('timestamp', '')
        self.symbol = kwargs.get('symbol', '')
        self.side = kwargs.get('side', '')
        self.type = kwargs.get('type', '')

        # setters will ensure Decimal conversion
        self.quantity = kwargs.get('quantity', 0)
        self.value = kwargs.get('value', 0)
        self.quote = kwargs.get('quote', 0)
        self.close_quote = kwargs.get('close_quote', 0)

    @property
    def quantity(self):
        return self._quantity

    @property
    def value(self):
        return self._value

    @property
    def quote(self):
        return self._quote

    @property
    def close_quote(self):
        return self._close_quote

    @quantity.setter
    def quantity(self, qty):
        self._quantity = qty if isinstance(qty, Decimal) else Decimal(qty)

    @value.setter
    def value(self, val):
        self._value = val if isinstance(val, Decimal) else Decimal(val)

    @quote.setter
    def quote(self, val):
        self._quote = val if isinstance(val, Decimal) else Decimal(val)

    @close_quote.setter
    def close_quote(self, val):
        self._close_quote = val if isinstance(val, Decimal) else Decimal(val)
    
    def to_dict(self):  
        val = self.__dict__.copy()
        val['quantity'] = val['_quantity']
        val['value'] = val['_value']
        val['quote'] = val['_quote']
        del val['_quantity']
        del val['_value']
        del val['_quote']

        if val['_close_quote'] != 0:
            val['close_quote'] = val['_close_quote']
        del val['_close_quote']
        
        return val