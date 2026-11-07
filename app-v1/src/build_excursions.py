#!/usr/bin/env python3
"""Phase 2: merge excursion research into data.json (idempotent).
Run from the folder that holds data.json:  python3 src/build_excursions.py
Every offer carries a price status, a source id (see sources[]) and a check date.
Nothing here is a date-specific 2027 quote: all prices are 'published' (a real figure on the
provider's own page, read 2026-11-06, no sailing selected) or 'unavailable' (no number shown)."""
import json

CHK = "2026-11-06"
d = json.load(open("data.json"))

# ------------------------------------------------------------------ sources
SRC = [
 # id, title, url, kind, publisher, note
 ("wpyr", "White Pass & Yukon Route: Excursions", "https://wpyr.com/excursions/", "first-party", "White Pass & Yukon Route",
  "Operator's own train prices. Page shows no season/year, no accessibility info and only a link for cancellation terms."),
 ("frontier", "Frontier Excursions (Skagway)", "https://frontierexcursions.com", "first-party", "Frontier Excursions",
  "Local Skagway bus operator. Prices, pickup at the pier, 24-hour cancellation rule and vehicle accessibility notes."),
 ("goldbelt_tix", "Goldbelt Tram: tram tickets", "https://www.goldbelttram.com/activities/tram-tickets/", "first-party", "Goldbelt Tram",
  "All-day pass $60 (page footer 2026; season not explicitly stated)."),
 ("goldbelt_update", "Goldbelt Tram update", "https://www.goldbelttram.com/goldbelt-tram-update/", "first-party", "Goldbelt Tram",
  "Operator statement (May 20, 2026): tram temporarily closed as assessments continue; no reopening date."),
 ("ktoo_tram", "Juneau's Goldbelt Tram reopening still in limbo after crash this spring", "https://www.ktoo.org/2026/09/24/juneaus-goldbelt-tram-reopening-still-in-limbo-after-crash-this-spring/", "news", "KTOO Public Media (Sep 24, 2026)",
  "Tram closed all 2026 season after an April crash; waiting on a part; 2027 is the stated target and a state certification is required first."),
 ("fs_mdh_fees", "Mendenhall fees and passes (US Forest Service)", "https://www.fs.usda.gov/r10/tongass/offices/mendenhall-fees-and-passes", "government", "USDA Forest Service",
  "Visitor center: $5 per day for ages 16+ ($15 season pass); page last updated Jul 21, 2025."),
 ("fs_mdh_vc", "Mendenhall Glacier Visitor Center (US Forest Service)", "https://www.fs.usda.gov/r10/tongass/offices/mendenhall-glacier-visitor-center", "government", "USDA Forest Service",
  "Visitor center reachable from parking lots by stairs, elevators and an easy ramp."),
 ("juneau_empire_fees", "Juneau meeting to discuss fee increases for Tongass National Forest", "https://www.juneauempire.com/2026/06/20/juneau-meeting-to-discuss-fee-increases-for-tongass-national-forest/", "news", "Juneau Empire (Jun 20, 2026)",
  "Proposal (not approved): Mendenhall day fee $5 to $15; Ketchikan Discovery Center $5 to $10."),
 ("juneau_ind_fees", "$15 charge instead of $5 at Mendenhall Glacier Visitor Center (proposed)", "https://www.juneauindependent.com/post/15-charge-instead-of-5-at-mendenhall-glacier-visitor-center-other-fee-changes-proposed-by-us-fore", "news", "Juneau Independent",
  "Same proposal; comment period May 22 to Jul 20, 2026; no effective date stated."),
 ("raptor", "Alaska Raptor Center: plan your visit", "https://www.alaskaraptor.org/visit/", "first-party", "Alaska Raptor Center",
  "Adult admission $17, bought in person; spring/summer 8 am to 4 pm daily (page does not state the year)."),
 ("truealaskan", "True Alaskan Tours (Allen Marine) home page", "https://www.truealaskantours.com", "first-party", "True Alaskan Tours / Allen Marine",
  "Direct-booking site. 'From' prices plus taxes and fees; page does not say adult vs child."),
 ("allen_juneau", "Allen Marine Tours: Juneau", "https://allenmarinetours.com/juneau/", "first-party", "Allen Marine Tours",
  "Tour list and booking guidance (cruise passengers via cruise line, independents via True Alaskan Tours). No prices on page."),
 ("allen_whale", "Allen Marine: Whale Watching & Wildlife Quest", "https://allenmarinetours.com/tour/whale-watching-wildlife-quest/", "first-party", "Allen Marine Tours",
  "Wheelchair accessible when booked through the cruise line (500 lb combined limit; device max 48 x 32 in). Cancellations go through the cruise line."),
 ("ziprider", "ZipRider: Icy Strait Point", "https://ziprider.com/rides/icy-strait-point/", "first-party", "ZipRider",
  "About 90-second ride; average ticket about $200; reservations generally must go through the cruise line."),
 ("nps_klgo_fees", "Klondike Gold Rush NHP: fees", "https://www.nps.gov/klgo/planyourvisit/fees.htm", "government", "National Park Service",
  "No entrance or tour fee; ranger programs and park museums free."),
 ("nps_sitk_fees", "Sitka National Historical Park: fees", "https://www.nps.gov/sitk/planyourvisit/fees.htm", "government", "National Park Service",
  "No entrance pass required."),
 ("visit_ktn_ars", "Alaska Rainforest Sanctuary (Visit Ketchikan listing)", "https://visit-ketchikan.com/members/alaska-rainforest-sanctuary/full-page", "first-party", "Visit Ketchikan",
  "Sanctuary at Herring Cove, about 8 road miles from Ketchikan; half-mile easy trail; tours 2.75 to 3.25 h with transfers. No price on page."),
 ("pr_juneau", "Princess shore excursions: Juneau", "https://www.princess.com/en-us/shore-excursions/juneau-alaska/", "first-party", "Princess Cruises",
  "Listing page 1 of 5 (12 of 63 excursions). 'From' prices per person, not specifically per adult. No sailing selected."),
 ("pr_skagway", "Princess shore excursions: Skagway", "https://www.princess.com/en-us/shore-excursions/skagway-alaska/", "first-party", "Princess Cruises",
  "Listing page 1 of 5 (12 of 51 excursions). 'From' prices."),
 ("pr_ketchikan", "Princess shore excursions: Ketchikan", "https://www.princess.com/en-us/shore-excursions/ketchikan-alaska/", "first-party", "Princess Cruises",
  "Listing page 1 (12 of 53 excursions). 'From' prices."),
 ("pr_sitka", "Princess shore excursions: Sitka", "https://www.princess.com/en-us/shore-excursions/sitka-alaska/", "first-party", "Princess Cruises",
  "Listing page 1 (12 of 41 excursions). 'From' prices."),
 ("pr_icy", "Princess shore excursions: Icy Strait Point", "https://www.princess.com/en-us/shore-excursions/icy-strait-point-alaska/", "first-party", "Princess Cruises",
  "Listing page 1 (12 of 20 excursions; page 2 not read). 'From' prices."),
 ("pr_whale", "Princess: Local Connections Whale Watching & Wildlife Quest (Allen family)", "https://www.princess.com/en-us/shore-excursions/juneau-alaska/local-connections-whale-watching-wildlife-quest-created-by-the-allen-family", "first-party", "Princess Cruises",
  "4 h, Easy. Page shows no price. $100 cash refund from the operator if no whale is sighted in June to August."),
 ("cn_whale", "Carnival: Whale Watching & Wildlife Quest (Juneau)", "https://www.carnival.com/shore-excursions/eco-tour/whale-watching-and-wildlife-quest-171006", "first-party", "Carnival Cruise Line",
  "$220.99 for ages 13+; 4 h; Easy; ambulatory accessible (collapsible wheelchairs yes, scooters no). No cancellation text."),
 ("cn_mdh", "Carnival: Mendenhall Glacier & Wildlife Quest (Juneau)", "https://www.carnival.com/shore-excursions/juneau/mendenhall-glacier--wildlife-quest-171005", "first-party", "Carnival Cruise Line",
  "$263.99 for ages 13+; 5.5 h; Easy; ambulatory accessible. No cancellation text."),
 ("cn_zip", "Carnival: Skyglider & World's Largest ZipRider (Icy Strait Point)", "https://carnival.com/shore-excursions/icy-strait-point/the-ziprider-adventure-701011", "first-party", "Carnival Cruise Line",
  "From $196.99; 1 h; Moderate; 75 to 275 lb; no wheelchairs, canes or rollators; 1/4 mile downhill gravel walk from gondola to ZipRider."),
 ("cn_rain", "Carnival: Rainforest Wildlife Sanctuary, Eagles & Totems (Ketchikan)", "https://www.carnival.com/shore-excursions/alaska/rainforest-wildlife-sanctuary-eagles-and-totems-170043", "first-party", "Carnival Cruise Line",
  "$140.99 for ages 13+; 2.75 h; Moderate; page says not accessible (uneven surfaces, stairs)."),
 ("ncl_wpyr", "NCL: White Pass Scenic Railway (SGY_01)", "https://www.ncl.com/shore-excursions/SGY_01/White-Pass-Scenic-Railway", "first-party", "Norwegian Cruise Line",
  "From $249.99 USD; ~2.75 h; Level 1 Easy; lift car (up to 30 in wide, 700 lb with lift); modify or cancel without penalty up to 48 h before the ship arrives."),
 ("ncl_mdh", "NCL: Mendenhall Glacier & Whale Quest (JNU_12)", "https://www.ncl.com/shore-excursions/JNU_12/Mendenhall-Glacier-Whale-Quest", "first-party", "Norwegian Cruise Line",
  "Adult from $269.99; ~5.5 h; Easy; Limited Accessibility (needs 250 yards unassisted on paved, inclined paths); 48 h free cancellation."),
 ("ncl_hatch", "NCL: Scenic Juneau & Hatchery (JNU_01)", "https://www.ncl.com/shore-excursions/JNU_01", "first-party", "Norwegian Cruise Line",
  "Adult from $109.99; ~2.25 h; Easy; accessible (manual wheelchairs yes, scooters no); 48 h free cancellation."),
 ("ncl_lumber", "NCL: Great Alaskan Lumberjack Show (KTN_09)", "https://app.ncl.com/shore-excursions/KTN_09/Great-Alaskan-Lumberjack-Show", "first-party", "Norwegian Cruise Line",
  "Page lists no price, duration or accessibility; says grandstands are covered, heated and cushioned."),
 ("ncl_totem", "NCL: Totem Bight State Park & Lumberjack Show (KTN_45)", "https://www.ncl.com/fr/en/shore-excursions/KTN_45/Totem-Bight-State-Park-Lumberjack-Show", "first-party", "Norwegian Cruise Line",
  "The page I could read was the French-site version priced in euros (from 134.40 EUR), so no USD price is used. Level 2 Moderate; about half a mile of uneven gravel trail; Limited Accessibility."),
 ("butchart", "The Butchart Gardens (home page)", "https://www.butchartgardens.com", "first-party", "The Butchart Gardens",
  "Linked for price and hours. The ticket page did not load for the automated reader, so no price is captured."),
 ("ase_juneau", "Alaska Shore Excursions: Juneau", "https://alaskashoreexcursions.com/juneau", "reseller", "Alaska Shore Excursions",
  "Independent third-party seller (not the operator). 49 Juneau tours with per-person prices (adult not specified). Site states 'Free Cancellation' generally; per-tour terms not read."),
 ("ase_skagway", "Alaska Shore Excursions: Skagway", "https://alaskashoreexcursions.com/skagway", "reseller", "Alaska Shore Excursions",
  "37 Skagway tours; per-person prices unless marked per vehicle/charter."),
 ("ase_ketchikan", "Alaska Shore Excursions: Ketchikan", "https://alaskashoreexcursions.com/ketchikan", "reseller", "Alaska Shore Excursions",
  "50 Ketchikan tours incl. Ward Cove shuttles; per-person prices unless marked."),
 ("ase_sitka", "Alaska Shore Excursions: Sitka", "https://alaskashoreexcursions.com/sitka", "reseller", "Alaska Shore Excursions",
  "30 Sitka tours; per-person prices unless marked."),
]
have = {s["id"] for s in d["sources"]}
for sid, title, url, kind, pub, note in SRC:
    if sid in have:
        d["sources"] = [s for s in d["sources"] if s["id"] != sid]
    d["sources"].append({"id": sid, "title": title, "url": url, "kind": kind, "publisher": pub, "checked": CHK, "note": note})
