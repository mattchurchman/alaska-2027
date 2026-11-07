# Phase 6 handoff - App A (Ideas, Route, Line & ship, Dates) - DONE (2026-11-07)

## What changed
- New site at `index.html` (the P0 setup page moved to `setup-test.html`). Code: `app/model.js` (loads catalog, prices, media, meta, sources; price/time helpers), `app/ui.js` (4 screens, maps, share links), `app/app.css`, `app/icon.svg`. No build step; reads `data/*.json` directly.
- **Ideas:** hero photo, travelers, 4 quick answers (lowest two-cabin, lowest June, lowest with Glacier Bay, most Alaska time ashore), 8 route-family cards (photo, why, trade-off, sailings, lines, from-price + status), glacier cards with route chips.
- **Route:** Leaflet + OSM map, every itinerary drawn in its family colour (dashed = one-way), tap a line or legend to highlight a family; pins with photo popups; ships-on-route list with Ship / Dates buttons.
- **Line & ship:** grouped by line; "About X in Alaska" (alaskaNotes, includes, fare basis, deposit); ship cards with photo + credit, built/guests/size, "For the parents" (line accessibility, glacier day, Alaska docks), tap-to-load youtube-nocookie tours, official link, date buttons.
- **Dates:** sailing calendar (rows = ships grouped by route, pill = two-cabin fare, solid/striped/dashed by price status, June shaded), route chips, June-only toggle, mini map of the picked sailing, sailing panel (two-cabin total + tips estimate, 4 cabin rows with status/checked/source, flags, day-by-day times with usable hours, port-time source). Sticky pick bar shows the chosen sailing everywhere.
- **Share links:** `#view=…&route=…&ship=…&sailing=…&june=1`; Share button uses the iOS share sheet, else copies. Back button works. Last view remembered in localStorage.
- Data: `mapLine` for the 28 itineraries that had none (`tools/p6_map_lines.py`, schematic graph extended with the BC Inside Passage, Prince Rupert, Haines, Stikine, Gulf of Alaska, Prince William Sound, Resurrection Bay). Route-family `short`, `why`, `tradeoff`, `bestFor`, `textBasis` (`tools/p6_route_text.py`). No price rows changed. validate OK.

## Tested
Headless Chrome at 390/820/1180/1280 (touch at the first three): no console errors, no horizontal page scroll on any screen; Ideas → Route → Dates → pick works; share link restores the sailing in a fresh tab; back button; video tap loads the iframe; June filter; map pin popup. Photos, tiles and videos can't load in the cloud workspace, so only their placeholders were seen.

## Not done / caveats
- **Not tested in Safari.** Needs the moderator's iPhone/iPad check (P8 script). Uses `color-mix()` for striped pills (Safari 16.2+; older Safari shows plain white pills).
- Interface decision: stayed in the Claude app; Claude Code on the moderator's computer is not needed for P7. Revisit for P8 only if the device test finds WebKit-only bugs.
- Glacier guide (`meta.glacierGuide`) is empty until P4; Ideas shows a "still being researched" note and uses place notes. Arrival-city costs (P2) not shown yet.
- Cabin location (near elevators) still not in data; the ship card says to ask when booking.

## Next: P7 (Opus 5.5, high)
"Phase 7 of the Alaska 2027 v2 plan. Repo mattchurchman/alaska-2027: read PLAN.md and handoffs/phase6.md there. Do only Phase 7 and follow the rules section." Build Days/Cost/Shortlist on top of `app/model.js` (add experiences.json and travel.json to `FILES`); the pick bar is the place for the always-visible cost strip.
