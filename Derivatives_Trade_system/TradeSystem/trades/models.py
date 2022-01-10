from django.db import models
import datetime
from django.utils import timezone
from django import forms
from django.core.files.base import ContentFile
from simple_history.models import HistoricalRecords
from django.core.validators import MinValueValidator
from django.db.models.signals import post_delete
from django.dispatch import receiver

class Error(models.Model):
	trade_id = models.ForeignKey('Trade', on_delete=models.CASCADE)
	field = models.CharField(max_length=40)
	old = models.FloatField()
	new = models.FloatField()

	@classmethod
	def create(cls,trade_id,field,old,new):
		error = cls(trade_id=trade_id,field=field,old=old,new=new)
		return error

class Company(models.Model):
	companyID = models.CharField(max_length=50, primary_key=True)
	companyName = models.CharField(max_length=50)

class ProductsSold(models.Model):
    product = models.CharField(max_length=40, primary_key=True)
    companyID = models.ForeignKey('Company', on_delete=models.CASCADE)
	#here company_id is a foreign key referencing the
	#company table where the primary key is the id.

class ProductPrices(models.Model):
	product = models.CharField(max_length=30)
	date = models.DateField()
	marketPrice = models.FloatField()

	class Meta:
		unique_together = (('product','date'),)
		ordering = ['-date', 'product']

class StockPrices(models.Model):
	date = models.DateField()
	companyID = models.ForeignKey('Company', on_delete=models.CASCADE)
	stockPrice = models.FloatField()

	class Meta:
		unique_together = (('date','companyID'))
		ordering = ['-date', 'companyID']


class Currency(models.Model):
	currency = models.CharField(max_length=3)
	date = models.DateField()
	valueInUSD = models.FloatField()

	class Meta:
		constraints = [
			models.UniqueConstraint(fields=['date','currency'],name='price_unique')
		]
		ordering = ['-date', 'currency']
	#maybe split currency into two tables? probably not

	#django does not support innate composite primary keys, instead we use unique_together
	#this means that sets of codes and dates have to be unique,
	#one code can have multiple dates, one date can have multiple codes
	#but you cannot have two entries with the same code and date

class Report(models.Model):
	date = models.DateField(primary_key=True)
	pdf = models.FileField(blank=True,upload_to='reports_pdf/')
	csv = models.FileField(blank=True,upload_to='reports_csv/')
	#blank allows the field to be blank, as we are not actually uploading any files
	#we will generate our own files and assign to the fields
@receiver(post_delete, sender=Report)
def file_delete(sender, instance, **kwargs):
	instance.pdf.delete(False)
	instance.csv.delete(False)
	#instance means only currenct model instance deletes
	#False states we dont save model
	#post_delete only occurs if parent object is deleted


class Trade(models.Model):
	product_name = models.CharField(max_length=30,default='')
	add_date = models.DateField(default=datetime.date.today)
	buying_party = models.CharField(max_length=40,default='')
	selling_party = models.CharField(max_length=40,default='')
	notional_amount = models.FloatField(default=None)
	notional_currency = models.CharField(max_length=3,default=None)
	underlying_price = models.FloatField(default=1000,validators=[MinValueValidator(0.01),])
	underlying_currency = models.CharField(max_length=3,default='')
	strike_price = models.FloatField(default=100, validators=[MinValueValidator(0.01),])
	quantity = models.IntegerField(default=50,validators=[MinValueValidator(0.01),])
	maturity_date = models.DateField(default=datetime.date.today)
	history = HistoricalRecords()
	
	def __dir__(self):
		return['product_name','add_date','buying_party','selling_party',
		'underlying_currency','strike_price','quantity','maturity_date']
		
	def get_underlying_price(self, product_name, selling_party, underlying_currency):
		if product_name == 'Stocks':
			price = StockPrices.objects.filter(companyID=selling_party.upper()).first().stockPrice
		else:
			price = ProductPrices.objects.filter(product__iexact=product_name).first().marketPrice
		if underlying_currency != 'USD':
			ccy = Currency.objects.filter(currency__iexact=underlying_currency).first().valueInUSD
		else:
			ccy = 1
		return price / ccy

	def save(self, *args, **kwargs):
		underlying = self.get_underlying_price(self.product_name, self.selling_party, self.underlying_currency)
		self.notional_amount = underlying * self.quantity
		self.underlying_price = underlying
		self.notional_currency = self.underlying_currency
		super().save(*args, **kwargs)
