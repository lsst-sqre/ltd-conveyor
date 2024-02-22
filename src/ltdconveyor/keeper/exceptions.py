"""Exceptions related to the LTD Keeper."""

__all__ = ("KeeperError",)

from typing import Optional

from ..exceptions import ConveyorError


class KeeperError(ConveyorError):
    """Error raised because of issues using the LTD Keeper API."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        body: Optional[str] = None,
    ):
        if status_code is not None:
            message = f"(LTD status code: {status_code})\n\n{message}"
        if body is not None:
            message = f"{body}\n\n{message}"
        super().__init__(message)
