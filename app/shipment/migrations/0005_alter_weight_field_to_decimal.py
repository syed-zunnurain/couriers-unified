# Generated manually to fix weight field type
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shipment', '0004_create_shipments_table'),
    ]

    operations = [
        migrations.RunSQL(
            "ALTER TABLE shipments ALTER COLUMN weight TYPE NUMERIC(10,2);",
            reverse_sql="ALTER TABLE shipments ALTER COLUMN weight TYPE INTEGER;"
        ),
    ]
