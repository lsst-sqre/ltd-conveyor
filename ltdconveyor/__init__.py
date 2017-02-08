import pkg_resources

from .s3upload import (upload_dir, upload_file, upload_object,  # noqa: F401
                       create_dir_redirect_object,  # noqa: F401
                       ObjectManager)  # noqa: F401
from .s3delete import delete_dir  # noqa: F401
from .s3copy import copy_dir  # noqa: F401
from .fastly import purge_key  # noqa: F401
from .exceptions import S3Error, FastlyError, ConveyorError  # noqa: F401


__version__ = pkg_resources.get_distribution("ltd-conveyor").version
