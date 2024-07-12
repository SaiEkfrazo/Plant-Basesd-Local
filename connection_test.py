import os
import django
from django.db import connections

# Set the settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vin.settings')

# Setup Django
django.setup()

print('something')

# Example: Fetching records from the local database
with connections['default'].cursor() as cursor:
    cursor.execute("SELECT * FROM LiquidPlant;")
    local_records = cursor.fetchall()
    print("Local records:", local_records)

# Example: Fetching records from the cloud database
with connections['cloud'].cursor() as cursor:
    cursor.execute("SELECT * FROM LiquidPlant")
    cloud_record = cursor.fetchall()
    print("Cloud record:", cloud_record)
