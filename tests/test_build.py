import datetime, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
import build

BASE = {"titolo": "T", "stemma": "assets/stemma.png", "goatcounter": "prova",
        "voci": [{"id": "sito", "titolo": "Sito", "url": "https://esempio.it"}]}
G = datetime.date(2026, 11, 9)


class Test(unittest.TestCase):
    def test_voce_visibile_e_contatore(self):
        h = build.costruisci(BASE, G)
        self.assertIn('data-goatcounter-click="sito"', h)
        self.assertIn("prova.goatcounter.com", h)

    def test_scadenza_inclusa_poi_nascosta(self):
        cfg = {**BASE, "voci": [{**BASE["voci"][0], "scadenza": "2026-12-02"}]}
        self.assertIn("Sito", build.costruisci(cfg, datetime.date(2026, 12, 2)))
        self.assertNotIn(">Sito<", build.costruisci(cfg, datetime.date(2026, 12, 3)))

    def test_nascosta(self):
        cfg = {**BASE, "voci": [{**BASE["voci"][0], "nascosta": True}]}
        self.assertNotIn(">Sito<", build.costruisci(cfg, G))

    def test_segnaposto_visibile_blocca(self):
        cfg = {**BASE, "voci": [{**BASE["voci"][0], "url": "https://DA-COMPLETARE"}]}
        with self.assertRaises(build.Errore):
            build.costruisci(cfg, G)

    def test_segnaposto_nascosto_ok(self):
        cfg = {**BASE, "voci": [{**BASE["voci"][0], "url": "https://DA-COMPLETARE", "nascosta": True}]}
        build.costruisci(cfg, G)

    def test_http_rifiutato_e_id_doppio(self):
        with self.assertRaises(build.Errore):
            build.costruisci({**BASE, "voci": [{**BASE["voci"][0], "url": "http://x.it"}]}, G)
        with self.assertRaises(build.Errore):
            build.costruisci({**BASE, "voci": BASE["voci"] * 2}, G)

    def test_senza_goatcounter_nessuno_script(self):
        self.assertNotIn("count.js", build.costruisci({**BASE, "goatcounter": ""}, G))

    def test_html_escape(self):
        cfg = {**BASE, "voci": [{**BASE["voci"][0], "titolo": "<b>x</b>"}]}
        self.assertNotIn("<b>x</b>", build.costruisci(cfg, G))


unittest.main() if __name__ == "__main__" else None
