"""S3 upload/sync utilities.
"""

__all__ = ('upload_dir', 'upload_file', 'upload_object',
           'create_dir_redirect_object', 'ObjectManager')

import os
import logging
import mimetypes

import boto3

from .exceptions import S3Error


def upload_dir(bucket_name, path_prefix, source_dir,
               upload_dir_redirect_objects=True,
               surrogate_key=None,
               surrogate_control=None, cache_control=None,
               acl=None,
               aws_access_key_id=None, aws_secret_access_key=None,
               aws_profile=None):
    """Upload a directory of files to S3.

    This function places the contents of the Sphinx HTML build directory
    into the ``/path_prefix/`` directory of an *existing* S3 bucket.
    Existing files on S3 are overwritten; files that no longer exist in the
    ``source_dir`` are deleted from S3.

    Parameters
    ----------
    bucket_name : `str`
        Name of the S3 bucket where documentation is uploaded.
    path_prefix : `str`
        The root directory in the bucket where documentation is stored.
    source_dir : `str`
        Path of the Sphinx HTML build directory on the local file system.
        The contents of this directory are uploaded into the ``/path_prefix/``
        directory of the S3 bucket.
    upload_dir_redirect_objects : `bool`, optional
        A feature flag to enable uploading objects to S3 for every directory.
        These objects contain ``x-amz-meta-dir-redirect=true`` HTTP headers
        that tell Fastly to issue a 301 redirect from the directory object to
        the `index.html`` in that directory.
    surrogate_key : `str`, optional
        The surrogate key to insert in the header of all objects
        in the ``x-amz-meta-surrogate-key`` field. This key is used to purge
        builds from the Fastly CDN when Editions change.
        If `None` then no header will be set.
    cache_control : `str`, optional
        This sets the ``Cache-Control`` header on the uploaded
        files. The ``Cache-Control`` header specifically dictates how content
        is cached by the browser (if ``surrogate_control`` is also set).
    surrogate_control : `str`, optional
        This sets the ``x-amz-meta-surrogate-control`` header
        on the uploaded files. The ``Surrogate-Control``
        or ``x-amz-meta-surrogate-control`` header is used in priority by
        Fastly to givern it's caching. This caching policy is *not* passed
        to the browser.
    acl : `str`, optional
        The pre-canned AWS access control list to apply to this upload.
        Can be ``'public-read'``, which allow files to be downloaded
        over HTTP by the public. See
        https://docs.aws.amazon.com/AmazonS3/latest/dev/acl-overview.html#canned-acl
        for an overview of S3's pre-canned ACL lists. Note that ACL settings
        are not validated locally. Default is `None`, meaning that no ACL
        is applied to an individual object. In this case, use ACLs applied
        to the bucket itself.
    aws_access_key_id : `str`, optional
        The access key for your AWS account. Also set
        ``aws_secret_access_key``.
    aws_secret_access_key : `str`, optional
        The secret key for your AWS account.
    aws_profile : `str`, optional
        Name of AWS profile in :file:`~/.aws/credentials`. Use this instead
        of ``aws_access_key_id`` and ``aws_secret_access_key`` for file-based
        credentials.

    Notes
    -----
    ``cache_control`` and  ``surrogate_control`` can be used together.
    ``surrogate_control`` takes priority in setting Fastly's POP caching,
    while ``cache_control`` then sets the browser's caching. For example:

    - ``cache_control='no-cache'``
    - ``surrogate_control='max-age=31536000'``

    together will ensure that the browser always does an ETAG server query,
    but that Fastly will cache the content for one year (or until purged).
    This configuration is good for files that are frequently changed in place.

    For immutable uploads simply using ``cache_control`` is more efficient
    since it allows the browser to also locally cache content.

    .. seelso:

       - `Fastly: Cache control tutorial
         <https://docs.fastly.com/guides/tutorials/cache-control-tutorial>`_.
       - `Google: HTTP caching <http://ls.st/39v>`_.
    """
    logger = logging.getLogger(__name__)

    logger.debug('s3upload.upload({0}, {1}, {2})'.format(
        bucket_name, path_prefix, source_dir))

    session = boto3.session.Session(
        profile_name=aws_profile,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key)
    s3 = session.resource('s3')
    bucket = s3.Bucket(bucket_name)

    metadata = {}
    if surrogate_key is not None:
        metadata['surrogate-key'] = surrogate_key
    if surrogate_control is not None:
        metadata['surrogate-control'] = surrogate_control

    manager = ObjectManager(session, bucket_name, path_prefix)

    for (rootdir, dirnames, filenames) in os.walk(source_dir):
        # name of root directory on S3 bucket
        bucket_root = os.path.relpath(rootdir, start=source_dir)
        if bucket_root in ('.', '/'):
            bucket_root = ''

        # Delete bucket directories that no longer exist in source
        bucket_dirnames = manager.list_dirnames_in_directory(bucket_root)
        for bucket_dirname in bucket_dirnames:
            if bucket_dirname not in dirnames:
                logger.debug(('Deleting bucket directory {0}'.format(
                    bucket_dirname)))
                manager.delete_directory(bucket_dirname)

        # Delete files that no longer exist in source
        bucket_filenames = manager.list_filenames_in_directory(bucket_root)
        for bucket_filename in bucket_filenames:
            if bucket_filename not in filenames:
                bucket_filename = os.path.join(bucket_root, bucket_filename)
                logger.debug(
                    'Deleting bucket file {0}'.format(bucket_filename))
                manager.delete_file(bucket_filename)

        # Upload files in directory
        for filename in filenames:
            local_path = os.path.join(rootdir, filename)
            bucket_path = os.path.join(path_prefix, bucket_root, filename)
            logger.debug('Uploading to {0}'.format(bucket_path))
            upload_file(local_path, bucket_path, bucket,
                        metadata=metadata, acl=acl,
                        cache_control=cache_control)

        # Upload a directory redirect object
        if upload_dir_redirect_objects is True:
            bucket_dir_path = os.path.join(path_prefix, bucket_root)
            create_dir_redirect_object(
                bucket_dir_path,
                bucket,
                metadata=metadata,
                acl=acl,
                cache_control=cache_control)


