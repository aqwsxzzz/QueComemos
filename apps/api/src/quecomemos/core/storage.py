"""S3-compatible object storage.

Dev runs MinIO from docker-compose, production runs Cloudflare R2. Both speak
S3, so only environment variables differ — there is no second code path.

boto3 is synchronous, so every call is pushed to a worker thread rather than
blocking the event loop.
"""

import asyncio
import logging
from functools import lru_cache
from typing import TYPE_CHECKING

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from quecomemos.core.config import get_settings
from quecomemos.core.errors import AppError

if TYPE_CHECKING:
    from mypy_boto3_s3.client import S3Client

logger = logging.getLogger(__name__)


class StorageError(AppError):
    status_code = 502
    code = "storage_unavailable"


@lru_cache
def get_client() -> S3Client:
    settings = get_settings()
    return boto3.client(
        "s3",
        endpoint_url=settings.storage_endpoint_url,
        aws_access_key_id=settings.storage_access_key,
        aws_secret_access_key=settings.storage_secret_key,
        region_name=settings.storage_region,
        config=Config(signature_version="s3v4", retries={"max_attempts": 3}),
    )


def _put(key: str, data: bytes, content_type: str) -> None:
    settings = get_settings()
    get_client().put_object(
        Bucket=settings.storage_bucket,
        Key=key,
        Body=data,
        ContentType=content_type,
        CacheControl="public, max-age=31536000, immutable",
    )


async def put_object(key: str, data: bytes, content_type: str) -> None:
    try:
        await asyncio.to_thread(_put, key, data, content_type)
    except ClientError as exc:
        logger.exception("failed to store %s", key)
        raise StorageError("No pudimos guardar la imagen. Probá de nuevo.") from exc


def _delete(keys: list[str]) -> None:
    settings = get_settings()
    get_client().delete_objects(
        Bucket=settings.storage_bucket,
        Delete={"Objects": [{"Key": key} for key in keys], "Quiet": True},
    )


async def delete_objects(keys: list[str]) -> None:
    """Best effort: a failed purge is logged, never surfaced to the caller."""
    if not keys:
        return
    try:
        await asyncio.to_thread(_delete, keys)
    except ClientError:
        logger.exception("failed to purge objects: %s", keys)


def public_url(key: str) -> str:
    """Photos are world-readable, so a plain URL beats a signed one per request."""
    settings = get_settings()
    base = (settings.storage_public_url or settings.storage_endpoint_url or "").rstrip("/")
    return f"{base}/{settings.storage_bucket}/{key}"
