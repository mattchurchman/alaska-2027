# Alaska 2027 Planner — v2 build plan

Copied from the claude.ai Project doc `claude/v2-plan.md` (2026-11-07) and kept here so every session, in the Claude app or Claude Code, reads the same plan. **This file is now the source of truth.** v1 stays live (https://claude.ai/artifact/LxFtFqdbT5VUqu4u5zQ3CQ) until v2 ships; its files are in `app-v1/` for reference.

## What v2 is for
An **idea generator and honest cost comparer** that the moderator (the brother running the planning) explores, then shares by link with the family. Family members open a link in Safari on iPhone/iPad, look at pictures, routes and ships, and send reactions by text.
Not a voting tool. Not a booking tool. Flights and hotels are background costs, not features.

**User flow:** Ideas → Route → Line & ship → Date → Days → Cost (cost strip always visible).

Travelers: 4 adults from ABQ. Brothers ~35: interior cabin, budget-minded, adventurous. Parents ~65: balcony near elevators, mom walks under ~2 mi/day. US citizens with passports. No loyalty status. Window: June 2027; late May or early July if much better.

## Keep / change / drop / add
- **Keep:** v1 Seattle sailing data, 43 experiences + 130 offers, cost split parents vs brothers, status + source + check date on every price, time-fit checks against all-aboard, local saved plans, JSON/CSV export.
- **Change:** route-first selection; each route family a distinct color on the map; **sailing calendar** replaces the date dot plot (rows = ships grouped by route family, colored by route, price label on each dot, tap = highlight route on map); time-of-day bar gets hour labels, arrival and all-aboard markers, and a legend; real Leaflet/OSM map; photos on every port, experience, glacier and ship card.
- **Drop:** voting/shared state; the standalone single-file build as a deliverable; the 7-step builder; the separate Flights & hotels tab.
- **Add:** Vancouver round trips and Vancouver ↔ Seward/Whittier one-ways; Alaska-specialist line notes; **glacier guide** (the "Glacier Bay decision"); DIY and budget alternatives (self-drive, public bus, self-guided walks); a **walking budget for the parents** (2 mi/day default, adjustable); ship tour videos + official ship page links; share links to a specific route or sailing; "add my quote" on any price (status `family-quote`); cost per arrival city.

## Hosting (decided in P0)
- GitHub Pages from the public repo `mattchurchman/alaska-2027`, branch `main`, folder `/ (root)`. Site: https://mattchurchman.github.io/alaska-2027/
- Leaflet is bundled in `vendor/leaflet/` (no CDN needed). Map tiles come from tile.openstreetmap.org with attribution. Photos are Wikimedia Commons URLs. Videos are tap-to-load youtube-nocookie embeds.
- **Privacy:** no names or personal details anywhere in the repo or site. The repo is public.

## Data layout (`data/`)
| file | holds |
|---|---|
| catalog.json | routeFamilies, lines, ships, itineraries (days with 24 h times, `routeFamily`, `mapLine`), sailings, places, pois, linesReviewed. **No prices.** |
| prices.json | `rows[]`, one per price (below) |
| experiences.json | experiences + offers (each offer has `priceRow`), `walkMiles`/`walkBasis` (P3/P4 fill), coverage, labels, offerKinds |
| media.json | photos (id, url, page, credit, license, for[]), videos (title, channel, date, url, for[]), officialLinks |
| travel.json | gateways (SEA, YVR, ANC), flights, hotels, groundTransfers, hotelRanges, coverage |
| sources.json | sources[] (id, title, url, kind, publisher, checked, note) — added in P0; prices and offers cite these ids |
| meta.json | travelers, assumptions, scoring weights, status definitions, presets, essentials, glacierGuide, phases, qa, migration |

**Price row:** `{id, for, item, amount, currency, usd, fx:{rate,date}|null, basis, status, source, url, checked, note, label?}`
- `for`: `kind:id` of the record it prices — `sailing:…`, `offer:…`, `line:…` (gratuity), `flight:…`, `hotel:…`, `gateway:…`, `transfer:…`, `hotelRange:…`.
- Records point back with fields ending in `Row` / `Rows` (`sailing.priceRows.interior`, `offer.priceRow`, `line.gratuityRow`, `flight.fareRows.saver`, `hotel.rateRow` …).
- Cabin rows are **per cabin for 2 adults** (v1 per-person × 2).
- `status`: verified | published | estimate | family-quote | unavailable.
- The app computes every total from these rows. No price lives anywhere else (`validate.py` enforces it).

**Route families** (P1 confirms; each has a color in catalog.json): SEA-GB, SEA-DAWES, SEA-TRACY, SEA-HUBBARD, SEA-NONE, YVR-RT, YVR-N (Vancouver → Seward/Whittier), YVR-S (Seward/Whittier → Vancouver).

**Tools (`tools/`):** `validate.py` (run before every commit) · `query.py` (small slices: `counts`, `get`, `rows`, `list`) · `make_csv.py` (writes `csv/`) · `linkcheck.py` (run on a normal computer; the cloud workspace can't reach most sites) · `migrate_v1.py` (one-time, provenance only).

## Rules for every phase (token efficiency)
1. Start by reading **this file + the previous handoff only** (`handoffs/phaseN.md`). Do not read the v1 artifact or `app-v1/` wholesale.
2. Read data with `tools/query.py` or `jq`. Never print a whole data file.
3. Research: WebSearch in standard mode first, extended only when results are thin. Give WebFetch a narrow prompt. Append compact findings to `notes/phaseN.md` as you go.
4. Write data with small scripts or `jq` edits. Run `python3 tools/validate.py` before every commit. Commit at each checkpoint.
5. **Context checkpoint:** at about 60% of the context window, finish the current item, commit, write the handoff with a "remaining" list, and stop. The next chat continues the same phase.
6. Handoff: 30 lines or less. What changed, counts, what was not captured, next steps.
7. Never invent a price. Unknown means `unavailable` with a note. A generic "from" price is `published`, never `verified`.
8. No mid-task narration in chat. One short summary at the end. The moderator is not a developer: end-of-phase messages say what changed and what (if anything) he needs to click, in plain words.

## Phases
Models: Opus 5.5, Sonnet 5.5, Haiku 5.5. Fable is not needed.

### P0 · Foundation and migration — Sonnet 5.5, medium — DONE except the iPhone check (see handoffs/phase0.md)

### P1 · Routes and sailings — Opus 5.5, high — DONE (see handoffs/phase1.md)
- Confirm route families. Research Vancouver round trips and both one-way directions, late May to early July 2027. Start with **Princess and Holland America**, then every other line.
- For each sailing: ship and dates; ports with arrival/departure times; glacier day; interior and balcony prices for 2 adults each, with taxes/fees; CAD → USD with rate and date.
- Line notes on Alaska experience: Glacier Bay access, land tours, years in Alaska. A short paragraph on small-ship lines (who, from-price, fit for the parents). No full data.
- Refresh prices for the top ~6 v1 Seattle sailings only.
- Out: catalog.json, prices.json, notes, handoff. Done when every sailing has a route family and port times, or a stated reason they're missing. Checkpoint split if needed: "Vancouver round trips done".
- **Interface:** Claude app (cruise booking sites often need a real browser).

### P2 · Arrival-city costs — Sonnet 5.5, low
- Representative fares for 4 adults on 2–3 date pairs: ABQ ↔ SEA (refresh), ABQ ↔ YVR, open-jaw ABQ → YVR / ANC → ABQ and the reverse. Ground SEA → Vancouver (train, bus, shuttle). Seward/Whittier → Anchorage transfers. One hotel price range per city (Seattle, Vancouver, Anchorage) with a search link. Rough numbers fine, labeled `published` or `estimate`.
- Out: travel.json, prices.json. Done when every route family has an arrival-city cost line.

### P3 · Experiences A: Juneau, Skagway, Ketchikan — Sonnet 5.5, high — DONE (see handoffs/phase3.md)
- Walking miles on every existing experience (dock to start + on-tour, basis noted); stairs and hills.
- At least 2 DIY or budget alternatives per port: rental car (who rents at the port, ship-day sellouts; Skagway: does the contract allow the Klondike Highway into Canada), public bus, self-guided walks with miles. Flag self-drive options easy for the parents.
- Check the 2027 status of the Goldbelt tram.
- Done when each port has walking miles on all experiences and 2+ DIY alternatives.

### P4 · Experiences B and the glacier guide — Sonnet 5.5, high
- Same treatment for Sitka, Icy Strait Point, Victoria, any new ports P1 found (e.g. Haines, Prince Rupert), Seward/Whittier and College Fjord.
- Glacier guide for Glacier Bay, Hubbard, Dawes/Endicott, Tracy Arm, College Fjord: what you see; hours in the area; how often ships reach the face or substitute (sourced); rangers aboard?; best viewing spots for the parents; which route families include it. Stored in `meta.glacierGuide`.
- Done when every port in catalog.json has experiences, and the guide covers every glacier day.

### P5 · Media — Sonnet 5.5, medium
- Wikimedia Commons photos (author, license, file page) for every port and glacier, ship exteriors, experiences where a matching photo exists.
- Per ship: official ship page; 1–2 recent YouTube ship tours (title, channel, publish date; after the last refit where possible); quick facts (year built/refit, guests, accessible-cabin notes).
- No logos, no cruise-line photos. Run a link check (on a normal computer, or note that it couldn't run).
- Done when every card type has a photo or a deliberate placeholder, and every shortlist ship has 1+ video.

P2–P5 touch different files and can run in parallel chats after P1 (all write prices.json: pull before editing, keep row ids unique per phase).

### P6 · App A: Ideas, Route, Ship, Date — Opus 5.5, high
- New app reading `data/*.json`, Safari-first, built for 390/820/1180/1280 px. Screens: **Ideas** (hero photos, route-family cards, glacier highlight, "why this route"); **Route** (Leaflet map with each family's color and line style; tap a route → its ships); **Line & ship** (photo, video, facts, notes for the parents); **Date** (sailing calendar; tap → highlight route and select). Share links (`#route=…&sailing=…`). Photo credits and offline placeholders.
- Reuse v1 logic by grepping specific functions in `app-v1/src/`, not by reading whole files.
- Done when Ideas → Date works end to end, no console errors at the 4 widths, share links restore the view.
- **Interface:** decide at the start of P6 whether Claude Code on the moderator's computer is worth it (real WebKit/Safari testing, link checks that reach every site).

### P7 · App B: Days, Cost, Shortlist — Opus 5.5, high
- **Days:** option groups per day: Easy for parents · Adventure · DIY & budget · Free · Stay aboard. Separate parents and brothers lanes. Hour-labeled time bar with arrival and all-aboard markers and a legend. Walking meter: parents' miles against the budget.
- **Cost:** stack-up chart for up to 4 shortlisted options (cruise, tips, arrival travel, hotel, excursions), shaded by price status; "add my quote" on any price (stored locally, exportable).
- **Shortlist:** stars, share links, JSON/CSV export, import. **Background costs:** flights and hotels as one assumptions panel with search links.
- Done when a full plan builds, totals match a hand check for 2 configurations, time-fit and walking warnings fire correctly.

### P8 · QA and release — Sonnet 5.5, medium
- Chrome checks at 4 widths; `validate.py` and `linkcheck.py`; CSVs; README (open, share, refresh); a **real-device test script** for the moderator (iPhone and iPad Safari, ~10 tasks); fix what comes back; propose the refresh routine below as a reusable skill.
- Done when the moderator signs off on the device test.

### Recurring · Price refresh — Sonnet 5.5, low
- Kickoff: "Refresh shortlist prices." Use `query.py rows status!=family-quote --oldest 10` (filtered to shortlisted items) — max ~10 rows per chat. Update each row, then validate, regenerate CSVs and push. Haiku 5.5 is enough for validate/CSV-only runs.

## Kickoff line for each chat
"Phase N of the Alaska 2027 v2 plan. Repo mattchurchman/alaska-2027: read PLAN.md and handoffs/phase{N-1}.md there. Do only Phase N and follow the rules section."