SRC_URL = {s[0]: s[2] for s in SRC}

ASE = "https://alaskashoreexcursions.com/"

# ------------------------------------------------------------------ offer helper
def O(kind, provider, title, pp, src, hours=None, level=None, wc="not_stated", unit="pp", url=None, note=None,
      cancel=None, line=None, status=None, frm=False):
    """kind: cruise | independent | reseller | free | diy.  pp None => no number shown (status unavailable)."""
    if status is None:
        status = "published" if pp is not None else "unavailable"
    return {"kind": kind, "provider": provider, "line": line, "title": title, "pp": pp, "unit": unit,
            "from": frm, "status": status, "hours": hours, "level": level, "wheelchair": wc,
            "cancel": cancel, "note": note, "source": src, "url": url or (SRC_URL.get(src) if src else None), "checked": CHK}

def PR(title, pp, src, hours, level, wc="not_stated", note=None, **kw):   # Princess listing row
    n = "'From' price per person on Princess's listing page; no sailing selected; adult fare not separately stated."
    if note: n += " " + note
    return O("cruise", "Princess Cruises shore excursion", title, pp, src, hours, level, wc, line="princess", frm=True, note=n, **kw)
def ASEO(title, pp, hours, src, slug, unit="pp", frm=False, note=None, wc="not_stated"):
    n = "Independent reseller listing; price per person unless noted; the operator is not named on the page."
    if note: n += " " + note
    return O("reseller", "Alaska Shore Excursions (reseller)", title, pp, src, hours, None, wc, unit, ASE + slug, n,
             cancel="Site-wide 'Free Cancellation' label only; confirm terms on the tour page.", frm=frm)

# label codes: ideal_parents | precautions | brothers | everyone | not_recommended
EX = []
def E(id, port, name, cat, blurb, exertion, label, group, mob, offers, caveat=None, risk=None, ebasis="line level + planner judgment",
      weather="low", seat="mixed", photo=None, extra_ports=None):
    EX.append({"id": id, "port": port, "ports": [port] + (extra_ports or []), "name": name, "category": cat, "blurb": blurb,
               "exertion": exertion, "exertionBasis": ebasis, "label": label, "group": group, "mobility": mob,
               "seating": seat, "weather": weather, "photoPlace": photo or port, "caveat": caveat, "risk": risk,
               "offers": [dict(o, id=f"{id}-{i+1}") for i, o in enumerate(offers)]})

