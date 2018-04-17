"""Helpers for the CLI (not click commands).
"""

import logging
import sys

import click

from ..keeper.login import get_keeper_token


def ensure_login(ctx):
    """Ensure a token is in the Click context object or authenticate and obtain
    the token from LTD Keeper.

    Parameters
    ----------
    ctx : `click.Context`
        The Click context. ``ctx.obj`` must be a `dict` that contains keys:
        ``keeper_hostname``, ``username``, ``password``, ``token``. This
        context object is prepared by the main Click group,
        `ltdconveyor.cli.main.main`.
    """
    logger = logging.getLogger(__name__)
    logger.info('utils name %r', __name__)

    if ctx.obj['token'] is None:
        if ctx.obj['username'] is None or ctx.obj['password'] is None:
            raise click.UsageError(
                'Use `ltd -u <username> -p <password> COMMAND` to '
                'authenticate to the LTD Keeper server.')
            sys.exit(1)

        logger.debug(
            'About to get token for user %s at %s',
            ctx.obj['username'],
            ctx.obj['keeper_hostname'])

        token = get_keeper_token(
            ctx.obj['keeper_hostname'],
            ctx.obj['username'],
            ctx.obj['password'])
        ctx.obj['token'] = token

        logger.debug(
            'Got token for user %s at %s',
            ctx.obj['username'],
            ctx.obj['keeper_hostname'])

    else:
        logger.debug(
            'Token already exists.')
