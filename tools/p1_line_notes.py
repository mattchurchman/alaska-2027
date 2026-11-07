#!/usr/bin/env python3
"""Phase 1 part 2: Alaska-experience notes on every line (catalog.lines[].alaskaNotes), luxury lines seen
leaving Vancouver/Seward and the small-ship paragraph (catalog.linesReviewed). No prices in catalog.json:
from-prices for small ships live in notes/phase1.md only as context. Idempotent.
Run from the repo root: python3 tools/p1_line_notes.py
"""
import sys
sys.path.insert(0, "tools")
from common import load, save

CHECKED = "2026-11-07"
d = load()
c, S = d["catalog"], d["sources"]["sources"]


def upsert(lst, rec, key="id"):
    for i, r in enumerate(lst):
        if r.get(key) == rec[key]:
            lst[i] = rec
            return
    lst.append(rec)


for src in [
    {"id": "princess_alaska_2027_release", "title": "Princess Cruises unveils 2027 Alaska season with return of Star Princess (news release, Aug 2025)",
     "url": "https://www.princess.com/news/news-releases/2025/08/princess-cruises-unveils-2027-alaska-season-with-return-of-star-princess",
     "kind": "first-party", "publisher": "Princess Cruises", "checked": CHECKED,
     "note": "Nearly 60 years in Alaska (since 1969); 85 Glacier Bay calls in 2027; five wilderness lodges incl. Mt. McKinley and Denali Princess lodges."},
    {"id": "hal_alaska_2027_release", "title": "Holland America Line unveils 2027 Alaska season (news release, Aug 7 2025)",
     "url": "https://www.hollandamerica.com/en/us/news/2025/August/news-08072025-Alaska-2027",
     "kind": "first-party", "publisher": "Holland America Line", "checked": CHECKED,
     "note": "80 years in Alaska in 2027; six ships; Glacier Bay on Eurodam Alaska Explorer and Glacier Discovery one-ways; National Park ranger boards for Glacier Bay; Holland America Denali Lodge; Glacier Guarantee; We Love Alaska and Alaska Up Close programs."},
    {"id": "pointsparty_glacier_bay_permits", "title": "Glacier Bay Cruises: Which Ships Go and How Permits Work",
     "url": "https://thepointsparty.com/articles/glacier-bay-cruise-ships-permits", "kind": "secondary", "publisher": "The Points Party",
     "checked": CHECKED,
     "note": "Lines authorized in Glacier Bay per the NPS list: Princess, Holland America, Norwegian, Seabourn, Cunard, Viking. No more than two cruise ships a day."},
    {"id": "nps_glba_cruise", "title": "Glacier Bay National Park: cruise ship services news release", "url": "https://www.nps.gov/glba/learn/news/glacier-bay-issues-new-contracts-for-cruise-ship-services.htm",
     "kind": "government", "publisher": "National Park Service", "checked": CHECKED, "note": "Concession contracts for cruise ship entry into Glacier Bay."},
    {"id": "pointsparty_alaska_cost", "title": "How Much Does an Alaska Cruise Cost? Fares From Eight Cruise Lines (Oct 7 2026 snapshot)",
     "url": "https://thepointsparty.com/articles/alaska-cruise-cost", "kind": "secondary", "publisher": "The Points Party", "checked": CHECKED,
     "note": "Small-ship and Viking from-prices used only as context in the small-ship paragraph."},
    {"id": "uncruise_pricing_2027", "title": "UnCruise: pricing, Alaska's Fjords & Glaciers with Ketchikan (Wilderness Discoverer)",
     "url": "https://uncruise.com/pages/pricing-photography-cruise-alaskas-fjords-glaciers-with-ketchikan", "kind": "first-party",
     "publisher": "UnCruise Adventures", "checked": CHECKED, "note": "Jun 27 2027, Juneau to Ketchikan, 76 guests; Navigator cabin double occupancy per person, port taxes and fees included, gratuities not included."},
]:
    upsert(S, src)

