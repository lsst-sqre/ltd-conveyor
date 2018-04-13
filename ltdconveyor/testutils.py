"""Test utilities available to test modules.
"""

__all__ = ('upload_test_files',)

import os
from tempfile import TemporaryDirectory


def upload_test_files(file_paths, bucket, bucket_root,
                      surrogate_key, cache_control, content_type):
    """Create and upload files to S3 as specified by their paths alone.

    This is useful for specifying a filesystem tree, and seeing if Conveyor's
    S3 interactions maintain or manipulate that tree properly.

    Parameters
    ----------
    file_paths : `list`
        List of file paths that specify a directory tree. For example:

        .. code-block:: py

           ['a.txt', 'b/c.txt', 'b/d/e.txt']
    bucket : `S3.Bucket`
        A boto3 bucket built from a ``boto3.session.Session``\ 's ``resource``
        method. Test files will be uploaded to this bucket.
    bucket_root : `str`
        Directory prefix in the bucket for testing.
    surrogate_key : `str`
        A Fastly CDN surrogate key for testing.
    cache_control : `str`
        Cache-control setting, such as ``"max-age=3600"``.
    content_type : `str`
        Content-type header of the test files, such as ``"text/plain"``.
    """
    with TemporaryDirectory() as temp_dir:
        for p in file_paths:
            full_path = os.path.join(temp_dir, p)
            full_dir = os.path.dirname(full_path)
            os.makedirs(full_dir, exist_ok=True)
            with open(full_path, 'w') as f:
                f.write('content')

            extra_args = {
                'Metadata': {'surrogate-key': surrogate_key},
                'ContentType': content_type,
                'CacheControl': cache_control}
            obj = bucket.Object(bucket_root + p)
            obj.upload_file(full_path, ExtraArgs=extra_args)
