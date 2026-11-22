"""Traitements du module M2 : séquence d'enseignement.

Ce module ne dépend ni de PyQt ni de la base de données : il reçoit une liste
de séances (dictionnaires) et la renvoie triée et prête à être affichée.

Une séance est un dictionnaire avec les clés :
    date        : datetime.date
    debut       : datetime.time
    duree       : float (en heures, ex. 1.5 pour 1h30)
    type        : str   ("Cours", "TD", "TP", "TP auto", "ctrl TP", ...)
    salle       : str
    groupe      : str
    enseignant  : str ou None (une séance peut ne pas avoir d'enseignant)

Les séances issues du nettoyage ADE (nettoyage_ade.py) ont à la place de
"groupe" et "enseignant" les listes "groupes" et "enseignants" : les deux
formes sont acceptées (plusieurs valeurs sont affichées séparées par une
virgule).

Auteur : Ndèye Yandé Seck
Créé le : 2026-10-19
Dernière modification : 2026-11-17
"""
from datetime import date, time

COLONNES = ["Date", "Horaire de début", "Durée", "Type", "Salle", "Groupe",
            "Enseignant"]


def _texte(seance, cle_liste, cle_texte):
    """Retourne le groupe ou l'enseignant d'une séance sous forme de texte.

    Utilise la liste ("groupes", "enseignants") si elle existe, sinon le texte
    simple ("groupe", "enseignant"). Une valeur absente donne "".

    :param seance: une séance
    :type seance: dict
    :param cle_liste: "groupes" ou "enseignants"
    :type cle_liste: str
    :param cle_texte: "groupe" ou "enseignant"
    :type cle_texte: str
    :return: texte, valeurs multiples séparées par ", "
    :rtype: str

    Exemple :
        >>> _texte({"groupes": ["A", "B"]}, "groupes", "groupe")
        'A, B'
        >>> _texte({"enseignant": None}, "enseignants", "enseignant")
        ''
    """
    if cle_liste in seance:
        return ", ".join(seance[cle_liste])
    return seance.get(cle_texte) or ""


def seances_fictives():
    """Retourne une liste de séances fictives (volontairement non triée).

    Sert à tester l'affichage avant d'avoir la base de données.

    :return: liste de séances
    :rtype: list[dict]

    Exemple :
        >>> len(seances_fictives()) > 0
        True
    """
    seances = [
        {"date": date(2026, 12, 3), "debut": time(8, 0), "duree": 2.0,
         "type": "TP", "salle": "RT05", "groupe": "RT1-TP3",
         "enseignant": "TREMBLAIS Benoit"},
        {"date": date(2026, 11, 2), "debut": time(9, 0), "duree": 3.0,
         "type": "TP auto", "salle": "RT05", "groupe": "RT1-TP3",
         "enseignant": None},
        {"date": date(2026, 10, 22), "debut": time(13, 0), "duree": 1.0,
         "type": "Cours", "salle": "RT04", "groupe": "RT1",
         "enseignant": "TREMBLAIS Benoit"},
        {"date": date(2026, 11, 2), "debut": time(9, 0), "duree": 3.0,
         "type": "TP auto", "salle": "RT-Projet", "groupe": "RT1-TP2",
         "enseignant": None},
        {"date": date(2026, 11, 12), "debut": time(9, 30), "duree": 1.5,
         "type": "TD", "salle": "RT-I-01", "groupe": "RT1-TD1",
         "enseignant": "TREMBLAIS Benoit"},
        {"date": date(2027, 1, 10), "debut": time(8, 0), "duree": 4.0,
         "type": "ctrl TP", "salle": "RT-I-01", "groupe": "RT1-TP2",
         "enseignant": "TREMBLAIS Benoit"},
    ]
    enseignements = [("R107", "Fondamentaux de la programmation"),
                     ("SAE-15", "Traiter des données")]
    for i, seance in enumerate(seances):
        seance["code"], seance["enseignement"] = enseignements[i % 2]
    return seances


