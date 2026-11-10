"""
Registre des commandes du serveur UPplanning.

Protocole : un message JSON par ligne (terminé par '\\n').

Requête :
    {"commande": "seances_vacataire", "params": {"vacataire": "DUPONT", ...}}

Réponse :
    {"statut": "ok", "donnees": ...}
    {"statut": "erreur", "message": "..."}

Pour ajouter une commande (M1, M2, M3), dans votre fichier :

    from dispatcher import commande, ErreurCommande

    @commande("seances_vacataire")
    def seances_vacataire(params, session):
        if "vacataire" not in params:
            raise ErreurCommande("Paramètre 'vacataire' manquant")
        return [...]   # liste, dict... sérialisable en JSON

Puis ajouter l'import de votre fichier à la fin de serveur.py.
"""

import hashlib
import hmac
import os

# ---------------------------------------------------------------------------
# Registre des commandes
# ---------------------------------------------------------------------------

COMMANDES = {}


class ErreurCommande(Exception):
    """Erreur "normale" renvoyée au client avec son message."""


def commande(nom, public=False):
    """
    Décorateur qui enregistre une fonction comme commande du serveur.

    :param nom: nom de la commande utilisé dans la requête JSON
    :param public: True si aucune connexion n'est nécessaire
    """
    def enregistrer(fonction):
        COMMANDES[nom] = {"fonction": fonction, "public": public}
        return fonction
    return enregistrer


# ---------------------------------------------------------------------------
# Rôles et droits (le droit d'une commande = son nom)
# ---------------------------------------------------------------------------

# >>> POUR M1, M2, M3 : si vous créez une NOUVELLE commande, ajoutez son nom
# >>> dans les rôles autorisés ci-dessous (sinon elle sera "Accès refusé").
# >>> Exemple : pour autoriser la secrétaire à utiliser "ma_commande",
# >>> écrire  "secretaire": {"seances_vacataire", "ma_commande"},
# >>> Le chef de département a accès à toutes les commandes : ne pas l'oublier.
DROITS_PAR_ROLE = {
    "secretaire": {"seances_vacataire"},
    "directeur_etudes": {"service_enseignant", "bilan_formation",
                         "controles_a_venir"},
    "enseignant": {"sequence_enseignement", "service_enseignant"},
    "responsable_apprentissage": {"enseignements_apprentis"},
    "chef_departement": {"seances_vacataire", "controles_a_venir",
                         "sequence_enseignement", "service_enseignant",
                         "bilan_formation", "enseignements_apprentis"},
    "administration": {"gestion_comptes"},
}


def droits_des_roles(roles):
    """Retourne l'ensemble des droits cumulés d'une liste de rôles."""
    droits = set()
    for role in roles:
        droits |= DROITS_PAR_ROLE.get(role, set())
    return droits


# ---------------------------------------------------------------------------
# Mots de passe (hachage salé)
# ---------------------------------------------------------------------------

def hacher_mot_de_passe(mot_de_passe, sel=None):
    """Retourne (sel, hachage) en hexadécimal (PBKDF2-SHA256)."""
    if sel is None:
        sel = os.urandom(16)
    else:
        sel = bytes.fromhex(sel)
    hache = hashlib.pbkdf2_hmac("sha256", mot_de_passe.encode("utf-8"),
                                sel, 200_000)
    return sel.hex(), hache.hex()


def verifier_mot_de_passe(mot_de_passe, sel, hache_attendu):
    """Vérifie un mot de passe contre le hachage stocké."""
    _, hache = hacher_mot_de_passe(mot_de_passe, sel)
    return hmac.compare_digest(hache, hache_attendu)


# ---------------------------------------------------------------------------
# Comptes de test en mémoire
# À REMPLACER par une requête SQL quand la base sera prête
# (voir chercher_compte).
# ---------------------------------------------------------------------------

def _compte_test(roles, mot_de_passe):
    sel, hache = hacher_mot_de_passe(mot_de_passe)
    return {"roles": roles, "sel": sel, "hache": hache}


