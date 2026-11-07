# Decisions

- **2026-11-07 · planning · Host on GitHub Pages** from public repo `mattchurchman/alaska-2027`, `main` / root. Reason: plain link with no login; outside photos, map tiles and video embeds load (the Claude artifact blocked all three).
- **2026-11-07 · planning · Data split into 7 files with one row per price** (`data/prices.json`). Reason: refreshes touch one row; the validator can prove no price lives elsewhere. `sources.json` added to the plan's six files because sources are shared by prices, offers and notes.
- **2026-11-07 · planning · Cabin prices stored per cabin for 2 adults** (v1 per-person × 2). Reason: v2 compares whole cabins (brothers interior + parents balcony).
- **2026-11-07 · planning · Leaflet bundled in `vendor/`** instead of a CDN. Reason: one fewer outside dependency; the site still needs the network for tiles and photos.
- **2026-11-07 · planning · CSV tool named `make_csv.py`**, not `csv.py`. Reason: `csv.py` shadows Python's csv module.
- **2026-11-07 · planning · Interface:** Claude app for P0–P5 (artifact/Project access, browser for cruise sites); revisit Claude Code at P6 for real Safari/WebKit testing.
- **2026-11-07 · planning · Agent-pipeline template not applied:** `mattchurchman/agent-pipeline-template` is not visible to Claude's GitHub access. A lean AGENTS.md was written instead; the template can be retrofitted later if access is granted.
- **2026-11-07 · p1 · Phase 1 window = departures May 22 – Jul 7, 2027** ("late May / early July"). Mid-May dates found along the way are noted but not added.
- **2026-11-07 · p1 · Sold-out categories stored as `unavailable` rows** (with the sold-out note) rather than omitted, so the app can show "sold out" next to real prices.
- **2026-11-07 · p1 · HAL cruisetour-only sailings not added as sailings**; recorded in `linesReviewed` instead, since the family is not buying a land tour.
- **2026-11-07 · p3 · `walkMiles` is a conservative one-person planning figure** (dock to start, on-tour walking, back to the dock; higher end of any range) with `walkConfidence` documented / derived / estimate. Reason: operators rarely publish walking distances; the parents' 2-mile budget needs a number, but it must not look measured.
- **2026-11-07 · p3 · Rental-car prices stored as `unavailable`.** No renter publishes a June 2027 rate; an aggregator's Turo-branded November price and a forum anecdote were deliberately not used. Juneau Car Rental's site is robots-blocked and was not read.
- **2026-11-07 · p3 · New experiences carry `diy: true`; self-drive ones that suit the parents carry `parentsDrive: true`.** The Skagway-to-Canada rental question is recorded as unresolved (no written renter policy found).
