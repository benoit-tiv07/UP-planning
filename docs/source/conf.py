import os
import sys

# Chemin vers les modules Python du projet
sys.path.insert(
    0,
    os.path.abspath("../../UP-planning-programmes")
)

# Informations du projet
project = "UPplanning"
author = "Groupe SAE 3.02"
release = "0.1.0"

# Extensions Sphinx
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
]

# Format de documentation
templates_path = ["_templates"]
exclude_patterns = []

# Apparence du site HTML
html_theme = "alabaster"
html_static_path = ["_static"]