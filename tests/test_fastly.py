"""Tests for `ltdconveyor.fastly`.
"""

import uuid
import pytest
import responses

from ltdconveyor.fastly import purge_key, FastlyError


@responses.activate
def test_purge_key():
    service_id = 'SU1Z0isxPaozGVKXdv0eY'
    api_key = 'd3cafb4dde4dbeef'
    surrogate_key = uuid.uuid4().hex

    url = 'https://api.fastly.com/service/{0}/purge/{1}'.format(
        service_id, surrogate_key)

    # Mock the API call and response
    responses.add(responses.POST, url, status=200)

    purge_key(surrogate_key, service_id, api_key)
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == url
    assert responses.calls[0].request.headers['Fastly-Key'] == api_key
    assert responses.calls[0].request.headers['Accept'] == 'application/json'


@responses.activate
def test_purge_key_fail():
    service_id = 'SU1Z0isxPaozGVKXdv0eY'
    api_key = 'd3cafb4dde4dbeef'
    surrogate_key = uuid.uuid4().hex

    url = 'https://api.fastly.com/service/{0}/purge/{1}'.format(
        service_id, surrogate_key)

    # Mock the API call and response
    responses.add(responses.POST, url, status=404)

    with pytest.raises(FastlyError):
        purge_key(surrogate_key, service_id, api_key)
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == url
    assert responses.calls[0].request.headers['Fastly-Key'] == api_key
    assert responses.calls[0].request.headers['Accept'] == 'application/json'
