import os
import boto3
from celery import shared_task
from django.conf import settings
from django.db import connections
from django.core.mail import send_mail
from django.template.loader import render_to_string
import environ
from collections import defaultdict
from datetime import datetime, date, timedelta
from .models import Defects, MachineParametersGraph, LiquidPlant



from datetime import datetime, date, timedelta
from django.utils import timezone
from collections import defaultdict
from django.core.mail import send_mail
from django.template.loader import render_to_string
from celery import shared_task
from django.conf import settings
from .models import LiquidPlant, MachineParametersGraph


# Initialize environment variables
env = environ.Env()
environ.Env.read_env(os.path.join(settings.BASE_DIR, '.env'))

@shared_task
def sync_data_with_cloud():
    try:
        with connections['default'].cursor() as local_cursor, connections['cloud'].cursor() as cloud_cursor:
            # Fetch all records from the local database
            local_cursor.execute("SELECT * FROM LiquidPlant;")
            local_records = local_cursor.fetchall()

            # Fetch existing record IDs and recorded_date_times in the cloud database for quick lookup
            cloud_cursor.execute("SELECT id, recorded_date_time FROM LiquidPlant;")
            cloud_records = cloud_cursor.fetchall()
            cloud_ids = {r[0] for r in cloud_records}
            cloud_recorded_dates = {str(r[1]) for r in cloud_records}

            # Initialize the S3 client for DigitalOcean Spaces
            s3_client = boto3.client(
                's3',
                region_name='us-east-1',
                endpoint_url=f"https://{env('SPACE_ENDPOINT')}",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
            )

            # Track synced records to avoid duplicates
            synced_records = []

            # Iterate through local records and compare with cloud records
            for record in local_records:
                record_id = record[0]
                recorded_date_time = str(record[2])

                # Check if the record ID or recorded_date_time already exists in the cloud database
                if record_id in cloud_ids or recorded_date_time in cloud_recorded_dates:
                    print(f"Skipping record {record_id} with recorded_date_time {recorded_date_time} as it already exists in the cloud.")
                    continue

                # Fetch the image path from the database (assuming it's stored in the 1st column, adjust if needed)
                image_relative_path = record[1]

                # Construct full image path without adding /media again
                if image_relative_path.startswith(settings.MEDIA_URL):
                    image_relative_path = image_relative_path[len(settings.MEDIA_URL):]
                image_path = os.path.join(settings.MEDIA_ROOT, image_relative_path.lstrip('/'))

                print(f"Constructed image path: {image_path}")  # Print the constructed image path

                if os.path.exists(image_path):
                    try:
                        # Extract information from the image file name
                        image_name_parts = os.path.basename(image_relative_path).split('_')
                        plant_id = image_name_parts[0]
                        defect_id = image_name_parts[1]
                        recorded_date = image_name_parts[2].split('T')[0]

                        # Fetch the defect name from the defect_id
                        local_cursor.execute("SELECT name FROM Defects WHERE id = %s;", [defect_id])
                        defect_name = local_cursor.fetchone()[0]

                        # Construct the S3 path
                        s3_path = os.path.join(plant_id, recorded_date, defect_name, os.path.basename(image_relative_path))

                        # Determine content type
                        content_type = 'image/png' if image_relative_path.lower().endswith('.png') else 'image/jpeg'

                        # Upload the image to DigitalOcean Spaces with public-read permission and content type
                        with open(image_path, 'rb') as image_file:
                            s3_client.upload_fileobj(
                                image_file, 
                                settings.AWS_STORAGE_BUCKET_NAME, 
                                s3_path,
                                ExtraArgs={'ACL': 'public-read', 'ContentType': content_type}  # Set public-read permission and content type
                            )

                        # Update the image URL to the cloud path
                        cloud_image_url = f"https://{env('SPACE_ENDPOINT')}/{settings.AWS_STORAGE_BUCKET_NAME}/{s3_path}"

                        # Insert the record into the cloud database
                        cloud_cursor.execute("""
                            INSERT INTO LiquidPlant (image, recorded_date_time, defects_id, department_id, machines_id, plant_id, product_id)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """, (cloud_image_url, record[2], record[3], record[4], record[5], record[6], record[7]))

                        # Optionally, log success
                        print(f"Record synced: {record}")

                        # Add the record ID to the synced list
                        synced_records.append(record_id)

                    except Exception as e:
                        print(f"Failed to upload image for record {record_id}: {e}")
                else:
                    print(f"Image file not found for record {record_id}: {image_path}")

            # Commit the transaction to persist changes
            cloud_cursor.connection.commit()

    except Exception as e:
        print(f"Error syncing records. Error: {e}")



from datetime import datetime, timedelta
from collections import defaultdict
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from .models import LiquidPlant, MachineParametersGraph, Defects
from django.conf import settings
from celery import shared_task

