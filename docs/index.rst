#######################
LSST the Docs: Conveyor
#######################

**Conveyor** is a common Python library and command-line app for LSST the Docs (LTD) services and clients.

Key features:

- :doc:`ltd <cli>` command-line app.

  The :program:`ltd upload` subcommand makes it easy to integrate documentation uploads with continuous integration jobs, particularly Travis CI.

- The `ltdconveyor` Python package provides APIs for working with LSST the Docs.

  `ltdconveyor.s3` subpackage provides S3 object management services.
  All documentation hosted by LTD is served through the `Fastly CDN <https://www.fastly.com>`_, which uses S3 object metadata to purge caches.
  Conveyor ensures that this metadata is properly set by all clients and microservices that upload, copy, or delete objects from S3.

  `ltdconveyor.fastly` provides Fastly cache management APIs.

  `ltdconveyor.keeper` provides APIs for working with `LTD Keeper's REST API <https://ltd-keeper.lsst.io>`_.

You can learn more about LTD in our `SQR-006 <https://sqr-006.lsst.io>`_ technote.

You can find the code at https://github.com/lsst-sqre/ltd-conveyor.

Installation
============

.. code-block:: bash

   pip install ltd-conveyor

Documentation
=============

.. toctree::

   cli
   api
   changes
   development
