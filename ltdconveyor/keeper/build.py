"""Register and confirm new build uploads with the LTD Keeper API.
"""

__all__ = ('register_build', 'confirm_build')

from urllib.parse import urljoin

import requests
import uritemplate

from .exceptions import KeeperError


def register_build(host, keeper_token, product, git_refs):
    """Register a new build for a product on LSST the Docs.

    Wraps ``POST /products/{product}/builds/``.

    Parameters
    ----------
    host : `str`
        Hostname of LTD Keeper API server.
    keeper_token : `str`
        Auth token (`ltdconveyor.keeper.get_keeper_token`).
    product : `str`
        Name of the product in the LTD Keeper service.
    git_refs : `list` of `str`
        List of Git refs that correspond to the version of the build. Git refs
        can be tags or branches.

    Returns
    -------
    build_info : `dict`
        LTD Keeper build resource.

    Raises
    ------
    ltdconveyor.keeper.KeeperError
        Raised if there is an error communicating with the LTD Keeper API.
    """
    data = {
        'git_refs': git_refs
    }

    endpoint_url = uritemplate.expand(
        urljoin(host, '/products/{p}/builds/'),
        p=product)

    r = requests.post(
        endpoint_url,
        auth=(keeper_token, ''),
        json=data)

    if r.status_code != 201:
        raise KeeperError(r.json())
    build_info = r.json()
    return build_info


def confirm_build(build_url, keeper_token):
    """Confirm a build upload is complete.

    Wraps ``PATCH /builds/{build}``.

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
    data = {
        'uploaded': True
    }

    r = requests.patch(
        build_url,
        auth=(keeper_token, ''),
        json=data)
    if r.status_code != 200:
        raise KeeperError(r)
