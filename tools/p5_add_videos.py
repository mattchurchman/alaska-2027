"""P5: add YouTube ship-tour videos to data/media.json. Idempotent.

Found 2026-11-07 by YouTube search ("<ship> ship tour"); exact publish dates read from each watch page.
These are third-party videos, not cruise-line promises. None were checked against refit dates (see notes/phase5.md).
Row: ship id, video id, title, channel, published, length.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from common import load, save

CHECKED = "2026-11-07"
V = [
 ["royal_princess","We4YsYePM4c","ROYAL PRINCESS - Complete Full 4K Tour of Royal Princess Cruise Ship!","Chris Frame the Maritime Historian","2025-11-18","12:42"],
 ["royal_princess","IWumvBF7gNw","ROYAL PRINCESS DECK BY DECK | FULL INTERIOR & EXTERIOR TOUR","The Port Lowdown","2026-02-15","44:23"],
 ["star_princess","amdSB9XdYD4","Star Princess Cruise Ship Full Tour | Princess Cruises","Princess Cruises","2025-10-28","10:03"],
 ["star_princess","y7RcuNrO1_Q","Star Princess | Full Walkthrough Ship Tour & Review | Brand New 2026 | Princess Cruise Lines","Cruises It","2026-01-03","24:27"],
 ["eurodam","jyD6NdWg9MY","Eurodam - Full Ship Tour and Review of this Holland America Cruise Ship","Let's All Cruise","2026-10-31","12:20"],
 ["eurodam","dNCaFssftO8","Holland America Eurodam Ship Tour for 2025!","The Port Lowdown","2025-02-23","31:30"],
 ["norwegian_encore","PmA4dFAMcuU","Norwegian Encore | Full Walkthrough Ship Tour & Review | Watch before booking","Cruises It","2025-10-25","32:48"],
 ["norwegian_encore","OTKMoyAJqBk","Norwegian Encore Full Ship Tour & Walkthrough: Spice H20, New Dining, Free at Sea, & New Spaces","Freestyle Travelers","2025-01-19","31:00"],
 ["norwegian_bliss","PLiia3x1tUw","Norwegian Bliss Full Ship Tour & Walkthrough | New Menus, Restaurants & Venues | NCL Bliss Alaska","Freestyle Travelers","2026-02-27","20:23"],
 ["norwegian_bliss","Tm9IwCZ3iO0","Norwegian Bliss | Full Walkthrough Ship Tour & Review | Cabins and Haven Area | After Dry Dock 2025","Cruises It","2025-08-03","30:53"],
 ["norwegian_joy","nXeynf91Y7g","THIS Cruise Ship Has EVERYTHING! Norwegian Joy: Complete Ship Tour","EECC Travels","2025-09-11","21:26"],
 ["norwegian_joy","JVS5vRM_EqU","Norwegian Joy Ship Tour - NEW for 2024 + MUST-KNOW tips!","CruiseTipsTV","2024-04-25","22:49"],
 ["voyager_of_the_seas","dsxwSt9IBMw","Voyager of the Seas | Full Walkthrough Ship Tour & Review with Cabins Suites |Royal Caribbean","Cruises It","2025-03-30","25:27"],
 ["voyager_of_the_seas","J_EgH_0TedE","Royal Caribbean Voyager of The Seas Full Walkthrough Tour & Review 2025","The Leckie Lifestyle","2025-01-31","16:46"],
 ["quantum_of_the_seas","EbdtOw_QqOE","Quantum of the seas | Full Walkthrough Ship Tour & Review | Ultra 4 Royal Caribbean Cruises","Cruises It","2025-11-09","24:44"],
 ["quantum_of_the_seas","Zw0IAWxx5Gk","Quantum of the Seas Full Ship Tour. A tour of this Royal Caribbean cruise ship","Let's All Cruise","2026-01-16","18:26"],
 ["celebrity_edge","ilrvKOkjYz8","Celebrity Edge Ship Tour: Suites, Dining and Onboard Experiences | Celebrity Cruises","Celebrity Cruises","2024-08-05","15:41"],
 ["celebrity_edge","Q2L7fgs8YVc","Celebrity Edge | Full Walkthrough Ship Tour & Review | Ultra HD | 2023 New | Celebrity Cruise Lines","Cruises It","2023-10-04","11:29"],
 ["carnival_legend","-kcCPYaufR8","Carnival Legend Cruise Ship Tour (NEW for 2026!)","CruiseTipsTV","2026-07-05","15:40"],
 ["carnival_legend","x1a3U5zCDow","Is the Carnival Legend Cruise Ship Legendary? FULL SHIP TOUR 2025","Travel With Matt Taylor","2025-09-13","18:21"],
 ["carnival_spirit","qvY6ZOjsYRk","Carnival Spirit | Full Walkthrough Ship Tour | 4k 2024 New Video| Fully Renovated","Cruises It","2024-06-07","14:18"],
 ["carnival_spirit","VX_N1CX4PaQ","Ultimate Carnival Spirit Ship Tour - Every Deck Revealed!","Sea Trippin' w/ Kim and Scott","2025-02-23","41:06"],
 ["msc_poesia","Iru5f4iKd2M","Ship Tour of MSC Poesia | MSC Cruises","MSC Cruises Official","2026-07-30","8:25"],
 ["msc_poesia","GMU0dbsTIiQ","MSC Poesia | Full Walkthrough Ship Tour 4K | NEWLY Refurbished for 2026 | Alaska & Caribbean","Cruises It","2026-08-15","18:21"],
 ["brilliant_lady","VaxmqwZomzs","Brilliant Lady FULL Ship Tour [4K] - Virgin Voyages Ship Walkthrough","VV Insider | Virgin Voyages guides, info and news","2025-08-19","33:46"],
 ["brilliant_lady","juiqnJr2dRc","Brilliant Lady | Full Walkthrough Ship Tour & Review | 4K Ultra | \"Adults Only\" | Virgin Cruises","Cruises It","2025-10-04","22:16"],
 ["oceania_riviera","dtX8UyAOYk4","Oceania Riviera Cruise Ship Tour | Luxury Cruise Ship Walkthrough 4K","S.W. Black Travel","2025-12-30","22:37"],
 ["oceania_riviera","B6S6RzDpzds","Oceania RIVIERA Decked! All you need to know in 4K and a top to bottom tour...","Peter Knego's MidShipCinema","2026-08-08","38:13"],
 ["emerald_princess","MIVxuLAJL7Q","Emerald Princess | Full Walkthrough Cruise Ship Tour & Review | Is this ship worth it?","Cruises It","2026-08-22","19:45"],
 ["emerald_princess","AILN0YzFJek","Emerald Princess: Full Ship Tour & Honest Review","Right Direction Adventures","2026-02-06","16:44"],
 ["crown_princess","vB0e-L9aWbo","FULL SHIP TOUR 2026 | Crown Princess","The Aussie Globetrotter","2026-03-16","13:01"],
 ["crown_princess","UkqHWTRG7C4","CROWN PRINCESS - Complete Full HD Tour of Crown Princess Cruise Ship","Chris Frame the Maritime Historian","2025-08-06","11:50"],
 ["discovery_princess","Ls-s2v8qsYI","Discovery Princess Full Ship Tour & Review | Everything You Need to See Before You Cruise","Cruises It","2026-09-13","16:57"],
 ["discovery_princess","_pMXJMXMpfY","NEW Discovery Princess Ship Tour - INSIDE LOOK!","CruiseTipsTV","2025-08-03","21:24"],
 ["coral_princess","ma3w6QejQEw","Coral Princess Full Walkthrough Tour and Review | Is This Princess Ship Worth It?","Cruises It","2026-09-06","18:44"],
 ["coral_princess","Q6DKeYVF2-k","Coral Princess Ship Tour 2026 - Full Narrated Deck-By-Deck Video Tour With Deck Plans - ParoDeeJay","ParoDeeJay","2026-02-02","20:33"],
 ["island_princess","D0SDpmw0DYA","Island Princess Full Cruise Ship Tour, Restaurants, Bars, Entertainment Venues & Facilities 2026","TPosition Travelogue","2026-02-13","23:56"],
 ["island_princess","VKPEkRPPwGM","Complete Island Princess Ship Tour - Fully Narrated","A Cruising Good Time","2025-03-07","29:26"],
 ["westerdam","cJxkW10Bpu8","Holland America Westerdam | Full Deck by Deck Cruise Ship Tour HD","Destination 4 Vacation","2025-08-23","32:13"],
 ["westerdam","VpZ_UVvPd8U","FULL SHIP TOUR: Holland America Line MS Westerdam (Alaska Cruise 2025)","Two Old Men (At Heart)","2025-10-26","21:58"],
 ["noordam","LESARFkGPSg","Holland America Line | MS Noordam Walking Ship Tour","Andrew Bibay","2026-02-20","15:10"],
 ["noordam","G27x38ZSOWg","Holland America Noordam | Deck by Deck Ship Tour | Destination 4 Vacation","Destination 4 Vacation","2025-06-30","33:48"],
 ["serenade_of_the_seas","-pPQALa_YGc","Serenade of the Seas Ship Tour | What’s Onboard?","Wandering Hewitts","2026-08-09","17:20"],
 ["serenade_of_the_seas","ebHtiUR56-g","Serenade of the Seas Cruise Ship Tour – What’s Onboard in 2025?","Amy's Turnkey Travel","2025-02-10","30:40"],
 ["anthem_of_the_seas","WndVHEv4gCY","Anthem of the Seas Full Ship Tour - Complete Cruise Ship Guide! | Royal Caribbean","The Curious Tourists","2025-09-10","12:04"],
 ["anthem_of_the_seas","uDMgtLTFqHQ","Anthem of the Seas Full Ship Tour & Review | Royal Caribbean | 4K","Harr Travel","2025-07-19","34:11"],
 ["celebrity_summit","987fuoLhFAE","Celebrity Summit Full Ship Walkthrough Tour & Review | Complete Deck-by-Deck Tour 2026","Cruises It","2026-10-11","18:53"],
 ["celebrity_summit","J2eQN_YKP1c","Celebrity Summit Ship Tour: Suites, Dining and Onboard Experiences | Celebrity Cruises","Celebrity Cruises","2024-08-05","9:48"],
 ["celebrity_solstice","-D6bJDomCsY","*RENEWED* Celebrity Solstice Cruise Ship Full Tour & Review (Best Spots Revealed!)","JJ Cruise","2026-06-07","25:59"],
 ["celebrity_solstice","5lFKjkSpFDI","REVITALIZED! Celebrity Solstice | 2026 Full Walkthrough Ship Tour & Review 4K | Celebrity Cruises","Harr Travel","2026-07-08","30:40"],
 ["norwegian_jade","y7KhCCELZQ4","Norwegian Jade Full Ship Tour (2026) | Complete Walkthrough","MIKE ON THE MOVE","2026-04-19","16:05"],
 ["norwegian_jade","RjDqWl8AvJ8","Norwegian Jade | Full Ship Walkthrough Tour | 2025 | 4K","Harr Travel","2025-09-14","32:40"],
 ["disney_wonder","oCZCYT1ns50","FULL 2025 Disney Wonder Alaska Ship Tour","Window Seat","2025-05-16","16:00"],
 ["disney_wonder","6Fx1eBg7RX0","Disney Wonder Full Ship Tour 2025 - Including NEW Changes!","Cruise With Ben and David","2025-01-01","26:13"],
 ["disney_magic","XKUdyt14bdg","Disney Magic Cruise Ship Overview | What to Know Before You Go","Take2Travel","2026-10-02","15:49"],
]

if __name__ == "__main__":
    d = load()
    m = d["media"]
    have = {v["id"] for v in m["videos"]}
    n = 0
    for ship, vid, title, ch, pub, ln in V:
        vid_id = "vid-" + vid
        if vid_id in have:
            continue
        m["videos"].append({
            "id": vid_id, "videoId": vid, "title": title, "channel": ch, "published": pub, "length": ln,
            "url": f"https://www.youtube.com/watch?v={vid}",
            "embed": f"https://www.youtube-nocookie.com/embed/{vid}",
            "for": [f"ship:{ship}"], "checked": CHECKED,
        })
        n += 1
    save("media", m)
    print("added", n, "videos; total", len(m["videos"]))
