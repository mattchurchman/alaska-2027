# Phase 5 raw notes (2026-11-07)

## How it was done
- The cloud shell cannot reach Wikimedia, YouTube or Wikipedia (proxy allowlist). WebFetch refused Commons pages. All lookups ran in the built-in browser pane on the moderator's computer, calling the Commons API, YouTube watch pages and the Wikipedia API from the page.
- Photo licensing/author/size: Commons API `extmetadata` (Artist, LicenseShortName), per file. Licenses used: CC BY 2.0/3.0/4.0, CC BY-SA 2.0/3.0/4.0, Public domain.
- Videos: YouTube search "<ship> ship tour", top results filtered to 6-70 min and ship name in title; exact publish date from each watch page; two per ship (Disney Magic one). Picks favour 2025-2026, official lines where present. Skipped a news-style "MSC Poesia detained" video.
- Ship facts: Wikipedia infobox via API. Capacity basis differs by ship, so `guestsSource` says which. Only Celebrity Solstice showed a refit (15 Jan - 2 Mar 2026).

## Official ship pages
Loaded (HTTP 200 in browser): Royal Princess, all NCL, all RCI, all Celebrity, Eurodam (/0), Westerdam (/8), Noordam (/7). Listed on the line's own index/nav: other Princess, Carnival, Disney. Search-only (not opened): MSC Poesia, Brilliant Lady, Riviera. HAL URLs without the trailing number return a bare shell page, so the numbered paths are stored.

## Photo choices worth a look
- Prince Rupert photo is portrait (mariner statue); Haines photo is a wide panorama; Sitka NHP photo is portrait. Crop with object-fit.
- Totem Bight photo is an old historic photo (public domain), not a current view.
- Ship photos are the same ship class/name but not all taken in Alaska (e.g. Crown Princess at Fremantle, Disney Wonder at Sydney). Discovery Princess (Juneau), Coral Princess (Alaska) and Westerdam (Skagway) are Alaska shots.
- Experience cards: only whale watching (2 experiences) and the lumberjack show have their own photos; others should fall back to their `poi` photo, then the port photo.

## Not found
- No Commons photo for Stikine Icecap (searched Icecap, Icefield, Shakes Glacier) or the Ketchikan Rainforest Sanctuary. Recorded in `media.placeholders`.
- Island Princess: no Wikipedia ship page matched; built year and guests left empty. Disney Wonder guests left empty (Wikipedia 2,713 is probably maximum occupancy).
- Accessible-cabin notes per ship: not captured. Needs each line's accessibility page; do it in P6/P8 or a follow-up.
- Refit dates after which each video was made: not checked except Solstice (videos are Jun-Jul 2026, after its Jan-Mar 2026 refit).
- Link check: `tools/linkcheck.py` could not run here. Photo file pages and YouTube links came straight from live Commons/YouTube responses today.
