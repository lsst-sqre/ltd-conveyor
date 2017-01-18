"""Test utilities available to test modules."""
from __future__ import (division, absolute_import, print_function,
                        unicode_literals)
from builtins import *  # noqa: F401,F403
from future.standard_library import install_aliases
install_aliases()  # noqa: F401

import os
try:
    from tempfile import TemporaryDirectory
except ImportError:
    # Python 2.7 compatibility
    from backports.tempfile import TemporaryDirectory


__all__ = ['upload_test_files']


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
            try:
                os.makedirs(full_dir, exist_ok=True)
            except TypeError:
                # work around Python 2.7, which doesn't have exist_ok
                _make_dirs(full_dir)
            with open(full_path, 'w') as f:
                f.write('content')

            extra_args = {
                'Metadata': {'surrogate-key': surrogate_key},
                'ContentType': content_type,
                'CacheControl': cache_control}
            obj = bucket.Object(bucket_root + p)
            obj.upload_file(full_path, ExtraArgs=extra_args)


def _make_dirs(full_dir_path):
    """Create a potentially nested directory structure (temporary Python 2.7
    affordance).
    """
    # Stripping out leading '/' because it prevents the split and join from
    # being reversible. We'll just add the leading '/' later.
    if full_dir_path.startswith('/'):
        make_absolute = True
        full_dir_path = full_dir_path.lstrip('/')
    else:
        make_absolute = False

    all_dirs = full_dir_path.split(os.path.sep)
    for i in range(len(all_dirs)):
        if i == 0:
            dir_path = all_dirs[0]
        else:
            dir_path = os.path.join(*all_dirs[:i + 1])

        if make_absolute:
            dir_path = '/' + dir_path

        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
