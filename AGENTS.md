# Agent guide — Alaska 2027 planner

Read this, then `PLAN.md`, then the latest file in `handoffs/`. Do only the phase you were given.

## Owner
The moderator is not a developer. He does not use git. Do all git work yourself; end every session with a short plain-language message: what changed, the site link if it changed, and any click he must make (with exact menu names).

## Hard rules
- **Never invent a price.** Unknown = status `unavailable` with a note. A generic "from" price is `published`, never `verified`.
- Every price is one row in `data/prices.json` with status, url (unless estimate/unavailable), and `checked` date. No price numbers anywhere else.
- **Public repo:** no names, emails, phone numbers, booking numbers or other personal details. Travelers are "brothers" and "parents".
- No brand logos or cruise-line photos. Photos: Wikimedia Commons (credit + license + file page). Videos: youtube-nocookie, tap to load.
- Safari on iPhone/iPad is the primary browser. Test at 390, 820, 1180 and 1280 px.

## Before every commit
```
python3 tools/validate.py      # must print OK
python3 tools/make_csv.py      # when prices changed
```
Commit messages: `pN: <what>` (e.g. `p1: add Vancouver round trips`). Push to `main`; GitHub Pages publishes it in 1–2 minutes.

## Reading data cheaply
`python3 tools/query.py counts | get <id> | rows <filters> | list <collection> <filters> --fields a,b`. Never cat a whole data file.

## Layout
`data/` data files · `tools/` scripts · `index.html` site entry (P0: setup test page) · `vendor/leaflet/` · `csv/` generated · `notes/phaseN.md` raw findings · `handoffs/phaseN.md` ≤30-line handoffs · `docs/DECISIONS.md` decisions log · `app-v1/` v1 reference only (do not edit).