GB_LIST = "pointsparty_glacier_bay_permits"
NOTES = {
    "princess": ("Alaska specialist: sailing Alaska since 1969 and the biggest Glacier Bay presence (85 Glacier Bay calls planned in 2027). "
                 "Owns five wilderness lodges (incl. Denali and Mt. McKinley Princess) for cruisetours. Glacier Bay on most Seattle and Vancouver itineraries here; "
                 "Voyage of the Glaciers one-ways add College Fjord or Hubbard.", ["princess_alaska_2027_release", GB_LIST]),
    "hal": ("Alaska specialist: 80 years in Alaska in 2027. Holds Glacier Bay permits (Eurodam Seattle Explorer and Glacier Discovery one-ways); a National Park ranger boards for the Glacier Bay day. "
            "Owns Holland America Denali Lodge for cruisetours; 'Glacier Guarantee' and Alaska Up Close talks aboard. Many summer Vancouver sailings are sold only as cruisetours.",
            ["hal_alaska_2027_release", GB_LIST]),
    "ncl": ("Holds Glacier Bay entry: Norwegian Jade's northbound Vancouver-Whittier sailings and some Joy 9-day Seattle trips include it. "
            "Sells Denali cruisetours around Jade's one-ways (Anchorage/Fairbanks Denali Express, Denali by Rail, etc. seen on ncl.com). Big resort-style ships; freestyle dining.",
            ["ncl_vb_jade_2027", GB_LIST]),
    "rci": ("No Glacier Bay permit (not on the NPS-authorized list); glacier days are Dawes/Endicott Arm, Tracy Arm or Hubbard. "
            "Big-ship activities (rock walls, North Star on Quantum-class). Anthem's Seward one-ways reach Hubbard Glacier.", [GB_LIST]),
    "celebrity": ("No Glacier Bay permit; glacier days are Dawes/Endicott Arm or Hubbard. More upscale feel than Royal Caribbean (same parent company); "
                  "Solstice one-ways to Seward add Hubbard Glacier.", [GB_LIST]),
    "carnival": ("No Glacier Bay permit; the Seattle itinerary here uses Tracy Arm. Lowest fares and the most casual atmosphere; a single ship (Carnival Legend) does the Seattle run.", [GB_LIST]),
    "msc": ("No Glacier Bay permit. Newer to Alaska (Seattle round trips); glacier day is Dawes/Endicott or Tracy Arm per itinerary.", [GB_LIST]),
    "virgin": ("No Glacier Bay permit. Adults-only (18+), so a family of four adults qualifies. Newer to Alaska.", [GB_LIST]),
    "oceania": ("No Glacier Bay permit. Premium small-ish ships (about 1,250 guests); adults-only per an agent listing. Seattle round trips start late June.", [GB_LIST]),
    "disney": ("No Glacier Bay permit; the glacier day is scenic viewing at the Stikine Icecap. Family-focused line sailing only from Vancouver in Alaska. "
               "Disney's own search page could not be read on 2026-11-07, so prices here are reseller samples.", ["dcl_alaska", GB_LIST]),
}
for l in c["lines"]:
    if l["id"] in NOTES:
        txt, srcs = NOTES[l["id"]]
        l["alaskaNotes"] = txt
        l["alaskaNotesSources"] = srcs
        l["glacierBayPermit"] = l["id"] in ("princess", "hal", "ncl")

LUX = [
    ("Crystal – Crystal Serenity (Vancouver → Seward)", "Seen in the June 2027 Vancouver departure pattern (Mondays to Seward). Luxury, all-inclusive pricing; not priced here.", None),
    ("Silversea – Silver Whisper (Vancouver → Seward)", "Thursday departures to Seward in June 2027 per the Vancouver weekly pattern. Luxury expedition-style; not priced here.", None),
    ("Seabourn – Seabourn Encore / Odyssey (Vancouver, Seward)", "Seabourn holds Glacier Bay authorization. Luxury small ship; not priced here.", GB_LIST),
    ("Explora Journeys – Explora III", "Listed among Vancouver departures in summer 2027. Ultra-luxury; not priced here.", None),
    ("Viking – Viking Venus", "10-night Vancouver-Seward style voyages (e.g. Jul 9-19 2027) rather than 7 nights; Viking holds Glacier Bay authorization. Out of the 7-night scope.", "pointsparty_alaska_cost"),
    ("Regent Seven Seas, Oceania (Vancouver/Seward voyages)", "Luxury/premium one-ways exist in some seasons; not researched for 2027 dates. Oceania's Seattle round trip is in the main data.", None),
    ("Small-ship and expedition lines (UnCruise, Lindblad, Alaskan Dream, American Cruise Lines)",
     "Ships of roughly 50-150 guests sailing from Juneau, Sitka or Ketchikan (not Seattle/Vancouver), with kayaks, skiffs and naturalists instead of shows. "
     "Prices are far higher: roughly 5 to 10 times a big-ship interior fare per person for a summer week (UnCruise and Lindblad samples in notes/phase1.md). "
     "Fit for the parents is mixed: most days include shore landings by small boat and wet-step or beach landings, and several of these ships have no elevator. Good fit for the brothers; check each ship's accessibility page before considering it for the parents. "
     "Alaskan Dream Cruises and American Cruise Lines were not priced.", "uncruise_pricing_2027"),
]
for name, finding, src in LUX:
    upsert(c["linesReviewed"], {"line": name, "finding": finding, "source": src}, key="line")

save("catalog", c); save("sources", d["sources"])
print("lines with notes", sum(1 for l in c["lines"] if l.get("alaskaNotes")), "/", len(c["lines"]), "| linesReviewed", len(c["linesReviewed"]))
