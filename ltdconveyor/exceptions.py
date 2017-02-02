"""Exception library."""


class ConveyorError(Exception):
    """Generic base exception class for ltdconveyor."""
    pass


class S3Error(ConveyorError):
    """Error related to AWS S3 usage."""
    pass


class FastlyError(ConveyorError):
    """Error related to Fastly API usage."""
    pass
