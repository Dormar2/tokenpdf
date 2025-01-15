import os
import sys
sys.path.insert(0, os.path.abspath('../../'))

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.napoleon', "myst_parser"]
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', 'main.rst', 'scripts', 'setup.rst']
templates_path = ['_templates']
html_theme = 'sphinx_rtd_theme'