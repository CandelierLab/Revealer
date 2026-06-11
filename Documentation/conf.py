# Configuration file for the Sphinx documentation builder.
# https://www.sphinx-doc.org/en/master/usage/configuration.html

project = "Revealer"
copyright = "Candelier Lab"
author = "Candelier Lab"

extensions = [
    "myst_parser",
]

myst_enable_extensions = [
    "colon_fence",
    "deflist",
]

source_suffix = {
    ".md": "markdown",
}

templates_path = []
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- HTML output -------------------------------------------------------------

html_theme = "furo"
html_title = "Revealer"
