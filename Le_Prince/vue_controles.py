"""Écran des contrôles à venir, en attente de la connexion au serveur."""

import sys
from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import (
    QApplication, QDateEdit, QFormLayout, QHeaderView, QLabel,
    QPushButton, QTableWidget, QVBoxLayout, QWidget, QAbstractItemView,
)


class VueControles(QWidget):
    """Présente une période et un tableau vide, sans charger de données."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("UPplanning — Le Prince — Contrôles à venir")
        self.resize(1000, 420)
        disposition = QVBoxLayout(self)
        formulaire = QFormLayout()
        self.date_debut = QDateEdit(QDate.currentDate())
        self.date_fin = QDateEdit(QDate.currentDate())
        for champ in (self.date_debut, self.date_fin):
            champ.setDisplayFormat("dd/MM/yyyy")
            champ.setCalendarPopup(True)
        formulaire.addRow("Date de début :", self.date_debut)
        formulaire.addRow("Date de fin :", self.date_fin)
        disposition.addLayout(formulaire)
        self.bouton = QPushButton("Rechercher")
        self.bouton.setEnabled(False)
        disposition.addWidget(self.bouton)
        self.tableau = QTableWidget(0, 7)
        self.tableau.setHorizontalHeaderLabels([
            "Date", "Début", "Durée", "Type de contrôle", "Salle", "Groupe", "Enseignement"
        ])
        self.tableau.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableau.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tableau.horizontalHeader().setStretchLastSection(True)
        disposition.addWidget(self.tableau)
        self.message = QLabel("Recherche indisponible : connexion au serveur à réaliser.")
        disposition.addWidget(self.message)


if __name__ == "__main__":
    application = QApplication(sys.argv)
    fenetre = VueControles()
    fenetre.show()
    sys.exit(application.exec_())
