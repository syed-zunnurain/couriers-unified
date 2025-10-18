from django.urls import path
from . import views

urlpatterns = [
    path('shipment-requests/', views.create_shipment_request, name='create_shipment_request'),
]
