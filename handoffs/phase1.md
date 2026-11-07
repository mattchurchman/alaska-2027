# Phase 1 handoff — part 1 of 2 (checkpoint, 2026-11-07)

Context checkpoint. Phase 1 is NOT done; the next chat continues Phase 1 ("part 2") from the remaining list below.

## What changed
- 69 new sailings (63 → 132), 23 new itineraries (14 → 37), 276 new price rows (439 → 715), 6 new places (Canada Place, Whittier, Seward, College Fjord, Prince Rupert, Inside Passage BC), 11 ships, 6 sources. All prices first-party, status `verified` (or `unavailable` = sold out), checked 2026-11-07. Window used: departures May 22 – Jul 7 2027.
- Princess: Emerald RT Vancouver (May 25 Glacier Bay, Jun 1–Jul 6 Dawes); Voyage of the Glaciers N/S on Crown, Discovery (Sat) and Coral, Island (Wed). Coral northbound and Island May 26 do Hubbard, not Glacier Bay. Discovery southbound calls Icy Strait instead of Skagway.
- Holland America: Noordam 7-day Seattle Explorer May 23, May 30, Jul 4 (SEA-DAWES; May 23 two-cabin $4,456). Westerdam southbound Whittier→Vancouver May 30, Jun 13, Jun 27 — verandahs sold out cruise-only. Koningsdam/Zaandam summer Vancouver RTs and other one-ways are cruisetour-only (in `linesReviewed`).
- Royal Caribbean: Serenade RT Vancouver (Sun, Tracy Arm; Juneau is a tender call), Anthem Vancouver↔Seward (Fri, Hubbard). Celebrity: Summit RT Vancouver (Sun, Dawes or Hubbard), Solstice Vancouver↔Seward (Fri).
- Scripts: `tools/p1_add_princess_hal.py`, `tools/p1_add_rci_celebrity.py` (idempotent). Raw findings and panel/voyage codes: `notes/phase1.md`.
- Cheapest two-cabin (interior + balcony, incl. taxes, no tips): Serenade May 30 $4,298; Voyager May 28 $4,302; Solstice SB May 28 $4,404; Noordam May 23 $4,456.

## Not captured / caveats
- Port times missing: Anthem SB with Ketchikan (Jun 18). Summit Hubbard times are from a September sailing. Noordam May 30 and Westerdam Jun 27 assumed same as sister dates.
- New itineraries have no `mapLine` (P6 can draw schematic lines). New ships lack built/guests (P5).
- All prices are USD on US sites, so no CAD conversion was needed.

## Remaining for Phase 1 part 2
1. Norwegian Jade Vancouver↔Whittier (Mon) and any other NCL Vancouver/Seward sailings (ncl.com vacation-builder; see app-v1 notes for URL pattern).
2. Disney Wonder (Mon) and Disney Magic (Thu) RT Vancouver.
3. One `linesReviewed` line each for luxury lines seen leaving Vancouver (Silversea, Crystal, Seabourn, Explora, Oceania, Regent, Viking) — no full data.
4. Line notes on Alaska experience for every line (Glacier Bay access, land tours, years in Alaska; Princess ~60 yrs/85 Glacier Bay calls, HAL 80 yrs — sources in notes) + short small-ship paragraph (UnCruise, Lindblad, Alaskan Dream, American Cruise Lines).
5. Refresh prices for the top ~6 v1 Seattle sailings.
6. Final check: validate, spot-check a few rows against the sites, regenerate CSVs, write the full handoff.

Kickoff: "Phase 1 part 2 of the Alaska 2027 v2 plan. Repo mattchurchman/alaska-2027: read PLAN.md and handoffs/phase1.md there. Do only the remaining Phase 1 items and follow the rules section."
