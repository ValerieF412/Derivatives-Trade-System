from rest_framework import serializers
from . models import Trade

class tradesSerializers(serializers.ModelSerializer):
	class Meta:
		model=Trade
		fields=('product','buyingParty','sellingParty','quantity','strikePrice')
