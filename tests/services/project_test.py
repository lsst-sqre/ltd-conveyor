"""Tests for ltdconveyor.services.projects."""

from __future__ import annotations

from pathlib import Path

import pytest
import respx
from httpx import AsyncClient

from ltdconveyor.factory import Factory
from tests.support.keepermock import MockKeeper


@pytest.mark.asyncio
async def test_upload(
    respx_mock: respx.Router,
    mock_keeper: MockKeeper,
) -> None:
    """Test uploading a build to a v1 API."""
    async with AsyncClient() as http_client:
        factory = Factory(
            http_client=http_client,
            api_base="https://keeper.example.com",
            api_username="username",
            api_password="password",
        )
        project_service = factory.get_project_service()

        test_site_dir = Path(__file__).parent.parent / "data" / "test-site"
        await project_service.upload_build(
            base_dir=test_site_dir,
            project="test-project",
            git_ref="main",
        )

        for route in respx_mock.routes:
            if not route.called:
                print(f"Not called: {route.name}")
        respx_mock.assert_all_called()

        build_keys = list(mock_keeper.builds.keys())
        assert len(build_keys) == 1
        assert mock_keeper.builds[build_keys[0]].uploaded is True
