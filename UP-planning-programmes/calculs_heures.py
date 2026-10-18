
def calculer_hetd(h_cours, h_td, h_tp, h_ctrl_tp):
    """
    Calcule les heures équivalent TD d'un enseignement.

    Formule :
    hETD = 1.5 * h_cours + h_td + h_tp + h_ctrl_tp

    Paramètres :
        h_cours (float): heures de cours.
        h_td (float): heures de TD.
        h_tp (float): heures de TP.
        h_ctrl_tp (float): heures de contrôle de TP.

    Retour :
        float: nombre d'heures équivalent TD.
    """
    return 1.5 * h_cours + h_td + h_tp + h_ctrl_tp

