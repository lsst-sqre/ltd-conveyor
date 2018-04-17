"""Command-line interface ``ltd`` as a Click application.
"""

__all__ = ('main',)

import logging

import click

from .upload import upload


# Add -h as a help shortcut option
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option(
    '--log-level', 'log_level',
    type=click.Choice(['warning', 'info', 'debug']),
    default='warning',
    help='Logging level (for first-party messages). Default: `warning`.'
)
@click.option(
    '--host', 'keeper_hostname',
    default='https://keeper.lsst.codes',
    envvar='LTD_HOST',
    help='Hostname of the LTD Keeper API (or `$LTD_HOST`). '
         'Default: `https://keeper.lsst.codes`.'
)
@click.option(
    '-u', '--user', 'username',
    envvar='LTD_USERNAME',
    help='Username for LTD Keeper (or `$LTD_USERNAME`).'
)
@click.option(
    '-p', '--password', 'password',
    envvar='LTD_PASSWORD',
    help='Password for LTD Keeper (or `$LTD_PASSWORD`).'
)
@click.version_option()
@click.pass_context
def main(ctx, log_level, keeper_hostname, username, password):
    """ltd is a command-line client for LSST the Docs.

    Use ltd to upload new site builds, and to work with the LTD Keeper API.
    """
    ch = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)8s %(name)s | %(message)s')
    ch.setFormatter(formatter)

    logger = logging.getLogger('ltdconveyor')
    logger.addHandler(ch)
    logger.setLevel(log_level.upper())

    # Subcommands should use the click.pass_obj decorator to get this
    # ctx.obj object as the first argument.
    ctx.obj = {
        'keeper_hostname': keeper_hostname,
        'username': username,
        'password': password,
        'token': None
    }


@main.command()
@click.argument('topic', default=None, required=False, nargs=1)
@click.pass_context
def help(ctx, topic, **kw):
    """Show help for any command.
    """
    # The help command implementation is taken from
    # https://www.burgundywall.com/post/having-click-help-subcommand
    if topic is None:
        click.echo(ctx.parent.get_help())
    else:
        click.echo(main.commands[topic].get_help(ctx))


# Add subcommands from other modules
main.add_command(upload)
