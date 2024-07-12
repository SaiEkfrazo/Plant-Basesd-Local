import os
import boto3
from botocore.config import Config
from dotenv import load_dotenv
import base64
import mimetypes

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

def upload_base64_image_to_space(base64_image, file_name):
    try:
        # Decode Base64 data
        image_data = base64.b64decode(base64_image)
        
        # Determine content type dynamically
        content_type = mimetypes.guess_type(file_name)[0] or 'application/octet-stream'
        
        # Upload the file to DigitalOcean Space
        response = client.put_object(
            Bucket=DO_SPACES_NAME,
            Key=file_name,
            Body=image_data,
            ContentType=content_type,
            ACL='public-read'  # Make the object publicly readable
        )
        
        # Generate a public URL for the uploaded image
        public_url = f"{PUBLIC_ENDPOINT}/{file_name}"
        return public_url
    except Exception as e:
        print(f"Error uploading file: {e}")
        return None

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
