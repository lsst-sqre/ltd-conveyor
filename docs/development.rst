###########
Development
###########

Installation for development
============================

Create a virtual environment for development.
Then install LTD Conveyor with development dependencies:

.. code-block:: bash

   make init

You can run tests with:

.. code-block:: bash

   tox

Releases
========

Releases are made by creating a Git tag with a semantic version and pushing to GitHub.

.. code-block:: bash

   git tag -s X.Y.Z -m "X.Y.Z"
   git push --tags

Travis CI creates the PyPI release itself and `setuptools_scm <https://github.com/pypa/setuptools_scm/>`_ ensures the PyPI version matches the Git tag.

GitHub CI
=========

The GitHub CI action needs AWS creds and an existing S3 bucket.
These creds and the bucket name are injected via repository-scoped Actions `secrets <https://github.com/lsst-sqre/ltd-conveyor/settings/secrets/actions>`_ and `variables <https://github.com/lsst-sqre/ltd-conveyor/settings/variables/actions>`_

These creds are attached to the `ltd-conveyor-tests IAM user <https://us-east-1.console.aws.amazon.com/iam/home?region=us-west-2#/users/details/ltd-conveyor-tests?section=permissions>`_.
This user has an attached `ltd-conveyor-tests policy <https://us-east-1.console.aws.amazon.com/iam/home?region=us-west-2#/policies/details/arn%3Aaws%3Aiam%3A%3A039289279626%3Apolicy%2Fltd-conveyor-tests?section=permissions>`_.
This policy grants access to the `lsst-the-docs-test S3 bucket <https://us-west-2.console.aws.amazon.com/s3/buckets/lsst-the-docs-test?region=us-west-2&bucketType=general&tab=objects>`_.
