"""Delete an S3 directory.
"""

__all__ = ('delete_dir',)

import logging
from pprint import pformat
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
        aws_secret_access_key=aws_secret_access_key,
        profile_name=aws_profile)
    s3 = session.resource('s3')
    bucket = s3.Bucket(bucket_name)

    # Normalize directory path for searching path prefixes of objects
    root_path.rstrip('/')

    # Find objects under this path prefix
    key_objects = [{'Key': obj.key}
                   for obj in bucket.objects.filter(Prefix=root_path)]
    if len(key_objects) == 0:
        logger.info('No objects deleted from bucket {0}:{1}'.format(
            bucket_name, root_path))
        return

    # Delete objects under this path prefix
    delete_keys = {'Objects': key_objects}
    logger.info('Deleting {0:d} objects from bucket {1}:{2}'.format(
        len(key_objects), bucket_name, root_path))
    # based on http://stackoverflow.com/a/34888103
    r = s3.meta.client.delete_objects(Bucket=bucket.name,
                                      Delete=delete_keys)
    logger.info(pformat(r))
    status_code = r['ResponseMetadata']['HTTPStatusCode']
    if status_code >= 300:
        msg = 'S3 could not delete {0} (status {1:d})'.format(
            root_path, status_code)
        logger.error(msg)
        raise S3Error(msg)
