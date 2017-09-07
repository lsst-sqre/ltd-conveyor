#######################
LSST the Docs: Conveyor
#######################

**Conveyor** is a common Python package for LSST the Docs (LTD) services that manage Amazon S3 objects.
All documentation hosted by LTD is served through the `Fastly CDN <https://www.fastly.com>`_, which uses S3 object metadata to purge caches.
Conveyor ensures that this metadata is properly set by all microservices that upload, copy, or delete objects from S3.
You can learn more about LTD in our `SQR-006 <https://sqr-006.lsst.io>`_ technote.

You can find the code at https://github.com/lsst-sqre/ltd-conveyor.

Installation
============

.. code-block:: bash

   pip install ltd-conveyor

Development
===========

Create a virtual environment for development.
Then install LTD Conveyor with development dependencies:

.. code-block:: bash

   pip install -e ".[dev]"

You can run tests with:

.. code-block:: bash

   pytest --flake8 --cov=ltdconveyor

Releases are made by creating a Git tag with a semantic version and pushing to GitHub.
Travis CI creates the PyPI release itself and `versioneer <https://github.com/warner/python-versioneer>`_ ensures the PyPI version matches the Git tag.

API reference
=============

.. automodapi:: ltdconveyor
   :no-inheritance-diagram:
