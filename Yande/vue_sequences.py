"""Vue PyQt : affichage de la séquence d'un enseignement.

Lancement depuis la racine du dépôt :
    python3 -m nomprojet.vue_sequences              (séances fictives)
    python3 -m nomprojet.vue_sequences ADECal.ics   (vraies séances ADE ; le
        fichier extraction_ade.py doit se trouver dans le dossier courant)

Auteur : Ndèye Yandé Seck
Créé le : 2026-10-19
Dernière modification : 2026-11-18
"""
import sys

from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import (QAbstractItemView, QApplication, QCheckBox,
                             QComboBox, QDateEdit, QHBoxLayout, QHeaderView,
                             QLabel, QPushButton, QTableWidget,
                             QTableWidgetItem, QVBoxLayout, QWidget)

from nomprojet.traitements_m2 import (COLONNES, lister_enseignements,
                                      preparer_sequence, seances_fictives)


class VueSequences(QWidget):
    """Écran « Séquence d'un enseignement » (formulaire en haut, tableau en bas).

    Auteur : Ndèye Yandé Seck
    Créé le : 2026-10-19 ; dernière modification : 2026-11-17

    Exemple :
        >>> app = QApplication([])          # doctest: +SKIP
        >>> VueSequences().show()           # doctest: +SKIP
    """

    def __init__(self, seances=None):
        """Crée les widgets : choix de l'enseignement, période, tableau.

        :param seances: séances à afficher ; si None, séances fictives
            (plus tard : réponse du serveur)
        :type seances: list[dict] | None

        Exemple :
            >>> VueSequences()              # doctest: +SKIP
        """
        super().__init__()
        self.seances = seances if seances is not None else seances_fictives()
        self.setWindowTitle("Séquence d'enseignement")
        self.resize(900, 500)

        self.combo_ressource = QComboBox()
        self.combo_ressource.addItem("Tous les enseignements", None)
        for code, nom in lister_enseignements(self.seances):
            self.combo_ressource.addItem(f"{code} - {nom}", code)

        self.case_periode = QCheckBox("Filtrer par période")
        self.date_debut = QDateEdit(QDate(2026, 9, 1))
        self.date_fin = QDateEdit(QDate(2027, 1, 31))
        for d in (self.date_debut, self.date_fin):
            d.setCalendarPopup(True)
            d.setDisplayFormat("dd-MM-yyyy")
            d.setEnabled(False)
        self.case_periode.toggled.connect(self.date_debut.setEnabled)
        self.case_periode.toggled.connect(self.date_fin.setEnabled)

        self.bouton = QPushButton("Afficher")
        self.bouton.clicked.connect(self.afficher)

        self.message = QLabel("")

        self.tableau = QTableWidget(0, len(COLONNES))
        self.tableau.setHorizontalHeaderLabels(COLONNES)
        self.tableau.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tableau.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)

        haut = QHBoxLayout()
        haut.addWidget(QLabel("Enseignement :"))
        haut.addWidget(self.combo_ressource, 1)
        haut.addWidget(self.case_periode)
        haut.addWidget(self.date_debut)
        haut.addWidget(QLabel("au"))
        haut.addWidget(self.date_fin)
        haut.addWidget(self.bouton)

        principal = QVBoxLayout(self)
        principal.addLayout(haut)
        principal.addWidget(self.message)
        principal.addWidget(self.tableau)

    def afficher(self):
        """Récupère les séances, les prépare et remplit le tableau.

        Si la période est invalide (début après fin), un message d'erreur
        est affiché et le tableau est vidé.

        Exemple :
            >>> VueSequences().afficher()   # doctest: +SKIP
        """
        debut = fin = None
        if self.case_periode.isChecked():
            debut = self.date_debut.date().toPyDate()
            fin = self.date_fin.date().toPyDate()

        code = self.combo_ressource.currentData()

        # Plus tard : envoyer la requête au serveur au lieu de self.seances.
        try:
            lignes = preparer_sequence(self.seances, debut, fin, code)
        except ValueError as erreur:
            self.remplir_tableau([])
            self.message.setText(str(erreur))
            return
        self.remplir_tableau(lignes)

    def remplir_tableau(self, lignes):
        """Affiche les lignes dans le tableau.

        :param lignes: liste de lignes de 7 textes ; liste vide possible
        :type lignes: list[list[str]]

        Exemple :
            >>> VueSequences().remplir_tableau([])   # doctest: +SKIP
        """
        self.tableau.setRowCount(len(lignes))
        for i, ligne in enumerate(lignes):
            for j, texte in enumerate(ligne):
                self.tableau.setItem(i, j, QTableWidgetItem(texte))
        self.message.setText("" if lignes else "Aucune séance trouvée.")


def charger_seances_ade(chemin):
    """Lit un fichier .ics ADE et retourne les séances nettoyées.

    Utilisé pour tester l'écran avec de vraies données.

    :param chemin: chemin du fichier .ics
    :type chemin: str
    :return: séances nettoyées
    :rtype: list[dict]
    :raises ImportError: si extraction_ade.py n'est pas dans le dossier courant
    :raises OSError: si le fichier est introuvable
    :raises ValueError: si le fichier est mal formé

    Exemple :
        >>> charger_seances_ade("ADECal.ics")   # doctest: +SKIP
    """
    from extraction_ade import extraire_evenements
    from nomprojet.nettoyage_ade import nettoyer_evenements
    seances, _ = nettoyer_evenements(extraire_evenements(chemin))
    return seances


def main():
    """Point d'entrée : ouvre la fenêtre (avec un .ics en argument, optionnel).

    Exemple :
        >>> main()                          # doctest: +SKIP
    """
    seances = None
    if len(sys.argv) > 1:
        try:
            seances = charger_seances_ade(sys.argv[1])
        except (ImportError, OSError, ValueError) as erreur:
            print(f"Chargement impossible : {erreur}")
            return 1
    app = QApplication(sys.argv[:1])
    fenetre = VueSequences(seances)
    fenetre.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
