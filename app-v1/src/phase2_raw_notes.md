# Phase 2 raw capture (excursions), checked 2026-11-06, Denver

All prices are "published, not date-verified": read on provider pages with no 2027 sailing selected. Nothing is labeled verified.

## What was captured
- Princess: first listing page per port (Juneau 12 of 63, Skagway 12 of 51, Ketchikan 12 of 53, Sitka 12 of 41, Icy Strait 12 of 20). "From" prices per person, activity level, "Wheelchair Accessible" flag in titles.
- Carnival: 4 pages with adult (13+) price, level, accessibility text (whale quest $220.99, Mendenhall quest $263.99, ZipRider $196.99 "from", Rainforest Sanctuary $140.99).
- NCL (USD pages): White Pass railway $249.99 from, Mendenhall & Whale Quest $269.99 from, Scenic Juneau & Hatchery $109.99 from; 48 h free cancellation text. Lumberjack Show page has no price. Totem Bight page readable only on the French site in EUR (134.40), so not used as USD.
- Operators direct: WP&YR (Summit $155, Steam Summit Loop $249, Bennett $289, Whitehorse combo $175, Fraser $108, Carcross $210), Frontier Excursions (Summit & City $77.70, Yukoner $140.70, Yukon Discovery $175.35; 24 h cancellation; vehicles not wheelchair accessible), True Alaskan Tours/Allen Marine ("from" prices: Juneau whale $159, Tracy Arm-Fords Terror $289 weekend, Sitka whale/otter $169, Ketchikan Waterfront & Wildlife $109, Misty Fjords & Wilderness Explorer $219), Goldbelt Tram $60, Alaska Raptor Center $17, Forest Service Mendenhall $5 (proposal: $15), NPS Skagway and Sitka free.
- Reseller Alaska Shore Excursions (alaskashoreexcursions.com): full per-port listings (Juneau 49, Skagway 37, Ketchikan 50, Sitka 30 tours). A selection of 51 offers is in data.json. Operator names are not shown on the listing pages. Site-wide "Free Cancellation" label only.

## Key findings
- Goldbelt Tram (Mount Roberts) was closed all of 2026 after an April crash; Goldbelt targets 2027 but needs state certification and a replacement part (KTOO Sep 24, 2026). Do not plan around it.
- Mendenhall visitor center day fee is $5 now (FS page, Jul 2025); Forest Service proposed $15 per person (comment period to Jul 20, 2026; no effective date; not approved as of the articles read). Ketchikan Discovery Center $5 to $10 also proposed.
- White Pass train: operator direct $155 vs about $250 on cruise lines (Princess lists Premium Class; NCL class not stated), so the gap may not be like-for-like.
- ZipRider: operator says reservations generally must go through the cruise line, so no independent price.
- Many Juneau/Ketchikan tours of 5+ hours do not fit the usable time on some routes: the app flags this per route ("Fits X of Y routes").

## Blocked or failed (do not retry the same way)
Era, Temsco, Gastineau Guiding, Capital Transit (robots.txt). Taquan Air, Butchart tickets, Icy Strait Point tours page, Holland America port page, Royal Caribbean and Celebrity port pages, NPS Glacier Bay, Alaska State Parks Totem Bight (page errors). lumberjackshow.com redirected to an unrelated ad domain; the redirect was not followed.

## Not captured (candidates for a later refresh)
HAL, RCI, Celebrity, MSC, Virgin, Oceania cruise-line excursion prices. Princess listing pages 2+. Icy Strait whale watching prices. Victoria excursions (Butchart). Walking distances dock to attractions. Per-operator cancellation and return-to-ship wording.

## To refresh prices
Edit offers in src/build_excursions.py (or data.json directly), then `python3 build_app.py`. Offers carry `pp`, `unit`, `from`, `status`, `source`, `url`, `checked`.
