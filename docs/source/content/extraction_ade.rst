Extraction brute ADE : livraison de Le Prince à M2
=================================================

Depuis la racine du projet :

.. code-block:: powershell

   python .\Le_Prince\le_prince.py

Le script principal le_prince.py appelle la fonction d'extraction du module
extraction_ade.py. Il lit data/ADECal.ics et écrit data/ADE_extraction_brute.txt.
Ce texte est un aperçu lisible de la liste de dictionnaires Python extraite,
pas le futur format commun de stockage ou de communication.

M2 peut réutiliser directement la fonction, sans relire cet aperçu :

.. code-block:: python

   from Le_Prince.extraction_ade import extraire_evenements

   evenements = extraire_evenements("data/ADECal.ics")
   for evenement in evenements:
       description_brute = evenement.get("DESCRIPTION", "")
       # M2 nettoiera et mettra en forme les données ici.

La fonction retourne une liste de dictionnaires, un par VEVENT, dans l'ordre
du fichier. Toutes les propriétés de chaque événement sont conservées,
notamment UID, DTSTART, DTEND, SUMMARY, LOCATION et DESCRIPTION. Les lignes
repliées sont réunies, mais les échappements tels que \n restent présents.
Les dates restent des chaînes UTC terminées par Z. Les doublons d'événements
restent présents. Les propriétés absentes restent absentes.

Aucun enseignant, groupe, type de contrôle ou statut vacataire n'est déduit.
M2 réalise ensuite le nettoyage et le format commun ; M3/M4 préparent
l'enregistrement en base sur le schéma validé collectivement.

Le lecteur refuse les événements incomplets, les sous-composants et les
propriétés répétées au lieu de perdre silencieusement des données. Ce n'est
pas un lecteur de toutes les variantes iCalendar. Une récurrence éventuelle
reste une propriété brute : aucune occurrence supplémentaire n'est calculée.
Seules les propriétés des VEVENT sont extraites ; l'en-tête du calendrier
reste dans le fichier source inchangé.

Le module d'extraction utilise open(), une boucle, des listes et des
dictionnaires. Il n'importe aucune bibliothèque. Le script principal utilise
os pour les chemins et pprint pour écrire un résultat lisible, tous deux
fournis avec Python.
Il est indépendant de PyQt, PostgreSQL et du serveur. L'interface ne lit
plus directement ADE : elle attendra les données de la base via le serveur.

.. automodule:: extraction_ade
   :members:
