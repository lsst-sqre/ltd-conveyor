"""Utilities for determining the API version that is supported by the
Keeper API server.
"""

from __future__ import annotations

import re
from typing import Tuple

import requests

from .exceptions import KeeperError

version_type = Tuple[int, int, int]

_version_pattern = re.compile(r"(^\d+)\.(\d+)\.(\d+)")


def get_server_version(base_url: str) -> version_type:
    r = requests.get(base_url)
    if r.status_code != 200:
        raise KeeperError(f"Could not connect to server {base_url}")

    data = r.json()
    try:
        server_version_string = data["data"]["server_version"]
    except KeyError:
        raise KeeperError("Could not not parse server version.")

    m = _version_pattern.match(server_version_string)
    if not m:
        raise KeeperError("Could not not parse server version.")
    return (
        int(m.group(1)),
        int(m.group(2)),
        int(m.group(3)),
    )
