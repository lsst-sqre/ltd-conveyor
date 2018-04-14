"""Management of Fastly CDN caching.

See https://docs.fastly.com/api for background.
"""

__all__ = ('purge_key', 'FastlyError')

import logging
import requests

from .exceptions import ConveyorError


def purge_key(surrogate_key, service_id, api_key):
    """Instant purge URLs with a given surrogate key from the Fastly caches.

    Parameters
    ----------
    surrogate_key : `str`
        Surrogate key header (``x-amz-meta-surrogate-key``) value of objects
        to purge from the Fastly cache.
    service_id : `str`
        Fastly service ID.
    api_key : `str`
        Fastly API key.

    Raises
    ------
    FastlyError
       Error with the Fastly API usage.

    Notes
    -----
    This function uses Fastly's ``/service/{service}/purge/{key}`` endpoint.
    See the `Fastly Purge documentation <http://ls.st/jxg>`_ for more
    information.

    For other Fastly APIs, consider using `fastly-py
    <https://github.com/fastly/fastly-py>`_.
    """
    logger = logging.getLogger(__name__)

    api_root = 'https://api.fastly.com'
    path = '/service/{service}/purge/{surrogate_key}'.format(
        service=service_id,
        surrogate_key=surrogate_key)
    logger.info('Fastly purge {0}'.format(path))
    r = requests.post(api_root + path,
                      headers={'Fastly-Key': api_key,
                               'Accept': 'application/json'})
    if r.status_code != 200:
        raise FastlyError(r.json)


class FastlyError(ConveyorError):
    """Error related to Fastly API usage.
    """
