"""ltd upload subcommand.
"""

__all__ = ('upload',)

import logging

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
    required=True,
    help='Git ref, or space-delimited list of git refs. This versions the '
         'build and helps LTD Keeper assign the build to an edition.'
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
@click.pass_context
def upload(ctx, product, git_ref, dirname, aws_id, aws_secret):
    """Upload a new build to LSST the Docs.
    """
    logger = logging.getLogger(__name__)

    ensure_login(ctx)

    git_refs = git_ref.split(' ')

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
