#!/usr/bin/env python3
"""Check the data files before every commit.   python3 tools/validate.py

Fails (exit 1) when:
- a price row is missing a field, has an unknown status, a bad date, or an amount that
  contradicts its status (unavailable must have no amount; anything else needs one);
- a verified / published / family-quote row has no url;
- a non-USD row has no fx {rate, date} or usd value;
- a row's 'for' points at nothing, a *Row/*Rows field points at a missing row,
  or a row is not referenced by its record (orphan);
- an id is duplicated, or a reference (line, ship, itinerary, place, route family,
  source, photo target) does not resolve;
- a price-like field (pp, total4, perRoomNight, pp_day, amount) appears outside prices.json.
"""
import re, sys
from common import load, entities, row_refs, STATUSES

d = load()
errors, warns = [], []
err = errors.append
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ents = entities(d)
src_ids = {s["id"] for s in d["sources"]["sources"]}
rows = d["prices"]["rows"]
row_ids = {}

# ---- price rows ----
REQ = ["id", "for", "item", "amount", "currency", "usd", "fx", "basis", "status", "source", "url", "checked", "note"]
for r in rows:
    rid = r.get("id", "?")
    for k in REQ:
        if k not in r:
            err(f"row {rid}: missing field '{k}'")
    if rid in row_ids:
        err(f"row {rid}: duplicate id")
    row_ids[rid] = r
    st = r.get("status")
    if st not in STATUSES:
        err(f"row {rid}: unknown status {st!r}")
    if not (isinstance(r.get("checked"), str) and DATE.match(r["checked"])):
        err(f"row {rid}: checked must be YYYY-MM-DD")
    amt = r.get("amount")
    if st == "unavailable" and amt is not None:
        err(f"row {rid}: unavailable but has an amount")
    if st in STATUSES - {"unavailable"} and not isinstance(amt, (int, float)):
        err(f"row {rid}: status {st} needs a numeric amount")
    if st in ("verified", "published", "family-quote") and not r.get("url"):
        err(f"row {rid}: {st} price needs a url")
    if st in ("estimate", "unavailable") and not (r.get("note") or r.get("basis")):
        err(f"row {rid}: {st} needs a note saying why")
    if r.get("currency") != "USD":
        fx = r.get("fx") or {}
        if not (fx.get("rate") and fx.get("date")):
            err(f"row {rid}: non-USD row needs fx.rate and fx.date")
        if amt is not None and r.get("usd") is None:
            err(f"row {rid}: non-USD row needs a usd value")
    elif amt is not None and r.get("usd") != amt:
        err(f"row {rid}: USD row with usd != amount")
    if r.get("for") not in ents:
        err(f"row {rid}: 'for' {r.get('for')!r} does not resolve")
    if r.get("source") and r["source"] not in src_ids:
        err(f"row {rid}: source {r['source']!r} not in sources.json")

# ---- row references ----
referenced = set()
for name in ("catalog", "experiences", "travel"):
    for path, rid in row_refs(d[name]):
        if rid not in row_ids:
            err(f"{name}.{path}: row {rid!r} does not exist")
        referenced.add(rid)
for rid in row_ids:
    if rid not in referenced:
        err(f"row {rid}: orphan (no record points at it)")

# ---- ids and references ----
c = d["catalog"]
for kind, items in (("routeFamily", c["routeFamilies"]), ("line", c["lines"]), ("ship", c["ships"]),
                    ("itinerary", c["itineraries"]), ("sailing", c["sailings"]), ("place", c["places"]),
                    ("poi", c["pois"]), ("experience", d["experiences"]["experiences"]),
                    ("source", d["sources"]["sources"]), ("photo", d["media"]["photos"]),
                    ("video", d["media"]["videos"]), ("flight", d["travel"]["flights"]), ("hotel", d["travel"]["hotels"])):
    seen = set()
    for r in items:
        if r["id"] in seen:
            err(f"{kind} {r['id']}: duplicate id")
        seen.add(r["id"])

def need(ref, kind, where):
    if ref is not None and f"{kind}:{ref}" not in ents:
        err(f"{where}: {kind} {ref!r} does not resolve")

for s in c["ships"]:
    need(s["line"], "line", f"ship {s['id']}")
for it in c["itineraries"]:
    need(it["line"], "line", f"itinerary {it['id']}")
    need(it["ship"], "ship", f"itinerary {it['id']}")
    need(it.get("routeFamily"), "route", f"itinerary {it['id']}")
    if not it.get("routeFamily"):
        err(f"itinerary {it['id']}: no routeFamily")
    for day in it.get("days") or []:
        for e in day:
            need(e.get("place"), "place", f"itinerary {it['id']}")
    for p in it.get("ports") or []:
        need(p, "place", f"itinerary {it['id']}")
for s in c["sailings"]:
    need(s["itinerary"], "itinerary", f"sailing {s['id']}")
    need(s["ship"], "ship", f"sailing {s['id']}")
for l in c["lines"]:
    need(l.get("terminal"), "place", f"line {l['id']}")
for p in c["pois"]:
    need(p.get("place"), "place", f"poi {p['id']}")
    if p.get("source") and p["source"] not in src_ids:
        err(f"poi {p['id']}: source {p['source']!r} missing")
for x in d["experiences"]["experiences"]:
    for p in [x["port"]] + (x.get("ports") or []):
        need(p, "place", f"experience {x['id']}")
    poi = x.get("poi")
    if poi and f"poi:{poi}" not in ents and f"place:{poi}" not in ents:
        err(f"experience {x['id']}: poi {poi!r} does not resolve")
    for o in x["offers"]:
        need(o.get("line"), "line", f"offer {o['id']}")
        if o.get("source") and o["source"] not in src_ids:
            err(f"offer {o['id']}: source {o['source']!r} missing")
for m in d["media"]["photos"] + d["media"]["videos"]:
    for f in m.get("for", []):
        if f not in ents:
            err(f"media {m['id']}: for {f!r} does not resolve")
    if m in d["media"]["photos"] and not (m.get("url") and m.get("credit") and m.get("license")):
        err(f"photo {m['id']}: needs url, credit and license")

# ---- no prices outside prices.json ----
PRICE_KEYS = {"pp", "total4", "perRoomNight", "pp_day", "amount", "totalFare4"}
def scan(obj, path, name):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in PRICE_KEYS and isinstance(v, (int, float)):
                err(f"{name}.{path}.{k}: price-like number outside prices.json")
            scan(v, f"{path}.{k}", name)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            scan(v, f"{path}[{i}]", name)
for name in ("catalog", "experiences", "travel", "media", "meta"):
    scan(d[name], "", name)

# ---- warnings (do not fail) ----
for r in rows:
    if r["status"] == "verified" and r.get("checked", "") < "2026-01-01":
        warns.append(f"row {r['id']}: verified but checked before 2026")

for e in errors[:60]:
    print("ERROR", e)
if len(errors) > 60:
    print(f"... and {len(errors) - 60} more errors")
for w in warns[:20]:
    print("warn ", w)
counts = {k: len(v) for k, v in c.items() if isinstance(v, list)}
print(f"rows {len(rows)} | " + " ".join(f"{k} {v}" for k, v in counts.items()) +
      f" | experiences {len(d['experiences']['experiences'])} offers {sum(len(x['offers']) for x in d['experiences']['experiences'])}"
      f" | photos {len(d['media']['photos'])} videos {len(d['media']['videos'])} | sources {len(src_ids)}")
print("FAIL" if errors else "OK", f"({len(errors)} errors, {len(warns)} warnings)")
sys.exit(1 if errors else 0)
