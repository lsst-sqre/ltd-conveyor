"""Interface to the LTD Keeper API service."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urljoin

import uritemplate
from httpx import AsyncClient

from ltdconveyor.keeper.exceptions import KeeperError

version_type = Tuple[int, int, int]

_version_pattern = re.compile(r"(^\d+)\.(\d+)\.(\d+)")

logger = logging.getLogger(__name__)


@dataclass
class PresignedPostUrl:
    """A presigned POST URL."""

    url: str

    fields: dict[str, str]


@dataclass
class BuildInfo:
    """Information about a build"""

    url: str

    post_prefix_urls: Dict[str, PresignedPostUrl]

    post_dir_urls: Dict[str, PresignedPostUrl]


class KeeperClient:
    """A client for the LTD Keeper API.

    Parameters
    ----------
    base_url : `str`
        Base URL of the LTD Keeper API.
    username : `str`
        Username for LTD Keeper.
    password : `str`
        Password for LTD Keeper.
    """

    def __init__(
        self,
        *,
        base_url: str,
        username: str,
        password: str,
        http_client: AsyncClient,
    ) -> None:
        """Initialize the client."""
        # Strip the trailing slash from the base URL so that we can
        # consistently append paths with /{path}
        if base_url.endswith("/"):
            base_url = base_url[:-1]

        self._base_url = base_url
        self._username = username
        self._password = password
        self._http_client = http_client

    async def get_token(self) -> str:
        """Get an authentication token."""
        endpoint = f"{self._base_url}/token"
        r = await self._http_client.get(
            endpoint, auth=(self._username, self._password)
        )
        if r.status_code != 200:
            raise KeeperError(
                f"Could not authenticate to {self._base_url}: "
                f"error {r.status_code}\n{r.json()}"
            )

        return r.json()["token"]

    async def get(
        self,
        *,
        path: Optional[str] = None,
        url: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        """Send a GET request."""
        if path is not None:
            endpoint = f"{self._base_url}{path}"
        elif url is not None:
            endpoint = url
        else:
            raise ValueError("Must provide a path or url argument")

        token = await self.get_token()

        r = await self._http_client.get(
            endpoint, auth=(token, ""), headers=headers or {}
        )
        if r.status_code >= 400:
            raise KeeperError(
                f"Failed to GET {endpoint}: {r.status_code}\n{r.text}"
            )
        return r.json()

    async def post(
        self,
        *,
        data: Any,
        path: Optional[str] = None,
        url: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        """Send a POST request."""
        if path is not None:
            endpoint = f"{self._base_url}{path}"
        elif url is not None:
            endpoint = url
        else:
            raise ValueError("Must provide a path or url argument")

        token = await self.get_token()

        r = await self._http_client.post(
            endpoint, json=data, auth=(token, ""), headers=headers or {}
        )
        if r.status_code >= 400:
            raise KeeperError(
                f"Failed to POST {endpoint}: {r.status_code}\n{r.text}"
            )
        return r.json()

    async def patch(
        self,
        *,
        data: Any,
        path: Optional[str] = None,
        url: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        """Send a PATCH request."""
        if path is not None:
            endpoint = f"{self._base_url}{path}"
        elif url is not None:
            endpoint = url
        else:
            raise ValueError("Must provide a path or url argument")

        token = await self.get_token()

        r = await self._http_client.patch(
            endpoint, json=data, auth=(token, ""), headers=headers or {}
        )
        if r.status_code >= 400:
            raise KeeperError(
                f"Failed to PATCH {endpoint}: {r.status_code}\n{r.text}"
            )
        return r.json()

    async def get_api_version(self) -> tuple[int, int, int]:
        """Get the API version of the LTD Keeper instance."""
        data = await self.get(path="/")

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

    async def register_build(
        self,
        *,
        project: str,
        git_ref: str,
        dirnames: List[str],
        org: Optional[str] = None,
    ) -> BuildInfo:
        """Register a build with the LTD Keeper API.

        Parameters
        ----------
        project : `str`
            Project slug.
        git_ref : `str`
            Git ref (branch or tag).
        dirnames : `list` of `str`
            List of directories to upload.
        org : `str`, optional
            Organization slug. Required for version 2+ API.

        Returns
        -------
        build_info : `BuildInfo`
            LTD Keeper build resource.

        Raises
        ------
        ltdconveyor.keeper.KeeperError
            Raised if there is an error communicating with the LTD Keeper API.
        """
        version = await self.get_api_version()
        if version >= (2, 0, 0):
            if org is None:
                raise ValueError(
                    "Must provide org argument for LTD Keeper version 2."
                )
            return await self._register_build_v2(
                project=project,
                git_ref=git_ref,
                dirnames=dirnames,
                org=org,
            )
        else:
            return await self._register_build_v1(
                project=project,
                git_ref=git_ref,
                dirnames=dirnames,
            )

    async def _register_build_v2(
        self, *, org: str, project: str, git_ref: str, dirnames: List[str]
    ) -> BuildInfo:
        data = {"git_ref": git_ref, "directories": list(dirnames)}

        endpoint_url = uritemplate.expand(
            urljoin(self._base_url, "/v2/orgs/{org}/projects/{p}/builds/"),
            p=project,
            org=org,
        )

        build_data = await self.post(
            url=endpoint_url,
            data=data,
        )
        logger.debug(
            "Registered a build, org=%s project=%s:\n%s",
            org,
            project,
            build_data,
        )
        post_prefix_urls = {
            dirname: PresignedPostUrl(
                url=build_data["post_prefix_urls"][dirname]["url"],
                fields=build_data["post_prefix_urls"][dirname]["fields"],
            )
            for dirname in dirnames
        }
        post_dir_urls = {
            dirname: PresignedPostUrl(
                url=build_data["post_dir_urls"][dirname]["url"],
                fields=build_data["post_dir_urls"][dirname]["fields"],
            )
            for dirname in dirnames
        }
        build_info = BuildInfo(
            url=build_data["self_url"],
            post_prefix_urls=post_prefix_urls,
            post_dir_urls=post_dir_urls,
        )
        return build_info

    async def _register_build_v1(
        self, *, project: str, git_ref: str, dirnames: List[str]
    ) -> Any:
        data = {"git_ref": git_ref, "directories": list(dirnames)}

        endpoint_url = uritemplate.expand(
            urljoin(self._base_url, "/products/{p}/builds/"), p=project
        )

        build_data = await self.post(
            url=endpoint_url,
            data=data,
            headers={"Accept": "application/vnd.ltdkeeper.v2+json"},
        )
        logger.debug(
            "Registered a build, project=%s:\n%s",
            project,
            build_data,
        )
        post_prefix_urls = {
            dirname: PresignedPostUrl(
                url=build_data["post_prefix_urls"][dirname]["url"],
                fields=build_data["post_prefix_urls"][dirname]["fields"],
            )
            for dirname in dirnames
        }
        post_dir_urls = {
            dirname: PresignedPostUrl(
                url=build_data["post_dir_urls"][dirname]["url"],
                fields=build_data["post_dir_urls"][dirname]["fields"],
            )
            for dirname in dirnames
        }
        build_info = BuildInfo(
            url=build_data["self_url"],
            post_prefix_urls=post_prefix_urls,
            post_dir_urls=post_dir_urls,
        )
        return build_info

    async def confirm_build(self, *, build_url: str) -> None:
        """Confirm a build's upload is complete."""
        data = {"uploaded": True}
        try:
            await self.patch(
                url=build_url,
                data=data,
            )
        except KeeperError as e:
            raise KeeperError(f"Failed to confirm build at {build_url}") from e
