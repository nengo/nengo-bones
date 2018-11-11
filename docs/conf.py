#!/usr/bin/env python3

import os

import project as proj

extensions = [
    "sphinx.ext.githubpages",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    "sphinx.ext.todo",
    "nengo_sphinx_theme",
]

# -- sphinx
nitpicky = True
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
source_suffix = ".rst"
source_encoding = "utf-8"
master_doc = "index"
project = "{{ PROJECT }}"
copyright = proj.__copyright__
author = "Applied Brain Research"
version = ".".join(proj.__version__.split(".")[:2])  # X.Y version
release = proj.__version__ # Full version with tags

# -- sphinx.ext.intersphinx
intersphinx_mapping = {
    "nengo": ("https://www.nengo.ai/", None)
}

# -- sphinx.ext.todo
todo_include_todos = True

# -- nengo_sphinx_theme
html_theme = "nengo_sphinx_theme"
pygments_style = "friendly"
templates_path = []
html_favicon = ""
html_static_path = ["_static"]
html_logo = os.path.join("_static", "logo.svg")
html_sidebars = {"**": ["sidebar.html"]}
html_context = {
    "css_files": [os.path.join("_static", "custom.css")],
}

# -- other
htmlhelp_basename = project

latex_elements = {
    # "papersize": "letterpaper",
    # "pointsize": "11pt",
    # "preamble": "",
    # "figure_align": "htbp",
}

latex_documents = [
    (master_doc,  # source start file
     "{{ SHORT PROJECT }}.tex",  # target name
     project,  # title
     author,  # author
     "manual"),  # documentclass
]

man_pages = [
    # (source start file, name, description, authors, manual section).
    (master_doc, "{{ SHORT PROJECT }}", project, [author], 1)
]

texinfo_documents = [
    (master_doc,  # source start file
     "{{ SHORT PROJECT }}",  # target name
     project,  # title
     author,  # author
     "{{ SHORT PROJECT }}",  # dir menu entry
     "{{ DESCRIPTION }}",  # description
     "Miscellaneous"),  # category
]
