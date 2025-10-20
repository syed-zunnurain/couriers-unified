from django.urls import path
from . import views

urlpatterns = [
    path('shipment-requests/', views.create_shipment_request, name='create_shipment_request'),
    path('shipment-labels/<str:reference_number>', views.get_shipment_label, name='get_shipment_label'),
]
