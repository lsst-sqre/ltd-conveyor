"""S3 utilities.
"""

__all__ = ('open_bucket',)

import boto3


def open_bucket(bucket_name,
                aws_access_key_id=None, aws_secret_access_key=None,
                aws_profile=None):
    """Open an S3 Bucket resource.

    Parameters
    ----------
    bucket_name : `str`
        Name of the S3 bucket.
    aws_access_key_id : `str`, optional
        The access key for your AWS account. Also set
        ``aws_secret_access_key``.
    aws_secret_access_key : `str`, optional
        The secret key for your AWS account.
    aws_profile : `str`, optional
        Name of AWS profile in :file:`~/.aws/credentials`. Use this instead
        of ``aws_access_key_id`` and ``aws_secret_access_key`` for file-based
        credentials.

    Returns
    -------
    bucket : Boto3 S3 Bucket instance
        The S3 bucket as a Boto3 instance.
    """
    session = boto3.session.Session(
        profile_name=aws_profile,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key)
    s3 = session.resource('s3')
    bucket = s3.Bucket(bucket_name)
    return bucket
