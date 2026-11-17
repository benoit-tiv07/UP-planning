import os
import sys
from pathlib import Path

# Sources personnelles Le Prince (indépendantes du répertoire M3).
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "Le_Prince"))

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
