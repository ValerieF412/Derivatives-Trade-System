from import_export import resources
from .models import Trade

class TradeResource(resources.ModelResource):
	class Meta:
		model=Trade