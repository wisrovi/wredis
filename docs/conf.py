# WRedis documentation build configuration
import os
import sys

sys.path.insert(0, os.path.abspath(".."))

project = "WRedis"
copyright = "2026, wisrovi"
author = "wisrovi"
release = "1.0.0"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinx.ext.coverage",
    "sphinx_copybutton",
    "myst_parser",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "furo"
html_static_path = ["_static"]
html_title = "WRedis Documentation"
html_favicon = None

html_theme_options = {
    "light_logo": "wredis-logo-light.png",
    "dark_logo": "wredis-logo-dark.png",
    "sidebar_hide_name": False,
    "navigation_with_keys": True,
    "top_of_page_button": "edit",
    "source_repository": "https://github.com/wisrovi/wredis",
    "source_branch": "main",
    "source_directory": "docs/",
}

autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "special-members": "__init__",
    "undoc-members": True,
    "exclude-members": "__weakref__",
    "show-inheritance": True,
}

autodoc_typehints = "description"
autodoc_class_signature = "separated"

napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_type_aliases = None

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "redis": ("https://redis.readthedocs.io/en/stable/", None),
}

myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "linkify",
]

todo_include_todos = True
