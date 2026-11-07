#!/usr/bin/env python3
"""Phase 1 part 2: add Norwegian Jade Vancouver <-> Whittier one-ways (May 22 - Jul 7 2027).
Source: ncl.com vacation builder (logged out, 2 guests, USD), checked 2026-11-07.
Prices are NCL 'combinedPrice' per person, shown on the stateroom page as
'Per Person. Includes taxes, fees and port expenses'. Idempotent.
Run from the repo root: python3 tools/p1_add_ncl_jade.py
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


upsert(c["places"], {"id": "haines", "name": "Haines, Alaska", "short": "Haines", "kind": "port", "country": "US",
    "tz": "America/Juneau", "lat": 59.2358, "lng": -135.4450,
    "notes": "Small town on Lynn Canal, about 15 mi by water south of Skagway. Quieter than Skagway; known for bald eagles (Chilkat preserve). Port Chilkoot dock is a short walk from town.",
    "dock": "Port Chilkoot dock", "coordBasis": "approximate"})
upsert(c["ships"], {"id": "norwegian_jade", "line": "ncl", "name": "Norwegian Jade", "built": None, "guests": None, "guestsSource": None})
upsert(S, {"id": "ncl_vb_jade_2027", "title": "Norwegian Cruise Line vacation builder: Norwegian Jade Alaska (Vancouver / Whittier) 2027",
    "url": "https://www.ncl.com/vacations?destination=alaska&ship=JADE", "kind": "first-party", "publisher": "Norwegian Cruise Line",
    "checked": CHECKED,
    "note": "Logged out, 2 guests, USD. Stateroom page shows 'Per Person. Includes taxes, fees and port expenses'. Auto-applied offers: 50% Off All Cruises, 2-For-1 Deposits, Risk-Free Cancellation. Port times from the vacation builder Itinerary tab."})

V, WH = "yvr_canada_place", "whittier"
def E(p, dep): return [{"type": "embark", "place": p, "dep": dep}]
def D(p, arr): return [{"type": "disembark", "place": p, "arr": arr}]
def Pt(p, a, b): return [{"type": "port", "place": p, "arr": a, "dep": b}]
def Sc(p, a=None, b=None): return [{"type": "scenic", "place": p, "arr": a, "dep": b}]
SEA = [{"type": "sea"}]
IP = Sc("inside_passage_bc")

ITS = [
    dict(id="ncl_jade_nb_gb", code="JADE7VANKTNJNUSGYICYWQF", routeFamily="YVR-N",
         name="7-Day Alaska From Vancouver to Whittier: Skagway, Juneau & Ketchikan (Glacier Bay)", weekday="Monday",
         glacier="Glacier Bay", glacierPlace="glacier_bay", timesStatus="verified",
         timesSource="NCL vacation builder Itinerary tab, packages 24218505-24218508 (identical). Glacier Bay scenic cruising has no listed hours; Icy Strait Point is an evening call the same day. Ketchikan call is at Ward Cove.",
         days=[E(V, "16:00"), IP, Pt("ketchikan_wc", "07:00", "16:30"), Pt("juneau", "09:00", "21:00"), Pt("skagway", "07:00", "20:00"),
               Sc("glacier_bay") + Pt("icy_strait", "17:00", "22:00"), SEA, D(WH, "05:00")]),
    dict(id="ncl_jade_sb_haines", code="JADE7WQFHNSICYSGYKTNVAN", routeFamily="YVR-S",
         name="7-Day Alaska from Whittier to Vancouver: Skagway & Ketchikan (Hubbard, Haines)", weekday="Monday",
         glacier="Hubbard Glacier", glacierPlace="hubbard", timesStatus="verified",
         timesSource="NCL vacation builder Itinerary tab, package 24218515. Hubbard Glacier has no listed hours. Ketchikan call is at Ward Cove.",
         days=[E(WH, "19:00"), Sc("hubbard"), Pt("haines", "11:00", "20:00"), Pt("icy_strait", "07:00", "17:00"), Pt("skagway", "06:00", "16:00"),
               Pt("ketchikan_wc", "11:00", "20:00"), IP, D(V, "07:00")]),
    dict(id="ncl_jade_sb_juneau", code="JADE7WQFICYJNUSGYKTNVAN", routeFamily="YVR-S",
         name="7-Day Alaska from Whittier to Vancouver: Skagway, Juneau & Ketchikan (Hubbard)", weekday="Monday",
         glacier="Hubbard Glacier", glacierPlace="hubbard", timesStatus="verified",
         timesSource="NCL vacation builder Itinerary tab, packages 24218516-24218517 (identical). Hubbard Glacier has no listed hours. Ketchikan call is at Ward Cove.",
         days=[E(WH, "19:00"), Sc("hubbard"), Pt("icy_strait", "07:00", "19:00"), Pt("juneau", "07:00", "20:00"), Pt("skagway", "06:00", "16:00"),
               Pt("ketchikan_wc", "11:00", "20:00"), IP, D(V, "07:00")]),
]
CODE = {}
for it in ITS:
    CODE[it["id"]] = it.pop("code")
    it.update(line="ncl", ship="norwegian_jade", mapLineBasis=None, addedIn="p1")
    upsert(c["itineraries"], it)

CATS = ["interior", "oceanview", "balcony", "miniSuite"]
LBL = ["Inside", "Oceanview", "Balcony", "Club Balcony Suite"]
BASIS = ("Cabin for 2 adults (pp x 2). NCL vacation builder 'From' price per stateroom type, per person for 2 guests, "
         "includes taxes, fees and port expenses (auto-applied 50% Off All Cruises offer). Service charge/gratuities not included.")
URL = "https://www.ncl.com/vacation-builder/planning/stateroom?itineraryCode={code}&packageId={pkg}&guests=2&stateroomTypeCode=INSIDE"
# (itinerary, depart, packageId, [INSIDE, OCEANVIEW, BALCONY, MINISUITE] per person)
SAIL = [
    ("ncl_jade_nb_gb", "2027-05-24", "24218505", [749, 1079, 2019, 2289]),
    ("ncl_jade_sb_haines", "2027-05-31", "24218515", [759, 959, 1859, 2069]),
    ("ncl_jade_nb_gb", "2027-06-07", "24218506", [919, 1039, 2159, 2349]),
    ("ncl_jade_sb_juneau", "2027-06-14", "24218516", [959, 1089, 2869, 2889]),
    ("ncl_jade_nb_gb", "2027-06-21", "24218507", [1049, 1249, 2339, 2619]),
    ("ncl_jade_sb_juneau", "2027-06-28", "24218517", [999, 1159, 2549, 2699]),
    ("ncl_jade_nb_gb", "2027-07-05", "24218508", [1049, 1219, 2339, 2559]),
]
for itid, dep, pkg, pp in SAIL:
    sid = f"{itid}_{dep}"
    ret = (date.fromisoformat(dep) + timedelta(days=7)).isoformat()
    url = URL.format(code=CODE[itid], pkg=pkg)
    rows = {}
    for cat, val, label in zip(CATS, pp, LBL):
        rid = f"sailing:{sid}:{cat}"
        upsert(P, {"id": rid, "for": f"sailing:{sid}", "item": f"cabin_{cat}", "amount": val * 2, "currency": "USD", "usd": val * 2,
                   "fx": None, "basis": BASIS, "status": "verified", "source": "ncl_vb_jade_2027", "url": url, "checked": CHECKED,
                   "note": f"{label} ${val:,} pp x 2.", "label": label})
        rows[cat] = rid
    flags = ["promo"] + (["holiday"] if dep == "2027-06-28" else [])
    upsert(c["sailings"], {"id": sid, "itinerary": itid, "ship": "norwegian_jade", "depart": dep, "return": ret, "nights": 7,
                           "code": pkg, "flags": flags, "note": None, "priceRows": rows, "priceSourceKind": "first-party", "addedIn": "p1"})

save("catalog", c); save("prices", d["prices"]); save("sources", d["sources"])
print("itineraries", len(c["itineraries"]), "sailings", len(c["sailings"]), "rows", len(P))
