
import unittest
import importlib.util
from pathlib import Path

# Chargement du fichier calculs_heures.py
chemin = (
    Path(__file__).resolve().parents[1]
    / "UP-planning-programmes"
    / "calculs_heures.py"
)

spec = importlib.util.spec_from_file_location(
    "calculs_heures", chemin
)

module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class TestCalculsM3(unittest.TestCase):

    def test_calcul_hetd(self):
        resultat = module.calculer_hetd(5, 12, 21, 3)
        self.assertEqual(resultat, 43.5)

    def test_calcul_service(self):
        seances = [
            {
                "hC": 2, "hTD": 3, "hTP": 4,
                "hcTP": 1, "hcC": 2, "hP": 5
            }
        ]

        resultat = module.calculer_service(seances)

        self.assertEqual(resultat["hC"], 2)
        self.assertEqual(resultat["hTD"], 3)
        self.assertEqual(resultat["hTP"], 4)
        self.assertEqual(resultat["hcTP"], 1)
        self.assertEqual(resultat["hcC"], 2)
        self.assertEqual(resultat["hP"], 5)
        self.assertEqual(resultat["hETD"], 11)

    def test_bilans_par_formation(self):
        seances = [
            {
                "formation": "BUT1",
                "hC": 2, "hTD": 0, "hTP": 0,
                "hcTP": 0, "hcC": 0, "hP": 2
            },
            {
                "formation": "BUT2",
                "hC": 0, "hTD": 3, "hTP": 0,
                "hcTP": 0, "hcC": 0, "hP": 3
            }
        ]

        bilans = module.calculer_bilans_par_formation(seances)

        self.assertEqual(bilans["BUT1"]["hETD"], 3)
        self.assertEqual(bilans["BUT2"]["hETD"], 3)

    def test_total_general(self):
        bilans = {
            "BUT1": {
                "hC": 2, "hTD": 0, "hTP": 0,
                "hcTP": 0, "hcC": 0, "hP": 2,
                "hETD": 3
            },
            "BUT2": {
                "hC": 0, "hTD": 3, "hTP": 0,
                "hcTP": 0, "hcC": 0, "hP": 3,
                "hETD": 3
            }
        }

        total = module.calculer_total_general(bilans)

        self.assertEqual(total["hC"], 2)
        self.assertEqual(total["hTD"], 3)
        self.assertEqual(total["hETD"], 6)

    def test_service_sans_seance(self):
        resultat = module.calculer_service([])

        self.assertEqual(resultat["hETD"], 0)
        self.assertEqual(resultat["hC"], 0)


if __name__ == "__main__":
    unittest.main()