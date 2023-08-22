"""ltd upload subcommand."""

import logging
import os
import re
import sys
from pathlib import Path
from typing import List, Optional

import click
import httpx

from ..factory import Factory
from .utils import run_with_asyncio

__all__ = ["upload"]


@click.command()
@click.option(
    "--product",
    required=False,
    default=None,
    help="Product name (deprecated, switch to project.",
)
@click.option("--project", required=False, default=None, help="Project name.")
@click.option("--org", required=False, default=None, help="Organization name.")
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
    "setting --gh when running in a GitHub Actions environment.",
)
@click.option(
    "--gh",
    "ci_env",
    flag_value="gh",
    help="Use environment variables from a GitHub Actions environment to set "
    "the --git-ref option.",
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
@run_with_asyncio
async def upload(
    ctx: click.Context,
    product: Optional[str],
    project: Optional[str],
    org: Optional[str],
    git_ref: Optional[str],
    dirname: str,
    ci_env: str,
    skip_upload: bool,
) -> None:
    """Upload a new site build to LSST the Docs."""
    logger = logging.getLogger(__name__)

    # Migrate --product to --project
    if project is None and product is not None:
        project = product
    if project is None:
        click.echo("Set a --project argument")
        sys.exit(1)

    if skip_upload:
        click.echo("Skipping ltd upload.")
        sys.exit(0)

    logger.debug("CI environment: %s", ci_env)

    # Detect git refs
    git_refs = _get_git_refs(ci_env, git_ref)
    base_dir = Path(dirname)

    async with httpx.AsyncClient() as http_client:
        factory = Factory(
            api_base=ctx.obj["keeper_hostname"],
            api_username=ctx.obj["username"],
            api_password=ctx.obj["password"],
            http_client=http_client,
        )
        project_service = factory.get_project_service()
        await project_service.upload_build(
            base_dir=base_dir,
            project=project,
            git_ref=git_refs[0],
            org=org,
        )


def _get_git_refs(
    ci_env: Optional[str], user_git_ref: Optional[str]
) -> List[str]:
    if ci_env == "gh" and user_git_ref is None:
        # Get git refs from GitHub Actions environment
        git_refs = _get_gh_actions_git_refs()
    elif user_git_ref is not None:
        # Get git refs from command line
        git_refs = user_git_ref.split()
    else:
        raise click.UsageError("--git-ref is required.")
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
