def calculer_hetd(h_cours, h_td, h_tp, h_ctrl_tp):
    """
    Calcule les heures équivalent TD.

    Formule :
    hETD = 1.5 * hC + hTD + hTP + hcTP
    """
    return 1.5 * h_cours + h_td + h_tp + h_ctrl_tp


def calculer_service(seances):
    """
    Calcule les totaux des heures pour une liste de séances.

    Chaque séance est représentée par un dictionnaire.
    """

    total = {
        "hC": 0,
        "hTD": 0,
        "hTP": 0,
        "hcTP": 0,
        "hcC": 0,
        "hP": 0,
        "hETD": 0
    }

    for seance in seances:
        total["hC"] += seance.get("hC", 0)
        total["hTD"] += seance.get("hTD", 0)
        total["hTP"] += seance.get("hTP", 0)
        total["hcTP"] += seance.get("hcTP", 0)
        total["hcC"] += seance.get("hcC", 0)
        total["hP"] += seance.get("hP", 0)

    total["hETD"] = calculer_hetd(
        total["hC"],
        total["hTD"],
        total["hTP"],
        total["hcTP"]
    )

    return total


def calculer_bilans_par_formation(seances):
    """
    Calcule les heures de chaque formation (BUT1, BUT2, BUT3).

    Chaque séance doit contenir une clé 'formation'.
    """

    bilans = {}

    for seance in seances:
        formation = seance["formation"]

        if formation not in bilans:
            bilans[formation] = []

        bilans[formation].append(seance)

    resultats = {}

    for formation, liste_seances in bilans.items():
        resultats[formation] = calculer_service(liste_seances)

    return resultats


def calculer_total_general(bilans):
    """
    Calcule le total général de toutes les formations.
    """
    toutes_les_seances = []

    for bilan in bilans.values():
        toutes_les_seances.append(bilan)

    total = {
        "hC": 0,
        "hTD": 0,
        "hTP": 0,
        "hcTP": 0,
        "hcC": 0,
        "hP": 0,
        "hETD": 0
    }

    for bilan in toutes_les_seances:
        for type_heure in total:
            total[type_heure] += bilan[type_heure]

    return total