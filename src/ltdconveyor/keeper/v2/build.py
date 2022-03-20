"""Register and confirm new build uploads with the LTD Keeper API (v2)."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Dict, Sequence
from urllib.parse import urljoin

import requests
import uritemplate

from ltdconveyor.keeper.exceptions import KeeperError
from ltdconveyor.s3.presignedpost import (
    prescan_directory,
    upload_dir,
    upload_directory_objects,
)

if TYPE_CHECKING:
    from pathlib import Path


logger = logging.getLogger(__name__)


def run_build_upload_v2(
    *,
    base_url: str,
    token: str,
    project: str,
    org: str,
    git_ref: str,
    base_dir: Path,
) -> None:
    """Service function for running a build with the v1 LTD Keeper API."""
    dirnames = prescan_directory(base_dir)

    build_resource = register_build(
        base_url=base_url,
        keeper_token=token,
        org=org,
        project=project,
        git_ref=git_ref,
        dirnames=dirnames,
    )

    # Do the upload.
    upload_dir(post_urls=build_resource["post_prefix_urls"], base_dir=base_dir)
    logger.debug("Upload complete for %r", build_resource["self_url"])

    # Upload directory objects for redirects
    upload_directory_objects(
        post_urls=build_resource["post_dir_urls"],
    )

    # Confim the upload
    confirm_build(build_url=build_resource["self_url"], keeper_token=token)

    logger.info("Upload complete for %r", build_resource["self_url"])


def register_build(
    *,
    base_url: str,
    keeper_token: str,
    org: str,
    project: str,
    git_ref: str,
    dirnames: Sequence[str],
) -> Dict[str, Any]:
    """Register a new build for a product on LSST the Docs.

    Wraps the ``POST /v2/orgs/<org>/projects/<project>/builds`` endpoint.

    Parameters
    ----------
    host : `str`
        Hostname of LTD Keeper API server.
    keeper_token : `str`
        Auth token (`ltdconveyor.keeper.get_keeper_token`).
    org: `str`
        Name of the organization in the LTD Keeper service.
    project : `str`
        Name of the project in the LTD Keeper service.
    git_ref : `list` of `str`
        The Git ref corresponding to the version of the build. Git refs
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

    data = {"git_ref": git_ref, "directories": list(dirnames)}

    endpoint_url = uritemplate.expand(
        urljoin(base_url, "/v2/orgs/{org}/projects/{p}/builds"),
        p=project,
        org=org,
    )

    r = requests.post(
        endpoint_url,
        auth=(keeper_token, ""),
        json=data,
        headers={"Accept": "application/json"},
    )

    if r.status_code != 201:
        raise KeeperError(r.json())
    build_info: Dict[str, Any] = r.json()
    logger.debug(
        "Registered a build, org=%s project=%s:\n%s", org, project, build_info
    )
    return build_info


def confirm_build(*, build_url: str, keeper_token: str) -> None:
    """Confirm a build upload is complete.

    Wraps the ``PATCH /v2/orgs/<org>/projects/<project>/builds`` endpoint.

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
    if r.status_code != 202:
        raise KeeperError(r)
