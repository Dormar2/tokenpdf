import os
import sys
from collections import namedtuple
from sphinx.transforms import Transform

sys.path.insert(0, os.path.abspath('../../'))
extensions = ['sphinx.ext.autodoc', 'sphinx.ext.napoleon', "myst_parser"]
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', 'main.rst', 'scripts', 'setup.rst']
templates_path = ['_templates']
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}
html_theme = 'sphinx_rtd_theme'

LINKS_REPLACE = {"README.md": "index.html",
                 "CHANGELOG.md": "changelog.html",
                 "CONFIGURATION_REFERENCE.md": "config.html"}

def modify_html(app, pagename, templatename, context, doctree):
    """
    Modify the HTML context before rendering -
    this is to replace references to md files in the index page that includes readme.md.
    This is because the readme.md is in the project root, so the links are not found
    during its compilation. 
    "relative-docs" myst extension should solve this, but currently not working
    ("no such extension" error).
    
    Args:
        app: The Sphinx application instance.
        pagename: The name of the current page being rendered.
        templatename: The template name for the current page.
        context: A dictionary of the template context.
        doctree: The doctree for the page, or None if it is not related to a document.
    """
    # Example: Modify a specific page's content
    if pagename == "index":
        # Replace a placeholder in the final rendered HTML
        if "body" in context:
            for link,replace in LINKS_REPLACE.items():
                context["body"] = context["body"].replace(
                    f'href="#{link}"', f'href="{replace}"'
                )

def setup(app):
    app.connect("html-page-context", modify_html)