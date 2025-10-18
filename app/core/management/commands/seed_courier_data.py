from django.core.management.base import BaseCommand
from core.models import Courier, ShipmentType, CourierShipmentType, Route, CourierRoute


class Command(BaseCommand):
    help = 'Seed the database with initial data'

    def handle(self, *args, **options):
        self.stdout.write('Starting to seed data...')
        
        # Create DHL courier
        dhl_courier, created = Courier.objects.get_or_create(
            name='DHL',
            defaults={
                'supports_cancellation': True,
                'is_active': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created DHL courier'))
        else:
            self.stdout.write('DHL courier already exists')
        
        # Create shipment types
        shipment_types_data = [
            {'name': 'NORMAL'},
            {'name': 'URGENT'},
            {'name': 'SAME_DAY_DELIVERY'}
        ]
        
        created_shipment_types = []
        for st_data in shipment_types_data:
            shipment_type, created = ShipmentType.objects.get_or_create(
                name=st_data['name']
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created shipment type: {shipment_type.name}'))
            else:
                self.stdout.write(f'Shipment type {shipment_type.name} already exists')
            created_shipment_types.append(shipment_type)
        
        # Link DHL to NORMAL and URGENT shipment types only
        normal_type = ShipmentType.objects.get(name='NORMAL')
        urgent_type = ShipmentType.objects.get(name='URGENT')
        
        for shipment_type in [normal_type, urgent_type]:
            courier_shipment_type, created = CourierShipmentType.objects.get_or_create(
                courier=dhl_courier,
                shipment_type=shipment_type
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Linked DHL to {shipment_type.name} shipment type'))
            else:
                self.stdout.write(f'DHL already linked to {shipment_type.name} shipment type')
        
        # Create routes
        routes_data = [
            {'origin': 'Bonn', 'destination': 'Berlin'},
            {'origin': 'Berlin', 'destination': 'Bonn'}
        ]
        
        created_routes = []
        for route_data in routes_data:
            route, created = Route.objects.get_or_create(
                origin=route_data['origin'],
                destination=route_data['destination']
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created route: {route.origin} → {route.destination}'))
            else:
                self.stdout.write(f'Route {route.origin} → {route.destination} already exists')
            created_routes.append(route)
        
        # Assign both routes to DHL courier
        for route in created_routes:
            courier_route, created = CourierRoute.objects.get_or_create(
                courier=dhl_courier,
                route=route,
                defaults={'is_active': True}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Assigned route {route.origin} → {route.destination} to DHL'))
            else:
                self.stdout.write(f'Route {route.origin} → {route.destination} already assigned to DHL')
        
        self.stdout.write(self.style.SUCCESS('Data seeding completed successfully!'))