# ================================================================== JUNEAU
E("jnu_whale", "juneau", "Whale watching cruise", "wildlife",
  "Small-boat whale watching from Auke Bay with a naturalist; humpbacks are the headline in summer. Mostly seated on a covered boat.",
  1, "ideal_parents", "family",
  "Boarding means a few steps and a short walk; seated for most of the 3 h on the water. Carnival's page: collapsible wheelchairs allowed, scooters not. Allen Marine says wheelchair access applies when booked through the cruise line.",
  [O("cruise", "Carnival shore excursion", "Whale Watching & Wildlife Quest", 220.99, "cn_whale", 4, "Easy", "ambulatory", note="Price is for ages 13+. Carnival's page describes a $100-per-participant refund if no whale is sighted (June to August).", line="carnival"),
   O("cruise", "Princess Cruises shore excursion", "Local Connections: Whale Watching & Wildlife Quest (Allen family)", None, "pr_whale", 4, "Easy", note="Page shows no price. $100 cash refund from the operator if no whale is seen (June to August).", line="princess"),
   PR("Whale Watching & Alaska Salmon Bake", 269.95, "pr_juneau", 5, "Easy"),
   O("independent", "True Alaskan Tours (Allen Marine), direct", "Whale Watching & Wildlife Quest", 159, "truealaskan", 4, None, "not_stated", frm=True,
     note="'From' price plus taxes and fees. Not stated whether the motorcoach from the dock is included; the cruise version includes a coach to Auke Bay. Wheelchair access is stated only for cruise-line bookings.", cancel="Not read on the page."),
   ASEO("Juneau Whale Watching Adventure Tour", 149, 3.5, "ase_juneau", "juneau/whale-watching-tour")],
  caveat="Allen Marine runs the boat for both options. The cruise price includes the coach to Auke Bay; confirm whether the independent price does before comparing.", weather="medium", seat="seated")

E("jnu_mdh_whale", "juneau", "Mendenhall Glacier + whale watching", "glacier",
  "The classic Juneau pairing: a whale watching cruise plus time at Mendenhall Glacier's visitor center and viewpoints. Long day; the biggest value for one port stop.",
  2, "precautions", "family",
  "NCL's page rates it Limited Accessibility: best for guests who can walk at least 250 yards unassisted on paved, inclined paths; several coach boardings; scooters not accommodated, manual wheelchairs OK with a companion.",
  [PR("Mendenhall Glacier & Whale Quest", 269.95, "pr_juneau", 5.5, "Easy"),
   O("cruise", "Norwegian Cruise Line shore excursion", "Mendenhall Glacier & Whale Quest", 269.99, "ncl_mdh", 5.5, "Easy", "limited", cancel="Modify or cancel without penalty up to 48 hours before the ship arrives in port.", line="ncl", frm=True,
     note="Adult 'from' price on NCL's page; no sailing selected."),
   O("cruise", "Carnival shore excursion", "Mendenhall Glacier & Wildlife Quest", 263.99, "cn_mdh", 5.5, "Easy", "ambulatory", note="Price is for ages 13+.", line="carnival"),
   ASEO("Juneau Whale Watching & Mendenhall Glacier Tour", 239, 4.5, "ase_juneau", "juneau/whale-watching-mendenhall-glacier-tour")],
  caveat="Itinerary matters: a 5.5 h tour needs a Juneau stop of roughly 7+ hours to be realistic (clearance, transfers, back aboard an hour early).", weather="medium")

E("jnu_mdh_bus", "juneau", "Mendenhall Glacier by bus (visitor center & viewpoints)", "glacier",
  "Shorter, cheaper way to see the glacier: a motorcoach to the Forest Service visitor center and viewing areas, with free time to walk as little or as much as you like.",
  2, "ideal_parents", "parents",
  "The visitor center is reached from the parking lots by stairs, elevators and an easy ramp (Forest Service). Longer trails to Nugget Falls exist but are optional; trail distances were not on the page. Keep to the visitor-center views to stay well under mom's 2-mile limit.",
  [PR("Mendenhall Glacier Explorer", 89.95, "pr_juneau", 3, "Easy"),
   ASEO("Juneau Mendenhall Glacier Express Bus", 79, 3, "ase_juneau", "juneau/mendenhall-glacier-express-bus",
        note="Not stated whether the Forest Service admission fee is included."),
   O("diy", "US Forest Service", "Mendenhall Visitor Center day fee (add to any transport)", 5, "fs_mdh_fees", None, None, "not_stated",
     note="$5 per day for ages 16+ on the Forest Service page (last updated Jul 21, 2025). A rise to $15 per person is proposed but not approved (no effective date). Public transit fare and schedule not captured: Capital Transit's site blocks automated access.")],
  caveat="Ask each seller whether the visitor-center fee is included. Under the 2026 proposal the day fee could be $15 per person for 2027.")

E("jnu_tram", "juneau", "Mount Roberts Tram (Goldbelt Tram)", "scenic",
  "A six-minute ride from the cruise docks to about 1,800 feet with sweeping views and optional alpine walks. Low effort and right at the dock, IF it is running.",
  1, "ideal_parents", "parents",
  "Base station sits on the cruise docks (490 S. Franklin St). Wheelchair/ADA details are not on the operator's pages; call (907) 463-3412 before planning around it.",
  [O("independent", "Goldbelt Tram (direct)", "All-day tram pass", 60, "goldbelt_tix", 3, None, "not_stated",
     note="Adult all-day pass; page footer reads 2026 but does not state the season. Cruise passengers can also buy through the ship's shore excursion desk. Ticket is non-refundable once used.",
     cancel="Non-refundable once used; lost tickets not replaced.")],
  caveat="Do not plan around this attraction yet. See operating risk.",
  risk={"level": "high", "text": "The tram was closed all of the 2026 cruise season after an April crash. Goldbelt says it is confident it will be ready for 2027 but still needs a state certification and a replacement part (KTOO, Sep 24, 2026). Treat as unavailable until the operator confirms a 2027 opening.", "source": "ktoo_tram"},
  weather="medium", seat="seated")

E("jnu_city", "juneau", "Juneau city highlights", "city",
  "Easy sightseeing without the long glacier drive: Glacier Gardens, a salmon hatchery, whale park, or just walking the downtown waterfront.",
  1, "ideal_parents", "parents",
  "NCL lists its hatchery tour as accessible (manual wheelchairs yes, motorized scooters no). Downtown is compact; the dock is at the edge of the shopping streets (Phase 1 note, general knowledge).",
  [PR("Juneau Highlights: Glacier Gardens & Whale Park", 99.95, "pr_juneau", 2.5, "Easy"),
   O("cruise", "Norwegian Cruise Line shore excursion", "Scenic Juneau & Hatchery", 109.99, "ncl_hatch", 2.25, "Easy", "accessible", cancel="Modify or cancel without penalty up to 48 hours before the ship arrives in port.", line="ncl", frm=True,
     note="Adult 'from' price on NCL's page; no sailing selected."),
   ASEO("Juneau City Tour", 59, 1.5, "ase_juneau", "juneau/juneau-city-tour-highlights"),
   O("free", "Self-guided", "Walk downtown Juneau from the dock", 0, None, None, None, "not_stated", status="estimate",
     note="No admission to walk the streets. Not separately sourced; distances were not measured.", url=None)])

E("jnu_heli", "juneau", "Helicopter glacier landing", "glacier",
  "The splurge: fly over the Juneau Icefield and land on a glacier. Short and spectacular, weather permitting. Boarding and walking on uneven ice make this a judgment call for the parents.",
  3, "precautions", "family",
  "Helicopter boarding, a seat belt briefing, and walking on uneven ice with provided boots. Weight limits and boarding requirements were not captured: Era and Temsco's own pages block automated access.",
  [PR("Helicopter Glacier Trek", 609.95, "pr_juneau", 4.25, "Strenuous"),
   PR("Taku Glacier Helicopter Landing & Airboat Tour", 729.95, "pr_juneau", 3.25, "Easy"),
   ASEO("Mendenhall Glacier Helicopter Tour & Guided Walk", 449, 2.5, "ase_juneau", "juneau/mendenhall-glacier-guided-walk-via-helicopter-tour"),
   ASEO("Juneau Icefield Helicopter Tour", 459, 2.5, "ase_juneau", "juneau/helicopter-icefield-tour", note="The listing does not say whether it includes a glacier landing."),
   ASEO("Juneau Helicopter Glacier Walkabout", 539, 3.25, "ase_juneau", "juneau/helicopter-glacier-walkabout")],
  caveat="Four-person cost is steep ($1,800 to $2,900+). Operator pages (Era, Temsco) could not be read, so the helicopter companies' own prices are not captured.", weather="high")

