__all__ = ('s3', 'fastly', 'ConveyorError')

import logging

from pkg_resources import get_distribution, DistributionNotFound

from . import s3
from . import fastly
from .exceptions import ConveyorError

# Allow applications to control the logging handler
logging.getLogger(__name__).addHandler(logging.NullHandler())

try:
    __version__ = get_distribution('ltd-conveyor').version
except DistributionNotFound:
    # Package is not installed
    __version__ = 'unknown'
