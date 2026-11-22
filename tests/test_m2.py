"""Tests unitaires du module M2 (traitements_m2)."""
import json
import os
from datetime import date, time

import pytest

from nomprojet.traitements_m2 import (filtrer_enseignement, filtrer_periode,
                                      formater_duree, formater_ligne,
                                      lister_enseignements, preparer_sequence,
                                      seance_depuis_json, seance_vers_json,
                                      seances_fictives, trier_seances,
                                      verifier_periode)


def _seance(d, h, groupe="RT1", enseignant="X"):
    return {"date": d, "debut": h, "duree": 1.0, "type": "TD",
            "salle": "RT04", "groupe": groupe, "enseignant": enseignant}


def test_tri_chronologique():
    resultat = trier_seances(seances_fictives())
    cles = [(s["date"], s["debut"]) for s in resultat]
    assert cles == sorted(cles)


def test_tri_ne_modifie_pas_la_liste_origine():
    seances = seances_fictives()
    copie = list(seances)
    trier_seances(seances)
    assert seances == copie


def test_tri_meme_jour_par_heure():
    a = _seance(date(2026, 11, 2), time(13, 0))
    b = _seance(date(2026, 11, 2), time(9, 0))
    assert trier_seances([a, b]) == [b, a]


def test_filtre_periode_bornes_incluses():
    s1 = _seance(date(2026, 11, 1), time(8, 0))
    s2 = _seance(date(2026, 11, 15), time(8, 0))
    s3 = _seance(date(2026, 12, 1), time(8, 0))
    res = filtrer_periode([s1, s2, s3], date(2026, 11, 1), date(2026, 11, 15))
    assert res == [s1, s2]


def test_filtre_sans_bornes_garde_tout():
    seances = seances_fictives()
    assert filtrer_periode(seances) == seances


def test_resultat_vide():
    assert preparer_sequence([]) == []
    hors = preparer_sequence(seances_fictives(), date(2030, 1, 1),
                             date(2030, 12, 31))
    assert hors == []


def test_seance_sans_enseignant():
    ligne = formater_ligne(_seance(date(2026, 11, 2), time(9, 0),
                                   enseignant=None))
    assert ligne[6] == ""
    assert len(ligne) == 7


def test_formater_duree():
    assert formater_duree(1.5) == "1h30"
    assert formater_duree(3) == "3h00"
    assert formater_duree(0.25) == "0h15"


def test_format_date_et_heure():
    ligne = formater_ligne(_seance(date(2026, 10, 22), time(13, 0)))
    assert ligne[0] == "22-10-2026"
    assert ligne[1] == "13h00"


def test_periode_invalide():
    with pytest.raises(ValueError):
        verifier_periode(date(2026, 12, 1), date(2026, 11, 1))
    with pytest.raises(ValueError):
        preparer_sequence(seances_fictives(), date(2026, 12, 1),
                          date(2026, 11, 1))


def test_periode_valide_ou_ouverte():
    verifier_periode(date(2026, 11, 1), date(2026, 11, 1))
    verifier_periode(None, date(2026, 11, 1))
    verifier_periode(None, None)


def test_json_aller_retour():
    for s in seances_fictives():
        texte = json.dumps(seance_vers_json(s))
        assert seance_depuis_json(json.loads(texte)) == s


def test_json_seance_sans_enseignant():
    s = _seance(date(2026, 11, 2), time(9, 0), enseignant=None)
    assert seance_vers_json(s)["enseignant"] is None


# ---- Tests de l'écran PyQt (sans affichage réel) ----

@pytest.fixture(scope="module")
def app():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    pytest.importorskip("PyQt6.QtWidgets")
    from PyQt6.QtWidgets import QApplication
    return QApplication.instance() or QApplication([])


def test_vue_sans_filtre(app):
    from nomprojet.vue_sequences import VueSequences
    v = VueSequences()
    v.afficher()
    assert v.tableau.rowCount() == len(seances_fictives())
    assert v.tableau.item(0, 0).text() == "22-10-2026"


def test_vue_avec_filtre(app):
    from PyQt6.QtCore import QDate
    from nomprojet.vue_sequences import VueSequences
    v = VueSequences()
    v.case_periode.setChecked(True)
    v.date_debut.setDate(QDate(2026, 11, 1))
    v.date_fin.setDate(QDate(2026, 11, 30))
    v.afficher()
    assert v.tableau.rowCount() == 3


def test_vue_aucun_resultat_et_periode_invalide(app):
    from PyQt6.QtCore import QDate
    from nomprojet.vue_sequences import VueSequences
    v = VueSequences()
    v.case_periode.setChecked(True)
    v.date_debut.setDate(QDate(2030, 1, 1))
    v.date_fin.setDate(QDate(2030, 12, 31))
    v.afficher()
    assert v.tableau.rowCount() == 0
    assert "Aucune séance" in v.message.text()
    v.date_debut.setDate(QDate(2030, 12, 31))
    v.date_fin.setDate(QDate(2030, 1, 1))
    v.afficher()
    assert v.tableau.rowCount() == 0
    assert "postérieure" in v.message.text()


def test_lister_enseignements():
    assert lister_enseignements(seances_fictives()) == [
        ("R107", "Fondamentaux de la programmation"),
        ("SAE-15", "Traiter des données")]
    assert lister_enseignements([]) == []
    assert lister_enseignements([_seance(date(2026, 11, 2), time(9, 0))]) == []


def test_filtrer_enseignement():
    seances = seances_fictives()
    r107 = filtrer_enseignement(seances, "R107")
    assert r107 and all(s["code"] == "R107" for s in r107)
    assert len(filtrer_enseignement(seances, None)) == len(seances)
    assert filtrer_enseignement(seances, "R999") == []


def test_sequence_filtree_par_enseignement():
    seances = seances_fictives()
    lignes = preparer_sequence(seances, code="SAE-15")
    assert len(lignes) == len(filtrer_enseignement(seances, "SAE-15"))
    assert preparer_sequence(seances, code="R999") == []


def test_vue_filtre_par_enseignement(app):
    from nomprojet.vue_sequences import VueSequences
    v = VueSequences()
    assert v.combo_ressource.itemText(0) == "Tous les enseignements"
    v.combo_ressource.setCurrentIndex(v.combo_ressource.findData("R107"))
    v.afficher()
    assert v.tableau.rowCount() == len(
        filtrer_enseignement(seances_fictives(), "R107"))


def test_vue_avec_des_seances_fournies(app):
    from nomprojet.vue_sequences import VueSequences
    seances = [dict(_seance(date(2026, 11, 2), time(9, 0)), code="R304",
                    enseignement="Services d'annuaires"),
               dict(_seance(date(2026, 11, 3), time(9, 0)), code="R305",
                    enseignement="Transmissions")]
    v = VueSequences(seances)
    assert [v.combo_ressource.itemText(i)
            for i in range(v.combo_ressource.count())] == [
        "Tous les enseignements", "R304 - Services d'annuaires",
        "R305 - Transmissions"]
    v.combo_ressource.setCurrentIndex(v.combo_ressource.findData("R305"))
    v.afficher()
    assert v.tableau.rowCount() == 1
    assert v.tableau.item(0, 0).text() == "03-11-2026"
