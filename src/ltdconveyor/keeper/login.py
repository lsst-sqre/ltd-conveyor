"""Login functionality for the LTD Keeper API."""

from urllib.parse import urljoin

import requests

from ltdconveyor.keeper.exceptions import KeeperError

__all__ = ["get_keeper_token"]


def get_keeper_token(host: str, username: str, password: str) -> str:
    """Get a temporary auth token from LTD Keeper.

    Parameters
    ----------
    host : `str`
        Hostname of the LTD Keeper API (e.g., ``'https://keeper.lsst.codes'``).
    username : `str`
        Username.
    password : `str`
        Password.

    Returns
    -------
    token : `str`
        LTD Keeper API token.

    Raises
    ------
    KeeperError
        Raised if the LTD Keeper API cannot return a token.
    """
    token_endpoint = urljoin(host, "/token")
    r = requests.get(token_endpoint, auth=(username, password))
    if r.status_code != 200:
        raise KeeperError(
            "Could not authenticate to {0}: error {1:d}\n{2}".format(
                host, r.status_code, r.json()
            )
        )
    return r.json()["token"]
