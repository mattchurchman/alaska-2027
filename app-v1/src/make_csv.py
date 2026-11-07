#!/usr/bin/env python3
"""Write the two cruise-comparison CSVs from data.json (run in the folder that holds data.json).

  cruise-comparison-all-sailings.csv   one row per sailing (late May - early July 2027)
  cruise-comparison-by-line.csv        one row per cruise line (plus lines reviewed that do not qualify)

Every value is derived from data.json by the rules below. Nothing is typed in by hand, and anything the
research did not capture stays blank (with a derived 'limitations' note) rather than being guessed.
The same rules are implemented in the app (planner_map.js, cruiseCSVs) so the Compare tab can re-export
fresh files after a price refresh. tools/test: both implementations must produce identical bytes.

Definitions (same as the app):
  two-cabin fare   = 2 x interior pp + 2 x balcony pp  (taxes and port fees included, gratuities not)
  gratuities       = line's published pp/day x 4 travelers x nights  (planning estimate)
  Alaska port hrs  = scheduled hours in US ports only (Victoria, BC excluded)
  usable shore hrs = per US port: scheduled hours minus 1.5 h (30 min off + 1 h back aboard), floor 0
"""
import csv, io, json


def money_num(x):
    if x is None:
        return ""
    s = f"{x:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("", "-0") else s


def hrs(a, b):
    if not a or not b:
        return None
    x = int(a[:2]) * 60 + int(a[3:5])
    y = 24 * 60 if b in ("23:59", "23:58") else int(b[:2]) * 60 + int(b[3:5])
    return (y - x) / 60


def load(path="data.json"):
    D = json.load(open(path, encoding="utf-8"))
    IDX = {k: {x["id"]: x for x in D[k]} for k in ("places", "lines", "ships", "itineraries", "sources")}
    for it in D["itineraries"]:
        ak = use = 0.0
        ports, sea = [], 0
        for day in it.get("days") or []:
            for e in day:
                if e["type"] == "sea":
                    sea += 1
                if e["type"] == "port" and IDX["places"][e["place"]]["country"] == "US":
                    h = hrs(e["arr"], e["dep"])
                    ak += h
                    use += max(0, h - 1.5)
                    ports.append(e["place"])
        if not it.get("days") and it.get("ports"):
            ports = [p for p in it["ports"] if IDX["places"][p]["kind"] == "port" and IDX["places"][p]["country"] == "US"]
        it["_ak"] = ak if it.get("days") else None
        it["_use"] = use if it.get("days") else None
        it["_ports"] = ports
        it["_sea"] = sea
    for s in D["sailings"]:
        it = IDX["itineraries"][s["itinerary"]]
        ln = IDX["lines"][it["line"]]
        p = s["prices"]
        i, b = p["interior"]["pp"], p["balcony"]["pp"]
        s["_fare"] = 2 * i + 2 * b if i is not None and b is not None else None
        s["_fstat"] = (
            ("verified" if p["interior"]["status"] == "verified" and p["balcony"]["status"] == "verified" else "published")
            if s["_fare"] is not None
            else "unavailable"
        )
        g = (ln.get("gratuity") or {}).get("pp_day")
        s["_grat"] = None if g is None else g * 4 * s["nights"]
        s["_total"] = s["_fare"] + s["_grat"] if s["_fare"] is not None and s["_grat"] is not None else None
        s["_june"] = "2027-06-01" <= s["depart"] <= "2027-06-30"
    return D, IDX


def glacier_text(it):
    return it.get("glacier") or "No glacier day"


def sailings_csv(D, IDX):
    head = ["line", "ship", "itinerary", "sailing_id", "depart", "return", "weekday", "nights", "june_2027",
            "glacier_or_scenic", "alaska_ports", "alaska_port_hours", "usable_shore_hours", "sea_days", "terminal",
            "interior_pp_usd", "interior_status", "oceanview_pp_usd", "oceanview_status", "balcony_pp_usd", "balcony_status",
            "suite_tier_pp_usd", "suite_tier_status", "two_cabin_fare_usd", "two_cabin_fare_status",
            "gratuity_pp_per_day_usd", "gratuity_status", "gratuities_4_travelers_usd", "two_cabin_fare_plus_gratuities_usd",
            "flags", "price_basis", "price_source_url", "price_checked", "note"]
    rows = [head]
    order = sorted(D["sailings"], key=lambda s: (s["depart"], IDX["lines"][IDX["itineraries"][s["itinerary"]]["line"]]["name"], IDX["ships"][s["ship"]]["name"]))
    for s in order:
        it = IDX["itineraries"][s["itinerary"]]
        ln = IDX["lines"][it["line"]]
        sh = IDX["ships"][s["ship"]]
        p = s["prices"]
        g = ln.get("gratuity") or {}
        rows.append([
            ln["name"], sh["name"], it["name"], s["id"], s["depart"], s["return"], it["weekday"], s["nights"],
            "Yes" if s["_june"] else "No", glacier_text(it),
            len(it["_ports"]), money_num(it["_ak"]), money_num(it["_use"]), it["_sea"], IDX["places"][ln["terminal"]]["name"],
            money_num(p["interior"]["pp"]), p["interior"]["status"],
            money_num(p["oceanview"]["pp"]), p["oceanview"]["status"],
            money_num(p["balcony"]["pp"]), p["balcony"]["status"],
            money_num(p["miniSuite"]["pp"]), p["miniSuite"]["status"],
            money_num(s["_fare"]), s["_fstat"],
            money_num(g.get("pp_day")), g.get("status") or "",
            money_num(s["_grat"]), money_num(s["_total"]),
            "; ".join(s.get("flags") or []), s.get("priceBasis") or "", (s.get("priceSource") or {}).get("url", ""),
            (s.get("priceSource") or {}).get("checked", ""), s.get("note") or "",
        ])
    return rows


