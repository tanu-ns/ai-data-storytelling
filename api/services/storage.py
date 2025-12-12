import os
import io
import shutil
from pathlib import Path
from minio import Minio
from fastapi import UploadFile

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ROOT_USER", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_ROOT_PASSWORD", "minioadmin")
MINIO_BUCKET = "datasets"
USE_LOCAL_STORAGE = os.getenv("USE_LOCAL_STORAGE", "True") # Default to True

# Global client holder
minio_client = None

def get_minio_client():
    global minio_client
    if not minio_client:
        minio_client = Minio(
            MINIO_ENDPOINT,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=False
        )
    return minio_client

def upload_file(file: UploadFile, object_name: str) -> str:
    if USE_LOCAL_STORAGE == "True":
        # Local Filesystem Fallback
        base_dir = Path("uploads") / MINIO_BUCKET
        base_dir.mkdir(parents=True, exist_ok=True)
        
        # Determine local path
        # object_name might be "tenant_id/file.csv"
        file_path = base_dir / object_name
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        return f"file://{file_path.absolute()}"
    
    else:
        # MinIO Upload
        client = get_minio_client()
        if not client.bucket_exists(MINIO_BUCKET):
            client.make_bucket(MINIO_BUCKET)
            
        content = file.file.read()
        file.file.seek(0)
        
        client.put_object(
            MINIO_BUCKET,
            object_name,
            io.BytesIO(content),
            length=len(content),
            content_type=file.content_type
        )
        return f"s3://{MINIO_BUCKET}/{object_name}"