E("jnu_fjord", "juneau", "Endicott Arm / Tracy Arm full-day fjord cruise", "glacier",
  "A fast catamaran into the fjord to the glacier face. Worth it only if the ship itself does not already cruise a fjord (Dawes Glacier, Glacier Bay, Hubbard).",
  1, "precautions", "family",
  "8.5 hours seated or on deck aboard a high-speed vessel; boarding steps; long day. Price/time only works on a very long Juneau call.",
  [PR("Endicott Arm Fjord & Glacier Explorer Cruise", 399.95, "pr_juneau", 8.5, "Easy"),
   O("independent", "True Alaskan Tours (Allen Marine), direct", "Tracy Arm-Fords Terror Wilderness Area & Glacier Explorer (weekend)", 289, "truealaskan", 8.5, None, frm=True,
     note="'From' price plus taxes and fees; the listing is labeled weekend.")],
  caveat="Redundant on itineraries that already include a scenic fjord or glacier day. 8.5 h exceeds the usable time on most Juneau calls.", weather="medium", seat="seated")

E("jnu_brews", "juneau", "Brews & scenic views", "food",
  "Guided tasting stops with views, light on walking. A good shared option for the brothers and, if the parents like it, the whole family.",
  1, "precautions", "family",
  "Mostly vehicle-based; walking limited to short stops (not specified in detail on the listings).",
  [PR("Juneau Brews & Scenic Views", 189.95, "pr_juneau", 3.75, "Easy"),
   ASEO("Juneau Craft Brews and Views Tour", 149, 3.75, "ase_juneau", "juneau/craft-brews-and-views-tour")])

E("jnu_active", "juneau", "Mendenhall adventures (kayak, canoe, hike, zipline)", "adventure",
  "For the brothers: paddle Mendenhall Lake among icebergs, hike toward the ice, or zipline through the rainforest.",
  4, "brothers", "brothers",
  "Paddling, trail hiking and ziplines require good mobility. Not recommended for the parents.",
  [PR("Alpine Zipline, Axe Throwing & Mendenhall Glacier Adventure", 309.95, "pr_juneau", 5.25, "Strenuous"),
   ASEO("Mendenhall Lake Canoe Tour", 239, 4, "ase_juneau", "juneau/mendenhall-lake-canoe-adventure-tour"),
   ASEO("Mendenhall Lake Kayaking Adventure", 279, 3.5, "ase_juneau", "juneau/juneau-mendenhall-lake-kayaking-adventure"),
   ASEO("Mendenhall Glacier Float Trip", 209, 3.5, "ase_juneau", "juneau/mendenhall-glacier-float-trip-tour"),
   ASEO("Guided Mendenhall Glacier Hike (6 h)", 209, 6, "ase_juneau", "juneau/guided-mendenhall-glacier-trek", frm=True, note="'From' price; a 6 h tour needs a long Juneau call.")],
  weather="medium")

E("jnu_salmon", "juneau", "Gold Creek salmon bake", "food",
  "A short, inexpensive Alaska meal in a rainforest setting near downtown. Low exertion.",
  1, "ideal_parents", "family",
  "Short sit-down meal; seating and ground surfaces not described on the listing.",
  [ASEO("Gold Creek Salmon Bake Tour", 79, 1.75, "ase_juneau", "juneau/salmon-bake-tour", note="Listing says 1.5 to 2 hours.")], seat="seated")

# ================================================================== SKAGWAY
E("skg_wpyr", "skagway", "White Pass Summit scenic railway", "rail",
  "The signature Skagway experience: a narrow-gauge train climbing to White Pass Summit past gorges and trestles. Seated, scenic, and the easiest big-ticket tour for the parents.",
  1, "ideal_parents", "family",
  "NCL's page calls it highly recommended for guests with limited mobility: a lift car on every train takes wheelchairs and scooters up to 30 in wide and 700 lb with lift. Walking limited to the depot and some cobblestone/steps.",
  [O("independent", "White Pass & Yukon Route (direct)", "White Pass Summit Excursion", 155, "wpyr", 2.75, None, "not_stated",
     note="Operator's own price; page shows no season/year, accessibility or terms. Duration listed as 2.5 to 2.75 h.", cancel="Policy is behind a link that was not retrievable."),
   O("cruise", "Norwegian Cruise Line shore excursion", "White Pass Scenic Railway", 249.99, "ncl_wpyr", 2.75, "Easy", "accessible", cancel="Modify or cancel without penalty up to 48 hours before the ship arrives in port.", line="ncl", frm=True,
     note="Adult 'from' price on NCL's page; no sailing selected; rail class not stated."),
   PR("White Pass Scenic Railway - Premium Class", 249.95, "pr_skagway", 2.75, "Easy", note="Premium Class per the listing; a different service level than the operator's standard Summit ticket."),
   ASEO("Skagway White Pass Railroad Summit Excursion & Train Tour", 169, 2.75, "ase_skagway", "skagway/white-pass-railroad-summit-excursion-tour")],
  caveat="The $155 operator price vs about $250 on cruise lines looks like a $95 per person gap, but class of service and inclusions are not confirmed to match. Check the class before booking the cheaper option.", weather="low", seat="seated")

E("skg_wpyr_long", "skagway", "Bennett Lake train journey & other long rail days", "rail",
  "Longer rail trips over the pass into British Columbia and the Yukon. Seated but long; passports needed for the border crossing.",
  2, "precautions", "family",
  "Long days (8 h for Bennett) with limited restrooms stops; mostly seated. A better fit if Skagway has a long port call.",
  [O("independent", "White Pass & Yukon Route (direct)", "Bennett Scenic Journey", 289, "wpyr", 8, None),
   O("independent", "White Pass & Yukon Route (direct)", "Steam Summit Loop Excursion", 249, "wpyr", 3, None),
   O("independent", "White Pass & Yukon Route (direct)", "Whitehorse-Skagway One Day Combo", 175, "wpyr", 10, None, note="10 h; not a fit for any cruise call shorter than about 12 h."),
   ASEO("Skagway Bennett Lake Scenic Railroad Journey", 319, 8, "ase_skagway", "skagway/bennett-scenic-railroad-journey-tour")],
  caveat="Skagway calls in the data run from about 11 h to 14.5 h; only the longest can fit an 8 h tour.", seat="seated")

E("skg_bus", "skagway", "Klondike Highway & Yukon by motorcoach", "scenic",
  "A cheaper alternative to the train: ride the Klondike Highway over the summit to the Yukon border, suspension bridge and Emerald Lake.",
  2, "precautions", "family",
  "Frontier's vehicles are not wheelchair or scooter accessible; semi-ambulatory guests and walkers can often be helped aboard with notice. Buses have no restroom (outhouses at stops; breaks up to 1.5 to 2 h apart on longer tours). Princess lists a wheelchair-accessible city/Klondike Highway/Days of '98 tour.",
  [O("independent", "Frontier Excursions (direct)", "White Pass Summit & City Tour", 77.70, "frontier", 2.75, None, "limited",
     cancel="Free to change or cancel 24+ hours ahead; no-shows charged in full (exceptions: ship skips Skagway or unrescheduled ship delay).",
     note="Pickup at the cruise pier or 3rd and Broadway. Page does not say adult vs child price."),
   O("independent", "Frontier Excursions (direct)", "Yukoner: Beyond White Pass (suspension bridge)", 140.70, "frontier", 4, None, "limited", cancel="Free to change or cancel 24+ hours ahead; no-shows charged in full."),
   O("independent", "Frontier Excursions (direct)", "Yukon Discovery Tour (Emerald Lake)", 175.35, "frontier", 6.5, None, "limited", cancel="Free to change or cancel 24+ hours ahead; no-shows charged in full."),
   PR("Easy Skagway: City, Klondike Highway & The Days of '98 Show (Wheelchair Accessible)", 89.95, "pr_skagway", 3.25, "Easy", "accessible"),
   ASEO("Skagway City and Summit Tour", 75, 2.75, "ase_skagway", "skagway/city-and-summit-tour"),
   ASEO("Skagway Yukon Discovery Adventure", 169, 6.5, "ase_skagway", "skagway/yukon-discovery-adventure-tour")],
  caveat="Yukon tours cross into Canada: bring passports (all four travelers have them).")

