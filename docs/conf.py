# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
import sys

sys.path.insert(0, os.path.abspath('..'))
project = 'Saahitt'
copyright = '2024, Dobaato'
author = 'Dobaato'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# conf.py

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx'
]

autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'private-members': True,
    'class-doc-from': 'both',
}

autodoc_class_signature = 'separated'

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


def skip_member(app, what, name, obj, skip, options):
    if what == "class" and name == "__init__":
        return False
    return skip


def setup(app):
    app.connect("autodoc-skip-member", skip_member)


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']
