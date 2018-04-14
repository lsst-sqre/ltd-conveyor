"""Command-line interface ``ltd`` as a Click application.
"""

__all__ = ('main',)

import logging

import click


# Add -h as a help shortcut option
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option(
    '--log-level', 'log_level',
    type=click.Choice(['warning', 'info', 'debug']),
    default='warning',
    help='Logging level (for first-party messages).'
)
@click.version_option()
@click.pass_context
def main(ctx, log_level):
    """ltd is a command-line client for LSST the Docs.

    Use ltd to upload new site builds, and to work with the LTD Keeper API.
    repository.
    """
    # Subcommands should use the click.pass_obj decorator to get this
    # ctx.obj object as the first argument. Subcommands shouldn't create their
    # own Repo instance.
    ctx.obj = {}

    # configure internal logging
    logger = logging.getLogger('ltdconveyor')
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(log_level.upper())


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