COMPTES_TEST = {
    "chef": _compte_test(["chef_departement", "enseignant"], "chef123"),
    "secretaire": _compte_test(["secretaire"], "secret123"),
    "admin": _compte_test(["administration"], "admin123"),
}


def chercher_compte(identifiant):
    """Retourne le compte (dict) ou None. Remplaçable par du SQL."""
    return COMPTES_TEST.get(identifiant)


# ---------------------------------------------------------------------------
# MODÈLE DE COMMANDE (à copier dans VOTRE fichier requetes_mX.py, pas ici)
#
# from dispatcher import commande, ErreurCommande
#
# @commande("seances_vacataire")          # nom envoyé par le client
# def seances_vacataire(params, session):
#     # params  = dict envoyé par le client, ex. {"vacataire": "DUPONT",
#     #           "date_debut": "2026-01-01", "date_fin": "2026-03-20"}
#     # session = infos de l'utilisateur connecté (identifiant, roles, droits)
#     if "vacataire" not in params:
#         raise ErreurCommande("Paramètre 'vacataire' manquant")
#
#     # 1. appeler votre requête SQL / votre traitement Python ici
#     # 2. retourner le résultat (liste, dict... convertible en JSON)
#     return [{"date": "2026-01-12", "debut": "13h00", "duree": "3h00"}]
#
# Le serveur vérifie tout seul que l'utilisateur est connecté et a le droit
# (voir DROITS_PAR_ROLE) AVANT d'appeler votre fonction : inutile de le refaire.
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Commandes de base
# ---------------------------------------------------------------------------

@commande("ping", public=True)
def ping(params, session):
    """Test de la communication."""
    return "pong"


@commande("connexion", public=True)
def connexion(params, session):
    """
    Authentifie l'utilisateur et remplit la session de la connexion.

    Paramètres : identifiant, mot_de_passe
    Retourne : identifiant, roles, droits (pour la navigation du client)
    """
    identifiant = params.get("identifiant", "")
    mot_de_passe = params.get("mot_de_passe", "")
    compte = chercher_compte(identifiant)

    # Même message dans les deux cas pour ne pas révéler les identifiants
    if compte is None or not verifier_mot_de_passe(
            mot_de_passe, compte["sel"], compte["hache"]):
        raise ErreurCommande("Identifiant ou mot de passe incorrect")

    session["identifiant"] = identifiant
    session["roles"] = compte["roles"]
    session["droits"] = droits_des_roles(compte["roles"])

    return {"identifiant": identifiant,
            "roles": compte["roles"],
            "droits": sorted(session["droits"])}


@commande("deconnexion")
def deconnexion(params, session):
    """Vide la session de la connexion."""
    session.clear()
    return "déconnecté"


# ---------------------------------------------------------------------------
# Traitement d'une requête
# ---------------------------------------------------------------------------

def traiter_requete(requete, session):
    """
    Vérifie la requête et les droits, exécute la commande.

    :param requete: dict déjà décodé depuis le JSON
    :param session: dict propre à la connexion du client
    :return: dict de réponse
    """
    if not isinstance(requete, dict) or "commande" not in requete:
        return {"statut": "erreur", "message": "Requête invalide"}

    nom = requete["commande"]
    params = requete.get("params", {})
    if nom not in COMMANDES:
        return {"statut": "erreur", "message": f"Commande inconnue : {nom}"}
    if not isinstance(params, dict):
        return {"statut": "erreur", "message": "'params' doit être un objet"}

    infos = COMMANDES[nom]

    if not infos["public"]:
        if "identifiant" not in session:
            return {"statut": "erreur", "message": "Connexion requise"}
        # Cette vérification est faite côté serveur, jamais seulement côté client
        if nom != "deconnexion" and nom not in session["droits"]:
            return {"statut": "erreur", "message": "Accès refusé"}

    try:
        donnees = infos["fonction"](params, session)
        return {"statut": "ok", "donnees": donnees}
    except ErreurCommande as erreur:
        return {"statut": "erreur", "message": str(erreur)}
    except Exception as erreur:  # bug interne : ne pas faire tomber le serveur
        print(f"[ERREUR] commande {nom} : {erreur!r}")
        return {"statut": "erreur", "message": "Erreur interne du serveur"}
