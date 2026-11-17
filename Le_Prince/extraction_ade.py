def extraire_evenements(chemin):
    """Lit les événements simples d'ADE, sans interpréter leurs valeurs.

    Retourne une liste de dictionnaires. Signale les structures incomplètes
    ou non prises en charge avec ValueError ; les erreurs de lecture remontent.
    """
    # Reconstituer les propriétés réparties sur plusieurs lignes.
    lignes = []
    with open(chemin, encoding="utf-8-sig") as fichier:
        for ligne in fichier:
            ligne = ligne.rstrip("\n")
            if ligne.startswith((" ", "\t")):
                if not lignes:
                    raise ValueError("Ligne repliée sans ligne précédente.")
                lignes[-1] += ligne[1:]
            else:
                lignes.append(ligne)
    if not lignes or lignes[0] != "BEGIN:VCALENDAR" or lignes[-1] != "END:VCALENDAR":
        raise ValueError("Calendrier iCalendar incomplet.")
    evenements = []
    evenement = None
    for ligne in lignes[1:-1]:
        if ligne == "BEGIN:VEVENT" and evenement is None:
            evenement = {}
        elif ligne == "END:VEVENT" and evenement is not None:
            evenements.append(evenement)
            evenement = None
        elif ligne.startswith(("BEGIN:", "END:")):
            raise ValueError("Structure d'événement non prise en charge.")
        elif evenement is not None:
            if ":" not in ligne:
                raise ValueError("Propriété sans séparateur dans un événement.")
            nom, valeur = ligne.split(":", 1)
            if nom in evenement:
                raise ValueError(f"Propriété répétée non prise en charge : {nom}")
            evenement[nom] = valeur
        elif ligne and ":" not in ligne:
            raise ValueError("Propriété invalide dans l'en-tête du calendrier.")
    if evenement is not None:
        raise ValueError("Événement non terminé.")
    return evenements
