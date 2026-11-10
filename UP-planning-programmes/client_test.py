"""
Petit client de test (sans PyQt) pour vérifier le serveur.
Lancement : python3 client_test.py
"""

import json
import socket

ADRESSE = "localhost"
PORT = 55300


def envoyer(fichier, connexion, commande, **params):
    """Envoie une commande et affiche la réponse du serveur."""
    requete = {"commande": commande, "params": params}
    connexion.sendall((json.dumps(requete) + "\n").encode("utf-8"))
    reponse = json.loads(fichier.readline())
    print(f"{commande} -> {reponse}")
    return reponse


if __name__ == "__main__":
    with socket.create_connection((ADRESSE, PORT)) as connexion:
        with connexion.makefile("r", encoding="utf-8") as fichier:
            envoyer(fichier, connexion, "ping")
            # Sans connexion : doit être refusé
            envoyer(fichier, connexion, "seances_vacataire")
            # Mauvais mot de passe
            envoyer(fichier, connexion, "connexion",
                    identifiant="chef", mot_de_passe="faux")
            # Bonne connexion
            envoyer(fichier, connexion, "connexion",
                    identifiant="chef", mot_de_passe="chef123")
            # Commande inconnue
            envoyer(fichier, connexion, "nimporte_quoi")
            envoyer(fichier, connexion, "deconnexion")
            # Après déconnexion : refusé de nouveau
            envoyer(fichier, connexion, "seances_vacataire")
