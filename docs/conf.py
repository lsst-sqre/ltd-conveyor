"""Sphinx configurations to build package documentation.

Note that this configuration might break if the sphinx configuration diverges
substantially for Science Pipelines usage.
"""

from documenteer.sphinxconfig.utils import read_git_commit_timestamp
import lsst_sphinx_bootstrap_theme
import ltdconveyor


# DEBUG only
automodsumm_writereprocessed = False

try:
    date = read_git_commit_timestamp()
except Exception:
    date = datetime.datetime.now()

c = {}
project = 'LTD Conveyor'
copyright = '2016-2018 Association of Universities for Research in Astronomy'
version = ltdconveyor.__version__
release = ltdconveyor.__version__
today = date.strftime('%Y-%m-%d')

# Sphinx extension modules
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.mathjax',
    'sphinx.ext.ifconfig',
    'sphinx.ext.viewcode',
    'sphinx_click.ext',
    'astropy_helpers.extern.numpydoc.numpydoc',
    'astropy_helpers.extern.automodapi.autodoc_enhancements',
    'astropy_helpers.extern.automodapi.automodsumm',
    'astropy_helpers.extern.automodapi.automodapi',
    'astropy_helpers.sphinx.ext.tocdepthfix',
    'astropy_helpers.sphinx.ext.doctest',
    'astropy_helpers.sphinx.ext.changelog_links',
    'astropy_helpers.extern.automodapi.smart_resolver',
    'documenteer.sphinxext',
]

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
source_suffix = '.rst'

# The encoding of source files.
source_encoding = 'utf-8-sig'

# The master toctree document.
master_doc = 'index'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['_build', 'README.rst']

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True

# Configuration for Intersphinx
intersphinx_mapping = {
    'python': ('http://docs.python.org/3/', None),
    'boto3': ('http://boto3.readthedocs.io/en/latest/', None),
}

# The reST default role (used for this markup: `text`)
default_role = 'obj'

# This is added to the end of RST files - a good place to put substitutions
# to be used globally.
rst_epilog = """
"""

# A list of warning types to suppress arbitrary warning messages. We mean
# to override directives in
# astropy_helpers.sphinx.ext.autodoc_enhancements, thus need to ignore
# those warning. This can be removed once the patch gets released in
# upstream Sphinx (https://github.com/sphinx-doc/sphinx/pull/1843).
# Suppress the warnings requires Sphinx v1.4.2
suppress_warnings = ['app.add_directive', ]

# Don't show summaries of the members in each class along with the
# class' docstring
numpydoc_show_class_members = False

autosummary_generate = True

automodapi_toctreedirnm = 'api'

# Class documentation should contain *both* the class docstring and
# the __init__ docstring
autoclass_content = "both"

# Render inheritance diagrams in SVG
graphviz_output_format = "svg"

graphviz_dot_args = [
    '-Nfontsize=10',
    '-Nfontname=Helvetica Neue, Helvetica, Arial, sans-serif',
    '-Efontsize=10',
    '-Efontname=Helvetica Neue, Helvetica, Arial, sans-serif',
    '-Gfontsize=10',
    '-Gfontname=Helvetica Neue, Helvetica, Arial, sans-serif'
]

# -- Options for HTML output ----------------------------------------------

templates_path = [
    '_templates',
    lsst_sphinx_bootstrap_theme.get_html_templates_path()]

html_theme = 'lsst_sphinx_bootstrap_theme'
html_theme_path = [lsst_sphinx_bootstrap_theme.get_html_theme_path()]

numfig = True
numfig_format = {'figure': 'Figure %s',
                 'table': 'Table %s',
                 'code-block': 'Listing %s'}

# Theme options are theme-specific and customize the look and feel of a
# theme further.  For a list of options available for each theme, see the
# documentation.
html_theme_options = {}

# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> documentation".
html_title = project

# A shorter title for the navigation bar.  Default is the same as
# html_title.
html_short_title = project

# The name of an image file (relative to this directory) to place at the
# top of the sidebar.
html_logo = None

# The name of an image file (within the static path) to use as favicon of
# the docs.  This file should be a Windows icon file (.ico) being 16x16 or
# 32x32 pixels large.
html_favicon = None

# Add any paths that contain custom static files (such as style sheets)
# here, relative to this directory. They are copied after the builtin
# static files, so a file named "default.css" will overwrite the builtin
# "default.css".
html_static_path = ['_static']

# Add any extra paths that contain custom files (such as robots.txt or
# .htaccess) here, relative to this directory. These files are copied
# directly to the root of the documentation.
# html_extra_path = []

# If not '', a 'Last updated on:' timestamp is inserted at every page
# bottom, using the given strftime format.
html_last_updated_fmt = '%b %d, %Y'

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
html_use_smartypants = True

# If false, no module index is generated.
html_domain_indices = False

# If false, no index is generated.
html_use_index = False

# If true, the index is split into individual pages for each letter.
html_split_index = False

# If true, links to the reST sources are added to the pages.
html_show_sourcelink = True

# If true, "Created using Sphinx" is shown in the HTML footer. Default is
# True.
html_show_sphinx = True

# If true, "(C) Copyright ..." is shown in the HTML footer. Default is
# True.
html_show_copyright = True

# If true, an OpenSearch description file will be output, and all pages
# will contain a <link> tag referring to it.  The value of this option must
# be the base URL from which the finished HTML is served.
# html_use_opensearch = ''

# This is the file name suffix for HTML files (e.g. ".xhtml").
html_file_suffix = '.html'

# Language to be used for generating the HTML full-text search index.
html_search_language = 'en'
