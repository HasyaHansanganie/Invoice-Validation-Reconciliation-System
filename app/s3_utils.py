import boto3
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# AWS credentials and config from environment
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

def upload_file_to_s3(file_path: str, s3_filename: str) -> str:
    
    """
    Upload a file to an AWS S3 bucket.
    Args:
        file_path (str): Local path to the file.
        s3_filename (str): Desired filename on S3.
    Returns:
        str: Public URL to access the file on S3, or an empty string on failure.
    """
    try:
        # Create S3 client using credentials from .env
        s3 = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )

        # Upload the file to the specified bucket
        s3.upload_file(file_path, AWS_BUCKET_NAME, s3_filename)

        # Generate and return public S3 URL
        s3_url = f"https://{AWS_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{s3_filename}"
        print(f"☁️ File uploaded to S3: {s3_url}")
        return s3_url

    except Exception as e:
        print(f"S3 Upload failed: {e}")
        return ""
