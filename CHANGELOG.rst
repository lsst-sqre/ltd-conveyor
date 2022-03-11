##########
Change log
##########

0.9.0 (unreleased)
==================

Adds support for LTD Keeper 2.0.

0.8.1 (2021-09-27)
==================

Fix parsing of the ``GITHUB_HEAD_REF`` environment variable in GitHub Actions.

0.8.0 (2021-09-15)
==================

The ``ltd upload`` command now works in pull requests workflows on GitHub Actions.

0.7.0 (2020-09-01)
==================

This release focuses on infrastructure improvements, and should not have a significant impact on users.

Infrastructure
--------------

- This tool is officially tested and supported on Python 3.7 and 3.8.
  Python 3.6 is no longer officially supported.

- Removed pins on third-party dependencies, including boto3, requests, uritemplate, and click.
  In doing so, LTD Conveyor is easier to integrate into your existing Python environment.

- We have migrated from Travis CI to GitHub Actions for testing, linting, documentation builds and deployment, and deployments to PyPI.
  In addition to on-demand testing, GitHub Actions tests the package on a daily basis to ensure compatibility with third-party dependencies.

- Internally, we use tox for running tests, linters, and to build documentation.
  tox makes it possible for local test runs to use the same set up as CI.

- The codebase is now automatically formatted with black and isort.
  By using pre-commit, we ensure that formatting is always applied.

- The codebase now has type annotations, which are tested with mypy.
  Type annotations help ensure that APIs are explicitly defined and correctly used.

0.6.1 (2020-02-23)
==================

Fixed
-----

- The ``--gh`` option for ``ltd upload`` now supports tag and PR events, in addition to branches.

0.6.0 (2020-02-20)
==================

Added
-----

- Added a ``--gh`` option to the ``ltd upload`` command to support usage in `GitHub Actions <https://help.github.com/en/actions>`__.

0.5.0 (2020-02-05)
==================

Added
-----

- LTD Conveyor can now upload new builds to S3 using Amazon's S3's presigned POST URL feature.
  This means that clients no longer need credentials for S3 — the LTD Keeper API server generates presigned POST URLs as part of the ``POST /products/<product>/builds/`` build registration step.
- The ``ltd`` command now uses the presigned POST-based URLs.
  The ``--aws-id`` and ``--aws-secret`` options have been removed, but the ``--user`` and ``--password`` options remain.

  If you use environment variables, there should be no change in how you use ``ltd upload`` (aside from not needing the ``$LTD_AWS_ID`` and ``$LTD_AWS_SECRET`` environment variables).

Fixed
-----

- In INFO-level and higher logging, the module path isn't displayed.
  Module paths are only shown in DEBUG-level logging where it's most useful.

Infrastructure
--------------

- Packaging is now done through a ``setup.cfg`` file and a ``pyproject.toml`` file (PEP 518).
- Updated Travis CI configuration to test with Python 3.8; also refactored the CI Pipeline with Travis CI stages.

0.4.2 (2018-10-09)
==================

Fixed
-----

- Fixed a bug where ``ltdconveyor.s3.delete_dir``, since 0.4.1, would raise a ``TypeError`` while deleting an empty directory (no objects in the S3 prefix).

0.4.1 (2018-10-08)
==================

Fixed
-----

- Fixed a bug where ``ltdconveyor.s3.delete_dir`` would fail if there are more than 1000 objects under a path prefix that is being deleted.
- Fixed title of the project in the documentation by updating to use a `Documenteer`_\ -based Sphinx set up.

0.4.0 (2018-04-17)
==================

Added
-----

- Added a new command-line app, ``ltd``, that provides subcommands for clients to work with the LSST the Docs API.
  This app is implemented with Click_, and its documentation is automatically generated from the command-line help with `sphinx-click`_.

  The first subcommand is ``ltd upload``, which lets a client upload a site to LTD as a new build.
  This command includes special features for using the client from Travis CI (``ltd upload --travis`` option) to populate the version information from the Travis environment.
  Other flags allow ``ltd upload`` to become a no-op under certain circumstances (for example, skip uploads on pull requests) or arbitrarily (set ``ltd upload --skip`` or ``export LTD_SKIP_UPLOAD=true``).

  .. note::

     With this feature, LTD Conveyor effectively deprecates `LTD Mason`_.
     LTD Mason was the original uploader for LSST the Docs, but it was also designed around the idea of building the `LSST Science Pipelines` documentation as well (hence the term "mason").
     Over time, we realized it is better to have a general purpose client and uploader for LSST the Docs (LTD Conveyor) and a dedicated tool for assembling the multi-package Sphinx documentation site (`Documenteer`_).

