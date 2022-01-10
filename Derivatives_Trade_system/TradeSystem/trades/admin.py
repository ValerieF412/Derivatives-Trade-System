from django.contrib import admin
from trades.models import Trade, Company, Currency

# Register your models here.
class TradeAdmin(admin.ModelAdmin):
	fields = ('trade_id', 'product_name', 'add_date', 'buying_party', 
			'selling_party', 'notional_amount', 'notional_currency', 
			'underlying_price', 'underlying_currency', 'strike_price', 'quantity')
    #fieldsets = (
     #   (None, {
		#    'fields': ('trade_id', 'product_name', 'add_date', 'buying_party',
		#	'selling_party', 'notional_amount', 'notional_currency',
		#	'underlying_price', 'underlying_currency', 'strike_price', 'quantity')
		#}),
		#('Correction Trade', {
		#    'classes': ('collapse',),
		#    'fields': ('',)
		#}),
	#)

admin.site.register(Trade, TradeAdmin)
admin.site.register(Company, TradeAdmin)
admin.site.register(Currency, TradeAdmin)
