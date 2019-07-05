"""S3 Upload client using presigned POST URLs generated by the LTD Keeper
server application.

For more information about S3 presigned POST URLs, see
https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-presigned-urls.html#generating-a-presigned-url-to-upload-a-file
"""

__all__ = ('prescan_directory', 'upload_dir', 'upload_file',
           'upload_directory_objects')

from copy import deepcopy
import mimetypes
import logging

import requests

from .exceptions import S3Error
from ..exceptions import ConveyorError


def prescan_directory(base_dir, _current_dir=None):
    """Make a list of all directories in a site, including the root
    directory.

    This function is used to the LTD Keeper API what presigned POST URLs to
    create for a build (see `ltdconveyor.keeper.build.register_build`).

    Parmameters
    -----------
    base_dir : `pathlib.Path`
        The (local) root directory of a web site.

    Returns
    -------
    dirnames : `list`
        A list of directory names, relative to the root directory. The root
        directory is represented by ``"/"``. All directory names end with
        ``"/"``.
    """
    dirs = []
    if _current_dir is None:
        _current_dir = base_dir
    dirs.append(format_relative_dirname(_current_dir, base_dir))
    for path in _current_dir.iterdir():
        if path.is_dir():
            dirs.extend(prescan_directory(base_dir, _current_dir=path))
    return dirs


def format_relative_dirname(directory, base_directory):
    """Formats a relative directory path in a way that's compatible with the
    presigned POST URLs.

    Parameters
    ----------
    directory : `pathlib.Path`
        The directory to compute a relative path/name for.
    base_directory : `pathlib.Path`
        The base directory.

    Returns
    -------
    name : `str`
        The relative directory name.

        Examples:

        - ``"base/`` relative to ``"/base/"`` is ``"/"``.
        - ``"base/a/`` relative to ``"/base/"`` is ``"a/"``.
        - ``"base/a/b`` relative to ``"/base/"`` is ``"a/b/"``.
    """
    name = str(directory.relative_to(base_directory))
    if name == '.':
        return '/'
    elif not name.endswith('/'):
        return name + '/'
    else:
        return name


def upload_dir(*, post_urls, base_dir, _current_dir=None):
    """Upload a local directory of files to S3 for an LSST the Docs build.

    Parameters
    ----------
    post_urls : `dict`
        This dictionary is obtained from the ``"post_prefix_urls"`` field of
        the ``ltdconveyor.keeper.build.register_build`` function. It contains
        presigned post POST URLs and fields for each directory in the site
        being uploaded (see the ``dirnames`` parameter to
        `~ltdconveyor.keeper.build.register_build`).
    base_dir : `pathlib.Path`
        Base directory of the site.

    See also
    --------
    upload_directory_objects
    """
    logger = logging.getLogger(__name__)

    if _current_dir is None:
        _current_dir = base_dir

    relative_dir = format_relative_dirname(_current_dir, base_dir)
    try:
        post_url = post_urls[relative_dir]
    except KeyError:
        logger.exception('A presigned POST URL is not available for the '
                         '%s directory', relative_dir)
        raise ConveyorError

    for path in _current_dir.iterdir():
        if path.is_file():
            upload_file(
                local_path=path,
                post_url=post_url['url'],
                post_fields=post_url['fields'])
        elif path.is_dir():
            upload_dir(
                post_urls=post_urls,
                base_dir=base_dir,
                _current_dir=path)


def upload_file(*, local_path, post_url, post_fields):
    """Upload a file using a presigned POST URL to S3.

    This function should primarily be used by `upload_dir`.

    Parameter
    ---------
    local_path : `pathlib.Path`
        Path to the file being uploaded.
    post_url : `str`
        URL to upload to.
    post_fields : `dict`
        Dictionary of fields for the POST. Generally these fields are created
        by the LST Keeper API server when it generates the presigned URLs.

    Raises
    ------
    ltdconveyor.s3.exceptions.S3Error
        Raised if the upload fails.
    """
    logger = logging.getLogger(__name__)

    filename = local_path.name
    # don't want to globally change post_fields
    post_fields = deepcopy(post_fields)

    # Detect the Content-Type. This is a required field for the post URL.
    content_type, content_encoding = mimetypes.guess_type(filename,
                                                          strict=False)
    if content_type is not None:
        post_fields['Content-Type'] = content_type
    else:
        post_fields['Content-Type'] = 'application/octet-stream'

    with open(local_path, 'rb') as f:
        files = {'file': (filename, f)}
        http_response = requests.post(post_url, data=post_fields, files=files)
    if http_response.status_code == 204:
        logger.debug('Uploaded %s using presigned POST URL fields %s',
                     local_path, post_fields)
    else:
        logger.error('Error uploading %s (code %i) using presigned POST URL '
                     'fields %s', local_path, http_response.status_code,
                     post_fields)
        raise S3Error


def upload_directory_objects(*, post_urls):
    """Upload directory redirect objects for an LSST the Docs product build.

    Parameters
    ----------
    post_urls : `dict`
        This dictionary is obtained from the ``"post_dir_urls"`` field of
        the ``ltdconveyor.keeper.build.register_build`` function. It contains
        presigned post POST URLs and fields for each directory in the site
        being uploaded (see the ``dirnames`` parameter to
        `~ltdconveyor.keeper.build.register_build`).

    See also
    --------
    upload_dir

    Notes
    -----
    Directory redirect objects in S3 are named after directories, don't have
    a trailing slash in their key name, and don't have any content. What
    they *do* have is a ``x-amz-meta-dir-redirect`` header key. The LSST the
    Docs Fastly configuration looks for this header, and when detected,
    redirects the request to the associated ``*/index.html`` object.
    """
    logger = logging.getLogger(__name__)
    for dirname, post_url in post_urls.items():
        url = post_url['url']
        fields = post_url['fields']
        files = {'file': ('', '')}
        http_response = requests.post(url, data=fields, files=files)
        if http_response.status_code == 204:
            logger.debug(
                'Uploaded directory object for %s',
                dirname)
        else:
            logger.error(
                'Error uploading directory object for %s (code %i) using '
                'presigned POST URL fields %s', dirname,
                http_response.status_code, fields)
            raise S3Error
