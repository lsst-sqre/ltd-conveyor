"""ltd upload subcommand.
"""

__all__ = ('upload',)

import logging
import os
import sys

import click

from ..keeper.build import register_build, confirm_build
from ..s3.upload import upload_dir
from .utils import ensure_login


@click.command()
@click.option(
    '--product',
    required=True,
    help='Product name.'
)
@click.option(
    '--git-ref',
    help='Git ref, or space-delimited list of git refs. This versions the '
         'build and helps LTD Keeper assign the build to an edition. '
         'Alternatively, version information can be auto-discovered by '
         'setting --travis in a Travis CI job.'
)
@click.option(
    '--dir', 'dirname',
    default='.',
    type=click.Path(exists=False, file_okay=False, dir_okay=True),
    help='Directory with files to upload. Default: `.` (current working '
         'directory).'
)
@click.option(
    '--aws-id', 'aws_id',
    required=True,
    envvar='LTD_AWS_ID',
    help='AWS ID (or `$LTD_AWS_ID`).'
)
@click.option(
    '--aws-secret', 'aws_secret',
    required=True,
    envvar='LTD_AWS_SECRET',
    help='AWS secret access key (or `$LTD_AWS_SECRET`).'
)
@click.option(
    '--travis', 'ci_env', flag_value='travis',
    help='Use environment variables from a Travis CI environment to set '
         'the --git-ref option.'
)
@click.option(
    '--on-travis-push/--no-travis-push', 'on_travis_push', default=True,
    help='Upload on a Travis CI push (enabled by default). Must be used with '
         '--travis.'
)
@click.option(
    '--on-travis-pr/--no-travis-pr', 'on_travis_pr', default=False,
    help='Upload on a Travis CI pull request event (disabled by default). '
         'Must be used with --travis.'
)
@click.option(
    '--on-travis-api/--no-travis-api', 'on_travis_api', default=True,
    help='Upload on a Travis CI API event (enabled by default). '
         'Must be used with --travis.'
)
@click.option(
    '--on-travis-cron/--no-travis-cron', 'on_travis_cron', default=True,
    help='Upload on a Travis CI cron event (enabled by default). '
         'Must be used with --travis.'
)
@click.option(
    '--skip', 'skip_upload', default=False, is_flag=True,
    envvar='LTD_SKIP_UPLOAD',
    help='Skip the upload, making the command a no-op. '
         'Useful in CI environments to disable a site upload just by setting '
         'this option or the environment variable $LTD_SKIP_UPLOAD=true.'
)
@click.pass_context
def upload(ctx, product, git_ref, dirname, aws_id, aws_secret, ci_env,
           on_travis_push, on_travis_pr, on_travis_api, on_travis_cron,
           skip_upload):
    """Upload a new site build to LSST the Docs.
    """
    logger = logging.getLogger(__name__)

    if skip_upload:
        click.echo('Skipping ltd upload.')
        sys.exit(0)

    logger.debug('CI environment: %s', ci_env)
    logger.debug('Travis events settings. '
                 'On Push: %r, PR: %r, API: %r, Cron: %r',
                 on_travis_push, on_travis_pr, on_travis_api, on_travis_cron)

    # Abort upload on Travis CI under certain events
    if ci_env == 'travis' and \
            _should_skip_travis_event(
                on_travis_push, on_travis_pr, on_travis_api, on_travis_cron):
        sys.exit(0)

    # Authenticate to LTD Keeper host
    ensure_login(ctx)

    # Detect git refs
    git_refs = _get_git_refs(ci_env, git_ref)

    build_resource = register_build(
        ctx.obj['keeper_hostname'],
        ctx.obj['token'],
        product,
        git_refs
    )
    logger.debug('Created build resource %r', build_resource)

    # Do the upload.
    # This cache_control is appropriate for builds since they're immutable.
    # The LTD Keeper server changes the cache settings when copying the build
    # over to be a mutable edition.
    upload_dir(
        build_resource['bucket_name'],
        build_resource['bucket_root_dir'],
        dirname,
        aws_access_key_id=aws_id,
        aws_secret_access_key=aws_secret,
        surrogate_key=build_resource['surrogate_key'],
        cache_control='max-age=31536000',
        surrogate_control=None,
        upload_dir_redirect_objects=True)
    logger.debug('Upload complete for %r', build_resource['self_url'])

    # Confirm upload
    confirm_build(
        build_resource['self_url'],
        ctx.obj['token']
    )
    logger.debug('Build %r complete', build_resource['self_url'])


def _should_skip_travis_event(on_travis_push, on_travis_pr, on_travis_api,
                              on_travis_cron):
    """Detect if the upload should be skipped based on the
    ``TRAVIS_EVENT_TYPE`` environment variable.

    Returns
    -------
    should_skip : `bool`
        True if the upload should be skipped based on the combination of
        ``TRAVIS_EVENT_TYPE`` and user settings.
    """
    travis_event = os.getenv('TRAVIS_EVENT_TYPE')
    if travis_event is None:
        raise click.UsageError(
            'Using --travis but the TRAVIS_EVENT_TYPE '
            'environment variable is not detected.')

    if travis_event == 'push' and on_travis_push is False:
        click.echo('Skipping upload on Travis push event.')
        return True
    elif travis_event == 'pull_request' and on_travis_pr is False:
        click.echo('Skipping upload on Travis pull request event.')
        return True
    elif travis_event == 'api' and on_travis_api is False:
        click.echo('Skipping upload on Travis pull request event.')
        return True
    elif travis_event == 'cron' and on_travis_cron is False:
        click.echo('Skipping upload on Travis cron event.')
        return True
    else:
        return False


def _get_git_refs(ci_env, user_git_ref):
    if ci_env == 'travis' and user_git_ref is None:
        # Get git refs from Travis environment
        git_refs = _get_travis_git_refs()
    elif user_git_ref is not None:
        # Get git refs from command line
        git_refs = user_git_ref.split()
    else:
        raise click.UsageError('--git-ref is required.')
    return git_refs


def _get_travis_git_refs():
    git_refs = [os.getenv('TRAVIS_BRANCH')]
    if git_refs[0] is None:
        raise click.UsageError(
            'Using --travis but the TRAVIS_BRANCH environment variable is '
            'not detected.')
    return git_refs
