#!/usr/bin/env python3
"""Print small slices of the data so a session never has to load a whole file.

  python3 tools/query.py counts
  python3 tools/query.py get <id | kind:id>          one record + its price rows
  python3 tools/query.py rows [filters] [--oldest N] [--limit N]
  python3 tools/query.py list <collection> [filters] [--fields a,b,c] [--limit N]

Filters: key=value (exact), key~text (contains, case-insensitive), key!=value.
Dotted keys reach inside records (e.g. priceSourceKind=first-party).
Collections: routeFamilies lines ships itineraries sailings places pois linesReviewed
             experiences offers flights hotels gateways photos videos sources
Examples:
  query.py rows for~sailing:hal status=verified --limit 5
  query.py rows status!=family-quote --oldest 10
  query.py list sailings depart~2027-06 itinerary~dawes --fields id,depart,ship
  query.py get sailing:hal_eurodam_explorer_2027-06-12
"""
import json, sys
from common import load, entities

d = load()
args = sys.argv[1:]
if not args:
    print(__doc__); sys.exit(0)
cmd, args = args[0], args[1:]


def opt(name, default=None):
    if name in args:
        i = args.index(name); v = args[i + 1]; del args[i:i + 2]; return v
    return default


def dig(r, key):
    for k in key.split("."):
        r = r.get(k) if isinstance(r, dict) else None
    return r


def match(r, filters):
    for f in filters:
        for op in ("!=", "~", "="):
            if op in f:
                k, v = f.split(op, 1); x = dig(r, k); s = "" if x is None else str(x)
                if op == "=" and s != v: return False
                if op == "!=" and s == v: return False
                if op == "~" and v.lower() not in s.lower(): return False
                break
    return True


def compact_row(r):
    amt = "—" if r["amount"] is None else f"{r['amount']:,.2f}".rstrip("0").rstrip(".")
    return f"{r['id']:<58} {amt:>9} {r['currency']} {r['status']:<12} {r['checked']}  {r['item']}"


COLL = {"routeFamilies": d["catalog"]["routeFamilies"], "lines": d["catalog"]["lines"], "ships": d["catalog"]["ships"],
        "itineraries": d["catalog"]["itineraries"], "sailings": d["catalog"]["sailings"], "places": d["catalog"]["places"],
        "pois": d["catalog"]["pois"], "linesReviewed": d["catalog"]["linesReviewed"], "experiences": d["experiences"]["experiences"],
        "offers": [dict(o, experience=x["id"]) for x in d["experiences"]["experiences"] for o in x["offers"]],
        "flights": d["travel"]["flights"], "hotels": d["travel"]["hotels"], "gateways": d["travel"]["gateways"],
        "photos": d["media"]["photos"], "videos": d["media"]["videos"], "sources": d["sources"]["sources"]}
rows = d["prices"]["rows"]

if cmd == "counts":
    for k, v in COLL.items():
        print(f"{k:<15} {len(v)}")
    print(f"{'priceRows':<15} {len(rows)}")
    from collections import Counter
    print("row status:", dict(Counter(r["status"] for r in rows)))
elif cmd == "get":
    key = args[0]
    ents = entities(d)
    hits = [k for k in ents if k == key or k.split(":", 1)[1] == key]
    hits += [f"source:{s['id']}" for s in COLL["sources"] if s["id"] == key]
    hits += [f"row:{r['id']}" for r in rows if r["id"] == key]
    if not hits:
        print("no match"); sys.exit(1)
    for h in hits[:3]:
        kind, id_ = h.split(":", 1)
        rec = ents.get(h) or next((s for s in COLL["sources"] if s["id"] == id_), None) or next((r for r in rows if r["id"] == id_), None)
        txt = json.dumps(rec, ensure_ascii=False, indent=1)
        print(f"== {h}\n" + (txt if len(txt) < 4000 else txt[:4000] + "\n... (truncated; use list --fields)"))
        for r in rows:
            if r["for"] == h:
                print("  " + compact_row(r))
elif cmd == "rows":
    oldest, limit = opt("--oldest"), int(opt("--limit", "50"))
    sel = [r for r in rows if match(r, args)]
    if oldest:
        sel = sorted(sel, key=lambda r: r["checked"])[:int(oldest)]
    for r in sel[:limit]:
        print(compact_row(r))
    print(f"({len(sel)} rows match{', showing ' + str(limit) if len(sel) > limit else ''})")
elif cmd == "list":
    name = args.pop(0)
    fields, limit = opt("--fields"), int(opt("--limit", "50"))
    sel = [r for r in COLL[name] if match(r, args)]
    for r in sel[:limit]:
        if fields:
            print(" | ".join(str(dig(r, f)) for f in fields.split(",")))
        else:
            print(json.dumps(r, ensure_ascii=False)[:300])
    print(f"({len(sel)} match)")
else:
    print(__doc__); sys.exit(1)
