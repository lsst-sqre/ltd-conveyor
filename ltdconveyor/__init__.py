__all__ = (
    'open_bucket', 'upload_dir', 'upload_file', 'upload_object',
    'create_dir_redirect_object', 'ObjectManager', 'delete_dir',
    'copy_dir', 'purge_key', 'S3Error', 'FastlyError', 'ConveyorError'
)

import logging

from pkg_resources import get_distribution, DistributionNotFound

from .s3utils import open_bucket
from .s3upload import (upload_dir, upload_file, upload_object,
                       create_dir_redirect_object,
                       ObjectManager)
from .s3delete import delete_dir
from .s3copy import copy_dir
from .fastly import purge_key
from .exceptions import S3Error, FastlyError, ConveyorError

# Allow applications to control the logging handler
logging.getLogger(__name__).addHandler(logging.NullHandler())

try:
    __version__ = get_distribution('ltd-conveyor').version
except DistributionNotFound:
    # Package is not installed
    __version__ = 'unknown'
