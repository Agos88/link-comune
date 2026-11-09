#!/usr/bin/env python3
"""Genera docs/index.html da link.json. Uso: python3 build.py [--oggi AAAA-MM-GG]

Valida il file e si ferma con un messaggio chiaro se qualcosa non va, così una
modifica sbagliata non va online. Nessuna dipendenza esterna.
"""
import json, shutil, sys, datetime, html, re
from pathlib import Path
from zoneinfo import ZoneInfo

RADICE = Path(__file__).parent
USCITA = RADICE / "docs"
SEGNAPOSTO = "DA-COMPLETARE"


class Errore(Exception):
    pass


def oggi(argv):
    if "--oggi" in argv:
        return datetime.date.fromisoformat(argv[argv.index("--oggi") + 1])
    return datetime.datetime.now(ZoneInfo("Europe/Rome")).date()


def data(valore, dove):
    try:
        return datetime.date.fromisoformat(valore)
    except (TypeError, ValueError):
        raise Errore(f"{dove}: la data «{valore}» non è nel formato AAAA-MM-GG")


def attiva(voce, giorno, dove):
    """Una voce è visibile se non è nascosta e la scadenza (inclusa) non è passata."""
    if voce.get("nascosta"):
        return False
    if voce.get("scadenza") and giorno > data(voce["scadenza"], dove):
        return False
    return True


def controlla_voce(voce, dove, visibile):
    for campo in ("id", "titolo", "url"):
        if not voce.get(campo):
            raise Errore(f"{dove}: manca il campo «{campo}»")
    if not re.fullmatch(r"[a-z0-9-]+", voce["id"]):
        raise Errore(f"{dove}: «id» solo minuscole, numeri e trattini ({voce['id']})")
    if not voce["url"].startswith("https://"):
        raise Errore(f"{dove}: l'indirizzo deve iniziare con https://")
    if visibile and SEGNAPOSTO in voce["url"]:
        raise Errore(f"{dove} («{voce['titolo']}»): indirizzo ancora da completare; "
                     "inseriscilo oppure metti \"nascosta\": true")


def attributi_clic(voce):
    return (f' data-goatcounter-click="{html.escape(voce["id"])}"'
            f' data-goatcounter-title="{html.escape(voce["titolo"])}"')


def costruisci(cfg, giorno):
    ev = cfg.get("in_evidenza")
    voci = cfg.get("voci", [])
    id_visti = set()
    ev_visibile = bool(ev) and attiva(ev, giorno, "in_evidenza")
    if ev:
        controlla_voce(ev, "in_evidenza", ev_visibile)
    visibili = []
    for n, v in enumerate(voci, 1):
        dove = f"voci[{n}]"
        vis = attiva(v, giorno, dove)
        controlla_voce(v, dove, vis)
        if v["id"] in id_visti:
            raise Errore(f"{dove}: l'id «{v['id']}» è usato due volte")
        id_visti.add(v["id"])
        if vis:
            visibili.append(v)
    e = html.escape
    social = "".join(
        f'<a class="social" href="{e(s["url"])}" rel="noopener"{attributi_clic({"id": s["nome"].lower(), "titolo": s["nome"]})}>{e(s["nome"])}</a>'
        for s in cfg.get("social", []))
    blocco_ev = ""
    if ev_visibile:
        img = ""
        if ev.get("immagine"):
            img = (f'<img src="{e(ev["immagine"])}" alt="{e(ev.get("alt", ""))}" '
                   'width="960" height="540" loading="lazy">')
        cred = f'<span class="credito">{e(ev["credito"])}</span>' if ev.get("credito") else ""
        blocco_ev = (f'<a class="evidenza" href="{e(ev["url"])}" rel="noopener"{attributi_clic(ev)}>{img}'
                     f'<span class="testo"><strong>{e(ev["titolo"])}</strong>'
                     f'<span>{e(ev.get("descrizione", ""))}</span>{cred}</span></a>')
    pulsanti = "".join(
        f'<a class="voce" href="{e(v["url"])}" rel="noopener"{attributi_clic(v)}>{e(v["titolo"])}</a>'
        for v in visibili)
    gc = cfg.get("goatcounter", "").strip()
    script = (f'<script data-goatcounter="https://{e(gc)}.goatcounter.com/count" async '
              'src="https://gc.zgo.at/count.js"></script>') if gc else ""
    return PAGINA.format(titolo=e(cfg["titolo"]), sottotitolo=e(cfg.get("sottotitolo", "")),
                         stemma=e(cfg["stemma"]), social=social, evidenza=blocco_ev,
                         voci=pulsanti, script=script)


