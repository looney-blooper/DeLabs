from minio import Minio
from minio.error import S3Error

from src.core.config import settings

class MinioStorageVault:
    def __init__(self):
        self.end_point = settings.MINIO_ENDPOINT
        self.access_key = settings.MINIO_ROOT_USER
        self.secret_key = settings.MINIO_ROOT_PASSWORD

        self.client = Minio(
            self.end_point,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=False
        )

        self._ensure_buckets_exist()

    def _ensure_buckets_exist(self):
        """Creates standard storage buckets if they do not exist."""
        buckets = ["delabs-code", "delabs-models"]
        for bucket in buckets:
            try:
                if not self.client.bucket_exists(bucket):
                    self.client.make_bucket(bucket)
            except S3Error as e:
                print(f"❌ MinIO Initialization Error: {e}")

    def upload_code(self, object_name: str, file_path: str) -> str:
        """Uploads a python file to the code vault and returns its internal storage path."""
        try:
            self.client.fput_object("delabs-code", object_name, file_path)
            return f"minio://delabs-code/{object_name}"
        except S3Error as e:
            raise IOError(f"Failed to upload code to MinIO: {e}")

    def upload_weights(self, object_name: str, file_path: str) -> str:
        """Uploads heavy weights (.pth/.safetensors) to the model vault."""
        try:
            self.client.fput_object("delabs-models", object_name, file_path)
            return f"minio://delabs-models/{object_name}"
        except S3Error as e:
            raise IOError(f"Failed to upload weights to MinIO: {e}")
            
    def get_presigned_download_url(self, bucket_name: str, object_name: str, expires_hours: int = 24) -> str:
        """Generates a transient download link for your dashboard frontend components."""
        import datetime
        try:
            return self.client.presigned_get_object(
                bucket_name, object_name, expires=datetime.timedelta(hours=expires_hours)
            )
        except S3Error as e:
            return ""