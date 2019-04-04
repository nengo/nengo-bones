"""Sphinx configuration options"""

import os

import nengo_bones

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.githubpages",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    "sphinx.ext.viewcode",
    "nengo_sphinx_theme",
    "numpydoc",
    "nbsphinx",
    "sphinx_click.ext",
]

templates_path = ["_templates"]

# -- sphinx.ext.autodoc
autoclass_content = "both"  # class and __init__ docstrings are concatenated
autodoc_default_options = {"members": None}
autodoc_member_order = "bysource"  # default is alphabetical

# -- sphinx.ext.intersphinx
intersphinx_mapping = {
    "numpy": ("https://docs.scipy.org/doc/numpy", None),
    "nengo": ("https://www.nengo.ai/nengo/", None),
}

# -- numpydoc config
numpydoc_show_class_members = False

# -- nbsphinx
nbsphinx_timeout = 300

# -- sphinx
exclude_patterns = ["_build", "**.ipynb_checkpoints"]
source_suffix = ".rst"
source_encoding = "utf-8"
master_doc = "index"
suppress_warnings = ["image.nonlocal_uri"]
linkcheck_ignore = [r"http://localhost:\d+"]
linkcheck_anchors = True
nitpicky = True
default_role = "py:obj"
exclude_patterns = ["examples/test-example.ipynb"]

project = u"Nengo Bones"
authors = u"Applied Brain Research"
copyright = nengo_bones.__copyright__
release = nengo_bones.__version__  # Full version, with tags
pygments_style = "friendly"

# -- Options for HTML output --------------------------------------------------

html_theme = "nengo_sphinx_theme"
html_title = "Nengo Bones {0} docs".format(release)
html_static_path = ["_static"]

htmlhelp_basename = 'Nengo Bones'
html_last_updated_fmt = ""  # default output format
html_show_sphinx = False
html_favicon = os.path.join("_static", "favicon.ico")
html_theme_options = {
    "sidebar_toc_depth": 4,
    "sidebar_logo_width": 200,
    "nengo_logo": "general-full-light.svg",
}
