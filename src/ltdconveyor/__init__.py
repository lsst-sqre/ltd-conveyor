__all__ = ("s3", "fastly", "ConveyorError")

import logging
from importlib.metadata import PackageNotFoundError, version

from . import fastly, s3
from .exceptions import ConveyorError

# Allow applications to control the logging handler
logging.getLogger(__name__).addHandler(logging.NullHandler())

__version__: str
"""The version string of Documenteer (PEP 440 / SemVer compatible)."""

try:
    __version__ = version("ltd-conveyor")
except PackageNotFoundError:
    # package is not installed
    __version__ = "0.0.0"
