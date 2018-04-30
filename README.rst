#######################
LSST the Docs: Conveyor
#######################

.. image:: https://img.shields.io/pypi/v/ltd-conveyor.svg
   :target: https://pypi.python.org/pypi/ltd-conveyor
   :alt: Python Package Index
.. image:: https://img.shields.io/travis/lsst-sqre/ltd-conveyor.svg
   :target: https://travis-ci.org/lsst-sqre/ltd-conveyor
   :alt: Travis CI build status
.. image:: https://img.shields.io/badge/ltd--conveyor-lsst.io-brightgreen.svg
   :target: https://ltd-conveyor.lsst.io
   :alt: Documentation

**Conveyor** is a common Python library and command-line app for LSST the Docs (LTD) services and clients.

Key features:

- ``ltd`` command-line app.

  The ``ltd upload`` subcommand makes it easy to integrate documentation uploads with continuous integration jobs, particularly Travis CI.

- The ``ltdconveyor`` Python package provides APIs for working with LSST the Docs.

  ``ltdconveyor.s3`` subpackage provides S3 object management services.
  All documentation hosted by LTD is served through the `Fastly CDN <https://www.fastly.com>`_, which uses S3 object metadata to purge caches.
  Conveyor ensures that this metadata is properly set by all clients and microservices that upload, copy, or delete objects from S3.

  ``ltdconveyor.fastly`` provides Fastly cache management APIs.

  ``ltdconveyor.keeper`` provides APIs for working with LTD Keeper's REST API.

You can learn more about LTD in our `SQR-006 <https://sqr-006.lsst.io>`_ technote.

**Read the docs:** https://ltd-conveyor.lsst.io
