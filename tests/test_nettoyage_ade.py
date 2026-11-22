"""Tests unitaires du module nettoyage_ade (événements bruts de ADECal.ics)."""
import json
from datetime import date, time

import pytest

from nomprojet.nettoyage_ade import (analyser_description, decoder_texte,
                                     deduire_formation, lire_date_heure,
                                     nettoyer_evenement, nettoyer_evenements,
                                     normaliser_code, normaliser_type)
from nomprojet.traitements_m2 import (preparer_sequence, seance_depuis_json,
                                      seance_vers_json)


def _brut(**changements):
    """Événement brut de référence (copié de ADECal.ics), modifiable."""
    evenement = {
        "UID": "ADE1", "DTSTAMP": "20261104T090451Z",
        "DTSTART": "20261102T130000Z", "DTEND": "20261102T160000Z",
        "SUMMARY": "R304 Services d'annuaires TP", "LOCATION": "RT28 [I04]",
        "DESCRIPTION": "\\n\\nRT2 TP1 FA S3\\nCOIRAULT PATRICK\\n\\n"
                       "(Updated :08/07/2026 18:12)",
    }
    evenement.update(changements)
    return evenement


def test_decoder_texte():
    assert decoder_texte("a\\nb\\, c\\;d\\\\e") == "a\nb, c;d\\e"


def test_date_utc_heure_hiver():
    d = lire_date_heure("20261102T130000Z")
    assert (d.date(), d.time()) == (date(2026, 11, 2), time(14, 0))


def test_date_utc_heure_ete():
    assert lire_date_heure("20260702T130000Z").time() == time(15, 0)


def test_date_locale_et_invalide():
    assert lire_date_heure("20261102T130000").time() == time(13, 0)
    with pytest.raises(ValueError):
        lire_date_heure("2 novembre")


def test_normaliser_code():
    assert normaliser_code("R304") == "R304"
    assert normaliser_code("R ROM316") == "R-ROM316"
    assert normaliser_code("SAE  ROM 303") == "SAE-ROM303"
    assert normaliser_code("SAE 301") == "SAE301"
    with pytest.raises(ValueError):
        normaliser_code("XYZ")


def test_normaliser_type():
    assert normaliser_type("CM", []) == "Cours"
    assert normaliser_type("TD", []) == "TD"
    assert normaliser_type("TP", []) == "TP"
    assert normaliser_type("TP autonomie", []) == "TP auto"
    assert normaliser_type("TP auto", []) == "TP auto"
    with pytest.raises(ValueError):
        normaliser_type("???", [])


def test_controle_cours_ou_tp_selon_groupe():
    assert normaliser_type("ctrl", ["RT2 promo S3"]) == "ctrl cours"
    assert normaliser_type("ctrl", ["RT2 TD1 FI-FA S3"]) == "ctrl cours"
    assert normaliser_type("ctrl", ["RT2 TP3 FI S3"]) == "ctrl TP"


def test_description_un_groupe_un_enseignant():
    d = _brut()["DESCRIPTION"]
    assert analyser_description(d) == (["RT2 TP1 FA S3"], ["COIRAULT PATRICK"])


def test_description_sans_enseignant():
    d = "\\n\\nRT2 TP1 FA S3\\n\\n(Updated :06/07/2026 11:14)"
    assert analyser_description(d) == (["RT2 TP1 FA S3"], [])


def test_description_plusieurs_groupes_et_enseignants():
    d = ("\\n\\nRT2 TP2 FI S3\\nRT2 TP3 FI S3\\nCAMARDA FLORENT\\n"
         "COUDERC TURQ SEBASTIEN\\nTREMBLAIS BENOIT\\n\\n(Updated :03/07)")
    groupes, enseignants = analyser_description(d)
    assert groupes == ["RT2 TP2 FI S3", "RT2 TP3 FI S3"]
    assert enseignants == ["CAMARDA FLORENT", "COUDERC TURQ SEBASTIEN",
                           "TREMBLAIS BENOIT"]


def test_formation():
    assert deduire_formation(["RT2 promo S3"]) == "BUT2"
    assert deduire_formation(["RT1 TD1"]) == "BUT1"
    assert deduire_formation([]) is None
    assert deduire_formation(["LP ARM"]) is None


def test_nettoyer_evenement_complet():
    s = nettoyer_evenement(_brut())
    assert s == {
        "uid": "ADE1", "date": date(2026, 11, 2), "debut": time(14, 0),
        "duree": 3.0, "type": "TP", "salle": "RT28",
        "groupes": ["RT2 TP1 FA S3"], "enseignants": ["COIRAULT PATRICK"],
        "code": "R304", "enseignement": "Services d'annuaires",
        "formation": "BUT2"}


def test_titre_avec_espaces_multiples_et_rom():
    s = nettoyer_evenement(_brut(
        SUMMARY="SAE ROM 304 Déployer un  service de téléphonie multi-sites TP"))
    assert s["code"] == "SAE-ROM304"
    assert s["enseignement"] == "Déployer un service de téléphonie multi-sites"


def test_duree_une_heure_trente():
    s = nettoyer_evenement(_brut(DTEND="20261102T143000Z"))
    assert s["duree"] == 1.5


def test_evenement_hors_enseignement_rejete():
    with pytest.raises(ValueError):
        nettoyer_evenement(_brut(SUMMARY="Evaluation des enseignements S3"))


def test_proprietes_manquantes_et_duree_invalide():
    brut = _brut()
    del brut["DTSTART"]
    with pytest.raises(ValueError):
        nettoyer_evenement(brut)
    with pytest.raises(ValueError):
        nettoyer_evenement(_brut(DTEND="20261102T120000Z"))


def test_localisation_absente():
    brut = _brut()
    del brut["LOCATION"]
    assert nettoyer_evenement(brut)["salle"] == ""


def test_nettoyer_evenements_rejets_et_doublons():
    evenements = [_brut(), _brut(),
                  _brut(UID="ADE2", SUMMARY="Evaluation des enseignements S3"),
                  _brut(UID="ADE3")]
    seances, rejets = nettoyer_evenements(evenements)
    assert [s["uid"] for s in seances] == ["ADE1", "ADE3"]
    assert len(rejets) == 2
    assert "Doublon" in rejets[0][1]
    assert "hors enseignement" in rejets[1][1]


def test_liste_vide():
    assert nettoyer_evenements([]) == ([], [])


def test_compatible_avec_affichage_m2_et_json():
    seances, _ = nettoyer_evenements([_brut(
        DESCRIPTION="\\n\\nRT2 TP2 FI S3\\nRT2 TP3 FI S3\\nREY LAURENT\\n"
                    "TREMBLAIS BENOIT\\n\\n(Updated :1)")])
    ligne = preparer_sequence(seances)[0]
    assert ligne[5] == "RT2 TP2 FI S3, RT2 TP3 FI S3"
    assert ligne[6] == "REY LAURENT, TREMBLAIS BENOIT"
    texte = json.dumps(seance_vers_json(seances[0]))
    assert seance_depuis_json(json.loads(texte)) == seances[0]