def trier_seances(seances):
    """Classe les séances par ordre chronologique.

    Critères : date, puis heure de début, puis groupe (pour un ordre stable
    quand plusieurs groupes ont cours en même temps). La liste d'origine n'est
    pas modifiée.

    :param seances: liste de séances
    :type seances: list[dict]
    :return: nouvelle liste triée
    :rtype: list[dict]
    :raises KeyError: si une séance n'a pas les clés "date" ou "debut"

    Exemple :
        >>> trier_seances([])
        []
    """
    return sorted(seances, key=lambda s: (s["date"], s["debut"],
                                          _texte(s, "groupes", "groupe")))


def lister_enseignements(seances):
    """Liste les enseignements présents dans les séances (sans doublon).

    Les séances sans clé "code" sont ignorées.

    :param seances: liste de séances
    :type seances: list[dict]
    :return: liste de couples (code, nom) triée par code
    :rtype: list[tuple[str, str]]

    Exemple :
        >>> lister_enseignements([{"code": "R304", "enseignement": "Annuaires"},
        ...                       {"code": "R304", "enseignement": "Annuaires"}])
        [('R304', 'Annuaires')]
        >>> lister_enseignements([])
        []
    """
    trouves = {}
    for seance in seances:
        if seance.get("code"):
            trouves[seance["code"]] = seance.get("enseignement") or ""
    return sorted(trouves.items())


def filtrer_enseignement(seances, code):
    """Garde les séances d'un enseignement.

    :param seances: liste de séances
    :type seances: list[dict]
    :param code: code de l'enseignement ("R304") ou None pour tout garder
    :type code: str | None
    :return: séances de cet enseignement ; liste vide s'il n'y en a pas
    :rtype: list[dict]

    Exemple :
        >>> filtrer_enseignement([{"code": "R304"}, {"code": "R305"}], "R305")
        [{'code': 'R305'}]
        >>> filtrer_enseignement([{"code": "R304"}], None)
        [{'code': 'R304'}]
    """
    if code is None:
        return list(seances)
    return [s for s in seances if s.get("code") == code]


def verifier_periode(date_debut, date_fin):
    """Vérifie qu'une période est valide (début <= fin).

    Une borne à None est acceptée (période ouverte).

    :param date_debut: première date ou None
    :type date_debut: datetime.date | None
    :param date_fin: dernière date ou None
    :type date_fin: datetime.date | None
    :raises ValueError: si date_debut est postérieure à date_fin

    Exemple :
        >>> verifier_periode(date(2026, 1, 1), date(2026, 2, 1))
        >>> verifier_periode(date(2026, 2, 1), date(2026, 1, 1))
        Traceback (most recent call last):
        ...
        ValueError: La date de début est postérieure à la date de fin.
    """
    if date_debut is not None and date_fin is not None \
            and date_debut > date_fin:
        raise ValueError("La date de début est postérieure à la date de fin.")


def filtrer_periode(seances, date_debut=None, date_fin=None):
    """Garde les séances comprises entre deux dates (bornes incluses).

    Une borne à None n'est pas appliquée.

    :param seances: liste de séances
    :type seances: list[dict]
    :param date_debut: première date conservée ou None
    :type date_debut: datetime.date | None
    :param date_fin: dernière date conservée ou None
    :type date_fin: datetime.date | None
    :return: séances de la période
    :rtype: list[dict]

    Exemple :
        >>> filtrer_periode([], date(2026, 1, 1), date(2026, 12, 31))
        []
    """
    resultat = []
    for s in seances:
        if date_debut is not None and s["date"] < date_debut:
            continue
        if date_fin is not None and s["date"] > date_fin:
            continue
        resultat.append(s)
    return resultat


def formater_duree(heures):
    """Convertit une durée en heures décimales en texte "XhYY".

    :param heures: durée en heures (>= 0)
    :type heures: float
    :return: texte, ex. "1h30"
    :rtype: str

    Exemple :
        >>> formater_duree(1.5)
        '1h30'
        >>> formater_duree(3)
        '3h00'
    """
    minutes_totales = round(heures * 60)
    return f"{minutes_totales // 60}h{minutes_totales % 60:02d}"


