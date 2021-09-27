"""ltd upload subcommand."""

import logging
import os
import re
import sys
from pathlib import Path
from typing import List, Optional

import click

from ltdconveyor.cli.utils import ensure_login
from ltdconveyor.keeper.build import confirm_build, register_build
from ltdconveyor.s3.presignedpost import (
    prescan_directory,
    upload_dir,
    upload_directory_objects,
)

__all__ = ["upload"]


@click.command()
@click.option("--product", required=True, help="Product name.")
@click.option(
    "--dir",
    "dirname",
    default=".",
    type=click.Path(exists=False, file_okay=False, dir_okay=True),
    help="Directory with files to upload. Default: `.` (current working "
    "directory).",
)
@click.option(
    "--git-ref",
    help="Git ref, or space-delimited list of git refs. This versions the "
    "build and helps LTD Keeper assign the build to an edition. "
    "Alternatively, version information can be auto-discovered by "
    "setting --travis in a Travis CI job or --gh for GitHub actions.",
)
@click.option(
    "--gh",
    "ci_env",
    flag_value="gh",
    help="Use environment variables from a GitHub Actions environment to set "
    "the --git-ref option.",
)
@click.option(
    "--travis",
    "ci_env",
    flag_value="travis",
    help="Use environment variables from a Travis CI environment to set "
    "the --git-ref option.",
)
@click.option(
    "--on-travis-push/--no-travis-push",
    "on_travis_push",
    default=True,
    help="Upload on a Travis CI push (enabled by default). Must be used with "
    "--travis.",
)
@click.option(
    "--on-travis-pr/--no-travis-pr",
    "on_travis_pr",
    default=False,
    help="Upload on a Travis CI pull request event (disabled by default). "
    "Must be used with --travis.",
)
@click.option(
    "--on-travis-api/--no-travis-api",
    "on_travis_api",
    default=True,
    help="Upload on a Travis CI API event (enabled by default). "
    "Must be used with --travis.",
)
@click.option(
    "--on-travis-cron/--no-travis-cron",
    "on_travis_cron",
    default=True,
    help="Upload on a Travis CI cron event (enabled by default). "
    "Must be used with --travis.",
)
@click.option(
    "--skip",
    "skip_upload",
    default=False,
    is_flag=True,
    envvar="LTD_SKIP_UPLOAD",
    help="Skip the upload, making the command a no-op. "
    "Useful in CI environments to disable a site upload just by setting "
    "this option or the environment variable $LTD_SKIP_UPLOAD=true.",
)
@click.pass_context
def upload(
    ctx: click.Context,
    product: str,
    git_ref: Optional[str],
    dirname: str,
    ci_env: str,
    on_travis_push: bool,
    on_travis_pr: bool,
    on_travis_api: bool,
    on_travis_cron: bool,
    skip_upload: bool,
) -> None:
    """Upload a new site build to LSST the Docs."""
    logger = logging.getLogger(__name__)

    if skip_upload:
        click.echo("Skipping ltd upload.")
        sys.exit(0)

    logger.debug("CI environment: %s", ci_env)
    logger.debug(
        "Travis events settings. " "On Push: %r, PR: %r, API: %r, Cron: %r",
        on_travis_push,
        on_travis_pr,
        on_travis_api,
        on_travis_cron,
    )

    # Abort upload on Travis CI under certain events
    if ci_env == "travis" and _should_skip_travis_event(
        on_travis_push, on_travis_pr, on_travis_api, on_travis_cron
    ):
        sys.exit(0)

    # Authenticate to LTD Keeper host
    ensure_login(ctx)

    # Detect git refs
    git_refs = _get_git_refs(ci_env, git_ref)

    # Prescan directory names. Each directory needs a presigned POST URL.
    base_dir = Path(dirname)
    dirnames = prescan_directory(base_dir)

    build_resource = register_build(
        ctx.obj["keeper_hostname"],
        ctx.obj["token"],
        product,
        git_refs,
        dirnames=dirnames,
    )
    logger.debug("Created build resource %r", build_resource)

    # Do the upload.
    upload_dir(post_urls=build_resource["post_prefix_urls"], base_dir=base_dir)
    logger.debug("Upload complete for %r", build_resource["self_url"])

    # Upload directory objects for redirects
    upload_directory_objects(
        post_urls=build_resource["post_dir_urls"],
    )

    # Confirm upload
    confirm_build(build_resource["self_url"], ctx.obj["token"])
    logger.info("Build %r complete", build_resource["self_url"])
    logger.info("Published build URL: %s", build_resource["published_url"])


def _should_skip_travis_event(
    on_travis_push: bool,
    on_travis_pr: bool,
    on_travis_api: bool,
    on_travis_cron: bool,
) -> bool:
    """Detect if the upload should be skipped based on the
    ``TRAVIS_EVENT_TYPE`` environment variable.

    Returns
    -------
    should_skip : `bool`
        True if the upload should be skipped based on the combination of
        ``TRAVIS_EVENT_TYPE`` and user settings.
    """
    travis_event = os.getenv("TRAVIS_EVENT_TYPE")
    if travis_event is None:
        raise click.UsageError(
            "Using --travis but the TRAVIS_EVENT_TYPE "
            "environment variable is not detected."
        )

    if travis_event == "push" and on_travis_push is False:
        click.echo("Skipping upload on Travis push event.")
        return True
    elif travis_event == "pull_request" and on_travis_pr is False:
        click.echo("Skipping upload on Travis pull request event.")
        return True
    elif travis_event == "api" and on_travis_api is False:
        click.echo("Skipping upload on Travis pull request event.")
        return True
    elif travis_event == "cron" and on_travis_cron is False:
        click.echo("Skipping upload on Travis cron event.")
        return True
    else:
        return False


def _get_git_refs(
    ci_env: Optional[str], user_git_ref: Optional[str]
) -> List[str]:
    if ci_env == "travis" and user_git_ref is None:
        # Get git refs from Travis environment
        git_refs = _get_travis_git_refs()
    elif ci_env == "gh" and user_git_ref is None:
        # Get git refs from GitHub Actions environment
        git_refs = _get_gh_actions_git_refs()
    elif user_git_ref is not None:
        # Get git refs from command line
        git_refs = user_git_ref.split()
    else:
        raise click.UsageError("--git-ref is required.")
    return git_refs


def _get_travis_git_refs() -> List[str]:
    git_refs = [os.getenv("TRAVIS_BRANCH", "")]
    if git_refs[0] == "":
        raise click.UsageError(
            "Using --travis but the TRAVIS_BRANCH environment variable is "
            "not detected."
        )
    return git_refs


def _get_gh_actions_git_refs() -> List[str]:
    if os.getenv("GITHUB_EVENT_NAME") == "pull_request":
        return [_match_pr_head_ref()]
    else:
        return [_match_github_ref()]


def _match_pr_head_ref() -> str:
    github_ref = os.getenv("GITHUB_HEAD_REF", "")
    if github_ref == "":
        raise click.UsageError(
            "Using --gh but the GITHUB_HEAD_REF environment variable is "
            "not detected."
        )
    return github_ref


def _match_github_ref() -> str:
    github_ref = os.getenv("GITHUB_REF", "")
    if github_ref == "":
        raise click.UsageError(
            "Using --gh but the GITHUB_REF environment variable is "
            "not detected."
        )
    match = re.match(r"refs/(heads|tags|pull)/(?P<ref>.+)", github_ref)
    if not match:
        raise click.UsageError(
            "Could not parse the GITHUB_REF environment variable: {0}".format(
                github_ref
            )
        )
    ref = match.group("ref")
    return ref
