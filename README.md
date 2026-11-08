# Alaska 2027 trip planner

A planning site for a family Alaska cruise in June 2027: routes, ships, dates, day-by-day activities and honest costs, with a source, status and check date on every price. It is an idea generator and cost comparer, not a booking tool.

**Site:** https://mattchurchman.github.io/alaska-2027/ (best in Safari on iPhone or iPad; no login).

## How to use it
Work left to right through the tabs:
1. **Ideas** – kinds of route (Glacier Bay, Dawes/Endicott Arm, Tracy Arm, Hubbard, no-glacier, Vancouver round trips, one-ways) and why you might pick each.
2. **Route** – map with each route family in its own color. Tap a route to see its ships.
3. **Line & ship** – photos, ship facts, tour videos (tap to load) and notes for the parents.
4. **Dates** – calendar of every sailing with its two-cabin price. Tap a dot to select it and highlight its route.
5. **Days** – each port day: options grouped Easy for parents, Adventure, DIY & budget, Free, Stay aboard. Separate lanes for parents and brothers. Picks that don't fit the port time are blocked; the parents' walking meter (2 mi/day default) warns when exceeded.
6. **Cost** – whole-trip total, parents/brothers split, per person and per day, and a stacked comparison of up to 4 options. Striped and hatched bars mean the number is published or estimated, not verified.
7. **★ Shortlist** – starred plans, JSON backup/import, CSV downloads.

**Price status:** verified, published (provider "from" price), estimate, family-quote (typed in by you with "add my quote"), unavailable (shown as not captured). Never treat published or estimate as a quote.

## Sharing
Tap **Share** on any screen: the link opens that exact route, sailing or day plan. On Shortlist, use **Backup** to save your picks and quotes to a file and **Import** to restore them on another device. Plans and quotes are stored only in your browser.

## Refreshing prices
All research lives in `data/` (`prices.json` holds every price). Claude updates it in short sessions: say "Refresh shortlist prices." Each session updates up to about 10 of the oldest rows, then runs `python3 tools/validate.py` and `python3 tools/make_csv.py` and pushes to `main`; GitHub Pages republishes in 1–2 minutes. Tools: `tools/query.py` (read slices), `tools/validate.py`, `tools/make_csv.py` (writes `csv/`), `tools/linkcheck.py` (run on a normal computer; the cloud workspace can't reach most sites).

## Known gaps
Vancouver/Anchorage flights and hotels show "not captured" until arrival-city costs are researched. Sitka, Icy Strait and Victoria picks have no walking miles yet, Haines and Prince Rupert have no experiences, and the glacier guide is not written. Safari/iOS has not been tested by Claude; see `docs/DEVICE-TEST.md`.

## Credits
Photos: Wikimedia Commons (author and license shown under each photo). Map: © OpenStreetMap contributors, drawn with Leaflet (BSD-2-Clause, `vendor/leaflet/LICENSE`).
