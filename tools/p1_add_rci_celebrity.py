#!/usr/bin/env python3
"""Phase 1: add Royal Caribbean (Serenade RT Vancouver, Anthem Vancouver<->Seward) and Celebrity
(Summit RT Vancouver, Solstice Vancouver<->Seward) from notes/phase1.md (checked 2026-11-07).
Idempotent. Run from the repo root: python3 tools/p1_add_rci_celebrity.py
"""
import sys
sys.path.insert(0, "tools")
from common import load, save

CHECKED = "2026-11-07"
d = load()
c, P, S = d["catalog"], d["prices"]["rows"], d["sources"]["sources"]

def upsert(lst, rec):
    for i, r in enumerate(lst):
        if r["id"] == rec["id"]:
            lst[i] = rec
            return
    lst.append(rec)

upsert(c["places"], {"id": "seward", "name": "Seward, Alaska (cruise port for Anchorage)", "short": "Seward",
    "kind": "terminal", "country": "US", "tz": "America/Anchorage", "lat": 60.1042, "lng": -149.4422,
    "notes": "Resurrection Bay port about 125 mi (2.5-3 h) by road from Anchorage; the Alaska Railroad also runs Seward-Anchorage in summer. Used by Royal Caribbean, Celebrity, Norwegian and luxury lines for one-way Gulf of Alaska cruises.",
    "dock": "Dock", "coordBasis": "approximate"})
upsert(c["places"], {"id": "prince_rupert", "name": "Prince Rupert, British Columbia", "short": "Prince Rupert",
    "kind": "port", "country": "CA", "tz": "America/Vancouver", "lat": 54.3150, "lng": -130.3208,
    "notes": "Small northern BC port (Northland cruise terminal is downtown). Canadian port: passports needed.",
    "dock": "Dock", "coordBasis": "approximate"})
upsert(c["places"], {"id": "inside_passage_bc", "name": "Inside Passage (British Columbia), scenic cruising", "short": "Inside Passage",
    "kind": "scenic", "country": "CA", "tz": "America/Vancouver", "lat": 51.5, "lng": -127.8,
    "notes": "Sheltered coastal channels between Vancouver Island and the mainland; ships list a scenic-cruising day with no landing.",
    "dock": "Scenic cruising (no landing)", "coordBasis": "approximate"})

for sid, name, line in [("serenade_of_the_seas", "Serenade of the Seas", "rci"), ("anthem_of_the_seas", "Anthem of the Seas", "rci"),
                        ("celebrity_summit", "Celebrity Summit", "celebrity"), ("celebrity_solstice", "Celebrity Solstice", "celebrity")]:
    upsert(c["ships"], {"id": sid, "line": line, "name": name, "built": None, "guests": None, "guestsSource": None})

for src in [
    {"id": "rci_search_yvr_2027", "title": "Royal Caribbean cruise search: from Vancouver / Seward, May 15-Jul 10 2027 (date panels)",
     "url": "https://www.royalcaribbean.com/cruises?search=departurePort:YVR|startDate:2027-05-15~2027-07-10", "kind": "first-party",
     "publisher": "Royal Caribbean", "checked": CHECKED,
     "note": "'Pricing shown includes all taxes & fees', starting price avg per person for 2 guests per stateroom type. Tags '10% Off Resident Rate' (not applied) and 'Early Booking Bonus'."},
    {"id": "celebrity_search_yvr_2027", "title": "Celebrity cruise search: from Vancouver / Seward, May 15-Jul 10 2027 (date panels)",
     "url": "https://www.celebritycruises.com/cruises?search=departurePort:YVR|startDate:2027-05-15~2027-07-10", "kind": "first-party",
     "publisher": "Celebrity Cruises", "checked": CHECKED,
     "note": "'Pricing shown includes all taxes & fees', starting price avg per person, 2 guests. Promos shown: 75% Off 2nd Guest, Up to $1,000 Instant Savings."},
]:
    upsert(S, src)

V, SW = "yvr_canada_place", "seward"
def E(p, dep): return [{"type": "embark", "place": p, "dep": dep}]
def D(p, arr): return [{"type": "disembark", "place": p, "arr": arr}]
def Pt(p, a, b, tender=False):
    e = {"type": "port", "place": p, "arr": a, "dep": b}
    if tender:
        e["tender"] = True
    return [e]
def Sc(p, a=None, b=None): return [{"type": "scenic", "place": p, "arr": a, "dep": b}]
SEA = [{"type": "sea"}]
IP = Sc("inside_passage_bc")

