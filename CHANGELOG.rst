##########
Change log
##########

Unreleased
==========

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