E("skg_town", "skagway", "Historic downtown & Klondike Gold Rush park", "city",
  "Skagway's boardwalk-lined Broadway is a preserved gold-rush town; the National Park Service runs free museum exhibits and ranger programs.",
  1, "ideal_parents", "parents",
  "Flat, compact historic district near the docks (Phase 1 note: roughly half a mile from the berths; general knowledge, not measured). Plan benches and a restaurant stop to stay under mom's 2-mile limit.",
  [O("free", "National Park Service", "Klondike Gold Rush NHP: museum exhibits and ranger programs", 0, "nps_klgo_fees", None, None, "not_stated", note="No entrance or tour fee per the NPS fees page."),
   PR("Exclusive Morning with the Madam at the Red Onion Saloon", 99.95, "pr_skagway", 2.5, "Easy")])

E("skg_adventure", "skagway", "Zipline & adventure park", "adventure",
  "Forest ziplines and canopy courses for the brothers.",
  4, "brothers", "brothers", "Strenuous per Princess; not suited to reduced mobility.",
  [PR("Adventure Park & Ziplines", 179.95, "pr_skagway", 3.25, "Strenuous"),
   ASEO("Skagway Adventure Park & Zipline Tour", 204, 3.5, "ase_skagway", "skagway/adventure-park-zipline-tour"),
   ASEO("Grizzly Falls Ziplining Adventure", 260, 4, "ase_skagway", "skagway/grizzly-falls-ziplining-adventure-tour")])

E("skg_bike", "skagway", "E-bike, hike & float", "adventure",
  "Self-powered options for the brothers: e-bikes to Reid Falls, a hike-and-float combo, or the Chilkoot Trail.",
  3, "brothers", "brothers", "Cycling, trail walking and river floats; moderate effort.",
  [ASEO("Skagway eBike Tour with Gold Panning & Reid Falls", 130, 3, "ase_skagway", "skagway/ebike-tour-with-gold-panning-reid-falls"),
   ASEO("Skagway Electric Bike Rental", 70, 3.5, "ase_skagway", "skagway/electric-bike-rental", frm=True, note="'From' price; listing says 3 to 4 hours."),
   ASEO("Skagway Hike and Float", 142, 4, "ase_skagway", "skagway/hike-and-float-tour"),
   ASEO("Skagway Chilkoot Trail Hike, Float & Summit Drive", 243, 6, "ase_skagway", "skagway/chilkoot-trail-hike-float-and-summit-drive"),
   ASEO("Skagway River Float", 100, 2.4, "ase_skagway", "skagway/river-float-tour", note="Listing says 2.25 to 2.5 hours.")])

E("skg_mushers", "skagway", "Musher's camp (sled dogs)", "wildlife",
  "Meet sled dogs and puppies at a working musher's camp; Princess rates it Easy.",
  1, "everyone", "family", "Princess lists the standard camp experiences as Easy; ground surfaces not described.",
  [PR("Musher's Camp & S'more Roasting Adventure", 159.95, "pr_skagway", 2.75, "Easy"),
   PR("Ultimate Musher's Camp Experience: Dog Sled Ride, Gold Panning & S'mores", 319.95, "pr_skagway", 4, "Easy"),
   ASEO("Skagway Musher's Camp and S'Mores Roasting", 150, 2.75, "ase_skagway", "skagway/mushers-camp-and-smores-roasting")])

E("skg_heli", "skagway", "Glacier helicopter", "glacier",
  "Flightseeing over Skagway's glaciers; pricey, weather-dependent.",
  2, "precautions", "family", "Helicopter boarding required; operator details not captured.",
  [ASEO("Skagway Glacier Helicopter Tour", 479, 2, "ase_skagway", "skagway/glacier-discovery-via-helicopter-tour"),
   ASEO("Skagway Glacier Dogsledding Demonstration by Helicopter", 649, 2, "ase_skagway", "skagway/dogsled-glacier-flightseeing-helicopter-tour")], weather="high")

# ================================================================== KETCHIKAN
E("ktn_lumber", "ketchikan", "Great Alaskan Lumberjack Show", "culture",
  "Competitive lumberjack sports in covered, heated, cushioned grandstands: a good rainy-day pick and a crowd-pleaser for the whole family.",
  1, "ideal_parents", "family",
  "About 1.25 h seated in covered grandstands (NCL's page). Distance from the downtown berths was not captured; Ward Cove calls need a shuttle. Princess's listing shows the show alone.",
  [PR("Great Alaskan Lumberjack Show", 43.00, "pr_ketchikan", 1.25, "Easy"),
   O("cruise", "Norwegian Cruise Line shore excursion", "Great Alaskan Lumberjack Show", None, "ncl_lumber", None, None, note="NCL's page shows no price, duration or accessibility.", line="ncl"),
   ASEO("Great Alaskan Lumberjack Show & Axe Throwing Challenge", 80, 1.75, "ase_ketchikan", "ketchikan/great-alaskan-lumberjack-show-axe-throwing-challenge"),
   ASEO("Great Alaskan Lumberjack Show & Axe Throwing Challenge at Ward Cove", 90, 2, "ase_ketchikan", "ketchikan/great-alaskan-lumberjack-show-axe-throwing-challenge-at-ward-cove")],
  caveat="Princess's $43 may be a bare show ticket; the reseller prices include the axe-throwing add-on.", seat="seated", extra_ports=["ketchikan_wc"])

E("ktn_city", "ketchikan", "Creek Street, totems & downtown", "city",
  "Ketchikan's historic boardwalk street, totem poles and waterfront. Flat and close to the downtown berths; often rainy.",
  1, "ideal_parents", "parents",
  "Creek Street is a short flat walk from the downtown gangway (Phase 1 note, not measured). Trolley and duck tours cover the sights without walking. From Ward Cove you need a shuttle first.",
  [PR("City Highlights, Totems & Creek Street by Trolley", 64.95, "pr_ketchikan", 1.5, "Easy"),
   PR("Totem Bight State Park & Ketchikan Highlights", 74.95, "pr_ketchikan", 2.5, "Easy"),
   ASEO("Ketchikan Duck Tour", 79, 1.5, "ase_ketchikan", "ketchikan/duck-tour"),
   O("free", "Self-guided", "Walk Creek Street and the downtown waterfront", 0, None, None, None, status="estimate", url=None,
     note="No admission to walk the streets. Not separately sourced."),
   O("diy", "US Forest Service", "Southeast Alaska Discovery Center admission", 5, "juneau_empire_fees", None, None, note="$5 per person per day per the Juneau Empire proposal article (a rise to $10 is proposed, not approved). Not verified on the Forest Service page.", status="published")],
  extra_ports=["ketchikan_wc"], weather="medium")

