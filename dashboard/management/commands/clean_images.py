import os
from django.core.management.base import BaseCommand
from dashboard.models import NMBDashboard, LiquidPlant, ShampooPlant
from django.conf import settings
from django.db import connection

class Command(BaseCommand):
    help = 'Delete records and images beyond the latest 30,000 records for each plant type'

    def handle(self, *args, **kwargs):
        # Uncomment others if needed
        # self.clean_plant_records(NMBDashboard)
        self.clean_plant_records(LiquidPlant)
        # self.clean_plant_records(ShampooPlant)

    def clean_plant_records(self, model):
        # Define the model name for SQL queries
        table_name = model._meta.db_table

        # Get the total number of records
        total_records = model.objects.count()

        # Calculate how many records to delete
        records_to_delete_count = total_records - 30000

        if records_to_delete_count <= 0:
            self.stdout.write(f"No records to delete for {table_name}.")
            return

        # Define batch size
        batch_size = 1000
        deleted_image_count = 0
        deleted_record_count = 0

        with connection.cursor() as cursor:
            while records_to_delete_count > 0:
                # Fetch IDs of the oldest records to delete
                cursor.execute(f"""
                    SELECT id, image
                    FROM {table_name}
                    ORDER BY recorded_date_time
                    LIMIT {batch_size}
                """)
                records = cursor.fetchall()

                # If there are no more records to process, break the loop
                if not records:
                    break

                # Delete associated images from the Docker volume
                for record_id, image in records:
                    if image:  # Ensure the image field is not empty
                        image_path = os.path.join(settings.MEDIA_ROOT, image)
                        if os.path.exists(image_path):
                            os.remove(image_path)
                            deleted_image_count += 1

                # Delete the old records from the database
                ids_to_delete = [record_id for record_id, _ in records]
                format_strings = ','.join(['%s'] * len(ids_to_delete))
                cursor.execute(f"""
                    DELETE FROM {table_name}
                    WHERE id IN ({format_strings})
                """, tuple(ids_to_delete))

                deleted_record_count += cursor.rowcount
                records_to_delete_count -= batch_size

        # Output summary
        self.stdout.write(f"Deleted {deleted_image_count} images and {deleted_record_count} records from {table_name}")
