from django.urls import path
from . import views
from . import webhook_views

urlpatterns = [
    # Shipment request endpoints
    path('shipment-requests/', views.create_shipment_request, name='create_shipment_request'),
    
    # Shipment label endpoints
    path('shipment-labels/<str:reference_number>/', views.get_shipment_label, name='get_shipment_label'),
    
    # Shipment tracking endpoints
    path('shipments/<str:reference_number>/track/', views.track_shipment, name='track_shipment'),
    
    # Shipment cancellation endpoints
    path('shipments/<str:reference_number>/cancel/', views.cancel_shipment, name='cancel_shipment'),
    
    # Webhook endpoints
    path('webhooks/dhl/', webhook_views.dhl_webhook, name='dhl_webhook'),
]