E("ktn_totems", "ketchikan", "Saxman Native Village & Totem Bight", "culture",
  "Native carving, a dance performance and totem parks just outside town.",
  2, "ideal_parents", "family",
  "Princess lists the Saxman tour as wheelchair accessible and Easy. NCL's Totem Bight tour is Level 2 Moderate with about half a mile of hard-packed, uneven gravel trail.",
  [PR("Saxman Native Village, Dance Performance & Totem Park (Wheelchair Accessible)", 94.95, "pr_ketchikan", 2, "Easy", "accessible"),
   O("cruise", "Norwegian Cruise Line shore excursion", "Totem Bight State Park & Lumberjack Show", None, "ncl_totem", 3.5, "Moderate", "limited", line="ncl",
     note="The readable NCL page showed 134.40 EUR (French site); no USD price captured."),
   ASEO("Ketchikan Nature Walk & Totem Park Tour", 95, 2, "ase_ketchikan", "ketchikan/nature-walk-totem-park-tour"),
   ASEO("Ketchikan Highlights, Lumberjack Show & Saxman Native Village", 129, 3.9, "ase_ketchikan", "ketchikan/highlights-lumberjack-show-saxman-native-village", note="Listing says 3.5 to 4.25 hours.")],
  extra_ports=["ketchikan_wc"])

E("ktn_misty_boat", "ketchikan", "Misty Fjords by boat", "wildlife",
  "A catamaran into the Misty Fjords National Monument: cliffs, waterfalls and wildlife. The easiest way to see the fjords.",
  1, "ideal_parents", "family",
  "Princess lists this boat tour as wheelchair accessible and Easy; 5.25 h seated on a covered vessel.",
  [PR("Misty Fjords & Wilderness Explorer Cruise (Wheelchair Accessible)", 259.95, "pr_ketchikan", 5.25, "Easy", "accessible"),
   O("independent", "True Alaskan Tours (Allen Marine), direct", "Misty Fjords & Wilderness Explorer", 219, "truealaskan", 5.25, None, frm=True, note="'From' price plus taxes and fees; listed as 5 h 15 min.")],
  caveat="A 5.25 h tour needs a Ketchikan call of about 7 h or more. Several itineraries stop only 6 to 6.5 h.", weather="medium", seat="seated", extra_ports=["ketchikan_wc"])

E("ktn_misty_air", "ketchikan", "Misty Fjords floatplane", "scenic",
  "Fly over (and sometimes land in) Misty Fjords. Short, scenic, weather-dependent.",
  2, "precautions", "family",
  "Floatplane boarding from a dock and a small cabin; weight/size limits were not captured because Taquan Air's page did not load.",
  [PR("Exclusive Flightseeing & Taste of Alaska", 419.95, "pr_ketchikan", 3, "Easy"),
   ASEO("Ketchikan Misty Fjords Flightseeing via Seaplane", 329, 2, "ase_ketchikan", "ketchikan/misty-fjords-national-monument-via-seaplane-tour"),
   ASEO("Ketchikan Misty Fjords Flightseeing Tour", 371, 1.5, "ase_ketchikan", "ketchikan/misty-fjords-flightseeing-tour"),
   ASEO("Deluxe Misty Fjords National Monument Tour", 385, 2, "ase_ketchikan", "ketchikan/deluxe-misty-fjords-tour")],
  weather="high", extra_ports=["ketchikan_wc"])

E("ktn_rain", "ketchikan", "Rainforest sanctuary, eagles & bears", "wildlife",
  "A wildlife center and rainforest trail at Herring Cove: eagles, owls, and black bears in season.",
  3, "precautions", "family",
  "Carnival's page says the tour is not accessible and needs walking medium distances over uneven ground with stairs. The sanctuary's own listing describes an easy half-mile trail. Treat as a risk for mom's mobility.",
  [O("cruise", "Carnival shore excursion", "Rainforest Wildlife Sanctuary, Eagles & Totems", 140.99, "cn_rain", 2.75, "Moderate", "no", note="Price is for ages 13+.", line="carnival"),
   PR("Rainforest Canoe & Nature Trail", 129.95, "pr_ketchikan", 3.5, "Moderate"),
   ASEO("Alaska Rainforest Sanctuary and Totem Park", 110, 2.75, "ase_ketchikan", "ketchikan/rainforest-wildlife-center-and-eagle-sanctuary-tour"),
   ASEO("Ketchikan Black Bear Express Tour", 200, 2, "ase_ketchikan", "ketchikan/black-bear-express-tour")],
  extra_ports=["ketchikan_wc"])

E("ktn_crab", "ketchikan", "Crab feast", "food",
  "All-you-can-eat style seafood meals at lodges and waterfront restaurants. Easy, short.",
  1, "ideal_parents", "family", "Sit-down meals; Princess rates the lodge feast Easy.",
  [PR("Crab Feast at George Inlet Lodge", 139.95, "pr_ketchikan", 2.5, "Easy"),
   ASEO("World Famous George Inlet Lodge Crab Feast", 110, 2.5, "ase_ketchikan", "ketchikan/world-famous-george-inlet-lodge-crab-feast"),
   ASEO("Ketchikan Harbor Haus Crab Feast", 109, 1.25, "ase_ketchikan", "ketchikan/harbor-haus-crab-feast")],
  seat="seated", extra_ports=["ketchikan_wc"])

E("ktn_wildlife", "ketchikan", "Wildlife & waterfront cruises", "wildlife",
  "Small-boat looks at harbor wildlife, eagles, sea lions and whales.",
  1, "everyone", "family", "Boat boarding with steps; mostly seated.",
  [O("independent", "True Alaskan Tours (Allen Marine), direct", "Waterfront & Wildlife Cruise", 109, "truealaskan", 2, None, frm=True, note="'From' price plus taxes and fees."),
   O("independent", "True Alaskan Tours (Allen Marine), direct", "Wildlife Safari & Beach Campfire", 169, "truealaskan", 3.5, None, frm=True, note="'From' price; ages 3+."),
   ASEO("Ketchikan Wildlife, Sightseeing and Whale Search Tour", 199, 2.75, "ase_ketchikan", "ketchikan/wildlife-sightseeing-and-whale-watching-tour", note="Listing says 2.5 to 3 hours.")],
  weather="medium", seat="seated", extra_ports=["ketchikan_wc"])

E("ktn_active", "ketchikan", "Zipline, UTV, kayak & e-bike", "adventure",
  "Active options for the brothers.",
  4, "brothers", "brothers", "Requires good mobility.",
  [PR("Rainforest Island Nature Walk & Seahawk Adventure", 219.95, "pr_ketchikan", 4, "Moderate"),
   ASEO("Ketchikan Rainforest Canopy & Zipline Adventure", 200, 3.5, "ase_ketchikan", "ketchikan/rainforest-canopy-zipline-tour"),
   ASEO("Ketchikan Mahoney Lake UTV Off Road Safari", 249, 3.5, "ase_ketchikan", "ketchikan/mahoney-lake-utv-off-road-safari", note="Listing says 3.25 to 3.75 hours."),
   ASEO("Ketchikan Sea Kayak Eco Tour", 149, 4, "ase_ketchikan", "ketchikan/sea-kayak-eco-tour"),
   ASEO("Ketchikan Electric Bike and Hike Tour", 149, 4, "ase_ketchikan", "ketchikan/electric-bike-and-hike-tour")],
  extra_ports=["ketchikan_wc"])

E("ktn_wc_shuttle", "ketchikan_wc", "Ward Cove to downtown shuttle", "transport",
  "Ships docking at Ward Cove (NCL calls) are about 7 miles from Creek Street; this is the transfer for independent exploring.",
  1, "precautions", "family",
  "Adds a vehicle transfer and a longer day for the parents.",
  [ASEO("Waterfront Shuttle: Ward Cove to Downtown Ketchikan", 65, 1, "ase_ketchikan", "ketchikan/waterfront-shuttle-ward-cove-to-downtown-ketchikan",
        note="Listing is one-way and does not say whether the price is per person; a separate listing covers the return trip, so a round trip could cost double. Confirm before relying on it.")],
  caveat="Cost to reach downtown from Ward Cove may be a real extra on NCL's Ketchikan stops.")

