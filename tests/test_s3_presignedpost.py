"""Tests for the ``ltdconveyor.s3.presignedpost`` module."""

from __future__ import annotations

import cgi
import sys
from io import BytesIO
from pathlib import Path, PosixPath
from typing import TYPE_CHECKING, Dict

import pytest
import responses

from ltdconveyor.exceptions import ConveyorError
from ltdconveyor.s3.exceptions import S3Error
from ltdconveyor.s3.presignedpost import (
    format_relative_dirname,
    prescan_directory,
    upload_dir,
    upload_directory_objects,
    upload_file,
)

if TYPE_CHECKING:
    from unittest.mock import Mock


@pytest.mark.parametrize(
    "directory,basedir,expected",
    [
        ("/home/project/sub/dir", "/home/project/", "sub/dir/"),
        ("/home/project/sub/dir", "/home/project", "sub/dir/"),
        ("/home/project/sub/dir/", "/home/project", "sub/dir/"),
        ("/home/project/", "/home/project/", "/"),
    ],
)
def test_relative_dirname(directory: str, basedir: str, expected: str) -> None:
    _directory = PosixPath(directory)
    _basedir = PosixPath(basedir)
    result = format_relative_dirname(_directory, _basedir)
    assert result == expected


def test_prescan_directory() -> None:
    """Test the prescan_directory function using a test directory in
    ``tests/data/test-site/``
    """
    base_dir = Path(__file__).parent / "data/test-site"
    assert base_dir.is_dir()

    dirs = prescan_directory(base_dir)
    assert "/" in dirs
    assert "a/" in dirs
    assert "a/aa/" in dirs
    assert "b/" in dirs
    assert len(dirs) == 4


def test_upload_dir(mocker: Mock) -> None:
    mock_upload_file = mocker.patch("ltdconveyor.s3.presignedpost.upload_file")

    post_urls = {
        "/": {
            "url": "https://example.com",
            "fields": {"key": "/prefix/{$filename}"},
        },
        "a/": {
            "url": "https://example.com",
            "fields": {"key": "/prefix/a/{$filename}"},
        },
        "a/aa/": {
            "url": "https://example.com",
            "fields": {"key": "/prefix/a/aa/{$filename}"},
        },
        "b/": {
            "url": "https://example.com",
            "fields": {"key": "/prefix/b/{$filename}"},
        },
    }
    base_dir = Path(__file__).parent / "data/test-site"

    upload_dir(post_urls=post_urls, base_dir=base_dir)

    assert mock_upload_file.call_count == 4


def test_upload_dir_bad_posturls(mocker: Mock) -> None:
    """Test upload_dir when post_urls do not include the directory."""
    mocker.patch("ltdconveyor.s3.presignedpost.upload_file")

    post_urls: Dict[str, str] = {}
    base_dir = Path(__file__).parent / "data/test-site"

    with pytest.raises(ConveyorError):
        upload_dir(post_urls=post_urls, base_dir=base_dir)


@responses.activate
def test_upload_file() -> None:
    local_path = Path(__file__).parent / "data/test-site/index.html"
    post_url = "https://example.com"
    post_fields = {"key": "bucket/base/${filename}"}

    responses.add(responses.POST, "https://example.com", status=204)

    upload_file(
        local_path=local_path, post_url=post_url, post_fields=post_fields
    )

    call = responses.calls[0]
    mimetype, options = cgi.parse_header(call.request.headers["Content-Type"])
    assert mimetype == "multipart/form-data"
    pdict = {
        "boundary": bytes(options["boundary"].encode("ascii")),
        "CONTENT-LENGTH": call.request.headers["Content-Length"].encode(
            "ascii"
        ),
    }
    assert isinstance(responses.calls[0].request.body, bytes)
    data = BytesIO(bytes(responses.calls[0].request.body))
    parsed_body = cgi.parse_multipart(data, pdict)

    if sys.version_info[:3] >= (3, 7, 0):
        assert parsed_body["Content-Type"] == ["text/html"]
        assert parsed_body["key"] == ["bucket/base/${filename}"]
    else:
        assert parsed_body["Content-Type"] == [b"text/html"]
        assert parsed_body["key"] == [b"bucket/base/${filename}"]


@responses.activate
def test_upload_file_failed() -> None:
    local_path = Path(__file__).parent / "data/test-site/index.html"
    post_url = "https://example.com"
    post_fields = {"key": "bucket/base/${filename}"}

    responses.add(responses.POST, "https://example.com", status=403)

    with pytest.raises(S3Error):
        upload_file(
            local_path=local_path, post_url=post_url, post_fields=post_fields
        )


@responses.activate
def test_upload_directory_objects() -> None:
    post_urls = {
        "/": {"url": "https://example.com", "fields": {"key": "bucket/base"}},
        "a/": {
            "url": "https://example.com",
            "fields": {"key": "bucket/base/a"},
        },
        "a/aa/": {
            "url": "https://example.com",
            "fields": {"key": "bucket/base/a/aa"},
        },
        "b/": {
            "url": "https://example.com",
            "fields": {"key": "bucket/base/b/{$filename}"},
        },
    }
    responses.add(responses.POST, "https://example.com", status=204)

    upload_directory_objects(post_urls=post_urls)

    assert len(responses.calls) == 4
