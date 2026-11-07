# Phase 1 handoff — DONE (2026-11-07, parts 1 + 2)

## What changed (totals now: 152 sailings, 42 itineraries, 796 price rows, 10 lines, 28 ships, 23 places, 83 sources)
- Part 1: Princess, Holland America, Royal Caribbean, Celebrity Vancouver round trips and Vancouver ↔ Seward/Whittier one-ways (see git history and `notes/phase1.md`).
- Norwegian Jade (Mondays, alternating): northbound Vancouver→Whittier with **Glacier Bay** + Icy Strait (May 24, Jun 7, Jun 21, Jul 5); southbound Whittier→Vancouver with Hubbard (May 31 via Haines; Jun 14, Jun 28 via Juneau). First-party ncl.com prices, `verified`. New place: Haines.
- Disney Wonder (Mon) and Disney Magic (Thu) Vancouver round trips, 13 sailings, glacier day = Stikine Icecap (new place). Disney's own search returned a 404 in the browser, so interior prices are reseller "from" prices (`published`), other cabins `unavailable`, port times `published` (third-party).
- Seattle refresh of the cheapest sailing per line (Voyager May 28, Carnival May 25, Bliss May 29, Star Princess May 30, Edge Jun 4, Eurodam May 29 interior): Carnival down $15–30 pp, Bliss balcony up $50 pp, the rest unchanged.
- `lines[].alaskaNotes` (+ `alaskaNotesSources`, `glacierBayPermit`) for all 10 lines. Only Princess, HAL and Norwegian among the big lines can enter Glacier Bay.
- `linesReviewed`: Crystal, Silversea, Seabourn, Explora, Viking, Regent/Oceania one-liners and a small-ship paragraph (UnCruise, Lindblad, Alaskan Dream, American Cruise Lines). Small-ship sample prices are kept in notes only.
- Scripts (idempotent): `tools/p1_add_ncl_jade.py`, `p1_add_disney.py`, `p1_refresh_seattle.py`, `p1_line_notes.py`.

## Route families confirmed
SEA-GB 16 · SEA-DAWES 32 · SEA-TRACY 16 · SEA-HUBBARD 1 · SEA-NONE 1 · YVR-RT 34 · YVR-N 25 · YVR-S 27. Every itinerary has a route family.

## Cheapest two-cabin (interior + balcony, 2 adults each, incl. taxes, no tips)
Serenade YVR May 30 $4,298 · Voyager SEA May 28 $4,302 · Carnival SEA May 25 $4,316 · Solstice SB May 28 $4,404 · Noordam SEA May 23 $4,456.

## Not captured / caveats
- Port times not first-party/complete: Anthem SB with Ketchikan (Jun 18), Summit Hubbard (from a Sep sailing), Disney (third-party), MSC/Virgin/Oceania (v1).
- Disney balcony prices; Disney gratuity. Retry Disney on a normal computer (the Disney cruise search may work outside the app's browser).
- Glacier Bay/Hubbard scenic days on NCL have no listed hours. New itineraries have no `mapLine` (P6). New ships lack built/guests (P5).
- HAL Eurodam balcony was not re-read (checked 2026-11-06).

## Next
P2–P5 can start (parallel chats OK; pull before editing prices.json). P4 should add Haines and Stikine Icecap to its port/glacier list.
Kickoff: "Phase 2 of the Alaska 2027 v2 plan. Repo mattchurchman/alaska-2027: read PLAN.md and handoffs/phase1.md there. Do only Phase 2 and follow the rules section."
