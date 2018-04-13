import os
from io import open

from setuptools import setup, find_packages


packagename = 'ltd-conveyor'
description = 'LSST the Docs Amazon S3 object management package'
author = 'Jonathan Sick'
author_email = 'jsick@lsst.org'
license = 'MIT'
url = 'https://github.com/lsst-sqre/ltd-conveyor'


def read(filename):
    full_filename = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        filename)
    return open(full_filename, mode='r', encoding='utf-8').read()


long_description = read('README.rst')


setup(
    name=packagename,
    description=description,
    long_description=long_description,
    url=url,
    author=author,
    author_email=author_email,
    license=license,
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='lsst',
    packages=find_packages(exclude=['docs', 'tests*', 'data']),
    install_requires=['future>=0.16.0',
                      # botocore 1.5.60 is known to have python 2.7 issues
                      # This temporarily freezes to a working release.
                      'boto3==1.4.4',
                      'botocore==1.5.24',
                      'backports.tempfile==1.0rc1',
                      'requests>=2.12.4'],
    extras_require={
        "dev": [
            # Development dependencies
            'responses==0.5.1',
            'pytest==3.0.5',
            'pytest-cov==2.4.0',
            'pytest-flake8==0.8.1',
            # Documentation dependencies
            'Sphinx==1.5.2',
            'astropy-helpers==1.3',
            'documenteer==0.1.10',
            'lsst-sphinx-bootstrap-theme==0.1.1',
            'ltd-mason==0.2.5',
        ]
    },
    setup_requires=['setuptools_scm'],
    use_scm_version=True,
    # package_data={},
    # entry_points={}
)