def upload_file(local_path, bucket_path, bucket,
                metadata=None, acl=None, cache_control=None):
    """Upload a file to the S3 bucket.

    This function uses the mimetypes module to guess and then set the
    Content-Type and Encoding-Type headers.

    Parameters
    ----------
    local_path : `str`
        Full path to a file on the local file system.
    bucket_path : `str`
        Destination path (also known as the key name) of the file in the
        S3 bucket.
    bucket : boto3 Bucket instance
        S3 bucket.
    metadata : `dict`, optional
        Header metadata values. These keys will appear in headers as
        ``x-amz-meta-*``.
    acl : `str`, optional
        A pre-canned access control list. See
        https://docs.aws.amazon.com/AmazonS3/latest/dev/acl-overview.html#canned-acl
        Default is `None`, mean that no ACL is applied to the object.
    cache_control : `str`, optional
        The cache-control header value. For example, ``'max-age=31536000'``.
    """
    logger = logging.getLogger(__name__)

    extra_args = {}
    if acl is not None:
        extra_args['ACL'] = acl
    if metadata is not None and len(metadata) > 0:  # avoid empty Metadata
        extra_args['Metadata'] = metadata
    if cache_control is not None:
        extra_args['CacheControl'] = cache_control

    # guess_type returns None if it cannot detect a type
    content_type, content_encoding = mimetypes.guess_type(local_path,
                                                          strict=False)
    if content_type is not None:
        extra_args['ContentType'] = content_type

    logger.debug(str(extra_args))

    obj = bucket.Object(bucket_path)
    # no return status from the upload_file api
    obj.upload_file(local_path, ExtraArgs=extra_args)


