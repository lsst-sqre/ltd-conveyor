"""Tests for the ``ltdconveyor.s3.presignedpost`` module.
"""

from pathlib import PurePosixPath

import pytest

from ltdconveyor.s3.presignedpost import format_relative_dirname


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
