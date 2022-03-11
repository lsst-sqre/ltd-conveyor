"""Tests for the Keeper versioning module."""

import responses

from ltdconveyor.keeper.versioning import get_server_version


@responses.activate
def test_parse_version() -> None:
    metadata_url = "https://example.com"
    response_data = {
        "data": {
            "documentation": "https://ltd-keeper.lsst.io",
            "message": "LTD Keeper is the API service for managing LSST "
            "the Docs projects.",
            "server_version": "1.22.0",
        },
        "links": {
            "products": "https://keeper.lsst.codes/products/",
            "self": "https://keeper.lsst.codes/",
            "token": "https://keeper.lsst.codes/token",
        },
    }
    responses.add(responses.GET, metadata_url, status=200, json=response_data)
    version = get_server_version(metadata_url)

    assert version == (1, 22, 0)
    assert version < (2, 0, 0)
    assert version > (1, 0, 0)
