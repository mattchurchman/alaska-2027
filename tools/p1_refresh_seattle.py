#!/usr/bin/env python3
"""Phase 1 part 2: refresh the cheapest Seattle sailing per major line (two-cabin interior + balcony),
re-read on the first-party sites on 2026-11-07. Per-person prices x 2. Idempotent.
Run from the repo root: python3 tools/p1_refresh_seattle.py
"""
import sys
sys.path.insert(0, "tools")
from common import load, save

CHECKED = "2026-11-07"
d = load()
P = {r["id"]: r for r in d["prices"]["rows"]}
CATS = ["interior", "oceanview", "balcony", "miniSuite"]
# sailing id -> per-person prices in CATS order (None = not re-read this time)
REFRESH = {
    "rci_voyager_dawes_2027-05-28": [751, 860, 1400, 2725],       # RCI date panel, incl. taxes & fees
    "carnival_tracy_2027-05-25": [794, 974, 1364, 2667],          # carnival.com itinerary page '*Taxes and fees are included.'
    "ncl_bliss_dawes_2027-05-29": [1039, 1259, 1659, 1889],       # NCL vacation builder, incl. taxes, fees and port expenses
    "princess_star_dawes_2027-05-30": [944, 1624, 1999, 2274],    # princess.com, avg/person, includes taxes and fees
    "celebrity_edge_dawes_2027-06-04": [1263, 1753, 2003, 2341],  # Celebrity date panel, incl. taxes & fees
    "hal_eurodam_explorer_2027-05-29": [1344, None, None, None],  # HAL itinerary page 'Inside from', all taxes and fees included
}
changed = []
for sid, pps in REFRESH.items():
    for cat, pp in zip(CATS, pps):
        if pp is None:
            continue
        r = P[f"sailing:{sid}:{cat}"]
        new = pp * 2
        if r["usd"] != new:
            changed.append(f"{sid}:{cat} {r['usd']} -> {new}")
            r["note"] = (r.get("note") or "") + f" Was ${r['usd']:,} on {r['checked']}."
        r["amount"] = r["usd"] = new
        r["status"] = "verified"
        r["checked"] = CHECKED
save("prices", d["prices"])
print("\n".join(changed) or "no changes")
