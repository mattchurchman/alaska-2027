"""P6: schematic map lines for itineraries that have none (Vancouver, one-way and new
Seattle itineraries added in P1). Idempotent: only fills itineraries whose mapLine is empty,
unless --all is passed.

The lines are SCHEMATIC: shortest path over a hand-placed graph of sea waypoints between
the scheduled stops. They show the order of stops, not the ship's actual track.
The v1 graph (app-v1/src/build_planner_data.py) is extended here with the BC Inside
Passage from Vancouver, Prince Rupert, Haines, the Stikine area, the Gulf of Alaska,
Prince William Sound (College Fjord, Whittier) and Resurrection Bay (Seward).
"""
import heapq, math, sys
from common import load, save

N = {
    # --- v1 graph ---
    "sea_p66": (47.611, -122.348), "sea_p91": (47.6297, -122.3822), "elliott": (47.63, -122.43),
    "pugetN": (47.95, -122.45), "admiralty": (48.17, -122.75), "jdfE": (48.25, -123.2),
    "victoria": (48.405, -123.39), "jdfMid": (48.30, -123.9), "jdfW": (48.45, -124.75),
    "flattery": (48.35, -125.4), "vi1": (49.0, -126.6), "vi2": (49.9, -128.1), "capeScott": (50.9, -129.1),
    "qcs": (51.7, -130.0), "hecateS": (52.6, -130.6), "hecateN": (53.8, -130.95), "dixon": (54.55, -131.15),
    "revilla": (55.08, -131.3), "ketchikan": (55.338, -131.645), "ketchikan_wc": (55.405, -131.735),
    "tongassN": (55.47, -131.86), "clarence1": (55.75, -132.2), "clarence2": (56.05, -132.75),
    "sumner": (56.3, -133.2), "frederick": (56.95, -133.7), "stephensS": (57.35, -133.78),
    "holkham": (57.74, -133.62), "endicott_arm": (57.52, -132.9), "tracy_arm": (57.835, -133.35),
    "stephens_passage": (57.95, -134.05), "gastineau": (58.2, -134.25), "juneau": (58.295, -134.40),
    "douglasW": (58.24, -134.63), "lynnS": (58.5, -134.98), "lynnM": (58.95, -135.18), "lynnN": (59.25, -135.36),
    "skagway": (59.445, -135.325), "icyE": (58.27, -135.15), "icy_strait": (58.135, -135.45),
    "icyW": (58.28, -135.85), "gbEntr": (58.38, -136.1), "gbMid": (58.75, -136.35), "glacier_bay": (58.98, -137.0),
    "crossSound": (58.13, -136.6), "gulf1": (58.5, -137.6), "gulf2": (59.1, -138.7), "yakutat": (59.75, -139.75),
    "hubbard": (60.0, -139.5), "outerBaranof": (57.3, -136.3), "sitkaSound": (57.0, -135.55), "sitka": (57.05, -135.34),
    "offBaranofS": (56.3, -135.1), "offPOW": (55.3, -133.9), "chathamS": (56.4, -134.65), "chathamM": (57.2, -134.65),
    "frederickW": (57.05, -134.2),
    # --- P6 additions (approximate channel waypoints) ---
    "yvr_canada_place": (49.289, -123.111), "firstNarrows": (49.315, -123.14), "englishBay": (49.30, -123.30),
    "georgiaS": (49.45, -123.75), "georgiaM": (49.85, -124.55), "georgiaN": (50.0, -125.0),
    "discovery": (50.15, -125.35), "johnstoneW": (50.42, -125.95), "johnstoneE": (50.55, -126.55),
    "qcStrait": (50.85, -127.35), "inside_passage_bc": (51.5, -127.8), "fitzhughN": (52.2, -128.15),
    "finlayson": (52.75, -128.6), "grenvilleS": (53.3, -129.25), "grenvilleN": (53.75, -129.95),
    "chathamSound": (54.2, -130.5), "prince_rupert": (54.315, -130.3208),
    "haines": (59.236, -135.445), "stikine_icecap": (56.85, -132.75),
    "gulfN1": (59.55, -142.3), "gulfN2": (59.75, -144.6), "hinchinbrook": (60.2, -146.6),
    "pws": (60.6, -147.3), "college_fjord": (61.1, -147.85), "passageCanal": (60.78, -148.45),
    "whittier": (60.774, -148.684), "kenaiS": (59.6, -148.4), "resurrection": (59.92, -149.35),
    "seward": (60.104, -149.442),
}
E = [
    # v1 edges
    ("sea_p66", "elliott"), ("sea_p91", "elliott"), ("elliott", "pugetN"), ("pugetN", "admiralty"), ("admiralty", "jdfE"),
    ("jdfE", "victoria"), ("jdfE", "jdfMid"), ("victoria", "jdfMid"), ("jdfMid", "jdfW"), ("jdfW", "flattery"),
    ("flattery", "vi1"), ("vi1", "vi2"), ("vi2", "capeScott"), ("capeScott", "qcs"), ("qcs", "hecateS"),
    ("hecateS", "hecateN"), ("hecateN", "dixon"), ("dixon", "revilla"), ("revilla", "ketchikan"),
    ("ketchikan", "ketchikan_wc"), ("ketchikan_wc", "tongassN"), ("tongassN", "clarence1"), ("clarence1", "clarence2"),
    ("clarence2", "sumner"), ("sumner", "frederick"), ("frederick", "stephensS"), ("stephensS", "holkham"),
    ("holkham", "endicott_arm"), ("holkham", "tracy_arm"), ("holkham", "stephens_passage"),
    ("stephens_passage", "gastineau"), ("gastineau", "juneau"), ("stephens_passage", "douglasW"), ("douglasW", "lynnS"),
    ("lynnS", "lynnM"), ("lynnM", "lynnN"), ("lynnN", "skagway"), ("lynnS", "icyE"), ("icyE", "icy_strait"),
    ("icyE", "icyW"), ("icy_strait", "icyW"), ("icyW", "gbEntr"), ("gbEntr", "gbMid"), ("gbMid", "glacier_bay"),
    ("icyW", "crossSound"), ("crossSound", "gulf1"), ("gulf1", "gulf2"), ("gulf2", "yakutat"), ("yakutat", "hubbard"),
    ("crossSound", "outerBaranof"), ("outerBaranof", "sitkaSound"), ("sitkaSound", "sitka"),
    ("sitkaSound", "offBaranofS"), ("offBaranofS", "offPOW"), ("offPOW", "dixon"), ("offBaranofS", "chathamS"),
    ("chathamS", "chathamM"), ("chathamM", "icyE"), ("chathamM", "frederickW"), ("frederickW", "stephensS"),
    ("frederickW", "frederick"), ("hecateN", "offPOW"),
    # P6: Vancouver and the BC Inside Passage
    ("yvr_canada_place", "firstNarrows"), ("firstNarrows", "englishBay"), ("englishBay", "georgiaS"),
    ("georgiaS", "georgiaM"), ("georgiaM", "georgiaN"), ("georgiaN", "discovery"), ("discovery", "johnstoneW"),
    ("johnstoneW", "johnstoneE"), ("johnstoneE", "qcStrait"), ("qcStrait", "inside_passage_bc"),
    ("inside_passage_bc", "fitzhughN"), ("fitzhughN", "finlayson"), ("finlayson", "grenvilleS"),
    ("grenvilleS", "grenvilleN"), ("grenvilleN", "chathamSound"), ("chathamSound", "prince_rupert"),
    ("chathamSound", "dixon"),
    # P6: Haines, Stikine area
    ("lynnN", "haines"), ("sumner", "stikine_icecap"), ("frederick", "stikine_icecap"),
    # P6: Gulf of Alaska, Prince William Sound, Resurrection Bay
    ("yakutat", "gulfN1"), ("gulfN1", "gulfN2"), ("gulfN2", "hinchinbrook"), ("hinchinbrook", "pws"),
    ("pws", "college_fjord"), ("pws", "passageCanal"), ("passageCanal", "whittier"),
    ("gulfN2", "kenaiS"), ("hinchinbrook", "kenaiS"), ("kenaiS", "resurrection"), ("resurrection", "seward"),
]

