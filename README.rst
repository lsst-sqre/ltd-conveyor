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

**Conveyor** is a common Python package for LSST the Docs (LTD) services that manage Amazon S3 objects.
All documentation hosted by LTD is served through the `Fastly CDN <https://www.fastly.com>`_, which uses S3 object metadata to purge caches.
Conveyor ensures that this metadata is properly set by all microservices that upload, copy, or delete objects from S3.
You can learn more about LTD in our `SQR-006 <https://sqr-006.lsst.io>`_ technote.

Read the docs
=============

https://ltd-conveyor.lsst.io

****

Copyright 2016-2017 Association of Universities for Research in Astronomy, Inc..

MIT licensed. See the LICENSE file.
