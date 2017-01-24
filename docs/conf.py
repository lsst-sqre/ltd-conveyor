#!/usr/bin/env python
"""Sphinx configurations to build package documentation.

Note that this configuration might break if the sphinx configuration diverges
substantially for Science Pipelines usage.
"""

from documenteer.sphinxconfig.stackconf import build_package_configs
import ltdconveyor


_g = globals()
_g.update(build_package_configs(
    project_name='LTD Conveyor',
    copyright='2017 Association of Universities for '
              'Research in Astronomy, Inc.',
    version=ltdconveyor.__version__,
    doxygen_xml_dirname=None))

# purposefully override the intersphinx mappings from documenteer to a more
# minimal set.
intersphinx_mapping = {
    'python': ('http://docs.python.org/3/', None),
    'boto3': ('http://boto3.readthedocs.io/en/latest/', None),
}

# DEBUG only
automodsumm_writereprocessed = False
