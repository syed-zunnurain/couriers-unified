"""
URL configuration for app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from shipment import views

urlpatterns = [
    path('api/shipment-requests/', views.create_shipment_request, name='create_shipment_request'),
    path('api/shipment-labels/<str:reference_number>', views.get_shipment_label, name='get_shipment_label'),
    path('api/shipments/<str:reference_number>/track', views.track_shipment, name='track_shipment'),
]
