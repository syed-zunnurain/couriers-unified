from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Seed all initial data (courier data + courier config)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true'
        )
        parser.add_argument(
            '--skip-migrations',
            action='store_true'
        )

    def check_tables_exist(self):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('couriers', 'courier_configs')
            """)
            existing_tables = [row[0] for row in cursor.fetchall()]
            return 'couriers' in existing_tables and 'courier_configs' in existing_tables
    
    def check_data_exists(self):
        try:
            from core.models import Courier
            return Courier.objects.exists()
        except Exception:
            return False

    def handle(self, *args, **options):
        self.stdout.write('🌱 Starting comprehensive database seeding...')
        
        # Check if tables exist
        if not options['skip_migrations'] and not self.check_tables_exist():
            self.stdout.write('⚠️  Required tables not found. Running migrations first...')
            try:
                call_command('migrate')
                self.stdout.write(self.style.SUCCESS('✅ Migrations completed'))
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Migration failed: {str(e)}')
                )
                raise
        
        # Check if data already exists
        if self.check_data_exists() and not options.get('force', False):
            self.stdout.write(
                self.style.WARNING('⚠️  Database already contains data. Skipping seeding.')
            )
            self.stdout.write('💡 Use --force to re-seed existing data')
            return
        
        try:
            # Run courier data seeding
            self.stdout.write('📦 Seeding courier data...')
            call_command('seed_courier_data')
            
            # Run courier config seeding
            self.stdout.write('⚙️ Seeding courier configurations...')
            call_command('seed_courier_config')
            
            self.stdout.write(
                self.style.SUCCESS('✅ Database seeding completed successfully!')
            )
            self.stdout.write('💡 Next time, you can run: python manage.py seed_all')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error during seeding: {str(e)}')
            )
            logger.error(f"Seeding error: {str(e)}")
            raise
