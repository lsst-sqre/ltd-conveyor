"""Register and confirm new build uploads with the LTD Keeper API."""

import logging
from typing import Any, Dict, Optional, Sequence
from urllib.parse import urljoin

import requests
import uritemplate

from ltdconveyor.keeper.exceptions import KeeperError

__all__ = ["register_build", "confirm_build"]


def register_build(
    host: str,
    keeper_token: str,
    product: str,
    git_refs: Sequence[str],
    dirnames: Optional[Sequence[str]] = None,
) -> Dict[str, Any]:
    """Register a new build for a product on LSST the Docs.

    Wraps the ``POST /products/{product}/builds/`` **v2 API** endpoint.

    Parameters
    ----------
    host : `str`
        Hostname of LTD Keeper API server.
    keeper_token : `str`
        Auth token (`ltdconveyor.keeper.get_keeper_token`).
    product : `str`
        Name of the product in the LTD Keeper service.
    git_refs : `list` of `str`
        List of Git refs that correspond to the version of the build. Git refs
        can be tags or branches.
    dirnames : `list` of `str`
        A list of relative directory names in the site. Each directory will
        get its own presigned POST URL in the response from the LTD Keeper API.

    Returns
    -------
    build_info : `dict`
        LTD Keeper build resource.

    Raises
    ------
    ltdconveyor.keeper.KeeperError
        Raised if there is an error communicating with the LTD Keeper API.
    """
    logger = logging.getLogger(__name__)

    data = {"git_refs": git_refs}
    if dirnames is not None:
        data["directories"] = list(dirnames)

    endpoint_url = uritemplate.expand(
        urljoin(host, "/products/{p}/builds/"), p=product
    )

    r = requests.post(
        endpoint_url,
        auth=(keeper_token, ""),
        json=data,
        headers={"Accept": "application/vnd.ltdkeeper.v2+json"},
    )

    if r.status_code != 201:
        raise KeeperError(r.json())
    build_info: Dict[str, Any] = r.json()
    logger.debug("Registered a build for product %s:\n%s", product, build_info)
    return build_info


def confirm_build(build_url: str, keeper_token: str) -> None:
    """Confirm a build upload is complete.

    Wraps ``PATCH /builds/{build}``.

    Parameters
    ----------
    build_url : `str`
        URL of the build resource. Given a build resource, this URL is
        available from the ``self_url`` field.
    keeper_token : `str`
        Auth token (`ltdconveyor.keeper.get_keeper_token`).

    Raises
    ------
    ltdconveyor.keeper.KeeperError
        Raised if there is an error communicating with the LTD Keeper API.
    """
    data = {"uploaded": True}

    r = requests.patch(build_url, auth=(keeper_token, ""), json=data)
    if r.status_code != 200:
        raise KeeperError(r)
