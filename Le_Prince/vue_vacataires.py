"""Interface Le Prince en attente des données fournies par le serveur."""

import sys
from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import (
    QApplication, QComboBox, QDateEdit, QFormLayout, QHeaderView,
    QLabel, QPushButton, QTableWidget, QVBoxLayout, QWidget, QAbstractItemView,
)


class VueVacataires(QWidget):
    """Affiche les critères et un tableau vide, sans lire le fichier ADE."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("UPplanning — Le Prince — Séances d'un vacataire")
        self.resize(1000, 420)
        disposition = QVBoxLayout(self)
        formulaire = QFormLayout()
        self.vacataire = QComboBox()
        self.vacataire.setEnabled(False)
        self.date_debut = QDateEdit(QDate.currentDate())
        self.date_fin = QDateEdit(QDate.currentDate())
        for champ in (self.date_debut, self.date_fin):
            champ.setDisplayFormat("dd/MM/yyyy")
            champ.setCalendarPopup(True)
        formulaire.addRow("Vacataire :", self.vacataire)
        formulaire.addRow("Date de début :", self.date_debut)
        formulaire.addRow("Date de fin :", self.date_fin)
        disposition.addLayout(formulaire)
        self.bouton = QPushButton("Rechercher")
        self.bouton.setEnabled(False)
        disposition.addWidget(self.bouton)
        self.tableau = QTableWidget(0, 7)
        self.tableau.setHorizontalHeaderLabels([
            "Date", "Début", "Durée", "Type", "Salle", "Groupe", "Enseignement"
        ])
        self.tableau.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableau.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tableau.horizontalHeader().setStretchLastSection(True)
        disposition.addWidget(self.tableau)
        self.message = QLabel("Recherche indisponible : connexion au serveur à réaliser.")
        disposition.addWidget(self.message)


if __name__ == "__main__":
    application = QApplication(sys.argv)
    fenetre = VueVacataires()
    fenetre.show()
    sys.exit(application.exec_())