# ================================================================== SITKA
E("sit_wildlife", "sitka", "Sea otter & whale watching cruise", "wildlife",
  "Short wildlife boat trips in Sitka Sound: sea otters, whales, eagles.",
  2, "precautions", "family",
  "Princess rates it Moderate. At Sitka a tender or a shuttle from the terminal may add steps and waiting; not confirmed per call.",
  [PR("Marine Expedition & Wildlife Quest", 159.95, "pr_sitka", 2.25, "Moderate"),
   O("independent", "True Alaskan Tours (Allen Marine), direct", "Whale Watch & Sea Otter Quest", 169, "truealaskan", 2, None, frm=True, note="'From' price plus taxes and fees."),
   ASEO("Sitka Sound Sea Otter & Marine Wildlife Quest", 169, 2, "ase_sitka", "sitka/sea-otter-marine-wildlife-quest"),
   ASEO("Sitka Whale Watching & Marine Adventure", 188, 2, "ase_sitka", "sitka/whale-watching-and-marine-wildlife-adventure")],
  weather="medium", seat="seated")

E("sit_town", "sitka", "Raptor Center, totems & Fortress of the Bear", "culture",
  "Sitka's compact cultural stops: eagles and owls at the Raptor Center, totem poles in the national park, and rescued bears.",
  2, "ideal_parents", "parents",
  "Princess lists the Odyssey Theater/totems tour and the city highlights tour as Easy; its Raptor/Park/Fortress combo is Moderate. The Raptor Center admission is paid in person. NPS park entry is free.",
  [PR("Totems, City & Raptor Encounter at the Alaskan Odyssey Theater", 99.95, "pr_sitka", 2.75, "Easy"),
   PR("Easy Sitka: Historic City Highlights", 124.95, "pr_sitka", 3.5, "Easy"),
   PR("Experience Sitka: Raptor Center, Park & Fortress of the Bear", 119.95, "pr_sitka", 3.5, "Moderate"),
   ASEO("Sitka Premium Scenic Tour: Fortress of the Bear, Raptor Center & Totem Village", 110, 2.5, "ase_sitka", "sitka/premium-scenic-tour-raptor-center-fortress-of-the-bears-and-totem-village"),
   ASEO("Sitka Fortress of the Bears & Totem Park Adventure", 95, 2, "ase_sitka", "sitka/fortress-of-the-bears-totem-park-adventure"),
   O("diy", "Alaska Raptor Center", "Raptor Center admission (self-guided)", 17, "raptor", None, None, note="Adult $17, bought in person. Hours 8 am to 4 pm in spring/summer (last admission 3:30 pm). Page does not state the year or accessibility."),
   O("free", "National Park Service", "Sitka National Historical Park (totem trail)", 0, "nps_sitk_fees", None, None, note="No entrance pass required. Getting there from the dock was not captured.")],
  caveat="Sitka's dock sits several miles from downtown (Phase 1 note); a shuttle or tour transport is part of the cost and timing.")

E("sit_active", "sitka", "Hike, kayak, bike & ATV", "adventure",
  "Active ways to see Sitka for the brothers.",
  4, "brothers", "brothers", "Strenuous per Princess for hiking and bike tours.",
  [PR("Tongass Rainforest Hike", 139.95, "pr_sitka", 3, "Strenuous"),
   PR("Alaska Wilderness ATV Adventure", 314.95, "pr_sitka", 3.5, "Moderate"),
   ASEO("Sitka Sound Kayak Adventure", 165, 2, "ase_sitka", "sitka/harbor-and-islands-guided-paddle-tour"),
   ASEO("Sitka Downtown Electric Bike Rental", 120, 4.5, "ase_sitka", "sitka/self-guided-electric-bike-rental", note="Listing says 4 to 5 hours.")])

# ================================================================== ICY STRAIT POINT
E("isp_zip", "icy_strait", "ZipRider", "adventure",
  "One of the world's longest, fastest ziplines: 5,495 feet, about 90 seconds, ending on the beach. Cruise-line booking is generally required.",
  3, "brothers", "brothers",
  "Weight limits 75 to 275 lb; guests must hold the straps and keep legs straight; Carnival's page says not accessible to wheelchairs, canes or rollators; 1/4 mile downhill gravel walk from the gondola; excluded for back/neck/heart conditions.",
  [PR("ZipRider Adventure & SkyPeak Gondola", 199.95, "pr_icy", 1.5, "Moderate"),
   O("cruise", "Carnival shore excursion", "Skyglider & World's Largest ZipRider", 196.99, "cn_zip", 1, "Moderate", "no", line="carnival", frm=True, note="'From' price."),
   O("independent", "ZipRider (operator)", "ZipRider, Icy Strait Point (average ticket)", 200, "ziprider", 1.5, None, "not_stated",
     note="Operator's page states an average ticket of about $200 and says reservations generally must go through the cruise line, so there is no separate independent booking price.")],
  caveat="No savings from booking independently: the operator routes reservations through cruise lines.", seat="standing")

E("isp_gondola", "icy_strait", "SkyPeak Gondola", "scenic",
  "A gondola ride above the cannery for views; the gentlest scenic add-on at this port.",
  1, "precautions", "parents",
  "Gondola ride itself is low effort; the walk to the ZipRider is 1/4 mile of downhill gravel, so avoid that. Whether the summit area is accessible was not stated.",
  [PR("SkyPeak Gondola", 54.95, "pr_icy", 1, "Easy")], seat="seated")

E("isp_culture", "icy_strait", "Hoonah cultural drive & local connections", "culture",
  "Tlingit-led scenic drive, tribal connections and a cooking class: easy ways to learn about the place.",
  1, "ideal_parents", "parents",
  "Princess lists these tours as Easy; both the scenic drive and the cooking class have wheelchair-accessible versions.",
  [PR("Easy Hoonah: Scenic Drive & Tribal Connections (Wheelchair Accessible)", 89.95, "pr_icy", 1.5, "Easy", "accessible"),
   PR("Local Connections: Cooking in Alaska's Wildest Kitchen (Wheelchair Accessible)", 129.95, "pr_icy", 1.5, "Easy", "accessible")], seat="seated")

E("isp_wildlife", "icy_strait", "Bear & wildlife viewing", "wildlife",
  "Search for Alaska brown bears and other wildlife around Hoonah.",
  2, "precautions", "family",
  "Princess rates the brown bear search Moderate; the jeep tour Easy.",
  [PR("Remote Wildlife & Brown Bear Search", 144.95, "pr_icy", 2.5, "Moderate"),
   PR("Back Country Jeep Adventure", 199.95, "pr_icy", 2.5, "Easy"),
   PR("Discover the Birds of Hoonah", 209.95, "pr_icy", 3.5, "Moderate")])

E("isp_active", "icy_strait", "Kayak, hike & ocean raft", "adventure",
  "Active excursions for the brothers.",
  4, "brothers", "brothers", "Strenuous kayaking; moderate hiking and raft.",
  [PR("Icy Strait Kayak Adventure", 149.95, "pr_icy", 2.5, "Strenuous"),
   PR("Wilderness Hike", 109.95, "pr_icy", 2.5, "Moderate"),
   PR("Ocean Raft Adventure", 194.95, "pr_icy", 2, "Moderate")])

# ================================================================== VICTORIA
E("vic_butchart", "victoria", "Butchart Gardens", "scenic",
  "Famous gardens near Victoria. Only workable on a daytime call.",
  2, "precautions", "parents",
  "Garden paths and transfer distance not captured. Most itineraries reach Victoria in the evening (Voyager of the Seas is the one with a full day, 8 am to 6 pm).",
  [O("independent", "The Butchart Gardens", "Butchart Gardens admission", None, "butchart", None, None, status="unavailable",
     note="Not captured: the ticket page did not load. Verify price, hours and the transfer from Ogden Point on the Butchart site.")],
  caveat="Skip unless the sailing reaches Victoria in daytime.", photo="victoria")

