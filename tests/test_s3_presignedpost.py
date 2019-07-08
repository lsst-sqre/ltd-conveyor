"""Tests for the ``ltdconveyor.s3.presignedpost`` module.
"""

import sys
import cgi
from io import BytesIO
from pathlib import Path, PurePosixPath
from unittest.mock import call

import pytest
import responses

from ltdconveyor.exceptions import ConveyorError
from ltdconveyor.s3.presignedpost import (
    format_relative_dirname, prescan_directory, upload_dir, upload_file,
    upload_directory_objects)
from ltdconveyor.s3.exceptions import S3Error


@pytest.mark.parametrize(
    'directory,basedir,expected',
    [
        ('/home/project/sub/dir', '/home/project/', 'sub/dir/'),
        ('/home/project/sub/dir', '/home/project', 'sub/dir/'),
        ('/home/project/sub/dir/', '/home/project', 'sub/dir/'),
        ('/home/project/', '/home/project/', '/'),
    ]
)
def test_relative_dirname(directory, basedir, expected):
    directory = PurePosixPath(directory)
    basedir = PurePosixPath(basedir)
    result = format_relative_dirname(directory, basedir)
    assert result == expected


def test_prescan_directory():
    """Test the prescan_directory function using a test directory in
    ``tests/data/test-site/``
    """
    base_dir = Path(__file__).parent / 'data/test-site'
    assert base_dir.is_dir()

    dirs = prescan_directory(base_dir)
    assert '/' in dirs
    assert 'a/' in dirs
    assert 'a/aa/' in dirs
    assert 'b/' in dirs
    assert len(dirs) == 4


@pytest.mark.xfail(
    reason='assert_has_calls fails for unknown reason on Travis')
def test_upload_dir(mocker):
    mock_upload_file = mocker.patch('ltdconveyor.s3.presignedpost.upload_file')

    post_urls = {
        '/': {
            'url': 'https://example.com',
            'fields': {'key': '/prefix/{$filename}'}
        },
        'a/': {
            'url': 'https://example.com',
            'fields': {'key': '/prefix/a/{$filename}'}
        },
        'a/aa/': {
            'url': 'https://example.com',
            'fields': {'key': '/prefix/a/aa/{$filename}'}
        },
        'b/': {
            'url': 'https://example.com',
            'fields': {'key': '/prefix/b/{$filename}'}
        }
    }
    base_dir = Path(__file__).parent / 'data/test-site'

    upload_dir(post_urls=post_urls, base_dir=base_dir)

    assert mock_upload_file.call_count == 4
    upload_file_calls = [
        call(local_path=base_dir / 'index.html',
             post_url=post_urls['/']['url'],
             post_fields=post_urls['/']['fields']),
        call(local_path=base_dir / 'a/index.html',
             post_url=post_urls['a/']['url'],
             post_fields=post_urls['a/']['fields']),
        call(local_path=base_dir / 'a/aa/index.html',
             post_url=post_urls['a/aa/']['url'],
             post_fields=post_urls['a/aa/']['fields']),
        call(local_path=base_dir / 'b/index.html',
             post_url=post_urls['b/']['url'],
             post_fields=post_urls['b/']['fields']),
    ]
    mock_upload_file.assert_has_calls(upload_file_calls)


def test_upload_dir_bad_posturls(mocker):
    """Test upload_dir when post_urls do not include the necessary directory.
    """
    mocker.patch('ltdconveyor.s3.presignedpost.upload_file')

    post_urls = {}
    base_dir = Path(__file__).parent / 'data/test-site'

    with pytest.raises(ConveyorError):
        upload_dir(post_urls=post_urls, base_dir=base_dir)


@responses.activate
def test_upload_file():
    local_path = Path(__file__).parent / 'data/test-site/index.html'
    post_url = 'https://example.com'
    post_fields = {'key': 'bucket/base/${filename}'}

    responses.add(responses.POST, 'https://example.com', status=204)

    upload_file(
        local_path=local_path,
        post_url=post_url,
        post_fields=post_fields)

    call = responses.calls[0]
    mimetype, options = cgi.parse_header(call.request.headers['Content-Type'])
    assert mimetype == 'multipart/form-data'
    pdict = {'boundary': options['boundary'].encode('ascii'),
             'CONTENT-LENGTH': call.request.headers['Content-Length']}
    data = BytesIO(responses.calls[0].request.body)
    parsed_body = cgi.parse_multipart(data, pdict)

    if sys.version_info[:3] >= (3, 7, 0):
        assert parsed_body['Content-Type'] == ['text/html']
        assert parsed_body['key'] == ['bucket/base/${filename}']
    else:
        assert parsed_body['Content-Type'] == [b'text/html']
        assert parsed_body['key'] == [b'bucket/base/${filename}']


@responses.activate
def test_upload_file_failed():
    local_path = Path(__file__).parent / 'data/test-site/index.html'
    post_url = 'https://example.com'
    post_fields = {'key': 'bucket/base/${filename}'}

    responses.add(responses.POST, 'https://example.com', status=403)

    with pytest.raises(S3Error):
        upload_file(
            local_path=local_path,
            post_url=post_url,
            post_fields=post_fields)


@responses.activate
def test_upload_directory_objects():
    post_urls = {
        '/': {
            'url': 'https://example.com',
            'fields': {'key': 'bucket/base'}
        },
        'a/': {
            'url': 'https://example.com',
            'fields': {'key': 'bucket/base/a'}
        },
        'a/aa/': {
            'url': 'https://example.com',
            'fields': {'key': 'bucket/base/a/aa'}
        },
        'b/': {
            'url': 'https://example.com',
            'fields': {'key': 'bucket/base/b/{$filename}'}
        }
    }
    responses.add(responses.POST, 'https://example.com', status=204)

    upload_directory_objects(post_urls=post_urls)

    assert len(responses.calls) == 4
