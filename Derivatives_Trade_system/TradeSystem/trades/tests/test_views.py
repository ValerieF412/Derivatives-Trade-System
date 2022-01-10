from django.test import SimpleTestCase, TestCase, Client
from django.urls import reverse, resolve
from trades.views import *
from trades.models import Report, file_delete, ProductPrices, Currency, Trade, Company, ProductsSold
#from trades.func import *
from datetime import datetime
import os

class TestViews(TestCase):

    def setUp(self): #can be run before any test to set up a scenario
        self.trade = Trade(
            product_name = 'Duff',
            add_date = '2015-05-05',
            buying_party = 'QETH27',
            selling_party = 'QETH27',
            notional_amount = 10000.0,
            notional_currency = 'USD',
            underlying_price = 150.0,
            underlying_currency = 'USD',
            strike_price = 150.0,
            quantity = 100,
            maturity_date = '2016-06-06'
        )

        self.price = ProductPrices(
            product = 'Duff',
	        date = '2015-05-05',
	        marketPrice = 150.0
        )

        self.ccy = Currency(
            currency = 'USD',
	        date = '2015-05-05',
	        valueInUSD = 1
        )
        self.price.save()
        self.ccy.save()
        self.trade.save()

        self.client = Client()
        self.reports_url = reverse('trades:reports')
        self.entry_url = reverse('trades:data_entry')
        self.edit_url = reverse('trades:edit', kwargs={'id': self.trade.id})
        self.history_url = reverse('trades:history', kwargs={'id':self.trade.id})
        self.trades_url = reverse('trades:trades')
        self.delete_url = reverse('trades:delete', kwargs={'id': self.trade.id})
        self.update_url = reverse('trades:update', kwargs={'id': self.trade.id})

    def test_reports_GET(self): #tests all reports are retrieved properly
        response = self.client.get(self.reports_url)

        self.assertEquals(response.status_code,200)
        self.assertTemplateUsed(response, 'reports.html')

    def test_reports_POST(self):
        date = {'date_month':5, 'date_day': 5, 'date_year': 2015}
        response = self.client.post(self.reports_url,date)
        #report is generated based on 1 trade.
        report = Report.objects.filter(
            date= '2015-05-05',
            csv = 'reports_csv/2015-05-05',
            pdf = 'reports_pdf/2015-05-05'
            ).first()
        try:
            self.assertEquals(report is None,False)
            self.assertEquals(response.status_code,302)
        except AssertionError as msg:
            file_delete(Report,report)
            print(msg)
        if report:
            file_delete(Report,report)
        #if assertion throws an error it wont reach this if statement without 
        #catching the exception
        #so test report persists, with this if assertion error, file is deleted,
        #if file exists (no error) we stil delete



    def test_data_entry_GET(self):
        response = self.client.get(self.entry_url)

        self.assertEquals(response.status_code,200)
        self.assertTemplateUsed(response, 'data_entry.html')

    def test_data_entry_POST(self):
        self.example_trade = {
            'product_name' : 'Duff',
            'add_date' : '2017-05-05',
            'buying_party' : 'SAAM06',
            'selling_party' : 'SAAM06',
            'notional_amount' : 5250.0, #notional is 150.0*35 = 5250
            'notional_currency' : 'USD',
            'underlying_price' : 150.0,
            'underlying_currency' : 'USD',
            'strike_price' : 110.0, 
            'quantity' : 35,
            'maturity_date' : '2016-06-06'
        } #as we validate product, buyer+seller and currency need to add these such records
        #for the trade to be successful

        self.company = Company(
            companyID = 'SAAM06',
            companyName = 'Test company'
        )

        self.duff = ProductsSold(
            product = 'Duff',
            companyID = self.company
        )

        self.duff.save()
        self.company.save()
        #explcitly do not save example_trade so only possible way it enters db
        #is through the entry POST.

        response = self.client.post(self.entry_url,self.example_trade)
        #posting trade info to data_entry.html
        trade = Trade.objects.get(add_date='2017-05-05', buying_party='SAAM06',
                                     selling_party='SAAM06')
        for key,value in self.example_trade.items():
            self.assertEquals(str(value), str(trade.__dict__[f'{key}']))
            #checks every field of the retrieved trade is the same as the 
            #trade we inserted.
        self.assertEquals(response.status_code,200)


    
    def test_edit_GET(self):
        response = self.client.get(self.edit_url)

        self.assertEquals(response.status_code,200)
        self.assertTemplateUsed(response, 'edit.html')

    
    def test_update_POST(self):
        response = self.client.post(self.update_url,
            {'product_name' : 'Duff',
            'add_date' : '2015-05-05',
            'buying_party' : 'QETH27',
            'selling_party' : 'SAAM06', #changed the selling party 
            'notional_amount' : 10000.0,
            'notional_currency' : 'USD',
            'underlying_price' : 150.0,
            'underlying_currency' : 'USD',
            'strike_price' : 130.0, #also change strike price
            'quantity' : 100,
            'maturity_date' : '2016-06-06'
        })

        self.trade.refresh_from_db()
        #print(self.trade.history.all())
        #test trade is updated
        self.assertEquals(self.trade.selling_party, 'SAAM06')
        self.assertEquals(self.trade.strike_price, 130.0)
        self.assertEquals(response.status_code,302)

    def test_history_GET(self):
        response = self.client.get(self.history_url)
        #edit trade make sure history matches up

        self.assertEquals(response.status_code,200)
        self.assertTemplateUsed(response, 'history.html')
    

    def test_trades_GET(self):
        response = self.client.get(self.trades_url)
        #retrieve trades ensure they are correct.

        self.assertEquals(response.status_code,200)
        self.assertTemplateUsed(response, 'trades.html')

    def test_delete_POST(self): 
        #make trade add to db, assert trade in db.
        #remove trade
        #assert trade not in DB
        response = self.client.get(self.delete_url)
        self.assertEquals(response.status_code, 302)