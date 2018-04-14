###########
Development
###########

Installation for development
============================

Create a virtual environment for development.
Then install LTD Conveyor with development dependencies:

.. code-block:: bash

   pip install -e ".[dev]"

You can run tests with:

.. code-block:: bash

   pytest

Releases
========

Releases are made by creating a Git tag with a semantic version and pushing to GitHub.

.. code-block:: bash

   git tag -s X.Y.Z -m "X.Y.Z"
   git push --tags

Travis CI creates the PyPI release itself and `setuptools_scm <https://github.com/pypa/setuptools_scm/>`_ ensures the PyPI version matches the Git tag.
