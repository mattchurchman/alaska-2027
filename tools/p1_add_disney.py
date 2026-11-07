#!/usr/bin/env python3
"""Phase 1 part 2: add Disney Wonder (Mon) and Disney Magic (Thu) 7-night round trips from Vancouver, May 22 - Jul 7 2027.
disneycruise.disney.go.com's cruise search (/cruises-destinations/list/) returned its 404 page in the browser on 2026-11-07,
so no first-party prices were captured. Interior 'from' prices come from a reseller listing (status published);
other cabins are unavailable. Port times from a third-party itinerary site (published). Idempotent.
Run from the repo root: python3 tools/p1_add_disney.py
"""
import sys
from datetime import date, timedelta
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


upsert(c["lines"], {"id": "disney", "name": "Disney Cruise Line", "badge": "DC", "color": "#1d3f8f", "terminal": "yvr_canada_place",
    "fareBasis": "Family-focused line. Alaska sailings 2027 are round trips from Vancouver only (Disney Wonder Mondays, Disney Magic Thursdays). Prices here are reseller 'from' samples; Disney's own search could not be read.",
    "includes": "Rotational dining (three main restaurants in turn), Broadway-style Disney shows, soft drinks at meals and drink stations. Alcohol, Wi-Fi, adult-only dining and gratuities extra.",
    "payment": {"finalPaymentDays": None, "deposit": "Not captured.", "status": "unavailable", "source": None, "note": ""},
    "accessibility": "Not captured.", "gratuityRow": "line:disney:gratuity"})
upsert(P, {"id": "line:disney:gratuity", "for": "line:disney", "item": "gratuity_pp_day", "amount": None, "currency": "USD", "usd": None,
    "fx": None, "basis": "per person per day, standard cabins", "status": "unavailable", "source": None, "url": None, "checked": CHECKED,
    "note": "Not captured."})
upsert(c["ships"], {"id": "disney_wonder", "line": "disney", "name": "Disney Wonder", "built": None, "guests": None, "guestsSource": None})
upsert(c["ships"], {"id": "disney_magic", "line": "disney", "name": "Disney Magic", "built": None, "guests": None, "guestsSource": None})
upsert(c["places"], {"id": "stikine_icecap", "name": "Stikine Icecap (scenic glacier viewing)", "short": "Stikine Icecap",
    "kind": "scenic", "country": "US", "tz": "America/Juneau", "lat": 57.0, "lng": -132.6,
    "notes": "Large icefield on the Alaska-BC border east of Petersburg and Wrangell. Disney lists a scenic glacier-viewing day here; which glacier face the ship approaches is not stated.",
    "dock": "Scenic cruising (no landing)", "coordBasis": "approximate"})

for src in [
    {"id": "alaskacruises_disney_2027", "title": "AlaskaCruises.com: Disney Wonder and Disney Magic 2027 sailing calendars",
     "url": "https://www.alaskacruises.com/ships/disney-cruises-disney-wonder-cruise-itineraries.html", "kind": "reseller",
     "publisher": "AlaskaCruises.com", "checked": CHECKED,
     "note": "'Priced From' Interior Stateroom, per person, double occupancy, 'Includes taxes & fees'. Magic page: /ships/disney-cruises-disney-magic-cruise-itineraries.html. Used because Disney's own search page returned a 404 in the browser on 2026-11-07."},
    {"id": "gangwaze_disney_2027", "title": "Gangwaze itinerary maps: Disney Wonder Jun 21 2027, Disney Magic Jun 17 2027",
     "url": "https://gangwaze.com/cruise-lines/disney-cruise-line/disney-wonder/2027-06-21/7-nights", "kind": "aggregator",
     "publisher": "Gangwaze", "checked": CHECKED, "note": "Day-by-day port times. Magic: /disney-magic/2027-06-17/7-nights."},
    {"id": "dcl_alaska", "title": "Disney Cruise Line: Alaska cruises", "url": "https://disneycruise.disney.go.com/cruise-destinations/alaska/",
     "kind": "first-party", "publisher": "Disney Cruise Line", "checked": CHECKED,
     "note": "Confirms departures from Vancouver and ports (Stikine Icecap glacier viewing, Icy Strait Point, Juneau, Ketchikan/Ward Cove, Skagway). No prices on this page."},
]:
    upsert(S, src)

V = "yvr_canada_place"
def E(p, dep): return [{"type": "embark", "place": p, "dep": dep}]
def D(p, arr): return [{"type": "disembark", "place": p, "arr": arr}]
def Pt(p, a, b): return [{"type": "port", "place": p, "arr": a, "dep": b}]
def Sc(p, a=None, b=None): return [{"type": "scenic", "place": p, "arr": a, "dep": b}]
SEA = [{"type": "sea"}]

