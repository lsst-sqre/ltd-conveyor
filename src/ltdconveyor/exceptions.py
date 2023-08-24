"""Exception library."""

__all__ = ["ConveyorError", "LtdKeeperHttpError", "LtdKeeperParsingError"]

from typing import Any

import httpx


class ConveyorError(Exception):
    """Generic base exception class for ltdconveyor."""


class LtdKeeperHttpError(ConveyorError):
    """Error communicating with the LTD Keeper API."""

    def __init__(self, message: str, error: httpx.HTTPError) -> None:
        self.message = message
        self.error = error

    def __str__(self) -> str:
        if isinstance(self.error, httpx.HTTPStatusError):
            return (
                "There was an error communicating with the LTD API: "
                f"{self.message}\n\n"
                f"Got {self.error.response.status_code} response from "
                f"{self.error.response.request.method} "
                f"{self.error.response.url}\n\n"
                f"{self.error.response.text}"
            )
        else:
            return self.message


class LtdKeeperParsingError(ConveyorError):
    """Error parsing a response from the LTD Keeper API."""

    def __init__(self, message: str, data: Any) -> None:
        self.message = message
        self.data = data

    def __str__(self) -> str:
        return (
            "There was an error parsing a response from the LTD Keeper API: "
            f"{self.message}\n\n"
            f"Data:\n\n"
            f"{self.data}"
        )