adj = {}
for a, b in E:
    adj.setdefault(a, []).append(b)
    adj.setdefault(b, []).append(a)


def dist(a, b):
    (la1, lo1), (la2, lo2) = N[a], N[b]
    return math.hypot(la1 - la2, (lo1 - lo2) * math.cos(math.radians((la1 + la2) / 2)))


def path(a, b):
    q, seen = [(0, a, [a])], set()
    while q:
        c, n, p = heapq.heappop(q)
        if n == b:
            return p
        if n in seen:
            continue
        seen.add(n)
        for m in adj.get(n, []):
            if m not in seen:
                heapq.heappush(q, (c + dist(n, m), m, p + [m]))
    raise ValueError(f"no path {a} -> {b}")


def main():
    redo_all = "--all" in sys.argv
    d = load()
    c = d["catalog"]
    changed = 0
    for it in c["itineraries"]:
        if it.get("mapLine") and not redo_all:
            continue
        stops = [e["place"] for day in it["days"] for e in day if e.get("place")]
        stops = [s for i, s in enumerate(stops) if i == 0 or s != stops[i - 1]]
        pts = []
        for a, b in zip(stops, stops[1:]):
            seg = path(a, b)
            for n in (seg if not pts else seg[1:]):
                pts.append([round(N[n][0], 3), round(N[n][1], 3)])
        it["mapLine"] = pts
        it["mapLineBasis"] = "schematic"
        changed += 1
    save("catalog", c)
    print(f"mapLine filled for {changed} itineraries")


if __name__ == "__main__":
    main()
