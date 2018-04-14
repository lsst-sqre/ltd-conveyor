"""Tests for s3copy.

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

from ltdconveyor.s3 import copy_dir, delete_dir
from ltdconveyor.testutils import upload_test_files


@pytest.mark.skipif(os.getenv('LTD_TEST_AWS_ID') is None or
                    os.getenv('LTD_TEST_AWS_SECRET') is None or
                    os.getenv('LTD_TEST_BUCKET') is None,
                    reason='Set LTD_TEST_AWS_ID, '
                           'LTD_TEST_AWS_SECRET and '
                           'LTD_TEST_BUCKET')
def test_copy_directory(request):
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

    initial_paths = ['test1.txt', 'test2.txt', 'aa/test3.txt']
    new_paths = ['test4.txt', 'bb/test5.txt']

    # add old and new file sets
    upload_test_files(initial_paths, bucket, bucket_root + 'a/',
                      'sample-key', 'max-age=3600', 'text/plain')
    upload_test_files(new_paths, bucket, bucket_root + 'b/',
                      'sample-key', 'max-age=3600', 'text/plain')

    # copy files
    copy_dir(
        bucket_name=os.getenv('LTD_TEST_BUCKET'),
        src_path=bucket_root + 'b/',
        dest_path=bucket_root + 'a/',
        aws_access_key_id=os.getenv('LTD_TEST_AWS_ID'),
        aws_secret_access_key=os.getenv('LTD_TEST_AWS_SECRET'),
        surrogate_key='new-key',
        surrogate_control='max-age=31536000',
        cache_control='no-cache')

    # Test files in the a/ directory are from b/
    for obj in bucket.objects.filter(Prefix=bucket_root + 'a/'):
        bucket_path = os.path.relpath(obj.key, start=bucket_root + 'a/')
        assert bucket_path in new_paths
        # ensure correct metadata
        head = s3.meta.client.head_object(
            Bucket=os.getenv('LTD_TEST_BUCKET'),
            Key=obj.key)
        assert head['CacheControl'] == 'no-cache'
        assert head['ContentType'] == 'text/plain'
        assert head['Metadata']['surrogate-key'] == 'new-key'
        assert head['Metadata']['surrogate-control'] == 'max-age=31536000'

    # Test that a directory object exists
    bucket_paths = [obj.key
                    for obj in bucket.objects.filter(Prefix=bucket_root + 'a')]
    assert os.path.join(bucket_root, 'a') in bucket_paths


def test_copy_dir_src_in_dest():
    """Test that copy_directory fails raises a RuntimeError if source in
    destination.
    """
    with pytest.raises(RuntimeError):
        copy_dir('example', 'dest/src', 'dest',
                 aws_access_key_id='id',
                 aws_secret_access_key='key')


def test_copy_dir_dest_in_src():
    """Test that copy_directory fails raises a RuntimeError if destination
    is part of the source.
    """
    with pytest.raises(RuntimeError):
        copy_dir('example', 'src', 'src/dest',
                 aws_access_key_id='id',
                 aws_secret_access_key='key')
