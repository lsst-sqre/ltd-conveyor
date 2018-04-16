"""Exceptions related to the LTD Keeper.
"""

__all__ = ('KeeperError',)

from ..exceptions import ConveyorError


class KeeperError(ConveyorError):
    """Error raised because of issues using the LTD Keeper API.
    """
