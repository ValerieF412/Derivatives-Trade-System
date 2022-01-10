from django.test import TestCase
from trades.forms import TradeForm, ReportForm, ErrorDetectedForm

class TestForms(TestCase):

    def test_trade_form_valid_data(self):
        form = TradeForm(data={
            'product_name': 'Stocks',
            'add_date': '2015-06-08',
            'buying_party': 'QETH27',
            'selling_party': 'some seller',
            'underlying_currency': 'auD',
            'strike_price': 111.1,
            'quantity': 65,
            'maturity_date': '2016-09-09'
        })

        self.assertTrue(form.is_valid())

    def test_trade_form_empty(self):
        form = TradeForm(data={})

        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors),8) #missing fields are always an error

    def test_trade_form_invalid_data(self):
        form = TradeForm(data={
            'product_name': 'Stocks', #valid name
            'add_date': '2016-03-40', #invalid date day 
            'quantity': 'twenty', #quant is a float
            'strike_price': -67, #cant have negative strike price
            'buying_party': '',
            'selling_party': '', #no buyers
            'underlying_currency': 'dollar', #incorrect notation
            'maturity_date': 'monday' #not a valid date
            #this should result in 8 errors
        })
        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors),7)

    def test_report_form_valid_data(self):
        form = ReportForm(data={
            'date' : '2016-05-05'
        })
        self.assertTrue(form.is_valid())

    def test_report_form_empty(self):
        form = ReportForm(data={})

        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors),1)

    def test_report_form_invalid_data(self):
        form = ReportForm(data={
            'date': 'monday the 27th'
        })
        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors),1)







        


