#######################
LSST the Docs: Conveyor
#######################

**Conveyor** is a common Python package for LSST the Docs (LTD) services that manage Amazon S3 objects.
All documentation hosted by LTD is served through the `Fastly CDN <https://www.fastly.com>`_, which uses S3 object metadata to purge caches.
Conveyor ensures that this metadata is properly set by all microservices that upload, copy, or delete objects from S3.
You can learn more about LTD in our `SQR-006 <https://sqr-006.lsst.io>`_ technote.

****

Copyright 2016-2017 Association of Universities for Research in Astronomy, Inc..

MIT licensed. See the LICENSE file.
