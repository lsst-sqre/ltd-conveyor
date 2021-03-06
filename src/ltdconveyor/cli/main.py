"""Command-line interface ``ltd`` as a Click application."""

import logging
from typing import Any, Optional

import click

from ltdconveyor.cli.upload import upload

__all__ = ["main"]

# Add -h as a help shortcut option
CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option(
    "--log-level",
    "log_level",
    type=click.Choice(["warning", "info", "debug"]),
    default="info",
    help="Logging level (for first-party messages). Default: `info`.",
)
@click.option(
    "--host",
    "keeper_hostname",
    default="https://keeper.lsst.codes",
    envvar="LTD_HOST",
    help="Hostname of the LTD Keeper API (or `$LTD_HOST`). "
    "Default: `https://keeper.lsst.codes`.",
)
@click.option(
    "-u",
    "--user",
    "username",
    envvar="LTD_USERNAME",
    help="Username for LTD Keeper (or `$LTD_USERNAME`).",
)
@click.option(
    "-p",
    "--password",
    "password",
    envvar="LTD_PASSWORD",
    help="Password for LTD Keeper (or `$LTD_PASSWORD`).",
)
@click.version_option()
@click.pass_context
def main(
    ctx: click.Context,
    log_level: str,
    keeper_hostname: str,
    username: str,
    password: str,
) -> None:
    """ltd is a command-line client for LSST the Docs.

    Use ltd to upload new site builds, and to work with the LTD Keeper API.
    """
    ch = logging.StreamHandler()
    if log_level in ("warning", "info"):
        formatter = logging.Formatter(
            "%(asctime)s %(levelname)8s | %(message)s"
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s %(levelname)8s %(name)s | %(message)s"
        )
    ch.setFormatter(formatter)

    logger = logging.getLogger("ltdconveyor")
    logger.addHandler(ch)
    logger.setLevel(log_level.upper())

    # Subcommands should use the click.pass_obj decorator to get this
    # ctx.obj object as the first argument.
    ctx.obj = {
        "keeper_hostname": keeper_hostname,
        "username": username,
        "password": password,
        "token": None,
    }


@main.command()
@click.argument("topic", default=None, required=False, nargs=1)
@click.pass_context
def help(ctx: click.Context, topic: Optional[str], **kw: Any) -> None:
    """Show help for any command."""
    # The help command implementation is taken from
    # https://www.burgundywall.com/post/having-click-help-subcommand
    if topic:
        if topic in main.commands:
            ctx.info_name = topic
            click.echo(main.commands[topic].get_help(ctx))
    else:
        assert ctx.parent
        click.echo(ctx.parent.get_help())


# Add subcommands from other modules
main.add_command(upload)
