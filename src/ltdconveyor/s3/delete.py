"""Delete an S3 directory."""

import logging
from typing import Any, Dict, Optional

import boto3

from ltdconveyor.s3.exceptions import S3Error

__all__ = ["delete_dir"]


def delete_dir(
    bucket_name: str,
    root_path: str,
    aws_access_key_id: Optional[str] = None,
    aws_secret_access_key: Optional[str] = None,
    aws_profile: Optional[str] = None,
) -> None:
    """Delete all objects in the S3 bucket named ``bucket_name`` that are
    found in the ``root_path`` directory.

    Parameters
    ----------
    bucket_name : `str`
        Name of an S3 bucket.
    root_path : `str`
        Directory in the S3 bucket that will be deleted.
    aws_access_key_id : `str`
        The access key for your AWS account. Also set
        ``aws_secret_access_key``.
    aws_secret_access_key : `str`
        The secret key for your AWS account.
    aws_profile : `str`, optional
        Name of AWS profile in :file:`~/.aws/credentials`. Use this instead
        of ``aws_access_key_id`` and ``aws_secret_access_key`` for file-based
        credentials.

    Raises
    ------
    ltdconveyor.s3.S3Error
        Thrown by any unexpected faults from the S3 API.
    """
    logger = logging.getLogger(__name__)

    session = boto3.session.Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )
    s3 = session.resource("s3")
    client = s3.meta.client

    # Normalize directory path for searching patch prefixes of objects
    if not root_path.endswith("/"):
        root_path.rstrip("/")

    paginator = client.get_paginator("list_objects_v2")
    pages = paginator.paginate(Bucket=bucket_name, Prefix=root_path)

    keys: Dict[str, Any] = dict(Objects=[])
    for item in pages.search("Contents"):
        try:
            keys["Objects"].append({"Key": item["Key"]})
        except TypeError:  # item is None; nothing to delete
            continue
        # Delete immediately when 1000 objects are listed
        # the delete_objects method can only take a maximum of 1000 keys
        if len(keys["Objects"]) >= 1000:
            try:
                client.delete_objects(Bucket=bucket_name, Delete=keys)
            except Exception:
                message = "Error deleting objects from %r" % root_path
                logger.exception(message)
                raise S3Error(message)
            keys = dict(Objects=[])

    # Delete remaining keys
    if len(keys["Objects"]) > 0:
        try:
            client.delete_objects(Bucket=bucket_name, Delete=keys)
        except Exception:
            message = "Error deleting objects from %r" % root_path
            logger.exception(message)
            raise S3Error(message)
