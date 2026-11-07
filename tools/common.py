"""Shared loader for the data files. Import from the tools in this folder."""
import json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
FILES = ["catalog", "prices", "experiences", "media", "travel", "sources", "meta"]
STATUSES = {"verified", "published", "estimate", "family-quote", "unavailable"}


def load():
    return {n: json.load(open(DATA / f"{n}.json")) for n in FILES}


def save(name, obj):
    with open(DATA / f"{name}.json", "w") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
        f.write("\n")


def entities(d):
    """Map 'kind:id' -> record for everything a price row or photo can be 'for'."""
    c, t, e = d["catalog"], d["travel"], d["experiences"]
    out = {}
    for kind, items in (("line", c["lines"]), ("ship", c["ships"]), ("itinerary", c["itineraries"]),
                        ("sailing", c["sailings"]), ("place", c["places"]), ("poi", c["pois"]),
                        ("route", c["routeFamilies"]), ("flight", t["flights"]), ("hotel", t["hotels"]),
                        ("gateway", t["gateways"]), ("transfer", t.get("groundTransfers", [])),
                        ("hotelRange", t.get("hotelRanges", [])), ("experience", e["experiences"])):
        for r in items:
            out[f"{kind}:{r['id']}"] = r
    for x in e["experiences"]:
        for o in x["offers"]:
            out[f"offer:{o['id']}"] = o
    return out


def row_refs(obj, path=""):
    """Yield (path, row_id) for every field named *Row (str) or *Rows (dict/list of str)."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{path}.{k}" if path else k
            if k.endswith("Row") and isinstance(v, str):
                yield p, v
            elif k.endswith("Rows") and isinstance(v, dict):
                for kk, vv in v.items():
                    yield f"{p}.{kk}", vv
            elif k.endswith("Rows") and isinstance(v, list):
                for i, vv in enumerate(v):
                    yield f"{p}[{i}]", vv
            else:
                yield from row_refs(v, p)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from row_refs(v, f"{path}[{i}]")