def formater_ligne(seance):
    """Transforme une séance en liste de 7 textes (une par colonne).

    Une séance sans enseignant (None) donne une cellule vide.

    :param seance: une séance
    :type seance: dict
    :return: [date, début, durée, type, salle, groupe, enseignant]
    :rtype: list[str]

    Exemple :
        >>> formater_ligne({"date": date(2026, 10, 22), "debut": time(13, 0),
        ...     "duree": 1.0, "type": "Cours", "salle": "RT04",
        ...     "groupe": "RT1", "enseignant": None})
        ['22-10-2026', '13h00', '1h00', 'Cours', 'RT04', 'RT1', '']
    """
    return [
        seance["date"].strftime("%d-%m-%Y"),
        seance["debut"].strftime("%Hh%M"),
        formater_duree(seance["duree"]),
        seance["type"],
        seance["salle"],
        _texte(seance, "groupes", "groupe"),
        _texte(seance, "enseignants", "enseignant"),
    ]


def preparer_sequence(seances, date_debut=None, date_fin=None, code=None):
    """Filtre par période, trie et formate les séances pour le tableau.

    :param seances: liste de séances
    :type seances: list[dict]
    :param date_debut: borne basse optionnelle
    :type date_debut: datetime.date | None
    :param date_fin: borne haute optionnelle
    :type date_fin: datetime.date | None
    :param code: code de l'enseignement à garder, None pour tous
    :type code: str | None
    :return: liste de lignes (chacune de 7 textes) ; liste vide si aucune séance
    :rtype: list[list[str]]
    :raises ValueError: si date_debut est postérieure à date_fin

    Exemple :
        >>> preparer_sequence([])
        []
    """
    verifier_periode(date_debut, date_fin)
    retenues = filtrer_periode(filtrer_enseignement(seances, code),
                               date_debut, date_fin)
    return [formater_ligne(s) for s in trier_seances(retenues)]


def seance_vers_json(seance):
    """Convertit une séance en dictionnaire compatible JSON.

    Les messages client/serveur sont en JSON : la date et l'heure de début sont
    donc transmises sous forme de texte ("AAAA-MM-JJ" et "HH:MM"). Les autres
    clés (groupe, groupes, enseignants, code...) sont copiées telles quelles.

    :param seance: une séance (voir l'en-tête du module)
    :type seance: dict
    :return: nouveau dictionnaire ne contenant que des types JSON
    :rtype: dict
    :raises KeyError: si "date" ou "debut" manque

    Exemple :
        >>> s = {"date": date(2026, 10, 22), "debut": time(13, 0),
        ...      "duree": 1.0, "type": "Cours", "salle": "RT04",
        ...      "groupe": "RT1", "enseignant": None}
        >>> seance_vers_json(s)["date"], seance_vers_json(s)["debut"]
        ('2026-10-22', '13:00')
    """
    resultat = dict(seance)
    resultat["date"] = seance["date"].isoformat()
    resultat["debut"] = seance["debut"].strftime("%H:%M")
    return resultat


def seance_depuis_json(donnees):
    """Reconstruit une séance à partir d'un dictionnaire reçu en JSON.

    Opération inverse de :func:`seance_vers_json`.

    :param donnees: dictionnaire reçu du serveur
    :type donnees: dict
    :return: séance avec de vrais objets date et time
    :rtype: dict
    :raises KeyError: si "date" ou "debut" manque
    :raises ValueError: si la date ou l'heure est mal écrite

    Exemple :
        >>> d = {"date": "2026-10-22", "debut": "13:00", "duree": 1.0}
        >>> seance_depuis_json(d)["date"]
        datetime.date(2026, 10, 22)
    """
    resultat = dict(donnees)
    resultat["date"] = date.fromisoformat(donnees["date"])
    resultat["debut"] = time.fromisoformat(donnees["debut"])
    return resultat
