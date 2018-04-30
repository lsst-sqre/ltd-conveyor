import os
from io import open

from setuptools import setup, find_packages


packagename = 'ltd-conveyor'
description = 'LSST the Docs Amazon client app and Python API library'
author = 'Jonathan Sick'
author_email = 'jsick@lsst.org'
license = 'MIT'
url = 'https://github.com/lsst-sqre/ltd-conveyor'
classifiers = [
    'Development Status :: 4 - Beta',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
]
keywords = 'lsst'


def read(filename):
    full_filename = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        filename)
    return open(full_filename, mode='r', encoding='utf-8').read()


long_description = read('README.rst')

# Core dependencies
install_requires = [
    'boto3==1.4.4',
    'requests>=2.12.4',
    'uritemplate>=3.0.0,<3.1.0',
    'click>=6.7,<7.0'
]

# Setup dependencies
setup_requires = [
    'pytest-runner>=2.11.1,<3',
    'setuptools_scm'
]

# Test dependencies
tests_require = [
    'responses==0.9.0',
    'pytest==3.5.0',
    'pytest-cov==2.5.1',
    'pytest-flake8==1.0.0',
]

# Optional/development dependencies
docs_require = [
    'Sphinx==1.5.2',
    'astropy-helpers==3.0.1',
    'documenteer==0.1.10',
    'lsst-sphinx-bootstrap-theme==0.1.1',
    'sphinx-click==1.1.0',
]
extras_require = {
    'dev': docs_require + tests_require
}


setup(
    name=packagename,
    description=description,
    long_description=long_description,
    url=url,
    author=author,
    author_email=author_email,
    license=license,
    classifiers=classifiers,
    keywords=keywords,
    packages=find_packages(exclude=['docs', 'tests*', 'data']),
    install_requires=install_requires,
    extras_require=extras_require,
    setup_requires=setup_requires,
    tests_require=tests_require,
    use_scm_version=True,
    # package_data={},
    entry_points={
        'console_scripts': [
            'ltd = ltdconveyor.cli.main:main',
        ]
    }
)
