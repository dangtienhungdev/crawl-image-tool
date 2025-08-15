"""
Wasabi S3 service for cloud storage integration
"""

import os
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from typing import Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WasabiService:
    """Service for interacting with Wasabi S3 storage"""

    def __init__(self):
        # Load Wasabi credentials from environment variables
        self.access_key = os.getenv('ACCESS_KEY')
        self.secret_key = os.getenv('SECRET_KEY')
        self.endpoint_url = os.getenv('ENDPOINT_URL')
        self.bucket_name = os.getenv('BUCKET_NAME')

        # Validate required environment variables
        if not all([self.access_key, self.secret_key, self.endpoint_url, self.bucket_name]):
            raise ValueError("Missing required Wasabi environment variables. Please check your .env file.")

        # Initialize S3 client
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            endpoint_url=self.endpoint_url,
            region_name='ap-southeast-1'  # Wasabi region
        )

        logger.info(f"Wasabi service initialized with bucket: {self.bucket_name}")

    def upload_file(self, file_path: str, s3_key: str, content_type: str = None) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Upload a file to Wasabi S3

        Args:
            file_path: Local path to the file
            s3_key: S3 key (path) for the file
            content_type: MIME type of the file

        Returns:
            Tuple of (success, cloud_url, error_message)
        """
        try:
            # Prepare upload parameters
            upload_params = {
                'Bucket': self.bucket_name,
                'Key': s3_key,
                'Filename': file_path
            }

            # Add content type if provided
            if content_type:
                upload_params['ExtraArgs'] = {'ContentType': content_type}

            # Upload file
            self.s3_client.upload_file(**upload_params)

            # Generate cloud URL
            cloud_url = f"{self.endpoint_url}/{self.bucket_name}/{s3_key}"

            logger.info(f"Successfully uploaded {file_path} to {cloud_url}")
            return True, cloud_url, None

        except FileNotFoundError:
            error_msg = f"File not found: {file_path}"
            logger.error(error_msg)
            return False, None, error_msg

        except NoCredentialsError:
            error_msg = "Wasabi credentials not found or invalid"
            logger.error(error_msg)
            return False, None, error_msg

        except ClientError as e:
            error_msg = f"Wasabi S3 error: {str(e)}"
            logger.error(error_msg)
            return False, None, error_msg

        except Exception as e:
            error_msg = f"Unexpected error uploading to Wasabi: {str(e)}"
            logger.error(error_msg)
            return False, None, error_msg

    def upload_bytes(self, file_bytes: bytes, s3_key: str, content_type: str = None) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Upload bytes directly to Wasabi S3

        Args:
            file_bytes: File content as bytes
            s3_key: S3 key (path) for the file
            content_type: MIME type of the file

        Returns:
            Tuple of (success, cloud_url, error_message)
        """
        try:
            # Prepare upload parameters
            upload_params = {
                'Bucket': self.bucket_name,
                'Key': s3_key,
                'Body': file_bytes
            }

            # Add content type if provided
            if content_type:
                upload_params['ContentType'] = content_type

            # Upload bytes
            self.s3_client.put_object(**upload_params)

            # Generate cloud URL
            cloud_url = f"{self.endpoint_url}/{self.bucket_name}/{s3_key}"

            logger.info(f"Successfully uploaded bytes to {cloud_url}")
            return True, cloud_url, None

        except NoCredentialsError:
            error_msg = "Wasabi credentials not found or invalid"
            logger.error(error_msg)
            return False, None, error_msg

        except ClientError as e:
            error_msg = f"Wasabi S3 error: {str(e)}"
            logger.error(error_msg)
            return False, None, error_msg

        except Exception as e:
            error_msg = f"Unexpected error uploading to Wasabi: {str(e)}"
            logger.error(error_msg)
            return False, None, error_msg

    def delete_file(self, s3_key: str) -> Tuple[bool, Optional[str]]:
        """
        Delete a file from Wasabi S3

        Args:
            s3_key: S3 key (path) of the file to delete

        Returns:
            Tuple of (success, error_message)
        """
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            logger.info(f"Successfully deleted {s3_key} from Wasabi")
            return True, None

        except ClientError as e:
            error_msg = f"Wasabi S3 error deleting file: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    def file_exists(self, s3_key: str) -> bool:
        """
        Check if a file exists in Wasabi S3

        Args:
            s3_key: S3 key (path) of the file

        Returns:
            True if file exists, False otherwise
        """
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=s3_key)
            return True
        except ClientError:
            return False

    def get_file_url(self, s3_key: str) -> str:
        """
        Generate public URL for a file in Wasabi S3

        Args:
            s3_key: S3 key (path) of the file

        Returns:
            Public URL for the file
        """
        return f"{self.endpoint_url}/{self.bucket_name}/{s3_key}"

    def test_connection(self) -> Tuple[bool, Optional[str]]:
        """
        Test connection to Wasabi S3

        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Try to list objects in bucket (limited to 1)
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                MaxKeys=1
            )
            logger.info("Wasabi S3 connection test successful")
            return True, None

        except NoCredentialsError:
            error_msg = "Wasabi credentials not found or invalid"
            logger.error(error_msg)
            return False, error_msg

        except ClientError as e:
            error_msg = f"Wasabi S3 connection test failed: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

        except Exception as e:
            error_msg = f"Unexpected error testing Wasabi connection: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
