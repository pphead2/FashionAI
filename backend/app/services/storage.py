from google.cloud import storage
from google.oauth2 import service_account
import os
import datetime
import logging
from pathlib import Path

from ..core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

class CloudStorage:
    def __init__(self):
        """Initialize Google Cloud Storage client"""
        try:
            # Check if we have service account credentials
            if hasattr(settings, "GCP_SERVICE_ACCOUNT_KEY_PATH") and settings.GCP_SERVICE_ACCOUNT_KEY_PATH:
                # Create service account credentials
                credentials = service_account.Credentials.from_service_account_file(
                    settings.GCP_SERVICE_ACCOUNT_KEY_PATH
                )
                # Initialize client with credentials
                self.client = storage.Client(
                    credentials=credentials,
                    project=settings.GCP_PROJECT_ID
                )
            else:
                # Use default credentials
                self.client = storage.Client(project=settings.GCP_PROJECT_ID)
            
            # Get the bucket
            self.bucket = self.client.bucket(settings.GCP_BUCKET_NAME)
            
            logger.info(f"Cloud Storage client initialized for bucket: {settings.GCP_BUCKET_NAME}")
        except Exception as e:
            logger.error(f"Failed to initialize Cloud Storage client: {str(e)}")
            raise Exception(f"Cloud Storage initialization error: {str(e)}")
    
    def generate_upload_path(self, user_id: str, filename: str) -> str:
        """Generate a path for the uploaded file based on user ID and timestamp"""
        # Create a timestamp-based directory structure
        today = datetime.datetime.now()
        year_month = today.strftime("%Y/%m")
        
        # Extract file extension
        _, extension = os.path.splitext(filename)
        if not extension:
            extension = ".jpg"  # Default to jpg if no extension
        
        # Generate a timestamp-based filename with original extension
        timestamp = today.strftime("%Y%m%d_%H%M%S")
        new_filename = f"{timestamp}{extension}"
        
        # Construct the full path: uploads/user_id/YYYY/MM/timestamp.ext
        upload_path = f"uploads/{user_id}/{year_month}/{new_filename}"
        
        return upload_path
    
    def upload_file(self, file_content: bytes, file_path: str, content_type: str = None) -> str:
        """
        Upload a file to Google Cloud Storage
        Returns the public URL of the uploaded file
        """
        try:
            # Create a new blob and upload the file's content
            blob = self.bucket.blob(file_path)
            
            # Upload the file
            blob.upload_from_string(
                file_content,
                content_type=content_type
            )
            
            # Make the blob publicly accessible
            blob.make_public()
            
            # Return the public URL
            return blob.public_url
        
        except Exception as e:
            logger.error(f"Failed to upload file to {file_path}: {str(e)}")
            raise Exception(f"Upload error: {str(e)}")
    
    def delete_file(self, file_path: str) -> bool:
        """Delete a file from Google Cloud Storage"""
        try:
            blob = self.bucket.blob(file_path)
            blob.delete()
            return True
        
        except Exception as e:
            logger.error(f"Failed to delete file {file_path}: {str(e)}")
            return False
    
    def get_file_url(self, file_path: str) -> str:
        """Get the public URL for a file"""
        blob = self.bucket.blob(file_path)
        return blob.public_url
    
    def download_file(self, file_path: str) -> bytes:
        """Download a file from Google Cloud Storage"""
        try:
            blob = self.bucket.blob(file_path)
            return blob.download_as_bytes()
        
        except Exception as e:
            logger.error(f"Failed to download file {file_path}: {str(e)}")
            raise Exception(f"Download error: {str(e)}")
    
    def list_files(self, prefix: str = None, delimiter: str = None) -> list:
        """List files in the bucket with the given prefix"""
        try:
            blobs = self.client.list_blobs(
                self.bucket,
                prefix=prefix,
                delimiter=delimiter
            )
            return [blob.name for blob in blobs]
        
        except Exception as e:
            logger.error(f"Failed to list files with prefix {prefix}: {str(e)}")
            return []

# Create instance
storage_client = CloudStorage() 