- Added the `ltdconveyor.keeper` subpackage that widens the scope of LTD Conveyor to be a full-service library for building LTD clients, not just an S3 upload client.

  - The `ltdconveyor.keeper.login.get_keeper_token` function lets you obtain a temporary auth token for the LTD Keeper API.

  - The `ltdconveyor.keeper.build` module includes functions for performing the build upload handshake with the LTD Keeper API.

Changed
-------

- Removed Python 2.7 and 3.4 compatibility.
  Now the codebase is entirely Python 3 (3.5, 3.6)-oriented.

- Completely reorganized Python namespace.
  Now all S3 APIs are in ``ltdconveyor.s3``.
  Fastly APIs are available from ``ltdconveyor.fastly``.

- Switched to using ``setuptools_scm`` to generate version strings for releases.

- Switched to using ``extras_require`` for development dependencies (``pip install -e ".[dev]"``).
  This lets us exclusively coordinate dependencies in ``setup.py``.

- Enable testing via ``python setup.py test``.
  Also upgrade the testing stack to ``pytest`` 3.5 and ``pytest-flake8`` 1.0.

- Compatibility updates to the Sphinx documentation infrastructure.

- Default to ``acl=None`` to support more AWS IAM users.
  It turns out that not all IAM users with ``PutObject`` permissions also have permissions to set the ``ACL`` for an object.
  We want to make it possible for many lightweight IAM users to upload to restricted sub-directories of the ``lsst-the-docs`` bucket, but it seems hard to make these users ACL grantees too.
  We now seek an alternative:

  - The ``lsst-the-docs`` bucket now has a PublicRead *bucket* policy
  - No ACL is set on individual objects.

Fixed
-----

- Changed assertions to ``RuntimeErrors``.
  Assertions shouldn't be used to raise exceptions in production code.

0.3.1 (2017-03-27)
==================

Added
-----

- Add ``open_bucket`` function.
  This provides a convenient API for getting a boto3 bucket resource, particularly for clients that use the upload_object and upload_file APIs directly that take a bucket only.

0.3.0 (2017-02-20)
==================

Added
-----

- Added ``content_type`` parameter to ``upload_object`` so that a user can specify ``text/html`` for an HTML upload.
  The ``upload_file``/``upload_dir`` functions avoid this problem by using Python's ``mimetypes`` library to guess the encoding, but ``upload_object`` is lower-level and warrants having the user explicitly provide the content type.
- Refactored new function ``create_dir_redirect_object``.
  This code used to be inside ``upload_dir``, but in `LTD Dasher`_ it seems necessary to upload files one at a time, and thus it's necessary to directly create these directory redirect objects.

Fixed
-----

- Fix issue where ``'..'`` shows up in directory names (seen when doing ``upload_dir`` with `LTD Dasher`_ asset directories).

0.2.0 (2017-02-02)
==================

Added
-----

- Ported Fastly ``purge_key`` function from `LTD Keeper`_.
  Any LTD application that uploads objects to S3 might also need to purge Fastly CDN caches.
  This purge capability is presented as a simple function.

0.1.0 (2017-01-25)
==================

Added
-----

- Port S3 codebase from `LTD Mason`_.
  The purpose of LTD Conveyor is to provide a set of common S3 APIs that can be used from both client (uploading docs from CI) and server (`LTD Keeper`_) settings.

.. _LTD Keeper: https://ltd-keeper.lsst.io
.. _LTD Mason: https://ltd-mason.lsst.io
.. _LTD Dasher: https://github.com/lsst-sqre/ltd-dasher
.. _Documenteer: https://documenteer.lsst.io
.. _Click: http://click.pocoo.org/
.. _sphinx-click: https://sphinx-click.readthedocs.io/en/latest/
.. _LSST Science Pipelines: https://pipelines.lsst.io
