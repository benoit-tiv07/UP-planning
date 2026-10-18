import unittest
import importlib.util
from pathlib import Path


chemin = (
    Path(__file__).resolve().parents[1]
    / "UP-planning-programmes"
    / "calculs_heures.py"
)

spec = importlib.util.spec_from_file_location(
    "calculs_heures", chemin
)
calculs_heures = importlib.util.module_from_spec(spec)
spec.loader.exec_module(calculs_heures)


class TestCalculerHetd(unittest.TestCase):

    def test_calcul_normal(self):
        resultat = calculs_heures.calculer_hetd(5, 12, 21, 3)
        self.assertEqual(resultat, 43.5)

    def test_toutes_les_heures_a_zero(self):
        resultat = calculs_heures.calculer_hetd(0, 0, 0, 0)
        self.assertEqual(resultat, 0)


if __name__ == "__main__":
    unittest.main()