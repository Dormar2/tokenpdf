import os
import sys
sys.path.insert(0, os.path.abspath('../../'))

project = 'tokenpdf'
author = 'Dor Marciano'
release = '0.1.0'

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.napoleon', "myst_parser"]
templates_path = ['_templates']
html_theme = 'sphinx_rtd_theme'