ITS = [
    dict(id="rci_serenade_yvr_tracy", line="rci", ship="serenade_of_the_seas", routeFamily="YVR-RT",
         name="7 Night Alaska Inside Passage Cruise (Tracy Arm, Icy Strait Point, Sitka)", weekday="Sunday",
         glacier="Tracy Arm Fjord", glacierPlace="tracy_arm", timesStatus="verified",
         timesSource="Royal Caribbean itinerary page SR07A481 (Jun 6). Juneau is a TENDER call on this itinerary.",
         days=[E(V, "16:00"), IP, Sc("tracy_arm", "06:30", "10:30") + Pt("juneau", "13:30", "22:00", tender=True),
               Pt("icy_strait", "08:00", "18:00"), Pt("sitka", "07:00", "17:00"), Pt("ketchikan", "08:00", "17:00"), IP, D(V, "07:00")]),
    dict(id="rci_serenade_yvr_rupert", line="rci", ship="serenade_of_the_seas", routeFamily="YVR-RT",
         name="7 Night Alaska Inside Passage Cruise (Sitka, Tracy Arm, Ketchikan, Prince Rupert)", weekday="Sunday",
         glacier="Tracy Arm Fjord", glacierPlace="tracy_arm", timesStatus="verified",
         timesSource="Royal Caribbean itinerary page SR07A482 (May 30)",
         days=[E(V, "16:00"), IP, Pt("sitka", "10:30", "20:00"), Sc("tracy_arm", "06:30", "10:30") + Pt("juneau", "13:30", "21:30"),
               Pt("ketchikan", "14:30", "22:00"), Pt("prince_rupert", "07:00", "17:00"), SEA, D(V, "07:00")]),
    dict(id="rci_anthem_nb_icy", line="rci", ship="anthem_of_the_seas", routeFamily="YVR-N",
         name="7 Night Northbound Alaska & Hubbard Glacier (Icy Strait Point)", weekday="Friday",
         glacier="Hubbard Glacier", glacierPlace="hubbard", timesStatus="verified",
         timesSource="Royal Caribbean itinerary page AN07A463 (May 28). Ketchikan call is at Ward Cove.",
         days=[E(V, "17:00"), SEA, Pt("ketchikan_wc", "07:00", "18:00"), Pt("icy_strait", "11:59", "21:00"), Pt("sitka", "07:00", "16:00"),
               Pt("skagway", "07:00", "16:00"), Sc("hubbard", "07:00", "11:00"), D(SW, "05:00")]),
    dict(id="rci_anthem_nb_juneau", line="rci", ship="anthem_of_the_seas", routeFamily="YVR-N",
         name="7 Night Northbound Alaska & Hubbard Glacier (Juneau)", weekday="Friday",
         glacier="Hubbard Glacier", glacierPlace="hubbard", timesStatus="verified",
         timesSource="Royal Caribbean itinerary page AN07A465 (Jun 11). Ketchikan call is at Ward Cove.",
         days=[E(V, "17:00"), SEA, Pt("ketchikan_wc", "07:00", "17:00"), Pt("sitka", "07:00", "17:00"), Pt("juneau", "08:00", "20:00"),
               Pt("skagway", "07:00", "16:00"), Sc("hubbard", "07:00", "11:00"), D(SW, "05:00")]),
    dict(id="rci_anthem_sb", line="rci", ship="anthem_of_the_seas", routeFamily="YVR-S",
         name="7 Night Southbound Alaska & Hubbard Glacier", weekday="Friday",
         glacier="Hubbard Glacier", glacierPlace="hubbard", timesStatus="verified",
         timesSource="Royal Caribbean itinerary page AN07A464/AN07A468 (Jul 2)",
         days=[E(SW, "20:00"), Sc("hubbard", "13:00", "17:00"), Pt("juneau", "09:00", "20:00"), Pt("skagway", "07:00", "20:00"),
               Pt("icy_strait", "07:00", "18:00"), SEA, SEA, D(V, "06:00")]),
    dict(id="rci_anthem_sb_ketchikan", line="rci", ship="anthem_of_the_seas", routeFamily="YVR-S",
         name="7 Night Southbound Alaska & Hubbard Glacier (with Ketchikan)", weekday="Friday",
         glacier="Hubbard Glacier", glacierPlace="hubbard", timesStatus="unavailable",
         timesSource="Search card lists Seward, Hubbard, Juneau, Skagway, Icy Strait Point, Ketchikan, Vancouver. The June itinerary page (AN07A462) redirected to a September sailing, so June port times were not captured.",
         days=[E(SW, None), Sc("hubbard"), Pt("juneau", None, None), Pt("skagway", None, None), Pt("icy_strait", None, None),
               Pt("ketchikan", None, None), SEA, D(V, None)]),
    dict(id="celebrity_summit_yvr_dawes", line="celebrity", ship="celebrity_summit", routeFamily="YVR-RT",
         name="7 Night Alaska Dawes Glacier (round trip Vancouver)", weekday="Sunday",
         glacier="Endicott Arm & Dawes Glacier", glacierPlace="endicott_arm", timesStatus="verified",
         timesSource="Celebrity itinerary page SM07A447 (Jun 6)",
         days=[E(V, "16:30"), IP, Sc("endicott_arm", "13:00", "18:00"), Pt("skagway", "07:00", "20:00"), Pt("juneau", "07:00", "18:00"),
               Pt("ketchikan", "13:30", "20:00"), IP, D(V, "07:00")]),
    dict(id="celebrity_summit_yvr_hubbard", line="celebrity", ship="celebrity_summit", routeFamily="YVR-RT",
         name="7 Night Alaska Hubbard Glacier (round trip Vancouver)", weekday="Sunday",
         glacier="Hubbard Glacier", glacierPlace="hubbard", timesStatus="published",
         timesSource="Times from a Sep 5, 2027 sailing of the same itinerary (SM07A453); the June page redirected there. June times not confirmed.",
         days=[E(V, "16:30"), IP, Pt("icy_strait", "15:30", "21:00"), Sc("hubbard", "09:30", "14:00"), Pt("juneau", "07:00", "18:00"),
               Pt("ketchikan", "13:30", "20:00"), IP, D(V, "07:00")]),
    dict(id="celebrity_solstice_nb", line="celebrity", ship="celebrity_solstice", routeFamily="YVR-N",
         name="7 Night Alaska Northbound Glacier", weekday="Friday",
         glacier="Endicott Arm + Hubbard Glacier", glacierPlace="hubbard", timesStatus="verified",
         timesSource="Celebrity itinerary page SL07A443 (Jun 18)",
         days=[E(V, "16:00"), IP, Pt("sitka", "09:30", "17:30"), Sc("endicott_arm", "09:00", "15:00"), Pt("icy_strait", "07:00", "17:00"),
               Pt("juneau", "07:00", "16:30"), Sc("hubbard", "07:00", "11:00"), D(SW, "06:00")]),
    dict(id="celebrity_solstice_sb", line="celebrity", ship="celebrity_solstice", routeFamily="YVR-S",
         name="7 Night Alaska Southbound Glacier", weekday="Friday",
         glacier="Hubbard Glacier", glacierPlace="hubbard", timesStatus="verified",
         timesSource="Celebrity itinerary page SL07A442 (May 28)",
         days=[E(SW, "20:00"), Sc("hubbard", "15:00", "18:00"), Pt("juneau", "10:00", "21:00"), Pt("skagway", "07:00", "19:30"),
               Pt("icy_strait", "07:00", "17:00"), Pt("ketchikan", "10:30", "19:30"), IP, D(V, "07:00")]),
]
for it in ITS:
    it.update(mapLineBasis=None, addedIn="p1")
    upsert(c["itineraries"], it)

