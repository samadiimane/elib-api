from botocore.client import Config
import boto3
from app.core.config import settings

_session = boto3.session.Session(
    aws_access_key_id=settings.storage_access_key,
    aws_secret_access_key=settings.storage_secret_key,
    region_name=settings.storage_region or "us-east-1",
)

_s3 = _session.client(
    "s3",
    endpoint_url=settings.storage_endpoint,
    config=Config(signature_version="s3v4"),
)

_presign_s3 = _session.client(
    "s3",
    endpoint_url=settings.storage_public_endpoint or settings.storage_endpoint,
    config=Config(signature_version="s3v4"),
)


def object_exists(key: str) -> bool:
    try:
        _s3.head_object(Bucket=settings.storage_bucket, Key=key)
        return True
    except Exception:
        return False


def presigned_get_url(key: str, expires: int = 3600) -> str:
    return _presign_s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.storage_bucket, "Key": key},
        ExpiresIn=expires,
    )
