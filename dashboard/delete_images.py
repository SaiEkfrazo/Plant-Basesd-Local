from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from datetime import datetime
import os
import boto3
from botocore.config import Config
from dotenv import load_dotenv
from django.core.paginator import Paginator
from .models import *

# Load environment variables from .env file
load_dotenv()

# Get environment variables with fallback values
DO_SPACES_KEY = os.getenv('DO_SPACES_KEY', 'default_key')
DO_SPACES_SECRET = os.getenv('DO_SPACES_SECRET', 'default_secret')
DO_SPACES_NAME = os.getenv('DO_SPACES_NAME', 'default_bucket_name')
DO_SPACES_REGION = 'blr1'  # Update your region if different
DO_SPACES_ENDPOINT = f"https://{DO_SPACES_REGION}.digitaloceanspaces.com"
PUBLIC_ENDPOINT = f"https://{DO_SPACES_NAME}.{DO_SPACES_REGION}.digitaloceanspaces.com"

# Configure boto3 to use DigitalOcean Spaces
session = boto3.session.Session()
client = session.client('s3',
                        region_name=DO_SPACES_REGION,
                        endpoint_url=DO_SPACES_ENDPOINT,
                        aws_access_key_id=DO_SPACES_KEY,
                        aws_secret_access_key=DO_SPACES_SECRET)

def delete_image_from_space(image_url):
    try:
        # Extract the file name from the image URL
        file_name = image_url.split('/')[-1]
        
        # Delete the file from DigitalOcean Space
        response = client.delete_object(
            Bucket=DO_SPACES_NAME,
            Key=file_name
        )
        return response
    except Exception as e:
        print(f"Error deleting file: {e}")
        return None

class DeleteRecordsByDateAPIView(APIView):
    MODEL_MAPPING = {
        2: NMBDashboard,
        3: LiquidPlant,
        4: ShampooPlant,
    }

    @swagger_auto_schema(
        operation_summary="Delete records within a date range",
        operation_description="Delete records within a specified date range and their associated images",
        manual_parameters=[
            openapi.Parameter('start_date', openapi.IN_QUERY, description="Start date (YYYY-MM-DD)", type=openapi.TYPE_STRING),
            openapi.Parameter('end_date', openapi.IN_QUERY, description="End date (YYYY-MM-DD)", type=openapi.TYPE_STRING),
            openapi.Parameter('plant_id', openapi.IN_QUERY, description="Plant ID", type=openapi.TYPE_INTEGER)
        ],
        responses={
            204: openapi.Response(description="Records and images deleted successfully"),
            400: openapi.Response(description="Invalid parameters provided"),
            500: openapi.Response(description="Failed to delete records")
        }
    )
    def delete(self, request, *args, **kwargs):
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)
        plant_id = request.query_params.get('plant_id', None)

        if not start_date or not end_date or not plant_id:
            return Response({'error': 'Missing required parameters.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Convert date strings to datetime objects
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')

            # Determine the model to use based on the plant_id
            model = self.MODEL_MAPPING.get(int(plant_id))
            if not model:
                return Response({'error': 'Invalid plant_id provided.'}, status=status.HTTP_400_BAD_REQUEST)

            # Find records within the date range
            records_to_delete = model.objects.filter(
                recorded_date_time__gte=start_date_obj,
                recorded_date_time__lte=end_date_obj
            )

            paginator = Paginator(records_to_delete, 100)  # Create paginator with 1000 items per page

            for page_number in paginator.page_range:
                page = paginator.page(page_number)
                for record in page.object_list:
                    if record.image:
                        delete_image_from_space(record.image)
                    record.delete()
                print(f"Deleted batch {page_number} of {paginator.num_pages}")

            return Response({'message': 'Records and images deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'error': f'Failed to delete records: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