PAGINA = """<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titolo}</title>
<meta name="description" content="{sottotitolo}">
<style>
:root{{--rosso:#C0000C;--rosso-scuro:#8f0009;--bianco:#fff;--testo:#262626;--grigio:#595959}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--rosso);color:var(--bianco);font:18px/1.45 system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;min-height:100vh}}
main{{max-width:560px;margin:0 auto;padding:32px 16px 40px;display:flex;flex-direction:column;gap:14px}}
header{{text-align:center;margin-bottom:8px}}
.stemma{{width:96px;height:96px;border-radius:50%;background:var(--bianco);padding:10px;object-fit:contain;display:block;margin:0 auto 14px}}
h1{{font-size:1.5rem;line-height:1.2;margin:0 0 6px}}
header p{{margin:0;opacity:.95}}
.sociali{{display:flex;gap:10px;justify-content:center;margin-top:14px;flex-wrap:wrap}}
a{{color:inherit}}
.social{{padding:8px 16px;border:2px solid var(--bianco);border-radius:999px;text-decoration:none;font-weight:600;font-size:.95rem}}
.evidenza{{display:block;background:var(--bianco);color:var(--testo);border-radius:16px;overflow:hidden;text-decoration:none}}
.evidenza img{{display:block;width:100%;height:auto;aspect-ratio:16/9;object-fit:cover}}
.evidenza .testo{{display:flex;flex-direction:column;gap:4px;padding:14px 16px 16px}}
.evidenza strong{{font-size:1.15rem;color:var(--rosso);text-wrap:balance}}
.credito{{font-size:.75rem;color:var(--grigio)}}
.voce{{display:block;background:var(--bianco);color:var(--rosso);text-align:center;text-decoration:none;font-weight:700;padding:16px;border-radius:999px;min-height:52px}}
a:hover,a:focus-visible{{filter:brightness(.94)}}
a:focus-visible{{outline:3px solid #ffd54a;outline-offset:3px}}
</style>
</head>
<body>
<main>
<header>
<img class="stemma" src="{stemma}" alt="Stemma del Comune di Castelluccio Superiore">
<h1>{titolo}</h1>
<p>{sottotitolo}</p>
<nav class="sociali" aria-label="Canali social">{social}</nav>
</header>
{evidenza}
<nav style="display:flex;flex-direction:column;gap:14px" aria-label="Collegamenti">{voci}</nav>
</main>
{script}
</body>
</html>
"""


def main(argv):
    try:
        cfg = json.loads((RADICE / "link.json").read_text(encoding="utf-8"))
    except json.JSONDecodeError as err:
        print(f"ERRORE link.json, riga {err.lineno}: {err.msg}", file=sys.stderr)
        return 1
    try:
        pagina = costruisci(cfg, oggi(argv))
    except Errore as err:
        print(f"ERRORE {err}", file=sys.stderr)
        return 1
    if USCITA.exists():
        shutil.rmtree(USCITA)
    (USCITA / "assets").mkdir(parents=True)
    for f in (RADICE / "assets").iterdir():
        shutil.copy(f, USCITA / "assets" / f.name)
    (USCITA / "index.html").write_text(pagina, encoding="utf-8")
    (USCITA / ".nojekyll").write_text("")
    print(f"Pagina generata in {USCITA}/index.html")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
