import boto3
from botocore.exceptions import ClientError
from typing import IO
from fastapi import HTTPException
from app.storage.base import StorageService
from app.core.config import settings

class S3StorageService(StorageService):
    def __init__(self):
        if not settings.S3_BUCKET:
            raise ValueError("S3_BUCKET is required when STORAGE_PROVIDER=s3")
            
        self.bucket = settings.S3_BUCKET
        self.s3_client = boto3.client(
            's3',
            endpoint_url=settings.S3_ENDPOINT_URL,
            region_name=settings.S3_REGION,
            aws_access_key_id=settings.S3_ACCESS_KEY_ID,
            aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY
        )

    def save(self, file_obj: IO, object_key: str, content_type: str) -> str:
        try:
            self.s3_client.upload_fileobj(
                file_obj,
                self.bucket,
                object_key,
                ExtraArgs={'ContentType': content_type}
            )
            return object_key
        except ClientError as e:
            raise HTTPException(status_code=500, detail="Failed to upload file to cloud storage")

    def delete(self, object_key: str) -> bool:
        try:
            self.s3_client.delete_object(Bucket=self.bucket, Key=object_key)
            return True
        except ClientError:
            return False

    def exists(self, object_key: str) -> bool:
        try:
            self.s3_client.head_object(Bucket=self.bucket, Key=object_key)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            raise

    def get(self, object_key: str) -> IO:
        try:
            response = self.s3_client.get_object(Bucket=self.bucket, Key=object_key)
            return response['Body']
        except ClientError as e:
            raise HTTPException(status_code=404, detail="File not found in cloud storage")