ITS = [
    dict(id="disney_wonder_yvr", line="disney", ship="disney_wonder", routeFamily="YVR-RT",
         name="7-Night Alaska Cruise (Stikine Icecap, Skagway, Juneau, Ketchikan)", weekday="Monday",
         glacier="Stikine Icecap", glacierPlace="stikine_icecap", timesStatus="published",
         timesSource="Third-party itinerary page (Gangwaze) for the Jun 21 2027 sailing; assumed the same for other dates. Disney's own pages could not be read. Glacier day has no listed hours.",
         days=[E(V, "16:00"), SEA, Sc("stikine_icecap"), Pt("skagway", "07:15", "20:00"), Pt("juneau", "06:45", "16:45"),
               Pt("ketchikan", "11:15", "19:00"), SEA, D(V, "08:00")]),
    dict(id="disney_magic_yvr", line="disney", ship="disney_magic", routeFamily="YVR-RT",
         name="7-Night Alaska Cruise (Stikine Icecap, Skagway, Icy Strait Point, Ketchikan)", weekday="Thursday",
         glacier="Stikine Icecap", glacierPlace="stikine_icecap", timesStatus="published",
         timesSource="Third-party itinerary page (Gangwaze) for the Jun 17 2027 sailing; assumed the same for other dates. Disney's own pages could not be read. No Juneau call. Glacier day has no listed hours.",
         days=[E(V, "15:00"), SEA, Sc("stikine_icecap"), Pt("skagway", "07:15", "20:30"), Pt("icy_strait", "07:00", "17:00"),
               Pt("ketchikan", "14:00", "19:00"), SEA, D(V, "08:00")]),
]
for it in ITS:
    it.update(mapLineBasis=None, addedIn="p1")
    upsert(c["itineraries"], it)

BASIS = "Cabin for 2 adults (pp x 2). Reseller 'Priced From' Interior Stateroom, per person, double occupancy, includes taxes & fees. Gratuities not included."
WURL = "https://www.alaskacruises.com/ships/disney-cruises-disney-wonder-cruise-itineraries.html"
MURL = "https://www.alaskacruises.com/ships/disney-cruises-disney-magic-cruise-itineraries.html"
SAIL = [
    ("disney_wonder_yvr", "2027-05-24", 2012), ("disney_wonder_yvr", "2027-05-31", 2159), ("disney_wonder_yvr", "2027-06-07", 2306),
    ("disney_wonder_yvr", "2027-06-14", 2131), ("disney_wonder_yvr", "2027-06-21", 2251), ("disney_wonder_yvr", "2027-06-28", 2425),
    ("disney_wonder_yvr", "2027-07-05", 2145),
    ("disney_magic_yvr", "2027-05-27", 1858), ("disney_magic_yvr", "2027-06-03", 2019), ("disney_magic_yvr", "2027-06-10", 2089),
    ("disney_magic_yvr", "2027-06-17", 2096), ("disney_magic_yvr", "2027-06-24", 2096), ("disney_magic_yvr", "2027-07-01", 2061),
]
NA = "Not captured: disneycruise.disney.go.com cruise search returned its 404 page in the browser on 2026-11-07, and the reseller lists only the interior 'from' price."
for itid, dep, pp in SAIL:
    ship = "disney_wonder" if "wonder" in itid else "disney_magic"
    sid = f"{itid}_{dep}"
    ret = (date.fromisoformat(dep) + timedelta(days=7)).isoformat()
    url = WURL if ship == "disney_wonder" else MURL
    rows = {}
    for cat in ["interior", "oceanview", "balcony", "miniSuite"]:
        rid = f"sailing:{sid}:{cat}"
        if cat == "interior":
            row = dict(amount=pp * 2, usd=pp * 2, status="published", source="alaskacruises_disney_2027", url=url,
                       note=f"Interior 'from' ${pp:,} pp x 2 (reseller listing, not Disney).", label="Interior")
        else:
            row = dict(amount=None, usd=None, status="unavailable", source=None, url=None, note=NA)
        row.update({"id": rid, "for": f"sailing:{sid}", "item": f"cabin_{cat}", "currency": "USD", "fx": None,
                    "basis": BASIS, "checked": CHECKED})
        upsert(P, row)
        rows[cat] = rid
    flags = ["family-line"] + (["holiday"] if dep in ("2027-06-28", "2027-07-01") else [])
    upsert(c["sailings"], {"id": sid, "itinerary": itid, "ship": ship, "depart": dep, "return": ret, "nights": 7, "code": None,
                           "flags": flags, "note": "Balcony price not captured (Disney's search could not be read).",
                           "priceRows": rows, "priceSourceKind": "reseller", "addedIn": "p1"})

save("catalog", c); save("prices", d["prices"]); save("sources", d["sources"])
print("itineraries", len(c["itineraries"]), "sailings", len(c["sailings"]), "rows", len(P))
