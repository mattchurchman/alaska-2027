# Phase 3 handoff — DONE (2026-11-07): Juneau, Skagway, Ketchikan

## What changed (totals: 56 experiences, 149 offers, 815 price rows, 103 sources; validate.py OK)
- All 28 existing experiences in the three ports (incl. Ward Cove shuttle) now have `walkMiles`, `walkConfidence` (documented | derived | estimate), `walkBasis` and `stairsHills`. `walkMiles` = conservative one-person figure: dock to start + on-tour + back (higher end of any range). Most are `estimate`; notable derived ones: Skagway town 2.3 mi, Ketchikan city 1.5 mi, Juneau downtown 1.1 mi (documented).
- 13 new DIY experiences (`diy: true`): Juneau 4 (downtown walk + free Capitol tour, city bus to Mendenhall, rental car, Basin Road hikes); Skagway 5 (SMART bus/shuttle, Yakutania Point, Gold Rush Cemetery, Lower Dewey Lake, rental car); Ketchikan 4 (Creek St/Totem Heritage walk, bus to Totem Bight, rental car, Deer Mountain). Self-drive picks for the parents: `parentsDrive: true` on `jnu_diy_car`, `skg_diy_car`, `ktn_diy_car`.
- 20 new sources, 19 new price rows (bus fares, SMART, free trails/tour = `published`; all rental cars, Totem Heritage admission, Princess walking tour = `unavailable`), place `logistics` for docks/transit, `experiences.coverage.phase3`, one assumption, decisions logged. Raw notes: `notes/phase3.md`. Script: `tools/p3_experiences_a.py` (idempotent).

## Findings that matter
- Goldbelt tram: still no 2027 date (KTOO Sep 24 2026: needs state certification and a part from France). Risk text updated; keep out of plans.
- City bus to Mendenhall ($2) means ~3 mi walking round trip and up to ~1.5 h each way: fails mom's 2-mi budget. Skagway walking from the dock to Broadway alone is ~1.8 mi round trip; the SMART bus ($3 each way / $5 day) fixes that.
- Skagway Canada drive: no renter's written policy found (forum says US citizens can cross with passports; Avis barred from gravel). Treat as unresolved.

## Not captured
First-party rental rates; ship-day rental sell-outs (no source); border hours; drive times to Carcross/Emerald Lake; dock-by-dock distances (Skagway, Ketchikan); Lumberjack Show distance; Totem Heritage admission; Ketchikan borough fare/schedule pages (2023 blog figures used, alaska.org says $1); Juneau bus frequency; juneaucarrental.com is robots-blocked.

## Next
P4 (Sitka, Icy Strait, Victoria, Haines, Prince Rupert, Seward/Whittier, College Fjord + glacier guide) should reuse the same fields and `p3_experiences_a.py` as the pattern. P6 should show `walkMiles` against the parents' budget and `walkConfidence` as a badge.
Kickoff: "Phase 4 of the Alaska 2027 v2 plan. Repo mattchurchman/alaska-2027: read PLAN.md and handoffs/phase3.md there. Do only Phase 4 and follow the rules section."
