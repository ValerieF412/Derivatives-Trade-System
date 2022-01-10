from django import forms
from django.forms import ModelForm
from . import models
from django.forms.widgets import SelectDateWidget

class TradeForm(ModelForm):
    '''https://docs.djangoproject.com/en/3.0/topics/forms/modelforms/'''
    #add_date = forms.DateField(input_formats=('%d-%m-%Y',))
    #maturity_date = forms.DateField(input_formats=('%d-%m-%Y',))
    class Meta:
        model = models.Trade
        fields = ['product_name', 'add_date', 'buying_party', 'selling_party', 'underlying_currency', 'strike_price', 'quantity', 'maturity_date']
        exclude = ['notional_amount', 'notional_currency','underlying_price']

class ReportForm(ModelForm):
    date = forms.DateField(widget=SelectDateWidget())

    class Meta:
        model = models.Report
        fields = ['date']
        exclude=['pdf','csv']

class ErrorDetectedForm(forms.Form):
    strike_price = forms.FloatField()
    quantity = forms.IntegerField()

    def pop_strike(self, *args, **kwargs):
        self.fields.pop('strike_price')
    def pop_quant(self, *args, **kwargs):
        self.fields.pop('quantity')


