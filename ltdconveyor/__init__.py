import pkg_resources

from .s3upload import upload_dir, upload_file, upload_object, ObjectManager  # noqa: F401,E501
from .exceptions import S3Error  # noqa: F401


__version__ = pkg_resources.get_distribution("ltd-conveyor").version
