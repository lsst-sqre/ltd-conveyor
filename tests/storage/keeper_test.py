"""Tests for the Keeper client."""

from __future__ import annotations

import base64
import json
from pathlib import Path
from typing import Any

import pytest
import respx
from httpx import AsyncClient

from ltdconveyor.storage.keeper import KeeperClient


def load_keeper_response(filename: str) -> Any:
    """Load a JSON response from the LTD Keeper API."""
    path = Path(__file__).parent.parent / "data" / "keeper" / filename
    return json.loads(path.read_text())


@pytest.mark.asyncio
async def test_get_token(respx_mock: respx.Router) -> None:
    """Test getting a token."""
    base_url = "https://keeper.example.com"
    username = "username"
    password = "password"
    expected_token = "1234"

    token_endpoint = respx_mock.get(
        f"{base_url}/token", name="GET /token"
    ).respond(status_code=200, json={"token": expected_token})

    async with AsyncClient() as httpx_client:
        client = KeeperClient(
            base_url=base_url,
            username=username,
            password=password,
            http_client=httpx_client,
        )
        token = await client.get_token()
        assert token == "1234"

        for route in respx_mock.routes:
            if not route.called:
                print(f"Not called: {route.name}")
        respx_mock.assert_all_called()

        auth_encoded = base64.b64encode(
            f"{username}:{password}".encode("utf-8")
        ).decode("utf-8")
        assert token_endpoint.calls[0].request.headers["Authorization"] == (
            f"Basic {auth_encoded}"
        )


@pytest.mark.asyncio
async def test_get_version(respx_mock: respx.Router) -> None:
    """Test getting the API version."""
    base_url = "https://keeper.example.com"
    username = "username"
    password = "password"
    expected_token = "1234"

    respx_mock.get(f"{base_url}/token", name="GET /token").respond(
        status_code=200, json={"token": expected_token}
    )
    respx_mock.get(f"{base_url}/", name="GET /").respond(
        status_code=200, json=load_keeper_response("metadata_v1.json")
    )

    async with AsyncClient() as httpx_client:
        client = KeeperClient(
            base_url=base_url,
            username=username,
            password=password,
            http_client=httpx_client,
        )
        version = await client.get_api_version()
        assert version == (1, 23, 0)

        for route in respx_mock.routes:
            if not route.called:
                print(f"Not called: {route.name}")
        respx_mock.assert_all_called()


@pytest.mark.asyncio
async def test_register_build_v1(respx_mock: respx.Router) -> None:
    """Test registering a build with the v1 API."""
    base_url = "https://keeper.example.com"
    username = "username"
    password = "password"
    expected_token = "1234"

    respx_mock.get(f"{base_url}/token", name="GET /token").respond(
        status_code=200, json={"token": expected_token}
    )
    respx_mock.get(f"{base_url}/", name="GET /").respond(
        status_code=200, json=load_keeper_response("metadata_v1.json")
    )
    respx_mock.post(f"{base_url}/products/test-project/builds").respond(
        status_code=200, json=load_keeper_response("new_build_v1.json")
    )

    async with AsyncClient() as httpx_client:
        client = KeeperClient(
            base_url=base_url,
            username=username,
            password=password,
            http_client=httpx_client,
        )
        build_info = await client.register_build(
            project="test-project",
            git_ref="main",
            dirnames=["/", "/dir1", "/dir2"],
        )
        assert build_info.url == "https://keeper.example.com/builds/1"
        assert build_info.post_prefix_urls["/"].url == (
            "https://test-project.s3.amazonaws.com/"
        )
        assert build_info.post_dir_urls["/"].url == (
            "https://test-project.s3.amazonaws.com/"
        )


@pytest.mark.asyncio
async def test_register_build_v2(respx_mock: respx.Router) -> None:
    """Test registering a build with the v2 API."""
    base_url = "https://keeper.example.com"
    username = "username"
    password = "password"
    expected_token = "1234"

    respx_mock.get(f"{base_url}/token", name="GET /token").respond(
        status_code=200, json={"token": expected_token}
    )
    respx_mock.get(f"{base_url}/", name="GET /").respond(
        status_code=200, json=load_keeper_response("metadata_v2.json")
    )
    respx_mock.post(
        f"{base_url}/v2/orgs/test-org/projects/test-project/builds"
    ).respond(status_code=200, json=load_keeper_response("new_build_v2.json"))

    async with AsyncClient() as httpx_client:
        client = KeeperClient(
            base_url=base_url,
            username=username,
            password=password,
            http_client=httpx_client,
        )
        build_info = await client.register_build(
            project="test-project",
            org="test-org",
            git_ref="main",
            dirnames=["/", "/dir1", "/dir2"],
        )
        assert build_info.url == "https://keeper.example.com/builds/1"
        assert build_info.post_prefix_urls["/"].url == (
            "https://test-project.s3.amazonaws.com/"
        )
        assert build_info.post_dir_urls["/"].url == (
            "https://test-project.s3.amazonaws.com/"
        )


@pytest.mark.asyncio
async def test_confirm_build(respx_mock: respx.Router) -> None:
    """Test confirming a build upload with the v1 / v2 APIs."""
    base_url = "https://keeper.example.com"
    username = "username"
    password = "password"
    expected_token = "1234"

    respx_mock.get(f"{base_url}/token", name="GET /token").respond(
        status_code=200, json={"token": expected_token}
    )
    respx_mock.get(f"{base_url}/", name="GET /").respond(
        status_code=200, json=load_keeper_response("metadata_v1.json")
    )
    patch_build_endpoint = respx_mock.patch(f"{base_url}/builds/1").respond(
        status_code=200, json={}
    )

    async with AsyncClient() as httpx_client:
        client = KeeperClient(
            base_url=base_url,
            username=username,
            password=password,
            http_client=httpx_client,
        )
        await client.confirm_build(
            build_url="https://keeper.example.com/builds/1"
        )

        assert json.loads(patch_build_endpoint.calls[0].request.content) == {
            "uploaded": True
        }
