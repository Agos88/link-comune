# Link in bio del Comune di Castelluccio Superiore

Pagina di collegamenti per il profilo Instagram/Facebook, al posto di Linktree.
Statica, senza cookie, con conteggio dei clic per voce (GoatCounter).

## Aggiornare le voci (senza strumenti)

1. Su GitHub apri `link.json` e premi la matita («Edit this file»).
2. Cambia, aggiungi o togli una voce. Ogni voce ha `id`, `titolo`, `url` (solo `https://`).
3. Premi «Commit changes». In circa un minuto la pagina è aggiornata.
   Se il file ha un errore, la pubblicazione si ferma e nella scheda **Actions** compare la riga da correggere.

| Campo | Cosa fa |
|---|---|
| `nascosta: true` | la voce resta nel file ma non si vede |
| `scadenza: "AAAA-MM-GG"` | l'ultimo giorno in cui la voce si vede; dal giorno dopo sparisce da sola (la pagina si rigenera ogni notte) |
| `in_evidenza` | la scheda grande con immagine in cima; immagine 16:9 in `assets/` |

`DA-COMPLETARE` come indirizzo è ammesso solo su voci `nascosta`.

## Statistiche

Il nome dell'account GoatCounter va in `goatcounter` dentro `link.json`. Ogni clic è registrato con l'`id` della voce, senza cookie né dati personali. I blocchi pubblicità possono far perdere una parte dei clic: i numeri vanno letti come stima per difetto.

## In locale

```
python3 -m unittest discover -s tests
python3 build.py            # scrive docs/index.html
python3 build.py --oggi 2026-12-03   # prova come sarà in un'altra data
```

## Attivazione (una volta)

Repo su GitHub → Settings → Pages → Source: **GitHub Actions**.
