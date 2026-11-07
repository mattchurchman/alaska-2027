# Phase 5 handoff - media - DONE (2026-11-07)

## What changed (media.json: photos 27 -> 67, videos 0 -> 55, officialLinks 0 -> 28; validate OK)
- 40 new Commons photos, each with author, license, file page, alt text, width/height, checked date. Now every ship (28), every port/scenic place except Stikine Icecap, and every attraction (`poi`) except the Ketchikan Rainforest Sanctuary has a photo. Those two are listed in `media.placeholders` (deliberate placeholder, with reason).
- Photo `for` targets: `ship:`, `place:`, `poi:`, plus `experience:` for whale watching (jnu_whale, jnu_mdh_whale) and the lumberjack show (ktn_lumber). Other experiences should use their `poi`, then the port photo.
- 55 YouTube ship tours (2 per ship, 1 for Disney Magic): title, channel, exact publish date, length, watch URL and `embed` (youtube-nocookie). All 28 ships have 1+.
- 28 official ship-page links in `officialLinks` with `verified`: loaded / listed / search (see notes/phase5.md).
- Ship facts filled where the infobox was clear: `built`, `builtSource`, `guests`, `guestsSource` (capacity basis labelled), `refit` (Solstice only).
- Scripts (idempotent): tools/p5_add_photos.py, p5_add_videos.py, p5_add_ship_facts.py.

## Not captured
- Island Princess built/guests; Disney Wonder guests.
- Accessible-cabin notes per ship (needs each line's accessibility page).
- Whether each video post-dates the ship's last refit (only Solstice checked).
- linkcheck.py could not run in the cloud shell; run it on a normal computer (P8).
- Experience-specific photos beyond whales and lumberjack show.

## Notes for P6
- Photos use Special:FilePath URLs (width=1000). Prince Rupert and Sitka NHP images are portrait, Haines is a wide panorama: use object-fit: cover.
- Videos: render a tap-to-load poster, load the `embed` URL on tap. Show channel and publish date; they are third-party videos.
- Ship cards: built year and guests come from `ships[]`; show `guestsSource` basis (double occupancy vs max).

## Next
P6 App A (Opus 5.5, high): "Phase 6 of the Alaska 2027 v2 plan. Repo mattchurchman/alaska-2027: read PLAN.md and handoffs/phase5.md there. Do only Phase 6 and follow the rules section." P2 and P4 handoffs are still outstanding; P6 can start without P2 if arrival-city costs are shown as unavailable.
