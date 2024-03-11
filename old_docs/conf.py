# -*- coding: utf-8 -*-
#
# Configuration file for the Sphinx documentation builder.
#
# This file does only contain a selection of the most common options. For a
# full list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
import os
import sys
import toytree
sys.path.insert(0, os.path.abspath('../../'))

# -- Project information -----------------------------------------------------
project = 'toytree'
author = 'Deren Eaton'
copyright = '2021, Deren Eaton'
version = toytree.__version__
release = toytree.__version__
extensions = [
    "sphinx.ext.autodoc",        # Core Sphinx library for auto html doc generation from docstrings
    "sphinx.ext.intersphinx",    # Link to other project's documentation (see mapping below)
    'sphinx.ext.mathjax',
    'sphinx.ext.viewcode',
    'sphinx.ext.doctest',
    'sphinx.ext.inheritance_diagram',
    'sphinx.ext.napoleon',
    'autodocsumm',
    # "sphinx.ext.autosummary",    # Create neat summary tables for modules/classes/methods etc
    'nbsphinx',
]

napoleon_numpy_docstring = True
napoleon_google_docstring = False
napoleon_use_ivar = False
napoleon_use_param = False
# numpydoc_show_class_members = False 
# 'numpydoc', 

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
language = 'en'
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', "**.ipynb_checkpoints"]
pygments_style = None
html_theme = 'sphinx_rtd_theme'
html_theme_options = {
    "collapse_navigation": False,
}
# html_static_path = ['_static']

html_context = {
    "display_github": True,
    "github_user": "eaton-lab",
    "github_repo": "toytree",
    "github_version": "main",
    "conf_py_path": "/docs/",
}


# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
#
# The default sidebars (for documents that don't match any pattern) are
# defined by theme itself.  Builtin themes are using these templates by
# default: ``['localtoc.html', 'relations.html', 'sourcelink.html',
# 'searchbox.html']``.
#
# html_sidebars = {}


# -- Options for HTMLHelp output ---------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'toytreedoc'


# -- Options for manual page output ------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, 'toytree', 'toytree Documentation',
     [author], 1)
]


# -- Options for Texinfo output ----------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, 'toytree', 'toytree Documentation',
     author, 'toytree', 'One line description of project.',
     'Miscellaneous'),
]


# -- Options for Epub output -------------------------------------------------

# Bibliographic Dublin Core info.
epub_title = project

# The unique identifier of the text. This can be a ISBN number
# or the project homepage.
#
# epub_identifier = ''

# A unique identification for the text.
#
# epub_uid = ''

# A list of files that should not be packed into the epub file.
epub_exclude_files = ['search.html']