CATS = ["interior", "oceanview", "balcony", "miniSuite"]
LBL = {"rci": ["Interior", "Outside View", "Balcony", "Suite"], "celebrity": ["Inside", "Ocean View", "Veranda", "Concierge Class"]}
BASIS = {"rci": "Cabin for 2 adults (pp x 2). Starting price per stateroom type, average per person for 2 guests, includes taxes & fees (Royal Caribbean date panel). Gratuities not included.",
         "celebrity": "Cabin for 2 adults (pp x 2). Starting price per stateroom type, average per person for 2 guests, includes taxes & fees (Celebrity date panel; promo pricing). Gratuities not included."}
SRC = {"rci": "rci_search_yvr_2027", "celebrity": "celebrity_search_yvr_2027"}
RCI_P = "https://www.royalcaribbean.com/cruises?search=departurePort%3A{port}%7CstartDate%3A2027-05-15%7E2027-07-10&itineraryPanel={panel}"
CEL_P = "https://www.celebritycruises.com/cruises?search=departurePort%3A{port}%7CstartDate%3A2027-05-15%7E2027-07-10&country=USA&currency=USD&itineraryPanel={panel}"
PANEL = {"rci_serenade_yvr_tracy": ("YVR", "SR07YVR-3848220377"), "rci_serenade_yvr_rupert": ("YVR", "SR07YVR-810324492"),
         "rci_anthem_nb_icy": ("YVR", "AN07YVR-1733859911"), "rci_anthem_nb_juneau": ("YVR", "AN07YVR-4066772602"),
         "rci_anthem_sb": ("SWD", "AN07SWD-3892106028"), "rci_anthem_sb_ketchikan": ("SWD", "AN07SWD-953470841"),
         "celebrity_summit_yvr_dawes": ("YVR", "SM07YVR-276982758"), "celebrity_summit_yvr_hubbard": ("YVR", "SM07YVR-248500956"),
         "celebrity_solstice_nb": ("YVR", "SL07YVR-2527737053"), "celebrity_solstice_sb": ("SWD", "SL07SWD-1391220359")}
