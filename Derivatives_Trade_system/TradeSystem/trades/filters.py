import django_filters
from django_filters import DateFilter
from .models import *

class TradeFilter(django_filters.FilterSet):
    start_date = DateFilter(field_name="add_date", lookup_expr="gte")
    end_date = DateFilter(field_name="add_date", lookup_expr="lte")
    class Meta:
        model = Trade
        fields = '__all__'
        exclude = [
                'add_date',
                'notional_amount',
                'notional_currency',
                'underlying_price',
                'underlying_currency',
                'strike_price',
                'quantity',
                'maturity_date',
                ]
