"""P5: ship quick facts + official ship page links. Idempotent; only fills fields that are empty.

Facts: English Wikipedia ship infoboxes, read 2026-11-07 (year in service/completed, passenger capacity, refit).
Capacity basis varies by ship (double occupancy vs maximum) and is labelled in guestsSource.
Official links: ship pages on each line's own site. `verified` says how: 'loaded' (fetched in a browser, HTTP 200),
'listed' (linked from the line's own ship index/navigation), 'search' (returned by a search limited to the line's domain; not opened).
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from common import load, save

CHECKED = "2026-11-07"
WP = "Wikipedia ship infobox, read 2026-11-07"

# ship id: (built, builtSource, guests, guestsSource, refit)
FACTS = {
 "eurodam": (None, None, 2104, WP + " (passengers)", None),
 "voyager_of_the_seas": (None, None, 3602, WP + " (double occupancy; max 4,000)", None),
 "brilliant_lady": (None, None, 2770, WP, None),
 "emerald_princess": (2007, WP + " (christened May 2007)", None, None, None),
 "crown_princess": (2006, WP + " (completed 26 May 2006)", 3080, WP, None),
 "discovery_princess": (2022, WP + " (completed 27 Jan 2022)", 3660, WP + " (passengers)", None),
 "westerdam": (2004, WP + " (in service 2004)", 1964, WP + " (passengers)", None),
 "noordam": (2006, WP + " (in service 2006)", 1916, WP + " (passengers)", None),
 "serenade_of_the_seas": (2003, WP + " (completed July 2003)", 2490, WP + " (passengers)", None),
 "anthem_of_the_seas": (2015, WP + " (completed 10 Apr 2015)", 4180, WP + " (double occupancy; max 4,905)", None),
 "celebrity_summit": (2001, WP + " (in service Nov 2001)", 2158, WP + " (lower berths; all berths 2,218)", None),
 "celebrity_solstice": (2008, WP + " (completed Oct 2008)", 2852, WP, "15 Jan 2026 to 2 Mar 2026 (Wikipedia infobox; scope not checked)"),
 "norwegian_jade": (2006, "Commons category 'Norwegian Jade (ship, 2006)'", 2402, WP + " (max 3,590)", None),
 "disney_wonder": (1999, WP + " (completed 17 Jun 1999)", None, None, None),
 "disney_magic": (1998, WP + " (completed 30 Jun 1998)", 1750, WP + " (double occupancy; max 2,713)", None),
}

# ship id -> (url, verified)
P, N, R, C, H = "princess", "ncl", "rci", "celebrity", "hal"
LINKS = {
 "royal_princess": ("https://www.princess.com/ships-and-experience/ships/rp-royal-princess", "loaded"),
 "star_princess": ("https://www.princess.com/ships-and-experience/ships/st-star-princess", "listed"),
 "emerald_princess": ("https://www.princess.com/ships-and-experience/ships/ep-emerald-princess", "listed"),
 "crown_princess": ("https://www.princess.com/ships-and-experience/ships/kp-crown-princess", "listed"),
 "discovery_princess": ("https://www.princess.com/ships-and-experience/ships/xp-discovery-princess", "listed"),
 "coral_princess": ("https://www.princess.com/ships-and-experience/ships/co-coral-princess", "listed"),
 "island_princess": ("https://www.princess.com/ships-and-experience/ships/ip-island-princess", "listed"),
 "eurodam": ("https://www.hollandamerica.com/en/us/cruise-ships/eurodam/0", "loaded"),
 "westerdam": ("https://www.hollandamerica.com/en/us/cruise-ships/westerdam/8", "loaded"),
 "noordam": ("https://www.hollandamerica.com/en/us/cruise-ships/noordam/7", "loaded"),
 "norwegian_encore": ("https://www.ncl.com/cruise-ships/norwegian-encore", "loaded"),
 "norwegian_bliss": ("https://www.ncl.com/cruise-ships/norwegian-bliss", "loaded"),
 "norwegian_joy": ("https://www.ncl.com/cruise-ships/norwegian-joy", "loaded"),
 "norwegian_jade": ("https://www.ncl.com/cruise-ships/norwegian-jade", "loaded"),
 "voyager_of_the_seas": ("https://www.royalcaribbean.com/cruise-ships/voyager-of-the-seas", "loaded"),
 "quantum_of_the_seas": ("https://www.royalcaribbean.com/cruise-ships/quantum-of-the-seas", "loaded"),
 "serenade_of_the_seas": ("https://www.royalcaribbean.com/cruise-ships/serenade-of-the-seas", "loaded"),
 "anthem_of_the_seas": ("https://www.royalcaribbean.com/cruise-ships/anthem-of-the-seas", "loaded"),
 "celebrity_edge": ("https://www.celebritycruises.com/cruise-ships/celebrity-edge", "loaded"),
 "celebrity_summit": ("https://www.celebritycruises.com/cruise-ships/celebrity-summit", "loaded"),
 "celebrity_solstice": ("https://www.celebritycruises.com/cruise-ships/celebrity-solstice", "loaded"),
 "carnival_legend": ("https://www.carnival.com/cruise-ships/carnival-legend", "listed"),
 "carnival_spirit": ("https://www.carnival.com/cruise-ships/carnival-spirit", "listed"),
 "msc_poesia": ("https://www.msccruisesusa.com/ships/msc-poesia", "search"),
 "brilliant_lady": ("https://www.virginvoyages.com/ships/brilliant-lady", "search"),
 "oceania_riviera": ("https://www.oceaniacruises.com/ships/riviera", "search"),
 "disney_wonder": ("https://disneycruise.disney.go.com/ships/wonder/", "listed"),
 "disney_magic": ("https://disneycruise.disney.go.com/ships/magic/", "listed"),
}

if __name__ == "__main__":
    d = load()
    ships = {s["id"]: s for s in d["catalog"]["ships"]}
    nf = 0
    for sid, (built, bsrc, guests, gsrc, refit) in FACTS.items():
        s = ships[sid]
        if built and not s.get("built"):
            s["built"] = built; s["builtSource"] = bsrc; nf += 1
        if guests and not s.get("guests"):
            s["guests"] = guests; s["guestsSource"] = gsrc; nf += 1
        if refit:
            s["refit"] = refit; s["refitSource"] = WP
    m = d["media"]
    have = {o["id"] for o in m["officialLinks"]}
    nl = 0
    for sid, (url, ver) in LINKS.items():
        oid = f"ol-ship-{sid}"
        if oid in have:
            continue
        m["officialLinks"].append({"id": oid, "title": f"{ships[sid]['name']} on the cruise line's site", "url": url,
                                   "for": [f"ship:{sid}"], "verified": ver, "checked": CHECKED})
        nl += 1
    save("catalog", d["catalog"]); save("media", m)
    print("ship facts set", nf, "| official links added", nl, "| total", len(m["officialLinks"]))
