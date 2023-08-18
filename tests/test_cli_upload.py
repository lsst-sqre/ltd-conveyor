"""Tests for ltdconveyor.cli.upload."""

from typing import Any, List, Optional

import click
import pytest

from ltdconveyor.cli.upload import _get_gh_actions_git_refs, _get_git_refs


def test_get_gh_actions_git_refs(monkeypatch: Any) -> None:
    import os

    monkeypatch.setattr(os, "getenv", lambda *args: "refs/heads/my_branch")

    assert _get_gh_actions_git_refs() == ["my_branch"]


def test_get_gh_actions_git_refs_no_env_var(monkeypatch: Any) -> None:
    import os

    monkeypatch.setattr(os, "getenv", lambda *args: "")

    with pytest.raises(click.UsageError):
        _get_gh_actions_git_refs()


@pytest.mark.parametrize(
    "env_var,ci_env,user_git_ref,expected",
    [
        # using GitHub Actions branch
        ("refs/heads/my_branch", "gh", None, ["my_branch"]),
        ("refs/tags/my_tag", "gh", None, ["my_tag"]),
        ("refs/pull/my_pr", "gh", None, ["my_pr"]),
        # overriding GitHub actions on command line
        ("refs/heads/my_branch", "gh", "user-branch", ["user-branch"]),
        # only using command line arg
        ("my_branch", None, "user-branch", ["user-branch"]),
        (None, None, "user-branch", ["user-branch"]),
        # parsing user git ref list
        (None, None, "a b   c", ["a", "b", "c"]),
    ],
)
def test_get_git_refs(
    monkeypatch: Any,
    env_var: Optional[str],
    ci_env: Optional[str],
    user_git_ref: Optional[str],
    expected: List[str],
) -> None:
    import os

    monkeypatch.setattr(os, "getenv", lambda *args: env_var)

    assert _get_git_refs(ci_env, user_git_ref) == expected
