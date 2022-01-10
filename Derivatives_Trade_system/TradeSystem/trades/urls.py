
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views
app_name = 'trades'
urlpatterns = [
    path('', views.index, name='index'), #index.html
    path('data_entry/', views.data_entry, name='data_entry'), #data_entry.html
    path('trade/', views.trades, name='trades'), #trades.html
    path('error_detected/<str:id>/<str:error_type>', views.error_detected, name='error_detected'),
    path('reports/', views.reports, name='reports'), #reports.html
    path('edit/<str:id>',views.edit, name='edit'),
    path('update/<str:id>',views.update, name='update'),
    path('delete/<str:id>',views.delete, name='delete'),
    path('history/<str:id>',views.history, name='history'),
    path('corrections/', views.correction, name='correction'),
    path('corrections/delete/<str:field>/<str:old>/<str:new>', views.delete_correction)
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

#goal is to make a model form on the data_entry.html
