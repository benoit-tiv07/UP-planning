"""Nettoyage des événements bruts ADE : transforme chaque événement en séance.

L'extraction (extraire_evenements) renvoie des dictionnaires dont les valeurs
sont du texte brut. Ce module les transforme en séances exploitables par le
reste de l'application.

Exemple d'événement brut :
    {"DTSTART": "20261102T130000Z", "DTEND": "20261102T160000Z",
     "SUMMARY": "R304 Services d'annuaires TP", "LOCATION": "RT28 [I04]",
     "DESCRIPTION": "\\n\\nRT2 TP1 FA S3\\nCOIRAULT PATRICK\\n\\n(Updated ...)",
     "UID": "ADE6032..."}

Séance obtenue (clés) :
    uid          : str, identifiant ADE unique de la séance
    date         : datetime.date (heure de Paris)
    debut        : datetime.time (heure de Paris)
    duree        : float, en heures (1.5 pour 1h30)
    type         : "Cours", "TD", "TP", "TP auto", "ctrl cours" ou "ctrl TP"
    salle        : str, sans le bâtiment ("RT28")
    groupes      : list[str], peut contenir plusieurs groupes
    enseignants  : list[str], peut être vide ou contenir plusieurs noms
    code         : str, code de l'enseignement ("R304", "SAE301", "R-ROM316")
    enseignement : str, nom de l'enseignement
    formation    : "BUT1", "BUT2", "BUT3" ou None si le groupe est inconnu

Auteur : Ndèye Yandé Seck
Créé le : 2026-11-17
Dernière modification : 2026-11-17
"""
import re
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

FUSEAU = ZoneInfo("Europe/Paris")
TYPES_NORMALISES = ("Cours", "TD", "TP", "TP auto", "ctrl cours", "ctrl TP")

_RE_TITRE = re.compile(
    r"^(?P<code>(?:SAE|R)\s*(?:ROM\s*)?\d+)\s+(?P<nom>.+?)\s+"
    r"(?P<type>CM|TD|TP\s+auto(?:nomie)?|TP|ctrl)$", re.IGNORECASE)
_RE_CODE = re.compile(r"^(SAE|R)\s*(ROM)?\s*(\d+)$", re.IGNORECASE)


def decoder_texte(valeur):
    """Décode les échappements d'une valeur texte iCalendar.

    Dans un fichier .ics, un saut de ligne est écrit "\\n" (deux caractères) et
    une virgule, un point-virgule ou un antislash sont précédés d'un antislash.

    :param valeur: texte brut
    :type valeur: str
    :return: texte décodé
    :rtype: str

    Exemple :
        >>> decoder_texte("a\\\\nb\\\\, c")
        'a\\nb, c'
    """
    return re.sub(r"\\(.)",
                  lambda m: "\n" if m.group(1) in "nN" else m.group(1),
                  valeur)


def lire_date_heure(valeur):
    """Convertit une date iCalendar en datetime à l'heure de Paris.

    Formats acceptés : "20261102T130000Z" (UTC) et "20261102T130000" (heure
    locale).

    :param valeur: date iCalendar
    :type valeur: str
    :return: date et heure à Paris
    :rtype: datetime.datetime
    :raises ValueError: si le format n'est pas reconnu

    Exemple :
        >>> lire_date_heure("20261102T130000Z").strftime("%d-%m-%Y %Hh%M")
        '02-11-2026 14h00'
    """
    try:
        if valeur.endswith("Z"):
            instant = datetime.strptime(valeur, "%Y%m%dT%H%M%SZ")
            return instant.replace(tzinfo=timezone.utc).astimezone(FUSEAU)
        return datetime.strptime(valeur, "%Y%m%dT%H%M%S").replace(
            tzinfo=FUSEAU)
    except ValueError:
        raise ValueError(f"Date non reconnue : {valeur!r}") from None


def normaliser_code(brut):
    """Met le code d'un enseignement sous une forme unique, sans espace.

    :param brut: code tel qu'il apparaît dans le titre ("R ROM316", "SAE 301")
    :type brut: str
    :return: code normalisé ("R-ROM316", "SAE301")
    :rtype: str
    :raises ValueError: si le code n'est pas reconnu

    Exemple :
        >>> normaliser_code("SAE  ROM 303"), normaliser_code("R304")
        ('SAE-ROM303', 'R304')
    """
    m = _RE_CODE.match(" ".join(brut.split()))
    if not m:
        raise ValueError(f"Code d'enseignement non reconnu : {brut!r}")
    prefixe, rom, numero = m.groups()
    return prefixe.upper() + ("-ROM" if rom else "") + numero


def normaliser_type(type_brut, groupes):
    """Convertit le type lu dans le titre en l'un des TYPES_NORMALISES.

    Le titre ne précise pas si un contrôle est de cours ou de TP : on le
    déduit des groupes (un groupe TPx donne "ctrl TP", sinon "ctrl cours").

    :param type_brut: "CM", "TD", "TP", "TP auto", "TP autonomie" ou "ctrl"
    :type type_brut: str
    :param groupes: groupes de la séance
    :type groupes: list[str]
    :return: type normalisé
    :rtype: str
    :raises ValueError: si le type n'est pas reconnu

    Exemple :
        >>> normaliser_type("CM", []), normaliser_type("TP autonomie", [])
        ('Cours', 'TP auto')
        >>> normaliser_type("ctrl", ["RT2 promo S3"])
        'ctrl cours'
    """
    t = " ".join(type_brut.split()).lower()
    if t == "cm":
        return "Cours"
    if t == "td":
        return "TD"
    if t == "tp":
        return "TP"
    if t.startswith("tp auto"):
        return "TP auto"
    if t == "ctrl":
        if any(re.search(r"\bTP\d", g) for g in groupes):
            return "ctrl TP"
        return "ctrl cours"
    raise ValueError(f"Type de séance non reconnu : {type_brut!r}")