def lines_csv(D, IDX):
    head = ["line", "qualifies_seattle_round_trip", "ships", "sailings_captured_may_to_july", "june_sailings",
            "june_sailings_with_two_cabin_fare", "cheapest_june_two_cabin_fare_usd", "cheapest_june_ship", "cheapest_june_depart",
            "cheapest_june_fare_status", "cheapest_june_fare_plus_gratuities_usd", "gratuity_pp_per_day_usd", "gratuity_status",
            "glacier_or_scenic_options_june", "most_alaska_port_hours_june", "terminal", "final_payment_days_before_sailing",
            "deposit_policy", "payment_rules_status", "fare_basis", "included_in_fare", "accessibility_note",
            "price_source_url", "price_checked", "limitations"]
    rows = [head]
    for ln in D["lines"]:
        sl = [s for s in D["sailings"] if IDX["itineraries"][s["itinerary"]]["line"] == ln["id"]]
        if not sl:
            continue
        june = [s for s in sl if s["_june"]]
        pool = june or sl
        with_fare = [s for s in june if s["_fare"] is not None]
        best = min(with_fare, key=lambda s: (s["_fare"], s["depart"])) if with_fare else None
        ships = sorted({IDX["ships"][s["ship"]]["name"] for s in pool})
        glac = sorted({glacier_text(IDX["itineraries"][s["itinerary"]]) for s in pool})
        akh = [IDX["itineraries"][s["itinerary"]]["_ak"] for s in june if IDX["itineraries"][s["itinerary"]]["_ak"] is not None]
        g = ln.get("gratuity") or {}
        pay = ln.get("payment") or {}
        lim = []
        if not june:
            lim.append("No June 2027 sailing captured.")
        elif len(with_fare) < len(june):
            lim.append(f"Two-cabin fare not captured for {len(june) - len(with_fare)} of {len(june)} June sailings (interior or balcony price unavailable).")
        if g.get("pp_day") is None:
            lim.append("Gratuity rate not captured.")
        elif g.get("status") != "verified":
            lim.append(f"Gratuity rate is {g.get('status')} (planning estimate).")
        if any(not IDX["itineraries"][s["itinerary"]].get("days") for s in pool):
            lim.append("Port arrival/departure times not captured, so days cannot be planned.")
        if pay.get("status") != "verified":
            lim.append(f"Deposit and final-payment rules: {pay.get('status') or 'not captured'}.")
        rows.append([
            ln["name"], "Yes", "; ".join(ships), len(sl), len(june), len(with_fare),
            money_num(best["_fare"]) if best else "", IDX["ships"][best["ship"]]["name"] if best else "", best["depart"] if best else "",
            best["_fstat"] if best else "", money_num(best["_total"]) if best else "",
            money_num(g.get("pp_day")), g.get("status") or "", "; ".join(glac), money_num(max(akh)) if akh else "",
            IDX["places"][ln["terminal"]]["name"], pay.get("finalPaymentDays") if pay.get("finalPaymentDays") is not None else "",
            pay.get("deposit") or "", pay.get("status") or "", ln.get("fareBasis") or "", ln.get("includes") or "",
            ln.get("accessibility") or "", (best["priceSource"]["url"] if best else ""), (best["priceSource"]["checked"] if best else ""),
            " ".join(lim),
        ])
    for x in D.get("linesReviewed") or []:
        src = IDX["sources"].get(x.get("source")) if x.get("source") else None
        r = [""] * len(head)
        r[0], r[1] = x["line"], "No"
        r[head.index("price_source_url")] = src["url"] if src else ""
        r[head.index("price_checked")] = src["checked"] if src else ""
        r[head.index("limitations")] = x["finding"]
        rows.append(r)
    return rows


def to_text(rows):
    buf = io.StringIO()
    csv.writer(buf, lineterminator="\r\n").writerows(rows)
    return "﻿" + buf.getvalue().rstrip("\r\n")


def main():
    D, IDX = load()
    for name, rows in (("cruise-comparison-all-sailings.csv", sailings_csv(D, IDX)), ("cruise-comparison-by-line.csv", lines_csv(D, IDX))):
        with open(name, "w", encoding="utf-8", newline="") as f:
            f.write(to_text(rows))
        print(name, len(rows) - 1, "rows")


if __name__ == "__main__":
    main()
