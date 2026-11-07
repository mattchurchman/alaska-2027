#!/usr/bin/env python3
"""Write the comparison CSVs from the data files.   python3 tools/make_csv.py

csv/all-sailings.csv  one line per sailing: route family, dates, cabin prices for 2 adults,
                      two-cabin total (brothers interior + parents balcony), estimated tips,
                      statuses, check date and source.
csv/by-line.csv       one line per line: its lowest two-cabin June sailing.
Totals are blank when either cabin price is unavailable. Nothing is filled in by guess.
"""
import csv as _csv  # file is make_csv.py so it does not shadow the csv module
from common import load, ROOT

d = load()
c = d["catalog"]
rows = {r["id"]: r for r in d["prices"]["rows"]}
L = {l["id"]: l for l in c["lines"]}
S = {s["id"]: s for s in c["ships"]}
I = {i["id"]: i for i in c["itineraries"]}
F = {f["id"]: f for f in c["routeFamilies"]}
P = {p["id"]: p for p in c["places"]}
out = ROOT / "csv"
out.mkdir(exist_ok=True)


def price(s, cat):
    rid = s["priceRows"].get(cat)
    return rows.get(rid) if rid else None


recs = []
for s in sorted(c["sailings"], key=lambda s: (s["depart"], s["id"])):
    it, ln = I[s["itinerary"]], L[I[s["itinerary"]]["line"]]
    inside, balc = price(s, "interior"), price(s, "balcony")
    two = inside["usd"] + balc["usd"] if inside and balc and inside["usd"] is not None and balc["usd"] is not None else None
    g = rows[ln["gratuityRow"]]
    tips = round(g["usd"] * 4 * s["nights"], 2) if g["usd"] is not None else None
    ports = [P[e["place"]]["short"] if "short" in P[e["place"]] else P[e["place"]]["name"]
             for day in (it.get("days") or []) for e in day if e.get("type") in ("port", "scenic")]
    recs.append({
        "line": ln["name"], "ship": S[s["ship"]]["name"], "route_family": it["routeFamily"],
        "route_family_name": F[it["routeFamily"]]["name"], "itinerary": it["name"],
        "depart": s["depart"], "return": s["return"], "nights": s["nights"],
        "ports_and_scenic": "; ".join(ports),
        "interior_2_adults_usd": inside["usd"] if inside else "", "interior_status": inside["status"] if inside else "unavailable",
        "balcony_2_adults_usd": balc["usd"] if balc else "", "balcony_status": balc["status"] if balc else "unavailable",
        "two_cabin_total_usd": two if two is not None else "",
        "tips_4_people_usd": tips if tips is not None else "", "tips_status": g["status"],
        "two_cabins_plus_tips_usd": round(two + tips, 2) if two is not None and tips is not None else "",
        "checked": inside["checked"] if inside else "", "source_url": inside["url"] if inside else "",
    })

with open(out / "all-sailings.csv", "w", newline="", encoding="utf-8") as f:
    w = _csv.DictWriter(f, fieldnames=list(recs[0].keys()))
    w.writeheader(); w.writerows(recs)

by = []
for ln in c["lines"]:
    mine = [r for r in recs if r["line"] == ln["name"]]
    june = [r for r in mine if r["depart"].startswith("2027-06")]
    priced = [r for r in june if r["two_cabin_total_usd"] != ""]
    best = min(priced, key=lambda r: r["two_cabin_total_usd"]) if priced else None
    by.append({"line": ln["name"], "sailings": len(mine), "june_sailings": len(june), "june_with_two_cabin_price": len(priced),
               "cheapest_june_ship": best["ship"] if best else "", "cheapest_june_depart": best["depart"] if best else "",
               "cheapest_june_route_family": best["route_family"] if best else "",
               "cheapest_june_two_cabin_usd": best["two_cabin_total_usd"] if best else "",
               "with_tips_usd": best["two_cabins_plus_tips_usd"] if best else "",
               "price_status": f"{best['interior_status']}/{best['balcony_status']}" if best else "",
               "checked": best["checked"] if best else "", "source_url": best["source_url"] if best else ""})
with open(out / "by-line.csv", "w", newline="", encoding="utf-8") as f:
    w = _csv.DictWriter(f, fieldnames=list(by[0].keys()))
    w.writeheader(); w.writerows(by)
print(f"csv/all-sailings.csv {len(recs)} rows; csv/by-line.csv {len(by)} rows")
