"""Tests for ltdconveyor.cli.upload.
"""

import click
import pytest

from ltdconveyor.cli.upload import (_should_skip_travis_event,
                                    _get_git_refs,
                                    _get_travis_git_refs)


@pytest.mark.parametrize(
    'event_type,on_push,on_pr,on_api,on_cron,expected',
    [
        ('push', True, True, True, True, False),
        ('push', False, True, True, True, True),
        ('pull_request', True, True, True, True, False),
        ('pull_request', True, False, True, True, True),
        ('api', True, True, True, True, False),
        ('api', True, True, False, True, True),
        ('cron', True, True, True, True, False),
        ('cron', True, True, True, False, True),
    ])
def test_should_skip_travis_event(monkeypatch, event_type, on_push, on_pr,
                                  on_api, on_cron, expected):
    """Test _should_skip_travis_event with different combinations of
    user settings and TRAVIS_EVENT_TYPE variables.
    """
    import os

    def mock_env_var(_):
        return event_type

    monkeypatch.setattr(os, 'getenv', mock_env_var)
    assert _should_skip_travis_event(on_push, on_pr, on_api, on_cron) \
        is expected


def test_get_travis_git_refs(monkeypatch):
    import os

    monkeypatch.setattr(os, 'getenv', lambda _: 'my_branch')

    assert _get_travis_git_refs() == ['my_branch']


def test_get_travis_git_refs_no_env_var(monkeypatch):
    import os

    monkeypatch.setattr(os, 'getenv', lambda _: None)

    with pytest.raises(click.UsageError):
        _get_travis_git_refs()


@pytest.mark.parametrize(
    'travis_branch_var,ci_env,user_git_ref,expected',
    [
        # using travis branch
        ('my_branch', 'travis', None, ['my_branch']),
        # overriding travis on command line
        ('my_branch', 'travis', 'user-branch', ['user-branch']),
        # only using command line arg
        ('my_branch', None, 'user-branch', ['user-branch']),
        (None, None, 'user-branch', ['user-branch']),
        # parsing user git ref list
        (None, None, 'a b   c', ['a', 'b', 'c']),
    ]
)
def test_get_git_refs(monkeypatch, travis_branch_var, ci_env, user_git_ref,
                      expected):
    import os

    monkeypatch.setattr(os, 'getenv', lambda _: travis_branch_var)

    assert _get_git_refs(ci_env, user_git_ref) == expected
