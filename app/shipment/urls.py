from django.urls import path
from . import views

urlpatterns = [
    # Shipment request endpoints
    path('shipment-requests/', views.create_shipment_request, name='create_shipment_request'),
    
    # Shipment label endpoints
    path('shipment-labels/<str:reference_number>/', views.get_shipment_label, name='get_shipment_label'),
    
    # Shipment tracking endpoints
    path('shipments/<str:reference_number>/track/', views.track_shipment, name='track_shipment'),
]
