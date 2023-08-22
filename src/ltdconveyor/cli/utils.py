"""Helpers for the CLI (not click commands)."""

from __future__ import annotations

import asyncio
import logging
import sys
from collections.abc import Callable, Coroutine
from functools import wraps
from typing import Any, TypeVar

import click

from ltdconveyor.keeper.v1.login import get_keeper_token

__all__ = ["ensure_login", "run_with_asyncio"]

T = TypeVar("T")


def ensure_login(ctx: click.Context) -> None:
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

    if ctx.obj["token"] is None:
        if ctx.obj["username"] is None or ctx.obj["password"] is None:
            raise click.UsageError(
                "Use `ltd -u <username> -p <password> COMMAND` to "
                "authenticate to the LTD Keeper server."
            )
            sys.exit(1)

        logger.debug(
            "About to get token for user %s at %s",
            ctx.obj["username"],
            ctx.obj["keeper_hostname"],
        )

        token = get_keeper_token(
            ctx.obj["keeper_hostname"],
            ctx.obj["username"],
            ctx.obj["password"],
        )
        ctx.obj["token"] = token

        logger.debug(
            "Got token for user %s at %s",
            ctx.obj["username"],
            ctx.obj["keeper_hostname"],
        )

    else:
        logger.debug("Token already exists.")


def run_with_asyncio(
    f: Callable[..., Coroutine[Any, Any, T]]
) -> Callable[..., T]:
    """Run the decorated function with `asyncio.run`.

    Intended to be used as a decorator around an async function that needs to
    be run in a sync context.  The decorated function will be run with
    `asyncio.run` when invoked.  The caller must not already be inside an
    asyncio task.

    Parameters
    ----------
    f
        The function to wrap.

    Examples
    --------
    An application that uses Safir and `Click`_ may use the following Click
    command function to initialize a database.

    .. code-block:: python

       import structlog
       from safir.asyncio import run_with_asyncio
       from safir.database import initialize_database

       from .config import config
       from .schema import Base


       @main.command()
       @run_with_asyncio
       async def init() -> None:
           logger = structlog.get_logger(config.safir.logger_name)
           engine = await initialize_database(
               config.database_url,
               config.database_password,
               logger,
               schema=Base.metadata,
           )
           await engine.dispose()
    """

    @wraps(f)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        return asyncio.run(f(*args, **kwargs))

    return wrapper
