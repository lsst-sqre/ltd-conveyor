"""LTD project management service."""

from __future__ import annotations

import asyncio
import mimetypes
from copy import deepcopy
from pathlib import Path
from typing import Dict, List, Optional

from httpx import AsyncClient, HTTPError

from ..exceptions import S3PresignedUploadError
from ..storage.keeper import KeeperClient, PresignedPostUrl


class ProjectService:
    """A service for managing LTD projects, including uploading builds."""

    def __init__(
        self, *, keeper_client: KeeperClient, http_client: AsyncClient
    ) -> None:
        self._keeper_client = keeper_client
        self._http_client = http_client

    async def upload_build(
        self,
        *,
        base_dir: Path,
        project: str,
        git_ref: str,
        org: Optional[str] = None,
    ) -> None:
        """Upload a new build to LSST the Docs."""
        dirnames = self._prescan_directory(base_dir)
        build_info = await self._keeper_client.register_build(
            project=project,
            git_ref=git_ref,
            dirnames=dirnames,
            org=org,
        )

        await self._upload_files(
            base_dir=base_dir, post_prefix_urls=build_info.post_prefix_urls
        )

        await self._upload_directory_objects(
            post_dir_urls=build_info.post_dir_urls
        )

        await self._keeper_client.confirm_build(build_url=build_info.url)

    def _prescan_directory(
        self, base_dir: Path, _current_dir: Optional[Path] = None
    ) -> List[str]:
        """Make a list of all directories in a site, including the root
        directory.

        This function is used to the LTD Keeper API what presigned POST URLs to
        create for a build (see `ltdconveyor.keeper.register_build`).

        Parmameters
        -----------
        base_dir : `pathlib.Path`
            The (local) root directory of a web site.

        Returns
        -------
        dirnames : `list`
            A list of directory names, relative to the root directory. The root
            directory is represented by ``"/"``. All directory names end with
            ``"/"``.
        """
        dirs = []
        if _current_dir is None:
            _current_dir = base_dir
        dirs.append(self._format_relative_dirname(_current_dir, base_dir))
        for path in _current_dir.iterdir():
            if path.is_dir():
                dirs.extend(
                    self._prescan_directory(base_dir, _current_dir=path)
                )
        return dirs

    def _format_relative_dirname(
        self, directory: Path, base_directory: Path
    ) -> str:
        """Formats a relative directory path in a way that's compatible with
        presigned POST URLs.

        Parameters
        ----------
        directory : `pathlib.Path`
            The directory to compute a relative path/name for.
        base_directory : `pathlib.Path`
            The base directory.

        Returns
        -------
        name : `str`
            The relative directory name.

            Examples:

            - ``"base/`` relative to ``"/base/"`` is ``"/"``.
            - ``"base/a/`` relative to ``"/base/"`` is ``"a/"``.
            - ``"base/a/b`` relative to ``"/base/"`` is ``"a/b/"``.
        """
        name = str(directory.relative_to(base_directory))
        if name == ".":
            return "/"
        elif not name.endswith("/"):
            return name + "/"
        else:
            return name

    async def _upload_files(
        self, *, base_dir: Path, post_prefix_urls: Dict[str, PresignedPostUrl]
    ) -> None:
        """Upload files to a build."""
        file_paths = base_dir.rglob("*")
        tasks = []
        for path in file_paths:
            if path.is_dir():
                continue
            relative_dirname = self._format_relative_dirname(
                path.parent, base_dir
            )
            if relative_dirname not in post_prefix_urls:
                raise RuntimeError(
                    f"Missing presigned post URL for {relative_dirname}"
                )
            tasks.append(
                asyncio.create_task(
                    self._upload_file(
                        path=path,
                        post_url=post_prefix_urls[relative_dirname],
                    )
                )
            )
        await asyncio.gather(*tasks)

    async def _upload_file(
        self, *, path: Path, post_url: PresignedPostUrl
    ) -> None:
        """Upload a file to a presigned POST URL."""
        fields = deepcopy(post_url.fields)

        content_type, _ = mimetypes.guess_type(str(path), strict=False)
        if content_type is not None:
            fields["Content-Type"] = content_type
        else:
            fields["Content-Type"] = "application/octet-stream"

        with path.open("rb") as f:
            try:
                r = await self._http_client.post(
                    post_url.url,
                    data=fields,
                    files={"file": (path.name, f)},
                )
                r.raise_for_status()
            except HTTPError as e:
                raise S3PresignedUploadError(
                    f"Error uploading {path} to S3", e
                ) from e

    async def _upload_directory_objects(
        self, post_dir_urls: Dict[str, PresignedPostUrl]
    ) -> None:
        """Upload directory objects to a build."""
        tasks = []
        for relative_dir, post_url in post_dir_urls.items():
            tasks.append(
                asyncio.create_task(
                    self._upload_directory_object(
                        relative_dir=relative_dir, post_url=post_url
                    )
                )
            )
        await asyncio.gather(*tasks)

    async def _upload_directory_object(
        self, *, relative_dir: str, post_url: PresignedPostUrl
    ) -> None:
        """Upload a directory object to a presigned POST URL."""
        fields = deepcopy(post_url.fields)

        try:
            r = await self._http_client.post(
                post_url.url,
                data=fields,
                files={"file": ("", "")},
            )
            r.raise_for_status()
        except HTTPError as e:
            raise S3PresignedUploadError(
                f"Error uploading directory object {relative_dir} to S3:", e
            ) from e
