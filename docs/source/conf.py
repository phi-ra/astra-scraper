# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
import sys
# basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
# basedir1 = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..', 'src'))

# sys.path.insert(0,basedir)
# sys.path.insert(0,basedir1)
print(sys.executable)
sys.path.insert(0, os.path.abspath('../..'))


project = 'Astra Scraper'
copyright = '2024, Philipp Ratz'
author = 'Philipp Ratz'
release = '0.01'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.napoleon']

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']
