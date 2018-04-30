"""Tests for s3delete.

These tests required the following environment variables:

``LTD_TEST_AWS_ID``
    AWS access key ID

``LTD_TEST_AWS_SECRET``
    AWS secret access key

``LTD_TEST_BUCKET``
    Name of an S3 bucket that already exists and can be used for testing.

The tests will be skipped if they are not available.

Note that this test will create a random uuid4) directory at the root of
``LTD_TEST_BUCKET``, though the test harness will attempt to delete
it.
"""

import os
import uuid

import boto3
import pytest

from ltdconveyor.s3 import delete_dir
from ltdconveyor.testutils import upload_test_files


@pytest.mark.skipif(os.getenv('LTD_TEST_AWS_ID') is None or
                    os.getenv('LTD_TEST_AWS_SECRET') is None or
                    os.getenv('LTD_TEST_BUCKET') is None,
                    reason='Set LTD_TEST_AWS_ID, '
                           'LTD_TEST_AWS_SECRET and '
                           'LTD_TEST_BUCKET')
def test_delete_dir(request):
    session = boto3.session.Session(
        aws_access_key_id=os.getenv('LTD_TEST_AWS_ID'),
        aws_secret_access_key=os.getenv('LTD_TEST_AWS_SECRET'))
    s3 = session.resource('s3')
    bucket = s3.Bucket(os.getenv('LTD_TEST_BUCKET'))

    bucket_root = str(uuid.uuid4()) + '/'

    def cleanup():
        print("Cleaning up the bucket")
        delete_dir(os.getenv('LTD_TEST_BUCKET'),
                   bucket_root,
                   aws_access_key_id=os.getenv('LTD_TEST_AWS_ID'),
                   aws_secret_access_key=os.getenv('LTD_TEST_AWS_SECRET'))
    request.addfinalizer(cleanup)

    file_paths = ['a/test1.txt', 'a/b/test2.txt', 'a/b/c/test3.txt']
    upload_test_files(file_paths, bucket, bucket_root,
                      'sample-key', 'max-age=3600', 'text/plain')

    # Delete b/*
    delete_dir(os.getenv('LTD_TEST_BUCKET'),
               bucket_root + 'a/b/',
               aws_access_key_id=os.getenv('LTD_TEST_AWS_ID'),
               aws_secret_access_key=os.getenv('LTD_TEST_AWS_SECRET'))

    # Ensure paths outside of that are still available, but paths in b/ are
    # deleted
    bucket_paths = []
    for obj in bucket.objects.filter(Prefix=bucket_root):
        if obj.key.endswith('/'):
            continue
        bucket_paths.append(obj.key)

    for p in file_paths:
        bucket_path = bucket_root + p
        if p.startswith('a/b'):
            assert bucket_path not in bucket_paths
        else:
            assert bucket_path in bucket_paths
