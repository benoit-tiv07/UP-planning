"""Tests d'extraction brute sur un calendrier explicitement fictif."""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from Le_Prince.extraction_ade import extraire_evenements


class TestExtractionAde(unittest.TestCase):
    def extraire(self, texte):
        with TemporaryDirectory() as dossier:
            chemin = Path(dossier) / "fictif.ics"
            with chemin.open("w", encoding="utf-8", newline="") as fichier:
                fichier.write(texte)
            return extraire_evenements(chemin)

    def test_valeurs_brutes_et_lignes_repliees(self):
        texte = (
            "BEGIN:VCALENDAR\nBEGIN:VEVENT\nUID:fictif\n"
            "DTSTART:20261102T130000Z\nSUMMARY:Texte\n replié\n"
            "DESCRIPTION:\\nGROUPE\\nNOM\\n(Updated :12:00)\n"
            "X-TEST;LANGUAGE=fr: valeur:conservée \n"
            "END:VEVENT\nEND:VCALENDAR\n"
        )
        evenement = self.extraire(texte)[0]
        self.assertEqual(evenement["SUMMARY"], "Textereplié")
        self.assertEqual(evenement["DTSTART"], "20261102T130000Z")
        self.assertEqual(evenement["DESCRIPTION"], r"\nGROUPE\nNOM\n(Updated :12:00)")
        self.assertEqual(evenement["X-TEST;LANGUAGE=fr"], " valeur:conservée ")
        self.assertNotIn("LOCATION", evenement)

    def test_ordre_et_doublons_conserves(self):
        evenement = "BEGIN:VEVENT\nUID:meme-uid-fictif\nEND:VEVENT\n"
        self.assertEqual(len(self.extraire(
            "BEGIN:VCALENDAR\n" + evenement * 2 + "END:VCALENDAR")), 2)

    def test_repli_tabulation_et_crlf(self):
        resultat = self.extraire(
            "BEGIN:VCALENDAR\r\nBEGIN:VEVENT\r\nSUMMARY:A\r\n\tB\r\n"
            "END:VEVENT\r\nEND:VCALENDAR\r\n")
        self.assertEqual(resultat[0]["SUMMARY"], "AB")

    def test_structures_invalides_signalees(self):
        for contenu in ("invalide", "BEGIN:VEVENT\nUID:x",
                        "BEGIN:VEVENT\nUID:x\nUID:y\nEND:VEVENT",
                        "BEGIN:VEVENT\nBEGIN:VALARM\nEND:VALARM\nEND:VEVENT"):
            with self.subTest(contenu=contenu), self.assertRaises(ValueError):
                self.extraire("BEGIN:VCALENDAR\n" + contenu + "\nEND:VCALENDAR")


if __name__ == "__main__":
    unittest.main()