def upload_object(bucket_path, bucket, content='',
                  metadata=None, acl=None, cache_control=None,
                  content_type=None):
    """Upload an arbitrary object to an S3 bucket.

    Parameters
    ----------
    bucket_path : `str`
        Destination path (also known as the key name) of the file in the
        S3 bucket.
    content : `str` or `bytes`, optional
        Object content.
    bucket : boto3 Bucket instance
        S3 bucket.
    metadata : `dict`, optional
        Header metadata values. These keys will appear in headers as
        ``x-amz-meta-*``.
    acl : `str`, optional
        A pre-canned access control list. See
        https://docs.aws.amazon.com/AmazonS3/latest/dev/acl-overview.html#canned-acl
        Default is `None`, meaning that no ACL is applied to the object.
    cache_control : `str`, optional
        The cache-control header value. For example, ``'max-age=31536000'``.
    content_type : `str`, optional
        The object's content type (such as ``text/html``). If left unset,
        no MIME type is passed to boto3 (which defaults to
        ``binary/octet-stream``).
    """
    obj = bucket.Object(bucket_path)

    # Object.put seems to be sensitive to None-type kwargs, so we filter first
    args = {}
    if metadata is not None and len(metadata) > 0:  # avoid empty Metadata
        args['Metadata'] = metadata
    if acl is not None:
        args['ACL'] = acl
    if cache_control is not None:
        args['CacheControl'] = cache_control
    if content_type is not None:
        args['ContentType'] = content_type

    obj.put(Body=content, **args)


def create_dir_redirect_object(bucket_dir_path, bucket, metadata=None,
                               acl=None, cache_control=None):
    """Create an S3 object representing a directory that's designed to
    redirect a browser (via Fastly) to the ``index.html`` contained inside
    that directory.

    Parameters
    ----------
    bucket_dir_path : `str`
        Full name of the object in the S3, which is equivalent to a POSIX
        directory path, like ``dir1/dir2``.
    bucket : boto3 Bucket instance
        S3 bucket.
    metadata : `dict`, optional
        Header metadata values. These keys will appear in headers as
        ``x-amz-meta-*``.
    acl : `str`, optional
        A pre-canned access control list. See
        https://docs.aws.amazon.com/AmazonS3/latest/dev/acl-overview.html#canned-acl
        Default is None, meaning that no ACL is applied to the object.
    cache_control : `str`, optional
        The cache-control header value. For example, ``'max-age=31536000'``.
    """
    # Just the name of the 'directory' itself
    bucket_dir_path = bucket_dir_path.rstrip('/')

    # create a copy of metadata
    if metadata is not None:
        metadata = dict(metadata)
    else:
        metadata = {}

    # header used by LTD's Fastly Varnish config to create a 301 redirect
    metadata['dir-redirect'] = 'true'

    upload_object(bucket_dir_path,
                  content='',
                  bucket=bucket,
                  metadata=metadata,
                  acl=acl,
                  cache_control=cache_control)


