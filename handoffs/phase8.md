# Phase 8 handoff - QA and release - PARTIAL (2026-11-07)

## Done
- `validate.py`: OK (0 errors, 0 warnings). Counts: 815 price rows (516 verified, 185 published, 9 estimate, 105 unavailable), 152 sailings, 56 experiences / 149 offers, 67 photos, 55 videos, 103 sources.
- `make_csv.py`: csv/all-sailings.csv (152 rows) and csv/by-line.csv (10 rows) regenerate with no diff.
- Headless Chrome (system Chrome via Playwright, local http.server) at 390, 820, 1180, 1280 over Ideas, Route, Ship, Dates, Days, Cost, Shortlist: no horizontal scroll, no JS errors. Only console errors are photo/tile loads blocked by the workspace network (ERR_TUNNEL_CONNECTION_FAILED), so photos and OSM tiles were NOT visually checked here.
- Tap targets: Dates calendar dots are 32 px tall with a 48 px hit area (::after). Inline text links are small by design.
- New: README.md rewritten (use, share, refresh, gaps); docs/DEVICE-TEST.md (10-task iPhone/iPad script).

## Not done / caveats
- `linkcheck.py`: workspace reaches almost no sites (15 of 15 sampled unreachable). Run on a normal computer: `python3 tools/linkcheck.py`.
- Safari/WebKit not tested. Moderator device test (docs/DEVICE-TEST.md) pending; fix whatever comes back.
- Refresh-routine skill not proposed yet.
- P2 (arrival-city costs) and P4 (Sitka/Icy Strait/Victoria walking miles, glacier guide) still open; README lists them as gaps.
- Moderator still needs to confirm GitHub Pages is on and the P0 iPhone smoke check.

## Next
Moderator runs docs/DEVICE-TEST.md; send results back to a P8 chat to fix. Then propose the refresh skill.
