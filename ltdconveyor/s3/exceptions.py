__all__ = ('S3Error',)

from ..exceptions import ConveyorError


class S3Error(ConveyorError):
    """Error related to AWS S3 usage.
    """
