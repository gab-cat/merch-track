# app/migrations/000X_set_initial_pks.py

from django.db import migrations

from django.db import migrations, connection

def set_initial_pks(apps, schema_editor):
    with connection.cursor() as cursor:
        cursor.execute("SELECT setval(pg_get_serial_sequence('customer', 'customerId'), 10000, false);")
        cursor.execute("SELECT setval(pg_get_serial_sequence('product', 'productId'), 20000, false);")
        cursor.execute("SELECT setval(pg_get_serial_sequence('order', 'orderId'), 30000, false);")
        cursor.execute("SELECT setval(pg_get_serial_sequence('order_item', 'orderItemId'), 40000, false);")
        cursor.execute("SELECT setval(pg_get_serial_sequence('payment', 'paymentId'), 50000, false);")
        cursor.execute("SELECT setval(pg_get_serial_sequence('inventory', 'inventoryId'), 60000, false);")
        cursor.execute("SELECT setval(pg_get_serial_sequence('fulfillment', 'fulfillmentId'), 70000, false);")

class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_customer_fulfillment_inventory_order_orderitem_and_more'),  # Replace with your last migration file
    ]

    operations = [
        migrations.RunPython(set_initial_pks),
    ]
