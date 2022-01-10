from django.test import TestCase
from trades.models import Trade, Company, ProductPrices, Currency


class TestModels(TestCase):
    def setUp(self):
        #self.trade = Trade(
        #    product_name = 'Duff',
        #    add_date = '2015-05-05',
        #    buying_party = 'QETH27',
        #    selling_party = 'QETH27',
        #    notional_amount = 15000.0,
        #    notional_currency = 'GBP',
        #    underlying_price = 150.0,
        #    underlying_currency = 'GBP',
        #    strike_price = 150.0,
        #    quantity = 100,
        #    maturity_date = '2016-06-06'
        #) This is the desired trade attributes
        self.form_input = {
            'product_name' : 'Duff',
            'add_date' : '2015-05-05',
            'buying_party' : 'QETH27',
            'selling_party' : 'QETH27',
            'underlying_currency' : 'GBP',
            'strike_price' : 150.0,
            'quantity' : 100,
            'maturity_date' : '2016-06-06'
        }

        self.price = ProductPrices(
            product = 'Duff',
	        date = '2015-05-05',
	        marketPrice = 150.0
        )

        self.ccy = Currency(
            currency = 'GBP',
	        date = '2015-05-05',
	        valueInUSD = 1
        )

        self.company = Company(
            companyID = 'SAAM06',
            companyName = 'Test company'
        )
        self.company.save()
        self.price.save()
        self.ccy.save()
        
    def test_assign_trade_on_input(self):
        self.trade = Trade()
        for key,value in self.form_input.items(): #dont actually set underlying
            self.trade.__dict__[f'{key}'] = value#price or notional amount or 
        self.trade.save()                           #notional curency.
        
        self.assertEquals(self.trade.notional_amount,15000.0) #underlying at 150, 100 items
        self.assertEquals(self.trade.notional_currency,self.trade.underlying_currency)
        
        
