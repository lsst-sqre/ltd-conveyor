__all__ = ("s3", "fastly", "ConveyorError")

import logging

from importlib_metadata import PackageNotFoundError, version

from . import fastly, s3
from .exceptions import ConveyorError

# Allow applications to control the logging handler
logging.getLogger(__name__).addHandler(logging.NullHandler())

try:
    __version__ = version("ltd-conveyor")
except PackageNotFoundError:
    # Package is not installed
    __version__ = "unknown"
