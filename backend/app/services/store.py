import os
import tempfile
from contextlib import contextmanager
from uuid import UUID

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from fastapi import UploadFile

from app.core.config import settings


class StoreService:
    def __init__(self) -> None:
        # Initialize S3 Client
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            region_name=settings.S3_REGION,
            endpoint_url=settings.S3_ENDPOINT_URL,
            config=Config(signature_version="s3v4"),
        )
        self.bucket = settings.S3_BUCKET_NAME

    def _download_file(self, file_id: UUID) -> str:
        """Download file from S3 to a temporary local path"""
        key = str(file_id)

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            local_path = tmp.name

        try:
            self.s3.download_file(self.bucket, key, local_path)
        except ClientError as e:
            if os.path.exists(local_path):
                os.remove(local_path)
            raise FileNotFoundError(f"File {file_id} not found on S3: {e}")

        return local_path

    def get_file_path(self, file_id: UUID) -> str:
        """Download file from S3 to a temporary local path"""
        return self._download_file(file_id)

    @contextmanager
    def get_file_path_context(self, file_id: UUID):
        """Download file from S3 to a temporary local path and auto-delete it after use"""
        local_path = self._download_file(file_id)
        try:
            yield local_path
        finally:
            if os.path.exists(local_path):
                os.remove(local_path)

    async def delete_file(self, file_id: UUID):
        """Delete file from S3"""
        try:
            self.s3.delete_object(Bucket=self.bucket, Key=str(file_id))
        except ClientError:
            pass

    async def save_file(self, file: UploadFile, file_id: UUID):
        """Upload file directly to S3 and validate size"""
        key = str(file_id)

        await file.seek(0)

        try:
            self.s3.upload_fileobj(file.file, self.bucket, key)

            # Validate size after upload
            response = self.s3.head_object(Bucket=self.bucket, Key=key)
            if response["ContentLength"] > settings.MAX_FILE_SIZE:
                await self.delete_file(file_id)
                raise ValueError(
                    f"File exceeds maximum allowed size of {settings.MAX_FILE_SIZE} bytes."
                )
        except ClientError:
            await self.delete_file(file_id)
            raise
