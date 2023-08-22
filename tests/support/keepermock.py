from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterator, List, Optional, Tuple
from unittest.mock import patch

import respx

from ltdconveyor.factory import keeper
from ltdconveyor.storage.keeper import BuildInfo, PresignedPostUrl


@dataclass
class RegisteredBuild:
    project: str
    git_ref: str
    org: Optional[str]
    uploaded: bool


class MockKeeper:
    def __init__(
        self,
        base_url: str,
        presigned_url_base: str,
        respx_mock: respx.Router,
        version: Tuple[int, int, int] = (1, 3, 0),
    ) -> None:
        self._base_url = base_url
        self._presigned_url_base = presigned_url_base
        self._respx_mock = respx_mock
        self._version = version
        self._builds: Dict[str, RegisteredBuild] = {}

    @property
    def builds(self) -> Dict[str, RegisteredBuild]:
        return self._builds

    async def get_token(self) -> str:
        return "1234"

    async def get_api_version(self) -> Tuple[int, int, int]:
        return self._version

    async def register_build(
        self,
        *,
        project: str,
        git_ref: str,
        dirnames: List[str],
        org: Optional[str] = None,
    ) -> BuildInfo:
        if org is not None:
            self_url = f"{self._base_url}/orgs/{org}/projects/builds/1"
        else:
            self_url = f"{self._base_url}/builds/1"

        post_prefix_urls: Dict[str, PresignedPostUrl] = {}
        post_dir_urls: Dict[str, PresignedPostUrl] = {}

        for dirname in dirnames:
            prefix_url = f"{self._presigned_url_base}{dirname}"
            self._respx_mock.post(
                prefix_url, name=f"POST {prefix_url}"
            ).respond(status_code=200)
            post_prefix_urls[dirname] = PresignedPostUrl(
                url=prefix_url, fields={"key": "123"}
            )

            dir_url = f"{self._presigned_url_base}/dir{dirname}"
            self._respx_mock.post(dir_url, name=f"POST {dir_url}").respond(
                status_code=200
            )
            post_dir_urls[dirname] = PresignedPostUrl(
                url=dir_url, fields={"key": "123"}
            )

        self._builds[self_url] = RegisteredBuild(
            project=project,
            git_ref=git_ref,
            org=org,
            uploaded=False,
        )

        return BuildInfo(
            url=self_url,
            post_prefix_urls=post_prefix_urls,
            post_dir_urls=post_dir_urls,
        )

    async def confirm_build(self, *, build_url: str) -> None:
        self._builds[build_url].uploaded = True


def patch_factory_keeper(respx_mock: respx.Router) -> Iterator[MockKeeper]:
    mock = MockKeeper(
        base_url="https://keeper.example.com",
        presigned_url_base="https://example.com/presigned-url",
        respx_mock=respx_mock,
    )
    with patch.object(keeper, "KeeperClient", return_value=mock):
        yield mock