class ObjectManager(object):
    """Manage objects existing in a bucket under a specific ``bucket_root``.

    The ObjectManager maintains information about objects that exist in the
    bucket, and can delete objects that no longer exist in the source.

    Parameters
    ----------
    session : :class:`boto3.session.Session`
        A boto3 session instance provisioned with the correct identities.
    bucket_name : `str`
        Name of the S3 bucket.
    bucket_root : `str`
        The version slug is the name root directory in the bucket where
        documentation is stored.
    """
    def __init__(self, session, bucket_name, bucket_root):
        super().__init__()
        self._logger = logging.getLogger(__name__)

        s3 = session.resource('s3')
        bucket = s3.Bucket(bucket_name)
        self._session = session
        self._bucket = bucket
        self._bucket_root = bucket_root
        # Strip trailing '/' from bucket_root for comparisons
        self._bucket_root = self._bucket_root.rstrip('/')

    def list_filenames_in_directory(self, dirname):
        """List all file-type object names that exist at the root of this
        bucket directory.

        Parameters
        ----------
        dirname : `str`
            Directory name in the bucket relative to ``bucket_root/``.

        Returns
        -------
        filenames : `list`
            List of file names (`str`), relative to ``bucket_root/``, that
            exist at the root of ``dirname``.
        """
        prefix = self._create_prefix(dirname)
        filenames = []
        for obj in self._bucket.objects.filter(Prefix=prefix):
            if obj.key.endswith('/'):
                # a directory redirect object, not a file
                continue
            obj_dirname = os.path.dirname(obj.key)
            if obj_dirname == prefix:
                # object is at root of directory
                filenames.append(os.path.relpath(obj.key,
                                                 start=prefix))
        return filenames

    def list_dirnames_in_directory(self, dirname):
        """List all names of directories that exist at the root of this
        bucket directory.

        Note that *directories* don't exist in S3; rather directories are
        inferred from path names.

        Parameters
        ----------
        dirname : `str`
            Directory name in the bucket relative to ``bucket_root``.

        Returns
        -------
        dirnames : `list`
            List of directory names (`str`), relative to ``bucket_root/``,
            that exist at the root of ``dirname``.
        """
        prefix = self._create_prefix(dirname)
        dirnames = []
        for obj in self._bucket.objects.filter(Prefix=prefix):
            # get directory name of every object under this path prefix
            dirname = os.path.dirname(obj.key)

            # dirname is empty if the object happens to be the directory
            # redirect object object for the prefix directory (directory
            # redirect objects are named after directories and have metadata
            # that tells Fastly to redirect the browser to the index.html
            # contained in the directory).
            if dirname == '':
                dirname = obj.key + '/'

            # Strip out the path prefix from the directory name
            rel_dirname = os.path.relpath(dirname, start=prefix)

            # If there's only one part then this directory is at the root
            # relative to the prefix. We want this.
            dir_parts = rel_dirname.split('/')
            if len(dir_parts) == 1:
                dirnames.append(dir_parts[0])

        # Above algorithm finds root directories for all *files* in sub
        # subdirectories; trim down to the unique set.
        dirnames = list(set(dirnames))

        # Remove posix-like relative directory names that can appear
        # in the bucket listing.
        for filtered_dir in ('.', '..'):
            if filtered_dir in dirnames:
                dirnames.remove(filtered_dir)

        return dirnames

    def _create_prefix(self, dirname):
        """Make an absolute directory path in the bucker for dirname,
        which is is assumed relative to the self._bucket_root prefix directory.
        """
        if dirname in ('.', '/'):
            dirname = ''
        # Strips trailing slash from dir prefix for comparisons
        # os.path.dirname() returns directory names without a trailing /
        prefix = os.path.join(self._bucket_root, dirname)
        prefix = prefix.rstrip('/')
        return prefix

    def delete_file(self, filename):
        """Delete a file from the bucket.

        Parameters
        ----------
        filename : `str`
            Name of the file, relative to ``bucket_root/``.
        """
        key = os.path.join(self._bucket_root, filename)
        objects = list(self._bucket.objects.filter(Prefix=key))
        for obj in objects:
            obj.delete()

    def delete_directory(self, dirname):
        """Delete a directory (and contents) from the bucket.

        Parameters
        ----------
        dirname : `str`
            Name of the directory, relative to ``bucket_root/``.

        Raises
        ------
        RuntimeError
            Raised when there are no objects to delete (directory
            does not exist).
        """
        key = os.path.join(self._bucket_root, dirname)
        if not key.endswith('/'):
            key += '/'

        key_objects = [{'Key': obj.key}
                       for obj in self._bucket.objects.filter(Prefix=key)]
        if len(key_objects) == 0:
            msg = 'No objects in bucket directory {}'.format(dirname)
            raise RuntimeError(msg)
        delete_keys = {'Objects': key_objects}
        # based on http://stackoverflow.com/a/34888103
        s3 = self._session.resource('s3')
        r = s3.meta.client.delete_objects(Bucket=self._bucket.name,
                                          Delete=delete_keys)
        self._logger.debug(r)
        if 'Errors' in r:
            raise S3Error('S3 could not delete {0}'.format(key))
