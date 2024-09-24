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
from .models import *

from django.core.cache import cache

from datetime import datetime, date, timedelta
from django.utils import timezone
from collections import defaultdict
from django.core.mail import send_mail
from django.template.loader import render_to_string
from celery import shared_task
from django.conf import settings
# from .models import LiquidPlant, MachineParametersGraph


# Initialize environment variables
env = environ.Env()
environ.Env.read_env(os.path.join(settings.BASE_DIR, '.env'))

CACHE_TIMEOUT = 60  # Cache timeout in seconds (1 minute)
CACHE_KEY = 'dashboard_data'

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
            cloud_records_dict = {r[0]: str(r[1]) for r in cloud_records}

            # Initialize the S3 client for DigitalOcean Spaces
            s3_client = boto3.client(
                's3',
                region_name='us-east-1',
                endpoint_url=f"https://{env('SPACE_ENDPOINT')}",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
            )

            # Iterate through local records and compare with cloud records
            for record in local_records:
                record_id = record[0]
                recorded_date_time = str(record[2])

                # Check if the record ID already exists in the cloud database
                if record_id in cloud_records_dict:
                    if cloud_records_dict[record_id] == recorded_date_time:
                        print(f"Record {record_id} with recorded_date_time {recorded_date_time} already exists in the cloud and is up-to-date.")
                        continue
                    else:
                        # Update the existing record
                        print(f"Updating record {record_id} in the cloud.")
                        cloud_cursor.execute("""
                            UPDATE LiquidPlant 
                            SET image = %s, recorded_date_time = %s, defects_id = %s, department_id = %s, machines_id = %s, plant_id = %s, product_id = %s,ocr = %s,shift=%s
                            WHERE id = %s
                        """, (record[1], recorded_date_time, record[3], record[4], record[5], record[6], record[7],record[8],record[9], record_id))
                else:
                    # Insert a new record
                    print(f"Inserting record {record_id} into the cloud.")
                    cloud_cursor.execute("""
                        INSERT INTO LiquidPlant (id, image, recorded_date_time, defects_id, department_id, machines_id, plant_id, product_id,ocr,shift)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (record_id, record[1], recorded_date_time, record[3], record[4], record[5], record[6], record[7],record[8],record[9]))

                # Fetch the image path from the database
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

                        # Update the record with the new image URL
                        cloud_cursor.execute("""
                            UPDATE LiquidPlant 
                            SET image = %s 
                            WHERE id = %s
                        """, (cloud_image_url, record_id))

                        # Optionally, log success
                        print(f"Record synced: {record_id}")

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
# from .models import LiquidPlant, MachineParametersGraph, Defects
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
                plant=record.plant,
                machine=record.machine  # Use machine_id here
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
                    plant=record.plant,
                    machine=record.machine  # Use machine directly here
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



# import logging
# from django.core.cache import cache
# from datetime import datetime, timedelta
# from .models import Dashboard, Defects  # Ensure these imports are correct
# from collections import OrderedDict
# from celery import shared_task

# logger = logging.getLogger(__name__)

# CACHE_KEY = 'dashboard_data'  # Define your cache key
# CACHE_TIMEOUT = 60 * 60  # Cache timeout in seconds (e.g., 1 hour)
# PLANT_ID = 2  # Plant ID to cache data for

# @shared_task
# def cache_dashboard_data():
#     now = datetime.utcnow()
#     from_date = now - timedelta(days=7)
#     to_date = now

#     # Convert datetime to string for easier comparison
#     from_date_str = from_date.strftime('%Y-%m-%d')
#     to_date_str = to_date.strftime('%Y-%m-%d')

#     # Filter queryset by plant_id
#     queryset = Dashboard.objects.filter(plant_id=PLANT_ID, recorded_date_time__contains='T')  # Adjust filter as needed
#     print('queryset',queryset)
#     response_data = {}
#     products_set = set()

#     for record in queryset:
#         if not record.recorded_date_time:
#             continue

#         try:
#             # Extract and parse the date part from the string
#             record_date_str = record.recorded_date_time.split('T')[0]  # Extract date part
#             date = datetime.strptime(record_date_str, '%Y-%m-%d').date()
#         except ValueError:
#             continue

#         if from_date.date() <= date <= to_date.date():
#             try:
#                 defect = Defects.objects.get(id=record.defects_id)
#                 defect_name = defect.name
#             except Defects.DoesNotExist:
#                 continue

#             product_name = record.product.name
#             products_set.add(product_name)

#             if str(date) not in response_data:
#                 response_data[str(date)] = {}

#             if defect_name not in response_data[str(date)]:
#                 response_data[str(date)][defect_name] = 0

#             response_data[str(date)][defect_name] += record.count

#     # Sort response_data by date
#     sorted_response_data = OrderedDict(sorted(response_data.items()))

#     # Add the active_products list
#     products_list = list(products_set)
#     sorted_response_data['active_products'] = products_list

#     # Set the sorted data in the cache
#     cache.set(CACHE_KEY, sorted_response_data, timeout=CACHE_TIMEOUT)
    
#     logger.info(f"Cache set with key '{CACHE_KEY}': {sorted_response_data}")


import logging
from django.core.cache import cache
from datetime import datetime, timedelta
# from .models import Dashboard, Defects  # Ensure these imports are correct
from collections import OrderedDict
from celery import shared_task

logger = logging.getLogger(__name__)

CACHE_KEY = 'dashboard_data'  # Define your cache key
CACHE_TIMEOUT = 60 * 60  # Cache timeout in seconds (e.g., 1 hour)
PLANT_ID = 3  # Plant ID to cache data for

@shared_task
def cache_dashboard_data():
    now = datetime.utcnow()
    from_date = now - timedelta(days=7)
    to_date = now

    # Convert datetime to string for filtering
    from_date_str = from_date.strftime('%Y-%m-%d')
    to_date_str = to_date.strftime('%Y-%m-%d')

    # Filter queryset by plant_id and date range
    queryset = Dashboard.objects.filter(
        plant_id=PLANT_ID,
        recorded_date_time__gte=from_date_str,
        recorded_date_time__lte=to_date_str
    )

    # logger.info(f"Queryset for plant_id={PLANT_ID}, date range {from_date_str} to {to_date_str}: {queryset}")
    response_data = {}
    products_set = set()

    for record in queryset:
        if not record.recorded_date_time:
            continue

        try:
            # Use the recorded_date_time directly as it is in 'YYYY-MM-DD' format
            record_date_str = record.recorded_date_time
            date = datetime.strptime(record_date_str, '%Y-%m-%d').date()
        except ValueError:
            logger.error(f"Invalid date format in record: {record.recorded_date_time}")
            continue

        if from_date.date() <= date <= to_date.date():
            try:
                defect = Defects.objects.get(id=record.defects_id)
                defect_name = defect.name
            except Defects.DoesNotExist:
                logger.error(f"Defect with ID {record.defects_id} does not exist.")
                continue

            try:
                product_name = record.product.name
                products_set.add(product_name)
            except AttributeError:
                logger.error(f"Product for record {record.id} does not exist.")
                continue

            if str(date) not in response_data:
                response_data[str(date)] = {}

            if defect_name not in response_data[str(date)]:
                response_data[str(date)][defect_name] = 0

            try:
                count = int(record.count)  # Convert count to int if needed
            except ValueError:
                logger.error(f"Invalid count value in record: {record.count}")
                continue

            response_data[str(date)][defect_name] += count

    # Sort response_data by date
    sorted_response_data = OrderedDict(sorted(response_data.items()))

    # Add the active_products list
    products_list = list(products_set)
    sorted_response_data['active_products'] = products_list

    # Set the sorted data in the cache
    cache.set(CACHE_KEY, sorted_response_data, timeout=CACHE_TIMEOUT)
    
    logger.info(f"Cache set with key '{CACHE_KEY}': {sorted_response_data}")


from datetime import datetime, timedelta
import os

logger = logging.getLogger(__name__)

# Docker volume path
DOCKER_VOLUME_PATH = '/var/lib/docker/volumes/plant-basesd-local_media_volume/_data/images/'

@shared_task
def delete_old_data_and_images():
    try:
        today = datetime.now().date()  # Get today's date
        cutoff_date = today - timedelta(days=15)  # Calculate cutoff date

        models = [NMBDashboard, LiquidPlant, ShampooPlant]
        
        for model in models:
            old_records = model.objects.filter(recorded_date_time__lt=cutoff_date.strftime('%Y-%m-%d'))
            count = old_records.count()
            logger.info(f"Number of records to delete from {model.__name__}: {count}")

            for record in old_records:
                logger.info(f"Processing record ID: {record.pk}, Image URL: {record.image}")

                image_url = record.image
                if image_url:
                    # Extract the file name from the image URL
                    file_name = os.path.basename(image_url)
                    
                    # Construct the full path to the image in the Docker volume
                    docker_image_path = os.path.join(DOCKER_VOLUME_PATH, file_name)
                    print('docker image path',docker_image_path)
                    if os.path.exists(docker_image_path):
                        try:
                            os.remove(docker_image_path)
                            logger.info(f"Successfully deleted image from Docker volume: {file_name}")
                        except Exception as e:
                            logger.error(f"Failed to delete image from Docker volume: {file_name}, Error: {e}")
                    else:
                        logger.warning(f"Image not found in Docker volume: {file_name}")
                
                # Delete the record from the database
                record.delete()
                if not model.objects.filter(pk=record.pk).exists():
                    logger.info(f"Successfully deleted record ID: {record.pk}")
                else:
                    logger.error(f"Failed to delete record ID: {record.pk}")
        
        logger.info('Successfully deleted old data and images.')
        return 'Successfully deleted old data and images.'
    
    except Exception as e:
        logger.error(f"Error in delete_old_data_and_images: {e}")
        return f"Error in delete_old_data_and_images: {e}"


@shared_task
def sync_dashboard_data():
    # Fetch all records from the local database
    local_records = Dashboard.objects.using('default').all()
    records_to_update = []
    records_to_create = []

    for record in local_records:
        # Extract the date part from recorded_date_time
        date_part = record.recorded_date_time.split('T')[0]

        with transaction.atomic(using='cloud'):
            # Check if a matching record exists in the global database
            global_record = Dashboard.objects.using('cloud').filter(
                recorded_date_time__startswith=date_part,
                machines=record.machines,
                department=record.department,
                product=record.product,
                defects=record.defects,
                plant=record.plant,
                shift=record.shift
            ).first()

            if global_record:
                # Update the existing record's count
                global_record.count = record.count
                records_to_update.append(global_record)
            else:
                # Create a new record
                new_global_record = Dashboard(
                    machines=record.machines,
                    department=record.department,
                    product=record.product,
                    defects=record.defects,
                    plant=record.plant,
                    recorded_date_time=record.recorded_date_time,
                    count=record.count,
                    shift=record.shift
                )
                records_to_create.append(new_global_record)

    # Perform bulk update
    if records_to_update:
        Dashboard.objects.using('cloud').bulk_update(records_to_update, ['count'])
        print(f'Updated {len(records_to_update)} records in global database')

    # Perform bulk create
    if records_to_create:
        Dashboard.objects.using('cloud').bulk_create(records_to_create)
        print(f'Created {len(records_to_create)} new records in global database')


from django.db import connection

@shared_task
def cleanup_old_records():
    # Define the SQL query
    query = """
    DELETE FROM LiquidPlant
    WHERE recorded_date_time < (
        SELECT recorded_date_time
        FROM (
            SELECT recorded_date_time
            FROM LiquidPlant
            ORDER BY recorded_date_time DESC
            LIMIT 1 OFFSET 9999
        ) AS cutoff
    );
    """
    
    # Execute the query
    with connection.cursor() as cursor:
        cursor.execute(query)