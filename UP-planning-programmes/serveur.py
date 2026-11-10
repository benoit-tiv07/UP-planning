"""
Serveur TCP d'UPplanning.

Un thread par client. Chaque message est un objet JSON sur une ligne.
Lancement : python3 serveur.py
"""

import json
import socket
import threading

from dispatcher import traiter_requete

# =====================================================================
# >>> ZONE POUR M1, M2, M3 : brancher vos commandes ici <<<
#
# Quand vous avez écrit vos commandes dans votre fichier (voir le modèle
# dans dispatcher.py), décommentez la ligne qui vous correspond.
# Un simple "import" suffit : il exécute vos @commande(...) et les
# enregistre automatiquement dans le serveur.
#
# import requetes_m1   # M1 : seances_vacataire, controles_a_venir
# import requetes_m2   # M2 : sequence_enseignement, enseignements_apprentis
# import requetes_m3   # M3 : service_enseignant, bilan_formation
# =====================================================================

HOTE = ""          # toutes les interfaces
PORT = 55300       # le client doit utiliser le même port
TAILLE_FILE_ATTENTE = 5


def gerer_client(connexion, adresse):
    """
    Boucle d'échange avec un client (exécutée dans un thread).

    Chaque connexion a sa propre session (identifiant, rôles, droits).
    """
    print(f"[+] Client connecté : {adresse}")
    session = {}

    try:
        with connexion, connexion.makefile("r", encoding="utf-8") as entree:
            for ligne in entree:
                ligne = ligne.strip()
                if not ligne:
                    continue
                try:
                    requete = json.loads(ligne)
                    reponse = traiter_requete(requete, session)
                except json.JSONDecodeError:
                    reponse = {"statut": "erreur", "message": "JSON invalide"}

                message = json.dumps(reponse, ensure_ascii=False) + "\n"
                connexion.sendall(message.encode("utf-8"))
    except (ConnectionError, OSError) as erreur:
        print(f"[!] Connexion perdue avec {adresse} : {erreur}")
    finally:
        print(f"[-] Client déconnecté : {adresse}")


def lancer_serveur():
    """Ouvre le socket d'écoute et crée un thread par client."""
    serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serveur.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
    serveur.bind((HOTE, PORT))
    serveur.listen(TAILLE_FILE_ATTENTE)
    print(f"Serveur UPplanning en écoute sur le port {PORT}")

    try:
        while True:
            connexion, adresse = serveur.accept()
            thread = threading.Thread(target=gerer_client,
                                      args=(connexion, adresse),
                                      daemon=True)
            thread.start()
    except KeyboardInterrupt:
        print("\nArrêt du serveur")
    finally:
        serveur.close()


if __name__ == "__main__":
    lancer_serveur()