E("vic_harbour", "victoria", "Inner Harbour stroll", "city",
  "Evening walk around Victoria's Inner Harbour and Parliament buildings if the ship's call allows.",
  1, "ideal_parents", "parents",
  "Ogden Point to the Inner Harbour is roughly 1.5 to 2 km per the Phase 1 port note, so budget a taxi or shuttle; evening calls are only 3 to 4 hours.",
  [O("free", "Self-guided", "Walk the Inner Harbour", 0, None, None, None, status="estimate", url=None,
     note="No admission. Transport from Ogden Point not captured.")], photo="victoria")

# ================================================================== SCENIC CRUISING (free, onboard)
SC = [("glacier_bay", "Glacier Bay: ranger commentary & deck viewing", "National Park Service rangers board ships for commentary (Phase 1 note; NPS page did not load for re-verification). A balcony works for the parents; the open bow decks get crowded."),
      ("endicott_arm", "Endicott Arm & Dawes Glacier: onboard viewing", "Morning fjord cruising to Dawes Glacier; ice conditions decide how close the ship gets."),
      ("tracy_arm", "Tracy Arm Fjord: onboard viewing", "Narrow fjord; large ships may substitute Endicott Arm if ice is heavy (Phase 1 note)."),
      ("hubbard", "Hubbard Glacier: onboard viewing", "North America's largest tidewater glacier; only on the Norwegian Joy Fri Jun 25 / Jul 9 sailing in this data set."),
      ("stephens_passage", "Stephens Passage: whale spotting from the ship", "Channel south of Juneau known for humpback whales; Holland America lists it as scenic cruising.")]
for pid, nm, bl in SC:
    E("scn_" + pid, pid, nm, "scenic", bl, 0, "ideal_parents", "family",
      "No walking: watch from the balcony, a window lounge or an open deck. No separate booking.",
      [O("free", "Onboard (included in cruise fare)", "Scenic cruising: no extra charge", 0, None, None, None, status="estimate", url=None,
         note="Included in the fare; not separately sourced. Scenic times come from Phase 1 itinerary data.")],
      ebasis="no activity required", seat="seated", weather="low")

# ------------------------------------------------------------------ port logistics found in Phase 2 (documented facts only)
LOG = {
 "juneau": [
   {"text": "Goldbelt Tram base station is on the cruise docks at 490 S. Franklin St. (tram closed in 2026; 2027 reopening unconfirmed).", "source": "goldbelt_update"},
   {"text": "Mendenhall Visitor Center is reached from its parking lots by stairs, elevators and an easy ramp.", "source": "fs_mdh_vc"},
   {"text": "Allen Marine's Juneau office is in Auke Bay (13391 Glacier Highway). Cruise whale tours include a motorcoach from downtown.", "source": "allen_juneau"}],
 "skagway": [
   {"text": "Frontier Excursions' default pickup is at the cruise pier where it meets land outside the security gates (or 3rd and Broadway).", "source": "frontier"},
   {"text": "No fee to enter Klondike Gold Rush NHP; ranger programs and museums are free.", "source": "nps_klgo_fees"}],
 "ketchikan": [
   {"text": "Alaska Rainforest Sanctuary is at Herring Cove, about 8 road miles from town.", "source": "visit_ktn_ars"}],
 "ketchikan_wc": [
   {"text": "A reseller lists a Ward Cove to downtown shuttle at $65 (one way, per-person basis unclear).", "source": "ase_ketchikan"}],
 "sitka": [
   {"text": "Alaska Raptor Center: 1000 Raptor Way; adult admission $17 in person; spring/summer 8 am to 4 pm.", "source": "raptor"},
   {"text": "Sitka National Historical Park has no entrance fee.", "source": "nps_sitk_fees"}],
 "icy_strait": [
   {"text": "ZipRider reservations generally must be made through the cruise line; ride is 5,495 ft over about 90 seconds.", "source": "ziprider"}],
}
for p in d["places"]:
    if p["id"] in LOG:
        p["logistics"] = LOG[p["id"]]

# ------------------------------------------------------------------ meta
cov = {
 "checked": CHK,
 "summary": "Excursion prices are published figures read on provider pages with no 2027 sailing selected. None are date-specific quotes, so none are labeled verified.",
 "linesWithCruiseExcursionPrices": {
   "princess": "Juneau, Skagway, Ketchikan, Sitka, Icy Strait Point: first page of each port listing only (12 excursions per port out of 20 to 63).",
   "carnival": "Four Alaska excursions (Juneau whale, Mendenhall, Icy Strait ZipRider, Ketchikan rainforest).",
   "ncl": "Four pages: White Pass railway, Mendenhall & whales, Juneau hatchery, Lumberjack Show (no price). A Totem Bight page showed euros only."},
 "linesNotCaptured": {
   "hal": "Holland America's excursion pages did not load for the automated reader.",
   "rci": "Royal Caribbean's port page returned an error.",
   "celebrity": "Celebrity's port page returned an error.",
   "msc": "Not attempted.", "virgin": "Not attempted.", "oceania": "Not attempted."},
 "operatorPagesBlocked": ["Era Alaska helicopters (robots.txt)", "Temsco helicopters (robots.txt)", "Gastineau Guiding (robots.txt)", "Capital Transit Juneau (robots.txt)", "Taquan Air (page error)", "Butchart Gardens ticket page (error)", "Icy Strait Point tours page (error)", "Holland America port page (error)", "Great Alaskan Lumberjack Show official site (domain redirected to an unrelated ad site; not followed)", "NPS Glacier Bay cruise-ship page (error)", "Alaska State Parks Totem Bight page (error)"],
 "gaps": [
   "Icy Strait Point whale-watching prices (Princess listing page 2 not read).",
   "Victoria excursion prices, including Butchart Gardens.",
   "Dock-to-attraction walking distances were not measured; mobility notes rely on documented cruise-line descriptions and planner judgment.",
   "Cancellation terms for most operators (only NCL 48 h, Frontier 24 h and the Goldbelt ticket rule were read).",
   "Return-to-ship protection wording for independent tours was not read per operator.",
   "Excursion-specific photos: cards use the port photo (Wikimedia Commons, already credited). Phase 4 can add tour photos."],
 "subjectiveFields": ["exertion (0-5) combines the cruise line's published Easy/Moderate/Strenuous level with planner judgment", "label (ideal for parents, suitable with precautions, best for brothers, great for everyone)", "weather sensitivity", "group suggestion"],
 "notes": [
   "Prices marked 'from' are minimums on listing pages; adult-specific fares were not always stated.",
   "Reseller prices (Alaska Shore Excursions) are third-party prices for tours run by local operators; the page did not name the operator.",
   "Low exertion is not the same as confirmed accessibility. Wheelchair flags are copied only where a page said so."]
}
d["meta"]["excursionCoverage"] = cov
d["meta"]["labels"] = {
  "ideal_parents": "Ideal for parents", "precautions": "Suitable with precautions", "brothers": "Best for brothers",
  "everyone": "Great for everyone", "not_recommended": "Not recommended for reduced mobility"}
d["meta"]["offerKinds"] = {
  "cruise": "Cruise-sponsored (Option A)", "independent": "Operator direct (Option B)", "reseller": "Independent reseller (Option B)",
  "free": "Free / self-guided", "diy": "Self-guided with admission"}
d["meta"]["version"] = "0.2.0-phase2"
d["meta"]["updated"] = CHK
for ph in d["meta"]["phases"]:
    if ph["n"] == 2: ph["status"] = "done"
    elif ph["n"] == 3: ph["status"] = "next"
d["excursions"] = EX
json.dump(d, open("data.json", "w"), ensure_ascii=False, indent=1)
n_off = sum(len(e["offers"]) for e in EX)
print("excursions", len(EX), "offers", n_off, "sources", len(d["sources"]))
