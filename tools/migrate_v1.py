#!/usr/bin/env python3
"""One-time migration (Phase 0): split app-v1/data.json into the v2 data files.

    python3 tools/migrate_v1.py        # run from the repo root

Every v1 price becomes one row in data/prices.json. Records keep a pointer to their
row ids; no amount is left anywhere else. Per-person cabin prices become cabin
prices for 2 adults (pp x 2), because v2 compares whole cabins.
Kept for provenance; later phases edit the data files directly, not this script.
"""
import json, copy, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
V1 = json.load(open(ROOT / "app-v1/data.json"))
OUT = ROOT / "data"
OUT.mkdir(exist_ok=True)
SRC = {s["id"]: s for s in V1["sources"]}

rows = []
v1_slots = 0  # every price-bearing field found in v1, for the count check


def row(id, for_, item, amount, basis, status, source=None, url=None, checked=None, note=None, label=None):
    if url is None and source in SRC:
        url = SRC[source]["url"]
    if checked is None and source in SRC:
        checked = SRC[source]["checked"]
    if checked is None:  # v1 recorded "not captured" without a date; v1 research day
        checked = "2026-11-06"
    r = dict(id=id, **{"for": for_}, item=item, amount=amount, currency="USD",
             usd=amount, fx=None, basis=basis, status=status, source=source,
             url=url, checked=checked, note=note)
    if label:
        r["label"] = label
    rows.append(r)
    return id


# ---------- route families (Phase 1 confirms and extends) ----------
FAMILIES = [
    dict(id="SEA-GB", name="Seattle round trip with Glacier Bay", gateway="SEA", glacier="glacier_bay", color="#0f766e", dash=None),
    dict(id="SEA-DAWES", name="Seattle round trip with Endicott Arm & Dawes Glacier", gateway="SEA", glacier="endicott_arm", color="#2563eb", dash=None),
    dict(id="SEA-TRACY", name="Seattle round trip with Tracy Arm", gateway="SEA", glacier="tracy_arm", color="#7c3aed", dash=None),
    dict(id="SEA-HUBBARD", name="Seattle round trip with Hubbard Glacier", gateway="SEA", glacier="hubbard", color="#c2410c", dash=None),
    dict(id="SEA-NONE", name="Seattle round trip, no glacier day", gateway="SEA", glacier=None, color="#64748b", dash="6 4"),
    dict(id="YVR-RT", name="Vancouver round trip", gateway="YVR", glacier=None, color="#b45309", dash=None, status="phase1"),
    dict(id="YVR-N", name="One way Vancouver to Seward/Whittier", gateway="YVR", glacier=None, color="#be123c", dash="10 4", status="phase1"),
    dict(id="YVR-S", name="One way Seward/Whittier to Vancouver", gateway="ANC", glacier=None, color="#9d174d", dash="10 4", status="phase1"),
]
FAM_BY_GLACIER = {"glacier_bay": "SEA-GB", "endicott_arm": "SEA-DAWES", "tracy_arm": "SEA-TRACY", "hubbard": "SEA-HUBBARD", None: "SEA-NONE"}

# ---------- media: photos pulled off records ----------
photos = []


def take_photo(rec, for_):
    p = rec.pop("photo", None)
    if not p:
        return
    pid = "ph-" + for_.replace(":", "-")
    photos.append(dict(id=pid, url=p.get("url"), page=p.get("page"), credit=p.get("credit"),
                       license=p.get("license"), **{"for": [for_]}))


# ---------- catalog ----------
lines = copy.deepcopy(V1["lines"])
for l in lines:
    g = l.pop("gratuity")
    v1_slots += 1
    l["gratuityRow"] = row(f"line:{l['id']}:gratuity", f"line:{l['id']}", "gratuity_pp_day", g.get("pp_day"),
                           "per person per day, standard cabins", g["status"], g.get("source"), note=g.get("note"))

ships = copy.deepcopy(V1["ships"])
for s in ships:
    take_photo(s, f"ship:{s['id']}")

places = copy.deepcopy(V1["places"])
for p in places:
    take_photo(p, f"place:{p['id']}")

itins = copy.deepcopy(V1["itineraries"])
for it in itins:
    it["routeFamily"] = FAM_BY_GLACIER[it.get("glacierPlace")]

sailings = copy.deepcopy(V1["sailings"])
for s in sailings:
    prices, ps = s.pop("prices"), s.pop("priceSource")
    basis = "Cabin for 2 adults (v1 per-person average x 2). " + (s.pop("priceBasis") or "")
    s.pop("currency", None)
    s["priceRows"] = {}
    for cat, v in prices.items():
        v1_slots += 1
        amt = v["pp"] * 2 if v.get("pp") is not None else None
        s["priceRows"][cat] = row(f"sailing:{s['id']}:{cat}", f"sailing:{s['id']}", f"cabin_{cat}", amt, basis.strip(),
                                  v["status"], None, ps.get("url"), ps.get("checked"),
                                  "; ".join(x for x in (v.get("note"), ps.get("note")) if x) or None, v.get("label"))
    s["priceSourceKind"] = ps.get("kind")

catalog = dict(routeFamilies=FAMILIES, lines=lines, ships=ships, itineraries=itins, sailings=sailings,
               places=places, pois=V1["pois"], linesReviewed=V1["linesReviewed"])