def analyser_description(valeur):
    """Sépare groupes et enseignants dans la description d'un événement.

    Les lignes contenant un chiffre sont des groupes ("RT2 TP1 FA S3"), les
    autres sont des enseignants ; la ligne "(Updated ...)" est ignorée. Les
    noms sont conservés tels qu'écrits dans ADE.

    :param valeur: description brute
    :type valeur: str
    :return: (groupes, enseignants), sans doublons, dans l'ordre d'apparition
    :rtype: tuple[list[str], list[str]]

    Exemple :
        >>> analyser_description("\\\\n\\\\nRT2 TD1 FA S3\\\\nREY LAURENT\\\\n\\\\n(Updated :1)")
        (['RT2 TD1 FA S3'], ['REY LAURENT'])
    """
    groupes, enseignants = [], []
    for ligne in decoder_texte(valeur).splitlines():
        ligne = " ".join(ligne.split())
        if not ligne or ligne.startswith("(Updated"):
            continue
        liste = groupes if re.search(r"\d", ligne) else enseignants
        if ligne not in liste:
            liste.append(ligne)
    return groupes, enseignants


def deduire_formation(groupes):
    """Déduit la formation (BUT1, BUT2, BUT3) du premier groupe "RTn ...".

    :param groupes: groupes de la séance
    :type groupes: list[str]
    :return: "BUT1", "BUT2", "BUT3" ou None
    :rtype: str | None

    Exemple :
        >>> deduire_formation(["RT2 TP1 FA S3"]), deduire_formation([])
        ('BUT2', None)
    """
    for groupe in groupes:
        m = re.match(r"^RT([123])\b", groupe)
        if m:
            return f"BUT{m.group(1)}"
    return None


def nettoyer_evenement(evenement):
    """Transforme un événement brut ADE en séance (voir l'en-tête du module).

    :param evenement: dictionnaire issu de extraire_evenements
    :type evenement: dict
    :return: séance
    :rtype: dict
    :raises ValueError: si une propriété manque, si la date est invalide, si
        la durée n'est pas positive ou si le titre n'est pas celui d'un
        enseignement (par exemple "Evaluation des enseignements S3")

    Exemple :
        >>> s = nettoyer_evenement({"UID": "1", "DTSTART": "20261102T130000Z",
        ...     "DTEND": "20261102T160000Z", "SUMMARY": "R304 Annuaires TP",
        ...     "LOCATION": "RT28 [I04]", "DESCRIPTION": ""})
        >>> s["type"], s["salle"], s["duree"], s["enseignants"]
        ('TP', 'RT28', 3.0, [])
    """
    for cle in ("UID", "DTSTART", "DTEND", "SUMMARY"):
        if cle not in evenement:
            raise ValueError(f"Propriété manquante : {cle}")
    debut = lire_date_heure(evenement["DTSTART"])
    fin = lire_date_heure(evenement["DTEND"])
    if fin <= debut:
        raise ValueError("Durée nulle ou négative.")

    titre = " ".join(decoder_texte(evenement["SUMMARY"]).split())
    m = _RE_TITRE.match(titre)
    if not m:
        raise ValueError(f"Titre hors enseignement : {titre!r}")

    groupes, enseignants = analyser_description(
        evenement.get("DESCRIPTION", ""))
    salle = re.sub(r"\s*\[.*?\]\s*$", "", evenement.get("LOCATION", "")).strip()

    return {
        "uid": evenement["UID"],
        "date": debut.date(),
        "debut": debut.time(),
        "duree": (fin - debut).total_seconds() / 3600,
        "type": normaliser_type(m.group("type"), groupes),
        "salle": salle,
        "groupes": groupes,
        "enseignants": enseignants,
        "code": normaliser_code(m.group("code")),
        "enseignement": m.group("nom"),
        "formation": deduire_formation(groupes),
    }


def nettoyer_evenements(evenements):
    """Nettoie une liste d'événements bruts.

    Les événements inutilisables (hors enseignement, données invalides) et les
    doublons d'UID ne font pas planter le traitement : ils sont renvoyés à
    part avec la raison du rejet.

    :param evenements: liste de dictionnaires bruts
    :type evenements: list[dict]
    :return: (séances, rejets) ; rejets est une liste de (événement, raison)
    :rtype: tuple[list[dict], list[tuple[dict, str]]]

    Exemple :
        >>> nettoyer_evenements([])
        ([], [])
    """
    seances, rejets, vus = [], [], set()
    for evenement in evenements:
        try:
            seance = nettoyer_evenement(evenement)
        except ValueError as erreur:
            rejets.append((evenement, str(erreur)))
            continue
        if seance["uid"] in vus:
            rejets.append((evenement, "Doublon (même UID)."))
            continue
        vus.add(seance["uid"])
        seances.append(seance)
    return seances, rejets
