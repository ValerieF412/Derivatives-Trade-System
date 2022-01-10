from django.test import SimpleTestCase
from django.urls import reverse, resolve
from trades.views import *


class TestUrls(SimpleTestCase): #basic url unit tests

    def test_index_url_resolves(self):
        url = reverse("trades:index")
        self.assertEquals(resolve(url).func,index)

    def test_data_entry_url_resolves(self):
        url = reverse("trades:data_entry")
        self.assertEquals(resolve(url).func,data_entry)

    def test_trades_url_resolves(self):
        url = reverse("trades:trades")
        self.assertEquals(resolve(url).func,trades)

    def test_reports_url_resolves(self):
        url = reverse("trades:reports")
        self.assertEquals(resolve(url).func,reports)
        
    def test_edit_url_resolves(self):
        url = reverse("trades:edit",args=['some_id'])
        self.assertEquals(resolve(url).func,edit)

    def test_update_url_resolves(self):
        url = reverse("trades:update",args=['some_id'])
        self.assertEquals(resolve(url).func,update)

    def test_delete_url_resolves(self):
        url = reverse("trades:delete",args=['some_id'])
        self.assertEquals(resolve(url).func,delete)

    def test_history_url_resolves(self):
        url = reverse("trades:history",args=['some_id'])
        self.assertEquals(resolve(url).func,history)