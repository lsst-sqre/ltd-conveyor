"""Register and confirm new build uploads with the LTD Keeper API (v2)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


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
