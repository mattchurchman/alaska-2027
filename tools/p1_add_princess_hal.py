#!/usr/bin/env python3
"""Phase 1: add Princess Vancouver/Whittier sailings and Holland America (Westerdam SB, Noordam SEA)
from notes/phase1.md (checked 2026-11-07). Idempotent: replaces records it owns.
Run from the repo root: python3 tools/p1_add_princess_hal.py
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

# ---------- places ----------
upsert(c["places"], {"id": "yvr_canada_place", "name": "Canada Place cruise terminal, Vancouver", "short": "Vancouver · Canada Place",
    "kind": "terminal", "country": "CA", "tz": "America/Vancouver", "lat": 49.2888, "lng": -123.1111,
    "notes": "Downtown Vancouver waterfront, next to Waterfront SkyTrain station. US-bound ships clear US border pre-clearance here before boarding. Canada Line SkyTrain runs from YVR airport to Waterfront (about 26 min).",
    "dock": "Dock", "coordBasis": "approximate"})
upsert(c["places"], {"id": "whittier", "name": "Whittier, Alaska (cruise port for Anchorage)", "short": "Whittier",
    "kind": "terminal", "country": "US", "tz": "America/Anchorage", "lat": 60.7739, "lng": -148.6836,
    "notes": "Small port about 60 mi by road from Anchorage. Road access is only through the one-lane Anton Anderson tunnel, which runs on a fixed schedule; rail also connects to Anchorage. Princess, Holland America and others use it for one-way Gulf of Alaska cruises.",
    "dock": "Dock", "coordBasis": "approximate"})
upsert(c["places"], {"id": "college_fjord", "name": "College Fjord, Alaska", "short": "College Fjord",
    "kind": "scenic", "country": "US", "tz": "America/Anchorage", "lat": 61.2, "lng": -147.8,
    "notes": "Fjord in northern Prince William Sound lined with tidewater and valley glaciers named after colleges. Ships cruise it in the evening before arriving in Whittier.",
    "dock": "Scenic cruising (no landing)", "coordBasis": "approximate"})

# ---------- ships ----------
for sid, name, line, guests, note in [
    ("emerald_princess", "Emerald Princess", "princess", 3090, "Guests from the Princess itinerary page."),
    ("crown_princess", "Crown Princess", "princess", None, None),
    ("discovery_princess", "Discovery Princess", "princess", None, None),
    ("coral_princess", "Coral Princess", "princess", 2000, "Princess page: inaugural Jan 17, 2003; refurbished Jan 14, 2019."),
    ("island_princess", "Island Princess", "princess", None, None),
    ("westerdam", "Westerdam", "hal", None, None),
    ("noordam", "Noordam", "hal", None, None),
]:
    rec = {"id": sid, "line": line, "name": name, "built": 2003 if sid == "coral_princess" else None,
           "guests": guests, "guestsSource": "Princess itinerary page" if guests else None}
    if note:
        rec["note"] = note
    upsert(c["ships"], rec)

# ---------- sources ----------
for src in [
    {"id": "princess_itin_2027", "title": "Princess itinerary-details pages (Alaska 2027, by voyage code)",
     "url": "https://www.princess.com/itinerary-details/?voyageCode=E715", "kind": "first-party", "publisher": "Princess Cruises",
     "checked": CHECKED, "note": "1 room / 2 guests, Princess Standard fare, avg per person incl. taxes and fees. Port times as listed."},
    {"id": "princess_search_yvr", "title": "Princess cruise search: Alaska from Vancouver or Anchorage (Whittier)",
     "url": "https://www.princess.com/cruise-search/", "kind": "first-party", "publisher": "Princess Cruises",
     "checked": CHECKED, "note": "18 products. In the window: Emerald 7-day Vancouver round trips and Voyage of the Glaciers (Crown, Discovery, Coral, Island)."},
    {"id": "hal_search_alaska", "title": "Holland America cruise search, Alaska (destinationIds:(A))",
     "url": "https://www.hollandamerica.com/en/us/find-a-cruise?destinationIds:(A)", "kind": "first-party", "publisher": "Holland America Line",
     "checked": CHECKED, "note": "143 cruises / 32 products incl. sold out. Summer Vancouver round trips and most one-ways are sold only as cruisetours."},
    {"id": "hal_booking_2027", "title": "Holland America booking step 'Choose your guests' (2 adults)",
     "url": "https://www.hollandamerica.com/en/us/booking/choose-your-guests", "kind": "first-party", "publisher": "Holland America Line",
     "checked": CHECKED, "note": "Reached from each voyage page's Continue button. 'FROM' average per person, all taxes and fees included."},
]:
    upsert(S, src)

# ---------- itineraries ----------
V, W = "yvr_canada_place", "whittier"
def E(place, dep): return [{"type": "embark", "place": place, "dep": dep}]
def D(place, arr): return [{"type": "disembark", "place": place, "arr": arr}]
def Pt(place, a, b): return [{"type": "port", "place": place, "arr": a, "dep": b}]
def Sc(place, a, b): return [{"type": "scenic", "place": place, "arr": a, "dep": b}]
SEA = [{"type": "sea"}]

def votg_n(skag, sixth):  # Vancouver -> Whittier
    return [E(V, "16:00"), SEA, Pt("ketchikan", "06:00", "14:00"), Pt("juneau", "08:00", "21:15"),
            Pt("skagway", skag, "20:30"), sixth, Sc("college_fjord", "18:00", "20:30"), D(W, "00:30")]
def coral_island_n(sixth):
    return [E(V, "16:00"), SEA, Pt("ketchikan", "06:00", "14:00"), Pt("juneau", "09:00", "21:15"),
            Pt("skagway", "06:30", "20:30"), sixth, Sc("college_fjord", "18:00", "20:30"), D(W, "00:30")]
def votg_s(fourth, skag=("06:00", "20:30")):  # Whittier -> Vancouver
    return [E(W, "20:30"), Sc("hubbard", "15:00", "20:00"), Sc("glacier_bay", "09:15", "18:15"),
            fourth or Pt("skagway", *skag), Pt("juneau", "06:30", "16:15"), Pt("ketchikan", "10:00", "17:00"), SEA, D(V, "07:30")]

ITS = [
    dict(id="princess_emerald_yvr_gb", line="princess", ship="emerald_princess", routeFamily="YVR-RT",
         name="7-Day Inside Passage (with Glacier Bay National Park), round trip Vancouver", weekday="Tuesday",
         glacier="Glacier Bay", glacierPlace="glacier_bay", timesSource="Princess itinerary page, voyage E714",
         days=[E(V, "15:00"), SEA, Pt("juneau", "14:00", "22:00"), Pt("skagway", "06:30", "20:30"),
               Sc("glacier_bay", "06:15", "15:15"), Pt("ketchikan", "10:00", "17:00"), SEA, D(V, "07:30")]),
    dict(id="princess_emerald_yvr_dawes", line="princess", ship="emerald_princess", routeFamily="YVR-RT",
         name="7-Day Inside Passage, round trip Vancouver", weekday="Tuesday",
         glacier="Endicott Arm & Dawes Glacier", glacierPlace="endicott_arm",
         timesSource="Princess itinerary pages, voyages E715-E720. Juneau arrival is 14:00 or 15:00 and Vancouver departure 15:00 or 16:00 depending on date (see sailing notes).",
         days=[E(V, "16:00"), SEA, Pt("juneau", "14:00", "22:00"), Pt("skagway", "06:30", "20:30"),
               Sc("endicott_arm", "08:00", "14:30"), Pt("ketchikan", "07:30", "17:00"), SEA, D(V, "07:30")]),
    dict(id="princess_crown_votg_n", line="princess", ship="crown_princess", routeFamily="YVR-N",
         name="7-Day Voyage of the Glaciers (Northbound), Vancouver to Whittier", weekday="Saturday",
         glacier="Glacier Bay + College Fjord", glacierPlace="glacier_bay", timesSource="Princess itinerary pages 3721, 3723, 3725, 3727",
         days=votg_n("06:00", Sc("glacier_bay", "06:15", "15:15"))),
    dict(id="princess_crown_votg_s", line="princess", ship="crown_princess", routeFamily="YVR-S",
         name="7-Day Voyage of the Glaciers with Glacier Bay (Southbound), Whittier to Vancouver", weekday="Saturday",
         glacier="Hubbard + Glacier Bay", glacierPlace="glacier_bay", timesSource="Princess itinerary pages 3722, 3724, 3726",
         days=votg_s(None, ("05:30", "20:45"))),
    dict(id="princess_discovery_votg_n", line="princess", ship="discovery_princess", routeFamily="YVR-N",
         name="7-Day Voyage of the Glaciers (Northbound), Vancouver to Whittier", weekday="Saturday",
         glacier="Glacier Bay + College Fjord", glacierPlace="glacier_bay", timesSource="Princess itinerary pages X723, X725, X727",
         days=votg_n("07:00", Sc("glacier_bay", "06:15", "15:15"))),
    dict(id="princess_discovery_votg_s", line="princess", ship="discovery_princess", routeFamily="YVR-S",
         name="7-Day Voyage of the Glaciers with Glacier Bay (Southbound), Whittier to Vancouver", weekday="Saturday",
         glacier="Hubbard + Glacier Bay", glacierPlace="glacier_bay",
         timesSource="Princess itinerary pages X722, X724, X726, X728. Calls at Icy Strait Point instead of Skagway. Vancouver arrival 08:00 on X724.",
         days=votg_s(Pt("icy_strait", "06:00", "19:00"))),
    dict(id="princess_coral_votg_n", line="princess", ship="coral_princess", routeFamily="YVR-N",
         name="7-Day Voyage of the Glaciers (Northbound), Vancouver to Whittier", weekday="Wednesday",
         glacier="Hubbard + College Fjord (no Glacier Bay)", glacierPlace="hubbard",
         timesSource="Princess itinerary pages 6710, 6712, 6714. Hubbard 15:30-20:30 (6712: 15:00-20:00).",
         days=coral_island_n(Sc("hubbard", "15:30", "20:30"))),
    dict(id="princess_coral_votg_s", line="princess", ship="coral_princess", routeFamily="YVR-S",
         name="7-Day Voyage of the Glaciers with Glacier Bay (Southbound), Whittier to Vancouver", weekday="Wednesday",
         glacier="Hubbard + Glacier Bay", glacierPlace="glacier_bay", timesSource="Princess itinerary pages 6709, 6711, 6713, 6715",
         days=votg_s(None)),
    dict(id="princess_island_votg_n_gb", line="princess", ship="island_princess", routeFamily="YVR-N",
         name="7-Day Voyage of the Glaciers (Northbound), Vancouver to Whittier", weekday="Wednesday",
         glacier="Glacier Bay + College Fjord", glacierPlace="glacier_bay", timesSource="Princess itinerary pages 2714, 2716, 2718",
         days=coral_island_n(Sc("glacier_bay", "06:00", "15:00"))),
    dict(id="princess_island_votg_n_hubbard", line="princess", ship="island_princess", routeFamily="YVR-N",
         name="7-Day Voyage of the Glaciers (Northbound), Vancouver to Whittier", weekday="Wednesday",
         glacier="Hubbard + College Fjord (no Glacier Bay)", glacierPlace="hubbard", timesSource="Princess itinerary page 2712",
         days=coral_island_n(Sc("hubbard", "15:00", "20:00"))),
    dict(id="princess_island_votg_s", line="princess", ship="island_princess", routeFamily="YVR-S",
         name="7-Day Voyage of the Glaciers with Glacier Bay (Southbound), Whittier to Vancouver", weekday="Wednesday",
         glacier="Hubbard + Glacier Bay", glacierPlace="glacier_bay", timesSource="Princess itinerary pages 2713, 2715, 2717",
         days=votg_s(None)),
    dict(id="hal_westerdam_gd_s", line="hal", ship="westerdam", routeFamily="YVR-S",
         name="7-Day Glacier Discovery Southbound, Whittier to Vancouver", weekday="Sunday",
         glacier="Hubbard + Glacier Bay", glacierPlace="glacier_bay",
         timesSource="Holland America voyage pages w733 and w737 (identical); w741 assumed the same",
         days=[E(W, "19:30"), Sc("hubbard", "15:00", "18:00"), Sc("glacier_bay", "08:30", "18:30"), Pt("skagway", "07:00", "21:00"),
               Pt("juneau", "08:00", "18:00"), Pt("ketchikan", "11:00", "19:00"), SEA, D(V, "07:00")]),
    dict(id="hal_noordam_explorer", line="hal", ship="noordam", routeFamily="SEA-DAWES",
         name="7-Day Alaska Explorer", weekday="Sunday",
         glacier="Endicott Arm & Dawes Glacier", glacierPlace="endicott_arm",
         timesSource="Holland America voyage pages n731 and n739 (identical); n734 assumed the same",
         days=[E("sea_p91", "15:00"), SEA, Sc("stephens_passage", None, None) + Pt("juneau", "12:30", "22:30"),
               Sc("endicott_arm", "08:00", "14:30"), Pt("sitka", "08:00", "16:00"), Pt("ketchikan", "07:00", "13:00"),
               Pt("victoria", "20:00", "23:59"), D("sea_p91", "07:00")]),
]
for it in ITS:
    it.update(timesStatus="verified", mapLineBasis=None, addedIn="p1")
    if it["id"] == "hal_westerdam_gd_s" or it["id"] == "hal_noordam_explorer":
        it["timesStatus"] = "verified"
    upsert(c["itineraries"], it)

# ---------- sailings + price rows ----------
PR_URL = "https://www.princess.com/itinerary-details/?voyageCode={}"
PR_BASIS = "Cabin for 2 adults (pp x 2). Princess Standard fare, average per person for 2 guests, includes taxes and fees. Gratuities not included."
HAL_BASIS = "Cabin for 2 adults (pp x 2). Lowest 'FROM' average per person for the category, 2 adults, all taxes and fees included. Gratuities not included."
CATS = ["interior", "oceanview", "balcony", "miniSuite"]
LABELS = {"princess": ["Interior", "Oceanview", "Balcony", "Mini-Suite"], "hal": ["Inside", "Ocean View", "Verandah", "Signature Suite"]}

# (itinerary, code, depart, return, nights, prices pp [interior, oceanview, balcony, miniSuite] (None = sold out), note)
SAIL = [
    ("princess_emerald_yvr_gb", "E714", "2027-05-25", "2027-06-01", [874, 1374, 2049, 2524], "Vancouver departure 15:00."),
    ("princess_emerald_yvr_dawes", "E715", "2027-06-01", "2027-06-08", [774, 874, 1499, 1874], "Vancouver departure 15:00."),
    ("princess_emerald_yvr_dawes", "E716", "2027-06-08", "2027-06-15", [794, 924, 1549, 1824], "Vancouver 15:00; Juneau 15:00-22:00."),
    ("princess_emerald_yvr_dawes", "E717", "2027-06-15", "2027-06-22", [824, 924, 1599, 1924], "Vancouver departure 15:00."),
    ("princess_emerald_yvr_dawes", "E718", "2027-06-22", "2027-06-29", [834, 1074, 1699, 1924], "Juneau 15:00-22:00."),
    ("princess_emerald_yvr_dawes", "E719", "2027-06-29", "2027-07-06", [924, 1074, 1699, 1974], None),
    ("princess_emerald_yvr_dawes", "E720", "2027-07-06", "2027-07-13", [924, 1004, 1599, 1924], None),
    ("princess_crown_votg_n", "3721", "2027-05-22", "2027-05-29", [774, 974, 2377, 2824], None),
    ("princess_crown_votg_s", "3722", "2027-05-29", "2027-06-05", [864, 1014, 2490, 2774], "Suites sold out."),
    ("princess_crown_votg_n", "3723", "2027-06-05", "2027-06-12", [974, 1304, 3081, 3224], None),
    ("princess_crown_votg_s", "3724", "2027-06-12", "2027-06-19", [874, 1304, 3125, 3383], None),
    ("princess_crown_votg_n", "3725", "2027-06-19", "2027-06-26", [1044, 1355, 2845, 3221], None),
    ("princess_crown_votg_s", "3726", "2027-06-26", "2027-07-03", [874, 1274, 2965, 3000], None),
    ("princess_crown_votg_n", "3727", "2027-07-03", "2027-07-10", [1044, 1273, 2825, None], "Mini-suites sold out."),
    ("princess_discovery_votg_s", "X722", "2027-05-22", "2027-05-29", [874, 2024, 1999, 2924], "Oceanview priced above balcony on the Princess page (few oceanview cabins on this ship)."),
    ("princess_discovery_votg_n", "X723", "2027-05-29", "2027-06-05", [1376, 2674, 2649, 3024], None),
    ("princess_discovery_votg_s", "X724", "2027-06-05", "2027-06-12", [1652, 2674, 2649, 3388], "Suites sold out. Vancouver arrival 08:00."),
    ("princess_discovery_votg_n", "X725", "2027-06-12", "2027-06-19", [1596, 2774, 2749, 3224], "Suites sold out."),
    ("princess_discovery_votg_s", "X726", "2027-06-19", "2027-06-26", [1652, 2874, 2849, 4446], "Suites sold out."),
    ("princess_discovery_votg_n", "X727", "2027-06-26", "2027-07-03", [1486, 2474, 2449, 3368], None),
    ("princess_discovery_votg_s", "X728", "2027-07-03", "2027-07-10", [1474, 2874, 2849, 3990], None),
    ("princess_coral_votg_s", "6709", "2027-05-26", "2027-06-02", [1188, 1480, 2349, 2658], "Suites sold out."),
    ("princess_coral_votg_n", "6710", "2027-06-02", "2027-06-09", [1074, 1174, 2049, 2521], "Suites sold out. Hubbard 15:30-20:30."),
    ("princess_coral_votg_s", "6711", "2027-06-09", "2027-06-16", [1120, 1341, 3325, 3468], "Suites sold out."),
    ("princess_coral_votg_n", "6712", "2027-06-16", "2027-06-23", [1074, 1174, 2239, 2554], "Hubbard 15:00-20:00."),
    ("princess_coral_votg_s", "6713", "2027-06-23", "2027-06-30", [1613, 1624, None, 3468], "Balcony sold out."),
    ("princess_coral_votg_n", "6714", "2027-06-30", "2027-07-07", [1074, 1124, 2049, 2566], "Hubbard 15:30-20:30."),
    ("princess_coral_votg_s", "6715", "2027-07-07", "2027-07-14", [1544, 1574, 2549, 3198], None),
    ("princess_island_votg_n_hubbard", "2712", "2027-05-26", "2027-06-02", [774, 874, 1849, 2117], None),
    ("princess_island_votg_s", "2713", "2027-06-02", "2027-06-09", [974, 1074, 2349, 2476], None),
    ("princess_island_votg_n_gb", "2714", "2027-06-09", "2027-06-16", [874, 974, 2349, 2432], None),
    ("princess_island_votg_s", "2715", "2027-06-16", "2027-06-23", [1124, 1224, 2649, 2926], None),
    ("princess_island_votg_n_gb", "2716", "2027-06-23", "2027-06-30", [1074, 1274, 2449, 2657], None),
    ("princess_island_votg_s", "2717", "2027-06-30", "2027-07-07", [974, 1024, 2749, 2746], None),
    ("princess_island_votg_n_gb", "2718", "2027-07-07", "2027-07-14", [974, 1174, 2549, 2657], None),
    ("hal_westerdam_gd_s", "w733", "2027-05-30", "2027-06-06", [839, 1069, None, None], "Verandah and all suites sold out for cruise-only (inventory likely held for cruisetours). Inside category without guarantee: $1,329 pp."),
    ("hal_westerdam_gd_s", "w737", "2027-06-13", "2027-06-20", [1024, 1309, None, None], "Verandah and suites sold out for cruise-only. Inside category: $1,514 pp."),
    ("hal_westerdam_gd_s", "w741", "2027-06-27", "2027-07-04", [999, 1289, None, None], "Verandah and suites sold out for cruise-only. Inside category: $1,489 pp. Port times not re-read for this date."),
    ("hal_noordam_explorer", "n731", "2027-05-23", "2027-05-30", [854, 924, 1374, 1974], None),
    ("hal_noordam_explorer", "n734", "2027-05-30", "2027-06-06", [964, 1074, 1524, 2364], "Port times not re-read for this date (same itinerary page)."),
    ("hal_noordam_explorer", "n739", "2027-07-04", "2027-07-11", [1179, 1329, 1929, 2629], None),
]
HAL_URL = {"hal_westerdam_gd_s": "https://www.hollandamerica.com/en/us/find-a-cruise/a7s07c/{}",
           "hal_noordam_explorer": "https://www.hollandamerica.com/en/us/find-a-cruise/a7e07c/{}"}
IT = {i["id"]: i for i in c["itineraries"]}
for itid, code, dep, ret, pp, note in SAIL:
    it = IT[itid]
    line = it["line"]
    sid = f"{itid}_{dep}"
    flags = []
    if dep in ("2027-06-29", "2027-06-30", "2027-07-03", "2027-07-04"):
        flags.append("holiday")
    rows = {}
    for cat, val, label in zip(CATS, pp, LABELS[line]):
        rid = f"sailing:{sid}:{cat}"
        url = PR_URL.format(code) if line == "princess" else HAL_URL[itid].format(code)
        if val is None:
            row = {"id": rid, "for": f"sailing:{sid}", "item": f"cabin_{cat}", "amount": None, "currency": "USD", "usd": None,
                   "fx": None, "basis": PR_BASIS if line == "princess" else HAL_BASIS, "status": "unavailable",
                   "source": "princess_itin_2027" if line == "princess" else "hal_booking_2027", "url": url,
                   "checked": CHECKED, "note": f"{label}: shown as SOLD OUT on {CHECKED}.", "label": label}
        else:
            row = {"id": rid, "for": f"sailing:{sid}", "item": f"cabin_{cat}", "amount": val * 2, "currency": "USD", "usd": val * 2,
                   "fx": None, "basis": PR_BASIS if line == "princess" else HAL_BASIS, "status": "verified",
                   "source": "princess_itin_2027" if line == "princess" else "hal_booking_2027", "url": url,
                   "checked": CHECKED, "note": f"{label} ${val:,} pp x 2.", "label": label}
        upsert(P, row)
        rows[cat] = rid
    upsert(c["sailings"], {"id": sid, "itinerary": itid, "ship": it["ship"], "depart": dep, "return": ret, "nights": 7,
                           "code": code, "flags": flags, "note": note, "priceRows": rows, "priceSourceKind": "first-party",
                           "addedIn": "p1"})

# route families now populated
for rf in c["routeFamilies"]:
    if rf["id"] in ("YVR-RT", "YVR-N", "YVR-S"):
        rf.pop("status", None)

save("catalog", c); save("prices", d["prices"]); save("sources", d["sources"])
print("itineraries", len(c["itineraries"]), "sailings", len(c["sailings"]), "rows", len(P))