@shared_task
def send_daily_defects_report():
    try:
        today = timezone.localtime(timezone.now()).date()
        start_of_today = timezone.make_aware(datetime.combine(today, datetime.min.time()))
        end_of_today = timezone.make_aware(datetime.combine(today, datetime.max.time()))

        print("Start of today:", start_of_today)
        print("End of today:", end_of_today)

        # Fetch all relevant machine parameters and defects
        parameters_graph = MachineParametersGraph.objects.all()
        defects = LiquidPlant.objects.all()

        # Initialize dictionaries to store defect counts and DPMU
        defect_counts_today = defaultdict(int)
        defect_counts_other_days = defaultdict(lambda: defaultdict(int))
        dpmu_today = defaultdict(float)
        dpmu_other_days = defaultdict(lambda: defaultdict(float))

        # Aggregate defect counts and DPMU for today and other days
        for defect in defects:
            try:
                defect_datetime = timezone.make_aware(datetime.strptime(defect.recorded_date_time, '%Y-%m-%dT%H:%M:%S'))
                if start_of_today <= defect_datetime <= end_of_today:
                    defect_name = defect.defects.name
                    defect_counts_today[defect_name] += 1
                else:
                    defect_date = defect_datetime.date()
                    defect_counts_other_days[str(defect_date)][defect.defects.name] += 1
            except ValueError:
                pass  # Handle invalid datetime format gracefully

        for graph in parameters_graph:
            try:
                graph_datetime = timezone.make_aware(datetime.strptime(graph.recorded_date_time, '%Y-%m-%dT%H:%M:%S'))
                date_only_str = graph.recorded_date_time[:10]  # Extracting date part

                if start_of_today <= graph_datetime <= end_of_today:
                    if graph.machine_parameter.parameter == "Reject Counter":
                        defect_counts_today[graph_datetime.date()][graph.machine.parameter] += int(graph.params_count)
                    elif graph.machine_parameter.parameter in ["Program Counter", "Machine Counter"]:
                        dpmu_today[date_only_str] += int(graph.params_count)  # Accumulate for DPMU calculation
                else:
                    if graph.machine_parameter.parameter == "Reject Counter":
                        defect_counts_other_days[str(graph_datetime.date())][graph.machine.parameter] += int(graph.params_count)
                    elif graph.machine_parameter.parameter in ["Program Counter", "Machine Counter"]:
                        dpmu_other_days[date_only_str] += int(graph.params_count)  # Accumulate for DPMU calculation

            except ValueError:
                pass  # Handle invalid datetime format gracefully

        # Calculate DPMU for today and other days
        for date_only_str, counts in dpmu_today.items():
            total_production_count = counts
            defect_count = defect_counts_today[date_only_str].get('Reject Counter', 0)

            if total_production_count > 0:
                defect_percentage = (defect_count / total_production_count) * 1000000
            else:
                defect_percentage = 0

            dpmu_today[date_only_str] = round(defect_percentage, 2)

        for date_only_str, counts in dpmu_other_days.items():
            total_production_count = counts
            defect_count = defect_counts_other_days[date_only_str].get('Reject Counter', 0)

            if total_production_count > 0:
                defect_percentage = (defect_count / total_production_count) * 1000000
            else:
                defect_percentage = 0

            dpmu_other_days[date_only_str] = round(defect_percentage, 2)

        # Prepare the final report structure including DPMU
        daily_defects_report = {}
        for date_str, defect_counts in defect_counts_other_days.items():
            daily_defects_report[date_str] = {
                'defects': dict(defect_counts),
                'dpmu': dpmu_other_days[date_str]
            }
        daily_defects_report[str(today)] = {
            'defects': dict(defect_counts_today),
            'dpmu': dpmu_today
        }

        print("Daily Defects Report:", daily_defects_report)

        # Render email template
        email_body = render_to_string('reports.html', {
            'date': today.isoformat(),
            'defect_data': daily_defects_report.get(str(today), {}).get('defects', {}),
            'dpmu_data': daily_defects_report.get(str(today), {}).get('dpmu', {}),
        })

        # Send email
        send_mail(
            subject=f'Daily Defects Report for {today.isoformat()}',
            message='',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=["saithimma@ekfrazo.in"],
            html_message=email_body
        )

        print("Daily defects report email sent successfully.")

    except Exception as e:
        print(f"Error sending daily defects report. Error: {e}")



##### tasks for syncing the machine parameteres graph ########

# tasks.py

from django.db import transaction
from datetime import datetime

@shared_task
def sync_machine_parameters():
    local_records = MachineParametersGraph.objects.using('default').all()
    records_to_update = []
    records_to_create = []

    for record in local_records:
        # Extract date part from recorded_date_time
        date_part = record.recorded_date_time.split('T')[0]

        with transaction.atomic(using='cloud'):
            # Check if the record exists in the global database
            global_record = MachineParametersGraph.objects.using('cloud').filter(
                recorded_date_time__startswith=date_part,
                machine_parameter=record.machine_parameter,
                plant=record.plant
            ).first()

            if global_record:
                # Update the existing record
                global_record.params_count = record.params_count
                records_to_update.append(global_record)
            else:
                # Create a new record
                new_global_record = MachineParametersGraph(
                    machine_parameter=record.machine_parameter,
                    params_count=record.params_count,
                    recorded_date_time=record.recorded_date_time,
                    plant=record.plant
                )
                records_to_create.append(new_global_record)

    # Perform bulk update
    if records_to_update:
        MachineParametersGraph.objects.using('cloud').bulk_update(records_to_update, ['params_count'])
        print(f'Updated {len(records_to_update)} records in global database')

    # Perform bulk create
    if records_to_create:
        MachineParametersGraph.objects.using('cloud').bulk_create(records_to_create)
        print(f'Created {len(records_to_create)} new records in global database')