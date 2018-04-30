"""Copy an S3 directory to another prefix in the same bucket.
"""

__all__ = ('copy_dir',)

import os
import boto3

from .delete import delete_dir


def copy_dir(bucket_name, src_path, dest_path,
             aws_access_key_id=None, aws_secret_access_key=None,
             aws_profile=None,
             surrogate_key=None, cache_control=None,
             surrogate_control=None,
             create_directory_redirect_object=True):
    """Copy objects from one directory in a bucket to another directory in
    the same bucket.

    Object metadata is preserved while copying, with the following exceptions:

    - If a new surrogate key is provided it will replace the original one.
    - If ``cache_control`` and ``surrogate_control`` values are provided they
      will replace the old one.

    Parameters
    ----------
    bucket_name : `str`
        Name of an S3 bucket.
    src_path : `str`
        Source directory in the S3 bucket. The ``src_path`` should ideally end
        in a trailing `'/'`. E.g. `'dir/dir2/'`.
    dest_path : `str`
        Destination directory in the S3 bucket. The ``dest_path`` should
        ideally end in a trailing `'/'`. E.g. `'dir/dir2/'`. The destination
        path cannot contain the source path.
    aws_access_key_id : `str`
        The access key for your AWS account. Also set
        ``aws_secret_access_key``.
    aws_secret_access_key : `str`
        The secret key for your AWS account.
    aws_profile : `str`, optional
        Name of AWS profile in :file:`~/.aws/credentials`. Use this instead
        of ``aws_access_key_id`` and ``aws_secret_access_key`` for file-based
        credentials.
    surrogate_key : `str`, optional
        The surrogate key to insert in the header of all objects in the
        ``x-amz-meta-surrogate-key`` field. This key is used to purge
        builds from the Fastly CDN when Editions change.
        If `None` then no header will be set.
        If the object already has a ``x-amz-meta-surrogate-key`` header then
        it will be replaced.
    cache_control : `str`, optional
        This sets (and overrides) the ``Cache-Control`` header on the copied
        files. The ``Cache-Control`` header specifically dictates how content
        is cached by the browser (if ``surrogate_control`` is also set).
    surrogate_control : `str`, optional
        This sets (and overrides) the ``x-amz-meta-surrogate-control`` header
        on the copied files. The ``Surrogate-Control``
        or ``x-amz-meta-surrogate-control`` header is used in priority by
        Fastly to givern it's caching. This caching policy is *not* passed
        to the browser.
    create_directory_redirect_object : `bool`, optional
        Create a directory redirect object for the root directory. The
        directory redirect object is an empty S3 object named after the
        directory (without a trailing slash) that contains a
        ``x-amz-meta-dir-redirect=true`` HTTP header. LSST the Docs' Fastly
        VCL is configured to redirect requests for a directory path to the
        directory's ``index.html`` (known as *courtesy redirects*).

    Raises
    ------
    ltdconveyor.s3.S3Error
        Thrown by any unexpected faults from the S3 API.
    RuntimeError
        Thrown when the source and destination directories are the same.
    """
    if not src_path.endswith('/'):
        src_path += '/'
    if not dest_path.endswith('/'):
        dest_path += '/'

    # Ensure the src_path and dest_path don't contain each other
    common_prefix = os.path.commonprefix([src_path, dest_path])
    if common_prefix == src_path:
        msg = 'Common prefix {0} is same as source dir {1}'.format(
            common_prefix, src_path)
        raise RuntimeError(msg)
    if common_prefix == dest_path:
        msg = 'Common prefix {0} is same as dest dir {1}'.format(
            common_prefix, dest_path)
        raise RuntimeError(msg)

    # Delete any existing objects in the destination
    delete_dir(bucket_name, dest_path,
               aws_access_key_id, aws_secret_access_key)

    session = boto3.session.Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        profile_name=aws_profile)
    s3 = session.resource('s3')
    bucket = s3.Bucket(bucket_name)

    # Copy each object from source to destination
    for src_obj in bucket.objects.filter(Prefix=src_path):
        src_rel_path = os.path.relpath(src_obj.key, start=src_path)
        dest_key_path = os.path.join(dest_path, src_rel_path)

        # the src_obj (ObjectSummary) doesn't include headers afaik
        head = s3.meta.client.head_object(Bucket=bucket_name,
                                          Key=src_obj.key)
        metadata = head['Metadata']
        content_type = head['ContentType']

        # try to use original Cache-Control header if new one is not set
        if cache_control is None and 'CacheControl' in head:
            cache_control = head['CacheControl']

        if surrogate_control is not None:
            metadata['surrogate-control'] = surrogate_control

        if surrogate_key is not None:
            metadata['surrogate-key'] = surrogate_key

        s3.meta.client.copy_object(
            Bucket=bucket_name,
            Key=dest_key_path,
            CopySource={'Bucket': bucket_name, 'Key': src_obj.key},
            MetadataDirective='REPLACE',
            Metadata=metadata,
            ACL='public-read',
            CacheControl=cache_control,
            ContentType=content_type)

    if create_directory_redirect_object:
        dest_dirname = dest_path.rstrip('/')
        obj = bucket.Object(dest_dirname)
        metadata = {'dir-redirect': 'true'}
        obj.put(Body='',
                ACL='public-read',
                Metadata=metadata,
                CacheControl=cache_control)