from datetime import date, timedelta
SAIL = [
    ("rci_serenade_yvr_tracy", "2027-05-23", [800, 940, 1429, 3272]),
    ("rci_serenade_yvr_rupert", "2027-05-30", [780, 875, 1369, 2218]),
    ("rci_serenade_yvr_tracy", "2027-06-06", [789, 888, 1491, 2792]),
    ("rci_serenade_yvr_tracy", "2027-06-13", [810, 938, 1671, 3096]),
    ("rci_serenade_yvr_tracy", "2027-06-20", [869, 950, 1669, 3061]),
    ("rci_serenade_yvr_tracy", "2027-06-27", [880, 959, 1579, 3181]),
    ("rci_serenade_yvr_tracy", "2027-07-04", [890, 967, 1564, 2903]),
    ("rci_anthem_nb_icy", "2027-05-28", [1020, 1070, 1449, 2975]),
    ("rci_anthem_sb", "2027-06-04", [1217, 1154, 1517, 5410]),
    ("rci_anthem_nb_juneau", "2027-06-11", [999, 1299, 1749, 4494]),
    ("rci_anthem_sb_ketchikan", "2027-06-18", [1079, 1399, 1680, None]),
    ("rci_anthem_nb_icy", "2027-06-25", [1130, 1300, 1729, 4596]),
    ("rci_anthem_sb", "2027-07-02", [912, 960, 1337, 3737]),
    ("rci_anthem_nb_icy", "2027-07-09", [1080, 1399, 1849, 4566]),
    ("celebrity_summit_yvr_dawes", "2027-05-23", [992, 1018, 1460, 1413]),
    ("celebrity_summit_yvr_hubbard", "2027-05-30", [1274, 1427, 2057, 2038]),
    ("celebrity_summit_yvr_dawes", "2027-06-06", [1097, 1656, 1542, 1574]),
    ("celebrity_summit_yvr_hubbard", "2027-06-13", [1279, 1278, 1989, 2520]),
    ("celebrity_summit_yvr_dawes", "2027-06-20", [1040, 1664, 1709, None]),
    ("celebrity_summit_yvr_hubbard", "2027-06-27", [1241, 1606, 2054, 2487]),
    ("celebrity_summit_yvr_dawes", "2027-07-04", [1735, 1645, 2463, 2463]),
    ("celebrity_solstice_sb", "2027-05-28", [852, 1175, 1350, 1629]),
    ("celebrity_solstice_nb", "2027-06-04", [880, 1105, 1544, 1715]),
    ("celebrity_solstice_sb", "2027-06-11", [986, 1304, 1553, 2212]),
    ("celebrity_solstice_nb", "2027-06-18", [845, 1578, 1602, 1862]),
    ("celebrity_solstice_sb", "2027-06-25", [954, 1473, 1914, 2151]),
    ("celebrity_solstice_nb", "2027-07-02", [1267, 1845, 1776, 2372]),
    ("celebrity_solstice_sb", "2027-07-09", [1152, 1843, 1821, 2292]),
]
IT = {i["id"]: i for i in c["itineraries"]}
for itid, dep, pp in SAIL:
    it = IT[itid]; line = it["line"]
    sid = f"{itid}_{dep}"
    ret = (date.fromisoformat(dep) + timedelta(days=7)).isoformat()
    port, panel = PANEL[itid]
    url = (RCI_P if line == "rci" else CEL_P).format(port=port, panel=panel)
    rows = {}
    for cat, val, label in zip(CATS, pp, LBL[line]):
        rid = f"sailing:{sid}:{cat}"
        if val is None:
            row = dict(amount=None, usd=None, status="unavailable", note=f"{label}: no price shown in the date panel on {CHECKED} (likely sold out).")
        else:
            row = dict(amount=val * 2, usd=val * 2, status="verified", note=f"{label} ${val:,} pp x 2.")
        row.update({"id": rid, "for": f"sailing:{sid}", "item": f"cabin_{cat}", "currency": "USD", "fx": None,
                    "basis": BASIS[line], "source": SRC[line], "url": url, "checked": CHECKED, "label": label})
        upsert(P, row)
        rows[cat] = rid
    flags = ["holiday"] if dep in ("2027-06-27", "2027-07-02", "2027-07-04") else []
    if line == "celebrity":
        flags.append("promo")
    upsert(c["sailings"], {"id": sid, "itinerary": itid, "ship": it["ship"], "depart": dep, "return": ret, "nights": 7,
                           "code": panel, "flags": flags, "note": None, "priceRows": rows, "priceSourceKind": "first-party", "addedIn": "p1"})

# Seattle terminal fields on lines refer to Seattle; nothing to change.
save("catalog", c); save("prices", d["prices"]); save("sources", d["sources"])
print("itineraries", len(c["itineraries"]), "sailings", len(c["sailings"]), "rows", len(P))