# ---------- experiences ----------
exps = copy.deepcopy(V1["excursions"])
UNIT = {"pp": "per adult", "vehicle": "per vehicle", "charter": "per charter"}
for e in exps:
    e.setdefault("walkMiles", None)
    e.setdefault("walkBasis", None)
    for o in e["offers"]:
        v1_slots += 1
        basis = UNIT.get(o.pop("unit"), "per adult") + (", 'from' price" if o.pop("from", False) else "")
        o["priceRow"] = row(f"offer:{o['id']}", f"offer:{o['id']}", "price", o.pop("pp"), basis, o.pop("status"),
                            o.get("source"), o.get("url"), o.get("checked"), o.get("note"))

# ---------- travel (Phase 2 rebuilds this around gateways) ----------
flights = copy.deepcopy(V1["flights"])
for f in flights:
    for cls, v in f.pop("fare").items():
        v1_slots += 1
        f.setdefault("fareRows", {})[cls] = row(f"flight:{f['id']}:{cls}", f"flight:{f['id']}", f"fare_{cls}_4adults_rt", v.get("total4"),
                                                "4 adults, round trip, taxes and fees included", v["status"], f["sources"][0], f.get("url"), f["checked"], v.get("note"))
    b = f.pop("bags")
    v1_slots += 1
    f["bagRow"] = row(f"flight:{f['id']}:bag", f"flight:{f['id']}", "first_checked_bag_pp", b.get("firstCheckedPerPerson"),
                      "per person, first checked bag (direction not confirmed)", b["status"], f["sources"][0], f.get("url"), f["checked"], b.get("note"))
    for i, leg in enumerate(f.get("outbound", [])):
        if "totalFare4" in leg:
            v1_slots += 1
            leg["fareRow"] = row(f"flight:{f['id']}:opt{i+1}", f"flight:{f['id']}", "fare_listed_4adults_rt", leg.pop("totalFare4"),
                                 "4 adults, round trip, as listed beside this outbound option", "published", f["sources"][0], f.get("url"), f["checked"])

hotels = copy.deepcopy(V1["hotels"])
for h in hotels:
    r, tf = h.pop("rate"), h.pop("taxesFees")
    h.pop("twoRooms")  # derived (2 x rate); the app computes it
    v1_slots += 2
    h["rateRow"] = row(f"hotel:{h['id']}:room_night", f"hotel:{h['id']}", "room_night", r["perRoomNight"],
                       "1 room, 2 guests, 1 night, taxes not stated", r["status"], h["sources"][0], h.get("url"), h["checked"], r.get("note"))
    h["taxRow"] = row(f"hotel:{h['id']}:taxes", f"hotel:{h['id']}", "taxes_fees", None, "per room night", tf["status"],
                      h["sources"][0], h.get("url"), h["checked"], tf.get("note"))
    take_photo(h, f"hotel:{h['id']}")

travel = dict(
    note="v1 Seattle-only travel data, migrated as is. Phase 2 adds YVR and ANC gateways, ground transfers and hotel ranges.",
    gateways=[dict(id="SEA", name="Seattle (SEA airport, Piers 66 and 91)", status="v1"),
              dict(id="YVR", name="Vancouver", status="phase2"), dict(id="ANC", name="Anchorage (for Seward/Whittier)", status="phase2")],
    flights=flights, hotels=hotels, groundTransfers=[], hotelRanges=[])

media = dict(policy=V1["photoPolicy"], photos=photos, videos=[], officialLinks=[])

meta = copy.deepcopy(V1["meta"])
meta["version"] = "2.0.0-p0"
meta["updated"] = "2026-11-07"
meta["statusDefinitions"]["family-quote"] = {"label": "Family quote", "desc": "A price someone in the family got directly (from a cruise line, agent or airline). Kept as entered."}
meta["glacierGuide"] = {}
meta["phases"] = [dict(n=n, name=nm, status="todo") for n, nm in
                  [(0, "Foundation and migration"), (1, "Routes and sailings"), (2, "Arrival-city costs"), (3, "Experiences A"),
                   (4, "Experiences B and glacier guide"), (5, "Media"), (6, "App A"), (7, "App B"), (8, "QA and release")]]
meta["phases"][0]["status"] = "done"
meta["migration"] = dict(fromVersion=V1["meta"]["version"], date="2026-11-07", v1PriceSlots=v1_slots,
                         note="v1 per-person cabin prices were doubled into 2-adult cabin prices. v1 'twoRooms' hotel estimates were dropped (the app computes them).")

assert len(rows) == v1_slots, (len(rows), v1_slots)
assert len({r["id"] for r in rows}) == len(rows), "duplicate row id"


def dump(name, obj):
    with open(OUT / name, "w") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
        f.write("\n")


dump("catalog.json", catalog)
dump("prices.json", dict(rows=rows))
dump("experiences.json", dict(experiences=exps, coverage=meta.pop("excursionCoverage"), labels=meta.pop("labels"), offerKinds=meta.pop("offerKinds")))
dump("media.json", media)
dump("travel.json", dict(travel, coverage=meta.pop("travelCoverage")))
dump("sources.json", dict(sources=V1["sources"]))
dump("meta.json", meta)
print(f"rows {len(rows)} (v1 slots {v1_slots}); photos {len(photos)}; sailings {len(sailings)}; experiences {len(exps)}; "
      f"offers {sum(len(e['offers']) for e in exps)}; sources {len(V1['sources'])}")
