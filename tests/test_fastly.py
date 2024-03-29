"""Tests for `ltdconveyor.fastly`."""

import uuid

import pytest
import responses
from requests import PreparedRequest

from ltdconveyor.fastly import FastlyError, purge_key


@responses.activate
def test_purge_key() -> None:
    service_id = "SU1Z0isxPaozGVKXdv0eY"
    api_key = "d3cafb4dde4dbeef"
    surrogate_key = uuid.uuid4().hex

    url = "https://api.fastly.com/service/{0}/purge/{1}".format(
        service_id, surrogate_key
    )

    # Mock the API call and response
    responses.add(responses.POST, url, status=200)

    purge_key(surrogate_key, service_id, api_key)
    assert len(responses.calls) == 1
    call = responses.calls[0]
    assert hasattr(call, "request")
    assert isinstance(call.request, PreparedRequest)
    assert call.request.url == url
    assert call.request.headers["Fastly-Key"] == api_key
    assert call.request.headers["Accept"] == "application/json"


@responses.activate
def test_purge_key_fail() -> None:
    service_id = "SU1Z0isxPaozGVKXdv0eY"
    api_key = "d3cafb4dde4dbeef"
    surrogate_key = uuid.uuid4().hex

    url = "https://api.fastly.com/service/{0}/purge/{1}".format(
        service_id, surrogate_key
    )

    # Mock the API call and response
    responses.add(responses.POST, url, status=404)

    with pytest.raises(FastlyError):
        purge_key(surrogate_key, service_id, api_key)
    assert len(responses.calls) == 1
    call = responses.calls[0]
    assert hasattr(call, "request")
    assert isinstance(call.request, PreparedRequest)
    assert call.request.url == url
    assert call.request.headers["Fastly-Key"] == api_key
    assert call.request.headers["Accept"] == "application/json"
