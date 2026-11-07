# Phase 0 handoff — foundation and migration (done 2026-11-07)

Repo `mattchurchman/alaska-2027` (public, `main`). Site: https://mattchurchman.github.io/alaska-2027/ (setup test page).

## What changed
- v1 artifact files pulled into `app-v1/` (data.json, src/*, CSVs; built index.html not kept, rebuildable with app-v1/src/build_app.py).
- `data/` split per PLAN.md: catalog, prices (439 rows), experiences (43 / 130 offers), media (27 photos, 0 videos), travel (7 flights, 9 hotels, 3 gateways), sources (67), meta. `tools/migrate_v1.py` asserts rows = v1 price slots (439).
- Row status counts: verified 222, published 159, unavailable 50, estimate 8. Cabin rows are per cabin for 2 adults (v1 pp × 2). Spot-checks match v1: Voyager Jun 25 two-cabin $5,034 ($5,552 with tips), Carnival Legend Jun 1 $5,136.
- Route families seeded in catalog.json (8, with colors); all 14 v1 itineraries assigned (SEA-*). YVR-RT/YVR-N/YVR-S have no itineraries yet.
- Tools: validate.py (planted-error test caught all 6), query.py, make_csv.py (writes csv/), linkcheck.py, common.py.
- index.html: setup test (Wikimedia photo, Leaflet + OSM tiles with the HAL Glacier Bay route from data, tap-to-load youtube-nocookie video, data counts, self-check pills). Leaflet 1.9.4 bundled in vendor/.
- AGENTS.md, CLAUDE.md, PLAN.md (plan now lives here), README.md, docs/DECISIONS.md.

## Tested
Headless Chrome at 390/820/1280: no console errors, no horizontal scroll, data loads and route draws. Photo, tiles and video could not load in the cloud workspace (allowlist), so they are untested until the moderator's iPhone check.

## Not done / open
- GitHub Pages: the API is blocked from Claude's session. Moderator turns it on (Settings → Pages → Deploy from a branch → main, / (root) → Save).
- Moderator's iPhone Safari check of the setup page (done-when for P0).
- Agent-pipeline template not applied (repo not visible to Claude). Lean AGENTS.md instead.
- linkcheck.py can't reach outside sites from the cloud workspace; run it on a normal computer.
- Videos: the test video (AG2jFHq0_qE) is a placeholder for the smoke test only, not in media.json.

## Next: P1 (Opus 5.5, high) in the Claude app
"Phase 1 of the Alaska 2027 v2 plan. Repo mattchurchman/alaska-2027: read PLAN.md and handoffs/phase0.md there. Do only Phase 1 and follow the rules section."
