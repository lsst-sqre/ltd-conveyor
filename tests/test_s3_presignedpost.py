"""Tests for the ``ltdconveyor.s3.presignedpost`` module.
"""

from pathlib import Path, PurePosixPath

import pytest

from ltdconveyor.s3.presignedpost import (
    format_relative_dirname, prescan_directory)


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
