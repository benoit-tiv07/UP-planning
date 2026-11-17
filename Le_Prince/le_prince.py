"""Script principal de Le Prince : lance pour l'instant l'extraction brute."""

import os
from pprint import pprint
from extraction_ade import extraire_evenements


def main():
    """Extrait le fichier ADE et écrit le résultat dans data."""
    dossier = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    try:
        evenements = extraire_evenements(os.path.join(dossier, "ADECal.ics"))
        with open(os.path.join(dossier, "ADE_extraction_brute.txt"),
                  "w", encoding="utf-8") as fichier:
            pprint(evenements, stream=fichier, sort_dicts=False, width=100)
    except (OSError, ValueError) as erreur:
        print(f"Extraction impossible : {erreur}")
        return 1
    print(f"{len(evenements)} événements extraits dans data/ADE_extraction_brute.txt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
