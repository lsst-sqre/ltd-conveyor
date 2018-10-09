"""Delete an S3 directory.
"""

__all__ = ('delete_dir',)

import logging
import boto3

from .exceptions import S3Error


def delete_dir(bucket_name, root_path,
               aws_access_key_id=None, aws_secret_access_key=None,
               aws_profile=None):
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
        aws_secret_access_key=aws_secret_access_key)
    s3 = session.resource('s3')
    client = s3.meta.client

    # Normalize directory path for searching patch prefixes of objects
    if not root_path.endswith('/'):
        root_path.rstrip('/')

    paginator = client.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket_name, Prefix=root_path)

    keys = dict(Objects=[])
    for item in pages.search('Contents'):
        keys['Objects'].append({'Key': item['Key']})
        # Delete immediately when 1000 objects are listed
        # the delete_objects method can only take a maximum of 1000 keys
        if len(keys['Objects']) >= 1000:
            try:
                client.delete_objects(Bucket=bucket_name, Delete=keys)
            except Exception:
                message = 'Error deleting objects from %r' % root_path
                logger.exception(message)
                raise S3Error(message)
            keys = dict(Objects=[])

    # Delete remaining keys
    if len(keys['Objects']):
        try:
            client.delete_objects(Bucket=bucket_name, Delete=keys)
        except Exception:
            message = 'Error deleting objects from %r' % root_path
            logger.exception(message)
            raise S3Error(message)
