#!/usr/bin/env python3
"""Phase 3: Juneau, Skagway, Ketchikan. Walking miles, stairs/hills and DIY/budget options.

- fills walkMiles / walkBasis / walkConfidence / stairsHills on every experience in those ports
  (walkMiles is a CONSERVATIVE planning figure for one person: dock to start, on-tour walking and
  back to the dock, taking the higher end when a source gives a range);
- adds 13 DIY experiences (rental car, public bus/shuttle, self-guided walks, free hikes);
- adds sources, price rows (unknown prices are `unavailable`), and place logistics.
Idempotent. Run from the repo root: python3 tools/p3_experiences_a.py
"""
import sys
sys.path.insert(0, "tools")
from common import load, save

CHECKED = "2026-11-07"
d = load()
S = d["sources"]["sources"]
R = d["prices"]["rows"]
X = d["experiences"]["experiences"]
PL = {p["id"]: p for p in d["catalog"]["places"]}


def upsert(lst, rec, key="id"):
    for i, r in enumerate(lst):
        if r.get(key) == rec[key]:
            lst[i] = rec
            return
    lst.append(rec)


def src(id, title, url, kind, publisher, note):
    upsert(S, {"id": id, "title": title, "url": url, "kind": kind, "publisher": publisher, "checked": CHECKED, "note": note})


# ---------------------------------------------------------------- sources
src("jcat_glacier", "How to Ride to the Mendenhall Glacier Visitor Center with Capital Transit", "https://juneaucapitaltransit.org/glacier",
    "first-party", "Capital Transit (Juneau)", "Routes 3, 4, 8 stop at Dredge Lake Rd; $2 adult cash fare; stop is about 1.5 mi (30 min) from the visitor center on a flat paved path; up to about 1.5 h each way.")
src("cruisehive_juneau", "Juneau Cruise Port, Alaska: Overview and Guide", "https://www.cruisehive.com/juneau-cruise-port-guide/99168",
    "secondary", "CruiseHive", "Docks, walking distances to downtown, $5 AJ Dock shuttle, wheelchair access at Franklin Dock and the cruise terminal.")
src("fs_mdh_trails_map", "Mendenhall Glacier Recreation Area trail map (Forest Service)", "https://www.fs.usda.gov/media/199080",
    "government", "USDA Forest Service", "Trail lengths: 1/3 mi paved round trip, Nugget Falls 2 mi round trip gravel, Trail of Time 1 mi loop, Steep Creek 0.25 mi loop. Fee area, amounts not on the map.")
src("fs_nugget_falls", "Nugget Falls Trail (Tongass National Forest)", "https://www.fs.usda.gov/r10/tongass/recreation/trails/nugget-falls-trail",
    "government", "USDA Forest Service", "Lists 0.8 mi without saying one way or round trip; mostly natural surface, gentle slope; starts just past the visitor center.")
src("juneau_museum_tours", "Juneau-Douglas City Museum walking tours (2026 schedule)", "https://juneau.org/library/museum/walking-tours",
    "government", "City and Borough of Juneau", "Historic Downtown tour 90 min, $31.50, Tue-Thu 1:45 pm, last tour June 30 2026; Capitol tour free on weekdays; tours may include inclines, stairs and uneven ground.")
src("gpsmycity_juneau", "Juneau Introduction Walking Tour (self guided)", "https://www.gpsmycity.com/tours/juneau-introduction-walking-tour-7102.html",
    "secondary", "GPSmyCity", "About 1.1 mi, about 2 h, 12 stops, first stop the Juneau Cruise Port; narrow streets and wooden boardwalks.")
src("alaskaorg_juneau_trails", "Parks & Trails in Juneau (alaska.org)", "https://alaska.org/destination/juneau/trails",
    "secondary", "Alaska.org", "Perseverance Trail about 3 mi moderate; Mount Roberts Trail difficult and steep, trailhead about 1 mi from downtown (Basin Road); Airport Dike Trail 1 mi paved.")
src("cc_juneau_rental", "Cruise Critic: car rental in Juneau and ideas for visiting with an older parent", "https://boards.cruisecritic.com/topic/2522669-car-rental-in-juneau-amp-ideas-for-visiting-with-older-parent/",
    "secondary", "Cruise Critic forum (anecdotal)", "Cruiser reports: Juneau Car Rental and Avis downtown, about a 20-minute walk from some berths; downtown office reportedly closes about 2 pm on cruise days; airport rentals cheaper but need a cab. Not first-party.")
src("skagway_getting_around", "Skagway: Getting Around (Skagway Convention & Visitors Bureau)", "https://www.skagway.com/plan-your-trip/travel-transportation/getting-around/",
    "first-party", "Skagway Convention & Visitors Bureau", "SMART bus $5 all day or $3 each way, 7 am-9 pm on ship days; on-demand shuttle $5 to River Bridge, $10 to end of pavement on Dyea/Liarsville Rd, $15 to Dyea; rental companies Affordable Car Rentals and Drive About.")
src("nps_klgo_hikes", "Skagway shorter day hikes (Klondike Gold Rush NHP)", "https://home.nps.gov/klgo/planyourvisit/shorterdayhikes.htm",
    "government", "National Park Service", "Yakutania Point 1-2 mi, 100 ft; Gold Rush Cemetery and Lower Reid Falls 4 mi, 50 ft; Lower Dewey Lake 0.9 mi to the lake or 3.6 mi around, 500 ft. Distances round trip from the NPS visitor center.")
src("cruisehive_skagway", "Skagway Cruise Port: What You Need to Know", "https://www.cruisehive.com/skagway-cruise-port/125515",
    "secondary", "CruiseHive", "Broadway Dock vs Railroad/Ore docks at the south end; under a mile (about 18 min) to downtown; heliport 5-15 min from the ship; piers wheelchair accessible.")
src("cc_skagway_rental", "Cruise Critic: car rental in Skagway, can you drive to Carcross", "https://boards.cruisecritic.co.uk/topic/947414-car-rental-in-skagway-can-you-drive-to-carcross/",
    "secondary", "Cruise Critic forum (anecdotal)", "Posters say US citizens can take a US rental into Canada with passports; Avis cars barred from gravel (Dyea Rd); Sourdough allows it; counter lines on ship days. No renter policy found in writing.")
src("wiki_skagway_fraser", "Skagway-Fraser Border Crossing", "https://en.wikipedia.org/wiki/Skagway%E2%80%93Fraser_Border_Crossing",
    "reference", "Wikipedia", "US port at Mile 6.8 of the Klondike Highway; US inspection station about 7.9 mi south of the border. Hours not stated.")
src("princess_ktn_blog", "Ketchikan cruise port (Princess blog)", "https://www.princess.com/blog/ketchikan-cruise-port",
    "first-party", "Princess Cruises", "Four downtown berths numbered 1-4 south to north; fifth berth at Ward Cove with a shuttle; Saxman about 2 mi south; Totem Bight a few miles north.")
src("acs_ktn_walk", "Creek Street and Beyond: a self-guided walking tour of Ketchikan", "https://alaskacruiseshirts.com/blogs/alaska-cruise-guide/ketchikan-walking-tour-creek-street-guide",
    "secondary", "Alaska Cruise Shirts", "Creek Street 1-2 h with flat but slippery boardwalk; Totem Heritage Center about a 15-minute walk from downtown; some downtown hills and stairs.")
src("pr_ktn_walk", "Historical Ketchikan and Creek Street Walking Tour (Princess)", "https://princess.com/ports-excursions/ketchikan-alaska-excursions/historical-ketchikan-and-creek-street-walking-tour",
    "first-party", "Princess Cruises", "About 9 blocks, 1.5 h, Easy, wheelchair accessible (manual chairs need a companion); no price shown on the page.")
src("flashpack_ktn_bus", "Ketchikan bus to Totem Bight State Historical Park", "https://www.flashpackingamerica.com/alaska-travel/ketchikan-bus-to-totem-bight-state-historical-park/",
    "secondary", "Flashpacking America (May 2023 schedule)", "$2 cash per ride, about hourly, about 25 min from the port, bus enters the park; $5 park entry by card; Ward Cove stop about 5 min and 3 mi from Totem Bight.")
src("alaskaorg_ktn_bus", "Ketchikan bus services (alaska.org)", "https://www.alaska.org/detail/ketchikan-bus-services",
    "secondary", "Alaska.org", "Whole bus fleet wheelchair accessible; routes reach Ward Cove, Totem Bight, Saxman; lists a $1 fare (conflicts with the $2 on newer blog); two free summer dock shuttles.")
src("cc_ktn_rental", "Cruise Critic: Ketchikan by rental car (Settlers Cove, Totem Bight, Ward Lake)", "https://boards.cruisecritic.com.au/topic/2164724-ketchikan-by-rental-car-review-settlers-cove-totem-bight-and-ward-lake/",
    "secondary", "Cruise Critic forum (anecdotal)", "Alaska Car Rental picked up and returned at the dock; Settlers Cove about 20 min drive; Totem Bight about 10 min beyond; Ward Lake loop 1.3 mi, flat.")
src("alaskaorg_deer", "Deer Mountain Trail (alaska.org)", "https://alaska.org/detail/deer-mountain-trail",
    "secondary", "Alaska.org", "5 mi, about 2,600 ft gain, difficult.")

# ---------------------------------------------------------------- price rows
def row(for_id, amount, status, basis, source, url, note, item="price"):
    rid = f"{for_id}" if item == "price" else f"{for_id}:{item}"
    upsert(R, {"id": rid, "for": for_id, "item": item, "amount": amount, "currency": "USD",
               "usd": amount, "fx": None, "basis": basis, "status": status, "source": source, "url": url,
               "checked": CHECKED, "note": note})
    return rid


def offer(oid, kind, provider, title, hours, level, wheelchair, cancel, note, source, url, price):
    """price = (amount|None, status, basis)."""
    amount, status, basis = price
    pid = f"offer:{oid}"
    row(pid, amount, status, basis, source if status != "unavailable" else None, url if status != "unavailable" else None,
        note if status != "unavailable" else note)
    return {"kind": kind, "provider": provider, "line": None, "title": title, "hours": hours, "level": level,
            "wheelchair": wheelchair, "cancel": cancel, "note": note, "source": source, "url": url,
            "checked": CHECKED, "id": oid, "priceRow": pid}


UNAV = (None, "unavailable", "No published rate captured")

# ---------------------------------------------------------------- walking data for existing experiences
# id: (walkMiles, confidence, basis, stairsHills)
WALK = {
    # Juneau
    "jnu_whale": (0.3, "estimate", "Cruise version includes a coach to Auke Bay, so on foot only dock to coach and boat boarding. Operator does not publish walking distance.", "A few boarding steps to the boat; no hills."),
    "jnu_mdh_whale": (1.0, "estimate", "Coach included. Visitor center paths: 1/3 mi paved round trip (Forest Service map) plus boat boarding. Nugget Falls adds about 2 mi round trip if you choose it.", "Visitor center from the lot by stairs, elevator or easy ramp (Forest Service); Photo Point path paved with an incline."),
    "jnu_mdh_bus": (0.7, "estimate", "Coach to the visitor center; 1/3 mi paved round trip on the Forest Service map plus parking-lot and building walks. Nugget Falls would add about 2 mi round trip.", "Stairs, elevators and an easy ramp from the lots; Nugget Falls gravel, gentle slope."),
    "jnu_tram": (0.3, "estimate", "Base station is on the cruise docks. Summit trail loops were not measured. Tram closed in 2026: planning figure only.", "None to reach the base; summit path details not captured."),
    "jnu_city": (1.1, "documented", "GPSmyCity self-guided downtown loop is about 1.1 mi starting at the cruise port. Coach tours (Glacier Gardens, hatchery) walk much less.", "Narrow streets and wooden boardwalks; downtown is mostly flat but the museum warns of inclines and stairs on its tours."),
    "jnu_heli": (0.4, "estimate", "Van transfer to the heliport; short walk on uneven ice with provided boots. Distances not published.", "Helicopter step-up and uneven ice; no hills on the approach."),
    "jnu_fjord": (0.3, "estimate", "Boarding and deck walking on a high-speed vessel; 8.5 h mostly seated or on deck.", "Boarding steps; moving deck."),
    "jnu_brews": (0.3, "estimate", "Vehicle-based with short stops; listings give no walking distance.", "Not specified; short stops only."),
    "jnu_active": (5.0, "estimate", "Hiking, paddling and zipline tours; higher end taken. Distances vary by tour and were not published.", "Trail hiking and uneven ground; strenuous for the parents."),
    "jnu_salmon": (0.3, "estimate", "Coach to a sit-down salmon bake; ground surfaces not described on the listing.", "Not described."),
    # Skagway
    "skg_wpyr": (0.3, "estimate", "Train boards at or beside the cruise dock (CruiseHive says the train can pick up at the terminal). Seated in the car.", "Boarding steps; a lift car is on every train (NCL listing). No hills on foot."),
    "skg_wpyr_long": (0.4, "estimate", "Same dock-side boarding; long seated days with short stops, plus a coach leg on Bennett.", "Boarding steps; lift car on the train; restroom stops limited on the long days."),
    "skg_bus": (0.3, "estimate", "Coach from the dock with short photo stops.", "Coach steps; Frontier's vehicles are not wheelchair accessible."),
    "skg_town": (2.3, "derived", "Dock to Broadway is under a mile each way (CruiseHive, about 18 min) = about 1.8 mi round trip, plus about 0.5 mi along Broadway and the NPS visitor center. The SMART bus ($3 each way) cuts this to about 0.8 mi.", "Flat, compact historic district; no hills."),
    "skg_adventure": (1.5, "estimate", "Zipline course and platforms; distances not published.", "Stairs and platforms; strenuous per Princess."),
    "skg_bike": (2.0, "estimate", "Walking portions of e-bike, hike and float tours; distances vary by tour.", "Trail walking and river boarding; moderate effort."),
    "skg_mushers": (0.3, "estimate", "Coach to the camp; short ground walks.", "Ground surface not described."),
    "skg_heli": (1.0, "estimate", "CruiseHive puts the waterfront heliport 5 to 15 minutes' walk from the ship depending on the pier, which is up to about 1.4 mi round trip if you walk; many sellers transfer you.", "Helicopter boarding; flat waterfront."),
    # Ketchikan
    "ktn_lumber": (0.8, "estimate", "Distance from the berths was not captured; planner assumes about a 10-minute walk each way if not transported. Verify.", "Covered grandstand seating with steps; no hills documented."),
    "ktn_city": (1.5, "derived", "Princess's walking tour covers about 9 blocks; a self-guided loop with the Totem Heritage Center (about a 15-minute walk each way) plus Creek Street is about 1.5 mi. Trolley and duck options cut it.", "Creek Street boardwalk is flat but slippery when wet; some downtown hills and stairs (secondary source)."),
    "ktn_totems": (0.8, "estimate", "Coach to Saxman (about 2 mi south) or Totem Bight (a few miles north) with short walks in the parks.", "Princess lists the Saxman tour Easy and wheelchair accessible; NCL's Totem Bight tour is Level 2 Moderate."),
    "ktn_misty_boat": (0.4, "estimate", "Boarding and moving about a covered vessel for 5.25 h.", "Boarding steps; mostly seated."),
    "ktn_misty_air": (0.3, "estimate", "Dock walk to a floatplane.", "Floatplane step-in from a dock and a small cabin."),
    "ktn_rain": (1.0, "estimate", "Carnival says walking medium distances on uneven ground; distance not stated.", "Uneven ground with stairs (Carnival)."),
    "ktn_crab": (0.2, "estimate", "Seated meal after a coach or boat transfer.", "Not described."),
    "ktn_wildlife": (0.3, "estimate", "Boat boarding; mostly seated.", "Boarding steps."),
    "ktn_active": (3.0, "estimate", "Zipline, UTV, kayak and e-bike options; distances not published.", "Requires good mobility."),
    "ktn_wc_shuttle": (0.2, "estimate", "Shuttle from the Ward Cove dock to downtown; walking only at each end.", "Vehicle steps; no hills on foot."),
}
for x in X:
    if x["id"] in WALK:
        m, conf, basis, sh = WALK[x["id"]]
        x["walkMiles"], x["walkConfidence"], x["walkBasis"], x["stairsHills"] = m, conf, basis, sh

# tram note
for x in X:
    if x["id"] == "jnu_tram":
        x["risk"]["text"] = ("The tram was closed all of the 2026 cruise season after an April crash. Goldbelt says it is confident it will be ready for 2027 "
                             "but still needs a state certification evaluation and a replacement part (KTOO, Sep 24, 2026); the Juneau Independent (Jul 22, 2026) "
                             "reported no date. As of 2026-11-07 no 2027 opening date was found. Treat as unavailable until the operator confirms.")

# ---------------------------------------------------------------- new DIY experiences
def exp(**kw):
    base = {"ports": [kw["port"]], "weather": "medium", "risk": None, "poi": None, "diy": True}
    base.update(kw)
    return base


NEW = []

# ---- Juneau
NEW.append(exp(
    id="jnu_diy_walk", port="juneau", name="Self-guided downtown Juneau walk (+ free Capitol tour)", category="city",
    blurb="Walk the compact downtown from the dock: a 12-stop self-guided loop of about 1.1 miles along South Franklin Street's boardwalks, plus the state Capitol's free weekday tour. No booking, no transport, leave whenever you like.",
    exertion=1, exertionBasis="planner judgment from the documented loop length", label="ideal_parents", group="family",
    mobility="Franklin Dock and the cruise terminal are fully wheelchair accessible with paved paths and ramps (CruiseHive). Downtown streets are narrow with wooden boardwalks; the city museum warns its own tours may include inclines, stairs and uneven ground.",
    seating="mixed", photoPlace="juneau",
    caveat="Capitol tours run on weekdays only (1:30 and 3:00 pm in 2026; 2027 times not published) and can be cancelled. The AJ Dock berth is about a mile from town; a $5 shuttle runs (secondary source).",
    walkMiles=1.1, walkConfidence="documented",
    walkBasis="GPSmyCity's self-guided loop is about 1.1 mi starting at the cruise port; the Capitol tour is indoors.",
    stairsHills="Narrow streets and boardwalks; the museum notes possible inclines and stairs.",
    offers=[
        offer("jnu_diy_walk-1", "free", "State Capitol (listed by the city museum)", "Alaska State Capitol tour", 1, None, "not_stated", None,
              "Free, about 60 minutes, weekdays, no reservations (2026 schedule: 1:30 and 3:00 pm, last tour Sept 25). May be cancelled. 2027 schedule not published.",
              "juneau_museum_tours", "https://juneau.org/library/museum/walking-tours", (0, "published", "per adult, free")),
        offer("jnu_diy_walk-2", "independent", "Juneau-Douglas City Museum", "Historic Downtown walking tour (guided)", 1.5, None, "not_stated", None,
              "2026 schedule: Tuesday to Thursday, 1:45 pm, last tour June 30 2026; 2027 dates not published, so it may not run when your ship is in. Reserve by phone. Accessibility not listed.",
              "juneau_museum_tours", "https://juneau.org/library/museum/walking-tours", (31.5, "published", "per adult, 2026 price")),
    ]))

NEW.append(exp(
    id="jnu_diy_bus", port="juneau", name="City bus to Mendenhall Glacier (do it yourself)", category="glacier",
    blurb="Capital Transit routes 3, 4 and 8 reach Dredge Lake Road, the stop nearest the visitor center, for a $2 adult fare. From there it is a flat, paved bike-path walk of about 1.5 miles each way. The cheapest way to the glacier, but the transit agency puts door to door at up to 1.5 hours each way.",
    exertion=3, exertionBasis="3 miles of walking round trip before any visitor-center trails, plus long transit time", label="not_recommended", group="brothers",
    mobility="The walk from the stop is flat on a paved, wheelchair-accessible bike path (Capital Transit) but about 3 miles round trip, more than a 2-mile daily budget before reaching any trail.",
    seating="mixed", photoPlace="juneau", poi="mendenhall_vc",
    caveat="Frequency is not stated on the transit page. Add the Forest Service visitor-center day fee ($5 now; see 'Mendenhall Glacier by bus'). Cash only, no change.",
    walkMiles=3.4, walkConfidence="derived",
    walkBasis="Dredge Lake Rd stop to the visitor center is about 1.5 mi each way (Capital Transit) = 3.0 mi, plus the 1/3 mi paved path (Forest Service map).",
    stairsHills="Flat paved path from the stop; the visitor center from the lots has stairs, elevators and an easy ramp.",
    offers=[
        offer("jnu_diy_bus-1", "diy", "Capital Transit (Juneau city bus)", "Adult fare, routes 3, 4 or 8 to Dredge Lake Road", 3, None, "not_stated", None,
              "$2 cash for adults 19 and over, drivers cannot make change. The page does not say whether the fare is per boarding or whether a day pass exists: plan on $2 each way. Up to about 1.5 h each way including the walk.",
              "jcat_glacier", "https://juneaucapitaltransit.org/glacier", (2, "published", "per adult, per boarding")),
    ]))

NEW.append(exp(
    id="jnu_diy_car", port="juneau", name="Rent a car: Mendenhall Glacier at your own pace", category="glacier",
    blurb="Drive to Mendenhall Glacier Visitor Center (about 12 miles from downtown) and walk only as far as you like: the short paved path is about a third of a mile round trip, the gravel Nugget Falls trail about 2 miles round trip. No tour clock, but ship-day rental logistics and return hours matter.",
    exertion=1, exertionBasis="driving plus about a third of a mile on the paved path", label="ideal_parents", group="family", parentsDrive=True,
    mobility="Visitor center: stairs, elevators and an easy ramp from the lots (Forest Service). A cruiser report says the Photo Point path is paved with an incline and the Nugget Falls trail is gravel and dirt and hard for wheelchairs.",
    seating="mixed", photoPlace="juneau", poi="mendenhall_vc",
    caveat="No rental rate captured: no June 2027 price is published, and Juneau Car Rental's site blocks automated readers. A cruiser report (not first-party) says the downtown office is about a 20-minute walk from some berths and may close around 2 pm on cruise days; confirm drop-off hours and the cancellation terms. No source documents ship-day sell-outs; book early.",
    walkMiles=1.0, walkConfidence="derived",
    walkBasis="Paved 1/3 mi round trip plus lot and building walks (Forest Service map). The Nugget Falls gravel trail (2 mi round trip on the map; 0.8 mi on the trail page, direction not stated) is optional and would break a 2-mile budget.",
    stairsHills="Stairs/elevators/ramp at the visitor center; Photo Point path inclined; Nugget Falls gravel, gentle slope.",
    offers=[
        offer("jnu_diy_car-1", "diy", "Rental cars near the Juneau docks (Juneau Car Rental, Avis; cruiser-reported)", "One-day rental car for Mendenhall", None, None, "not_stated", None,
              "No published June 2027 daily rate captured. Airport rentals are generally cheaper but need a cab or timed bus (forum). Add the $5 Forest Service day fee.",
              "cc_juneau_rental", "https://boards.cruisecritic.com/topic/2522669-car-rental-in-juneau-amp-ideas-for-visiting-with-older-parent/", UNAV),
    ]))

NEW.append(exp(
    id="jnu_diy_hike", port="juneau", name="Hike from downtown: Perseverance or Mount Roberts Trail", category="adventure",
    blurb="Free trails start at Basin Road, about a mile from the docks. Perseverance Trail is rated moderate at about 3 miles along a former rail line; the Mount Roberts Trail is rated difficult and steep. Rain gear and a firm return-to-ship time are essential.",
    exertion=4, exertionBasis="alaska.org difficulty ratings plus about 2 mi round trip to the trailhead", label="brothers", group="brothers",
    mobility="Steep, uneven mountain trails: not suitable for the parents.",
    seating="standing", photoPlace="juneau", weather="high",
    caveat="alaska.org does not say whether Perseverance's 3 miles is one way or round trip, and it gives no length or gain for Mount Roberts. Check the trail distances with the Forest Service before relying on the time.",
    walkMiles=5.0, walkConfidence="derived",
    walkBasis="About 1 mi each way to the Basin Road trailhead (alaska.org) plus Perseverance Trail at about 3 mi; 5 mi is the minimum, up to about 8 mi if the 3 mi is one way.",
    stairsHills="Steep climbing on Mount Roberts; Perseverance climbs gradually above Gold Creek.",
    offers=[
        offer("jnu_diy_hike-1", "free", "Public trails (Basin Road trailheads)", "Perseverance Trail or Mount Roberts Trail", None, None, "no", None,
              "No fee found on the alaska.org pages. Trail conditions and any bear or weather closures are not captured.",
              "alaskaorg_juneau_trails", "https://alaska.org/destination/juneau/trails", (0, "published", "per adult, free")),
    ]))

# ---- Skagway
NEW.append(exp(
    id="skg_diy_smart", port="skagway", name="SMART bus and shuttle (skip the dock-to-town walk)", category="transport",
    blurb="The SMART bus runs from the cruise dock to downtown from 7 am to 9 pm when ships are in: $3 each way or $5 all day. An on-demand shuttle also reaches the Skagway River Bridge ($5), the end of pavement on Dyea or Liarsville Road ($10) and Dyea ($15). It saves most of the roughly mile-long walk to Broadway.",
    exertion=1, exertionBasis="planner judgment: removes about 1.8 miles of walking for the parents", label="ideal_parents", group="parents",
    mobility="CruiseHive says every terminal and pier is wheelchair accessible and that shuttles help guests with mobility needs; the vehicles' own accessibility features were not found.",
    seating="seated", photoPlace="skagway", weather="low",
    caveat="The on-demand shuttle needs 24 hours' notice outside regular hours and its fares are per person. Check the bus runs when your ship is in; the page says 'when cruise ships are in port'.",
    walkMiles=0.8, walkConfidence="derived",
    walkBasis="With the bus, only the dock-side stop to your destination and about 0.5 mi along Broadway remain (versus about 2.3 mi walking from the dock).",
    stairsHills="Flat town; vehicle steps.",
    offers=[
        offer("skg_diy_smart-1", "diy", "SMART (Skagway Municipal and Regional Transit)", "SMART bus: all-day pass, dock to downtown", None, None, "not_stated", None,
              "Pay the driver; 7 am to 9 pm daily when cruise ships are in port.",
              "skagway_getting_around", "https://www.skagway.com/plan-your-trip/travel-transportation/getting-around/", (5, "published", "per person, all day")),
        offer("skg_diy_smart-2", "diy", "SMART (Skagway Municipal and Regional Transit)", "SMART bus: one way, dock to downtown", None, None, "not_stated", None,
              "Pay the driver. Cheaper than the day pass only for a single leg.",
              "skagway_getting_around", "https://www.skagway.com/plan-your-trip/travel-transportation/getting-around/", (3, "published", "per person, each way")),
        offer("skg_diy_smart-3", "diy", "SMART on-demand shuttle", "On-demand shuttle: dock to Dyea", None, None, "not_stated", None,
              "Per person. Book ahead, 24 hours' notice outside regular hours. Cheaper zone stops: River Bridge $5, end of pavement on Dyea or Liarsville Road $10. Dyea road is gravel past the end of pavement.",
              "skagway_getting_around", "https://www.skagway.com/plan-your-trip/travel-transportation/getting-around/", (15, "published", "per person, zone fare")),
    ]))

NEW.append(exp(
    id="skg_diy_yakutania", port="skagway", name="Yakutania Point walk (self-guided)", category="scenic",
    blurb="A short, easy NPS-listed walk from town: 1 to 2 miles round trip with about 100 feet of climb, a footbridge and rock steps. Free, and the nearest of Skagway's trails to the docks, but the dock walk adds to the total.",
    exertion=2, exertionBasis="NPS rates it easy; rock steps and outcrops plus the dock-to-town walk", label="precautions", group="family",
    mobility="NPS describes a trail through alders with a footbridge, rock steps and rock outcroppings; surface and wheelchair access are not stated. Plus the dock-to-town walk unless you take the SMART bus.",
    seating="standing", photoPlace="skagway", weather="medium",
    caveat="NPS gives distances from its visitor center (2nd Ave and Broadway), not from the docks.",
    walkMiles=3.8, walkConfidence="derived",
    walkBasis="Up to 2 mi round trip on the trail (NPS) plus about 1.8 mi round trip between the dock and the NPS visitor center (CruiseHive: under a mile each way). With the SMART bus: about 2.4 mi.",
    stairsHills="Rock steps and a footbridge; about 100 ft of gain.",
    offers=[
        offer("skg_diy_yakutania-1", "free", "National Park Service listing", "Yakutania Point trail", None, "Easy", "not_stated", None,
              "Free public trail; distances round trip from the NPS visitor center.",
              "nps_klgo_hikes", "https://home.nps.gov/klgo/planyourvisit/shorterdayhikes.htm", (0, "published", "per adult, free")),
    ]))

NEW.append(exp(
    id="skg_diy_cemetery", port="skagway", name="Gold Rush Cemetery and Lower Reid Falls (self-guided)", category="scenic",
    blurb="NPS lists it as easy: about 4 miles round trip with 50 feet of climb, on a gravel road and then a short forest trail, starting north of downtown behind the railroad yards. Free. With the dock walk it is a long outing for most travelers.",
    exertion=3, exertionBasis="NPS easy rating, but about 6 miles of walking in total with the dock walk", label="brothers", group="brothers",
    mobility="Gravel road then a short forest trail; wheelchair access not stated. Far beyond a 2-mile daily budget for the parents.",
    seating="standing", photoPlace="skagway", weather="medium",
    caveat="Directions in the NPS listing cross the highway and pass behind the railroad yards; confirm the route is open and safe on your day.",
    walkMiles=5.8, walkConfidence="derived",
    walkBasis="4 mi round trip from the NPS visitor center (NPS) plus about 1.8 mi round trip from the dock (CruiseHive: under a mile each way).",
    stairsHills="Flat-ish; about 50 ft of gain.",
    offers=[
        offer("skg_diy_cemetery-1", "free", "National Park Service listing", "Gold Rush Cemetery and Lower Reid Falls", None, "Easy", "not_stated", None,
              "Free public trail; distances round trip from the NPS visitor center.",
              "nps_klgo_hikes", "https://home.nps.gov/klgo/planyourvisit/shorterdayhikes.htm", (0, "published", "per adult, free")),
    ]))

NEW.append(exp(
    id="skg_diy_dewey", port="skagway", name="Lower Dewey Lake hike (self-guided)", category="adventure",
    blurb="The classic steep climb above town: 0.9 miles to the lake or 3.6 miles around it, about 500 feet of gain, with a wooden staircase and rocky sections. Free. For the brothers; allow a firm turn-around time.",
    exertion=4, exertionBasis="NPS moderate rating with 500 ft of climb and steep uphill sections", label="brothers", group="brothers",
    mobility="Wooden staircase, footbridge, steep uphill, earthen levee and rocky sections (NPS): not suitable for the parents.",
    seating="standing", photoPlace="skagway", weather="medium",
    caveat="Trailhead is east on 2nd Ave past the depot, then north along the tracks (NPS).",
    walkMiles=5.4, walkConfidence="derived",
    walkBasis="3.6 mi around the lake (NPS) plus about 1.8 mi round trip from the dock; the 0.9 mi out-and-back to the lake alone would total about 3.6 mi.",
    stairsHills="About 500 ft of climb on stairs and steep trail.",
    offers=[
        offer("skg_diy_dewey-1", "free", "National Park Service listing", "Lower Dewey Lake trail", None, "Moderate", "no", None,
              "Free public trail; distances from the NPS visitor center.",
              "nps_klgo_hikes", "https://home.nps.gov/klgo/planyourvisit/shorterdayhikes.htm", (0, "published", "per adult, free")),
    ]))

NEW.append(exp(
    id="skg_diy_car", port="skagway", name="Rent a car: Klondike Highway toward Carcross and Emerald Lake", category="scenic",
    blurb="A rental car lets you drive the scenic highway north from Skagway at your own pace. Passports are required if you cross into Canada. Rental desks are in town; whether each company allows the Canada drive was not found in writing, so ask before you book.",
    exertion=1, exertionBasis="driving with short roadside stops", label="ideal_parents", group="family", parentsDrive=True,
    mobility="Seated in the car; stops are roadside. No wheelchair statement applies; vehicle choice is yours.",
    seating="seated", photoPlace="skagway", poi="carcross",
    caveat="No renter's written Canada policy was found: Cruise Critic posters say US citizens can take a US rental into Canada with passports and that Avis cars are barred from gravel roads such as Dyea Road. Border hours and drive times were not captured; the US inspection station is on the highway (Mile 6.8). Counter lines were reported on ship days; no sell-out data. Confirm return hours against your all-aboard time.",
    walkMiles=0.3, walkConfidence="estimate",
    walkBasis="Car-based; short roadside stops and rental-desk walks. Affordable Car Rentals is at 648 Broadway, about the end of the compact downtown.",
    stairsHills="None on foot beyond stops.",
    offers=[
        offer("skg_diy_car-1", "diy", "Affordable Car Rentals; Drive About Car Rental (listed by Skagway visitor bureau)", "One-day rental car, Klondike Highway", None, None, "not_stated", None,
              "No published June 2027 daily rate captured; an aggregator's Turo-branded November price is not comparable. Sourdough and Avis are also mentioned by cruisers; Avis's Skagway page did not load.",
              "skagway_getting_around", "https://www.skagway.com/plan-your-trip/travel-transportation/getting-around/", UNAV),
    ]))

# ---- Ketchikan
NEW.append(exp(
    id="ktn_diy_walk", port="ketchikan", name="Self-guided: Creek Street, Totem Heritage Center and waterfront", category="city",
    blurb="Ketchikan's compact waterfront is walkable from the downtown berths: Creek Street's boardwalk (allow 1 to 2 hours with Dolly's House) and the Totem Heritage Center about a 15-minute walk from downtown. Princess also sells a gentle 9-block walking tour that is listed wheelchair accessible.",
    exertion=1, exertionBasis="flat boardwalks and short walks; some hills and stairs downtown", label="ideal_parents", group="family",
    mobility="Princess lists its walking tour Easy and wheelchair accessible (electric chairs and scooters accommodated; manual chairs need to complete the tour alone or with a companion). Creek Street's boardwalk is flat but slippery when wet.",
    seating="mixed", photoPlace="ketchikan", poi="creek_street",
    caveat="Applies to downtown berths only; Ward Cove calls need a shuttle first. Totem Heritage Center admission and hours were not captured. Distances are not measured on any page.",
    walkMiles=1.5, walkConfidence="derived",
    walkBasis="Princess walking tour is about 9 blocks; Totem Heritage Center is about a 15-minute walk from downtown (about 0.7 mi each way) = 1.5 mi round trip, plus Creek Street.",
    stairsHills="Some downtown hills and stairs (secondary source); Creek Street boardwalk flat.",
    offers=[
        offer("ktn_diy_walk-1", "free", "Self-guided", "Creek Street and downtown waterfront on foot", 1.5, None, "not_stated", None,
              "No admission found to walk Creek Street or the waterfront; not separately sourced.",
              None, None, (0, "estimate", "per adult, free")),
        offer("ktn_diy_walk-2", "cruise", "Princess Cruises shore excursion", "Historical Ketchikan and Creek Street Walking Tour", 1.5, "Easy", "accessible", None,
              "About 9 blocks. The page shows no price. Guests with disabilities must contact the onboard tour office at least 48 hours ahead.",
              "pr_ktn_walk", "https://princess.com/ports-excursions/ketchikan-alaska-excursions/historical-ketchikan-and-creek-street-walking-tour", UNAV),
        offer("ktn_diy_walk-3", "diy", "Totem Heritage Center", "Totem Heritage Center admission", None, None, "not_stated", None,
              "Admission and hours were not captured.", None, None, UNAV),
    ]))
# the walking offer carries a line for the Princess tour
for o in NEW[-1]["offers"]:
    if o["id"] == "ktn_diy_walk-2":
        o["line"] = "princess"

NEW.append(exp(
    id="ktn_diy_bus", port="ketchikan", name="City bus to Totem Bight State Park (do it yourself)", category="culture",
    blurb="The borough bus north from the docks enters Totem Bight State Historical Park in about 25 minutes. It runs roughly hourly, so the return needs planning. From Ward Cove the same bus is about 5 minutes and 3 miles away, which makes it a cheap alternative to the Ward Cove shuttle.",
    exertion=2, exertionBasis="short stop walks plus the park trail; hourly bus adds timing risk", label="precautions", group="family",
    mobility="The whole bus fleet is wheelchair accessible (alaska.org). At Totem Bight the bus stops inside the park, a short walk from the trail start and self-pay station; park surfaces were not captured.",
    seating="mixed", photoPlace="ketchikan", poi="totem_bight",
    caveat="Schedule and fare come from a May 2023 blog; alaska.org lists an older $1 fare; the borough's fares and schedule pages were not read. Confirm the summer 2027 timetable and last bus before relying on it. Park entry is paid by card at a self-pay station.",
    walkMiles=1.0, walkConfidence="estimate",
    walkBasis="Stop in front of a coffee shop near the port (5 to 10 minutes from the farthest berth) plus a short walk in the park; park trail length not captured.",
    stairsHills="Not captured; the bus entrance is inside the park.",
    offers=[
        offer("ktn_diy_bus-1", "diy", "Ketchikan Gateway Borough bus", "Bus to Totem Bight (cash fare per ride)", 0.5, None, "accessible", None,
              "$2 cash per ride per a May 2023 blog; about hourly (northbound near :25, return near :13 in that timetable); about 25 minutes from the port. alaska.org lists $1. Bring dollar bills, no change.",
              "flashpack_ktn_bus", "https://www.flashpackingamerica.com/alaska-travel/ketchikan-bus-to-totem-bight-state-historical-park/", (2, "published", "per adult, per ride (secondary source, 2023)")),
        offer("ktn_diy_bus-2", "diy", "Alaska State Parks", "Totem Bight State Historical Park entry", None, None, "not_stated", None,
              "$5 per a May 2023 blog, paid by card at a self-pay station. Not read on the state's own page.",
              "flashpack_ktn_bus", "https://www.flashpackingamerica.com/alaska-travel/ketchikan-bus-to-totem-bight-state-historical-park/", (5, "published", "per adult (secondary source, 2023)")),
    ]))

NEW.append(exp(
    id="ktn_diy_car", port="ketchikan", name="Rent a car: Totem Bight, Settlers Cove and the Ward Lake loop", category="scenic",
    blurb="Drive north to Totem Bight State Park, Settlers Cove and Ward Lake at your own pace. A cruiser reports Settlers Cove about a 20-minute drive from town, Totem Bight about 10 minutes beyond it, and the Ward Lake nature loop at 1.3 miles and flat. Easy on the legs, but rental logistics matter.",
    exertion=1, exertionBasis="driving plus a flat 1.3-mile loop (cruiser report)", label="ideal_parents", group="family", parentsDrive=True,
    mobility="Settlers Cove has gentle slopes and a few sets of stairs; Ward Lake's 1.3-mile loop is flat (cruiser report). No first-party accessibility information.",
    seating="mixed", photoPlace="ketchikan", poi="totem_bight",
    caveat="No rental rate captured; one cruiser's roughly $60 for the day is an anecdote and is not stored as a price. The same poster says Alaska Car Rental picked up and returned at the dock; confirm that and the return hours. No source documents ship-day sell-outs; book early.",
    walkMiles=1.5, walkConfidence="derived",
    walkBasis="Ward Lake loop 1.3 mi (cruiser report) plus parking-lot walks; skip the loop for a shorter day.",
    stairsHills="A few stair sets at Settlers Cove; Ward Lake loop flat.",
    offers=[
        offer("ktn_diy_car-1", "diy", "Alaska Car Rental (cruiser-reported dock pickup)", "One-day rental car", None, None, "not_stated", None,
              "No published June 2027 rate captured. A forum anecdote of about $60 for a day is not used as a price.",
              "cc_ktn_rental", "https://boards.cruisecritic.com.au/topic/2164724-ketchikan-by-rental-car-review-settlers-cove-totem-bight-and-ward-lake/", UNAV),
    ]))

NEW.append(exp(
    id="ktn_diy_deer", port="ketchikan", name="Deer Mountain Trail (self-guided hike)", category="adventure",
    blurb="Ketchikan's classic climb starts near downtown: 5 miles with about 2,600 feet of gain, rated difficult. Free, but it is a long, steep day for the brothers and needs a firm turn-around time in a wet climate.",
    exertion=5, exertionBasis="alaska.org: difficult, 5 miles, about 2,600 ft gain", label="brothers", group="brothers",
    mobility="Steep mountain trail: not suitable for the parents.",
    seating="standing", photoPlace="ketchikan", weather="high",
    caveat="alaska.org does not say whether 5 miles is one way or round trip; assume round trip unless the Forest Service says otherwise. The trailhead is a gravel lot just up Ketchikan Lakes Road, roughly half a mile from downtown by its directions.",
    walkMiles=7.0, walkConfidence="derived",
    walkBasis="5 mi trail (alaska.org) plus roughly 1 mi each way between the berths and the trailhead (planner estimate); higher if 5 mi is one way.",
    stairsHills="About 2,600 ft of steep climbing.",
    offers=[
        offer("ktn_diy_deer-1", "free", "Public trail", "Deer Mountain Trail", None, None, "no", None,
              "No fee found on the alaska.org page.",
              "alaskaorg_deer", "https://alaska.org/detail/deer-mountain-trail", (0, "published", "per adult, free")),
    ]))

for e in NEW:
    upsert(X, e)

# ---------------------------------------------------------------- place logistics
def log(place, text, source):
    L = PL[place].setdefault("logistics", [])
    for r in L:
        if r["text"] == text:
            return
    L.append({"text": text, "source": source})


log("juneau", "Franklin Dock and the cruise terminal are a few minutes' walk to downtown and fully wheelchair accessible; AJ Dock is about 1 mile south of the center with a $5 shuttle.", "cruisehive_juneau")
log("juneau", "Capital Transit routes 3, 4 and 8 stop at Dredge Lake Road, about 1.5 miles (30 minutes' flat paved walk) from the Mendenhall visitor center; $2 adult fare, up to about 1.5 hours each way.", "jcat_glacier")
log("juneau", "Mendenhall paths: 1/3 mile paved round trip; Nugget Falls gravel trail about 2 miles round trip on the Forest Service map.", "fs_mdh_trails_map")
log("juneau", "No 2027 reopening date for the Goldbelt tram as of 2026-11-07; it needs a state certification evaluation first.", "ktoo_tram")
log("skagway", "SMART bus runs dock to downtown 7 am to 9 pm on ship days ($3 each way, $5 all day); on-demand shuttle to the River Bridge ($5), Dyea Road pavement end ($10) and Dyea ($15).", "skagway_getting_around")
log("skagway", "Under a mile (about 18 minutes) from the ships to downtown; Broadway Dock at the edge of Broadway, Railroad and Ore docks at the south end of town; all piers wheelchair accessible.", "cruisehive_skagway")
log("skagway", "Rental companies listed by the visitor bureau: Affordable Car Rentals (648 Broadway) and Drive About (202 9th Ave). Canada-driving rules were not found in writing; cruisers say US citizens can cross with passports.", "skagway_getting_around")
log("ketchikan", "Four downtown berths (1 to 4, south to north) put the ship on Front Street; Saxman is about 2 miles south, Totem Bight a few miles north.", "princess_ktn_blog")
log("ketchikan", "Totem Heritage Center is about a 15-minute walk from downtown; Creek Street's boardwalk is flat but slippery when wet.", "acs_ktn_walk")
log("ketchikan", "Borough bus to Totem Bight takes about 25 minutes and runs roughly hourly (May 2023 timetable); $2 cash fare, whole fleet wheelchair accessible.", "flashpack_ktn_bus")
log("ketchikan_wc", "From the Ward Cove bus stop, Totem Bight is about 5 minutes and 3 miles by borough bus (May 2023 blog).", "flashpack_ktn_bus")

# ---------------------------------------------------------------- coverage + meta
cov = d["experiences"]["coverage"]
cov["phase3"] = {
    "checked": CHECKED,
    "summary": ("Juneau, Skagway and Ketchikan: walkMiles, walkConfidence, walkBasis and stairsHills on every existing experience; "
                "13 new DIY or budget experiences (rental car, public bus or shuttle, self-guided walks, free hikes). "
                "walkMiles is a conservative one-person planning figure (dock to start, on-tour walking, back to the dock; higher end of any range). "
                "walkConfidence: documented (a published length), derived (arithmetic from published lengths) or estimate (planner judgment; no operator figure)."),
    "notCaptured": [
        "First-party rental rates (none published for June 2027); ship-day rental sell-out data.",
        "Any rental company's written policy on driving the Klondike Highway into Canada; border hours.",
        "Dock-by-dock distances in Skagway and Ketchikan; Lumberjack Show and Totem Heritage Center distances and admission.",
        "Ketchikan borough bus fare and schedule pages (blog figures used); Juneau bus frequency.",
        "Goldbelt tram: no 2027 opening date exists yet.",
    ],
}
m = d["meta"]
for p in m["phases"]:
    if p["n"] == 3:
        p["status"] = "done"
note = ("walkMiles on experiences is one person's conservative planning figure (dock to start, on-tour walking, back to the dock; the higher end of any range). "
        "walkConfidence says whether it is documented, derived or an estimate; it is not a measured accessibility rating.")
if note not in m["assumptions"]:
    m["assumptions"].append(note)

for n in ("sources", "prices", "experiences", "meta"):
    pass
save("sources", d["sources"])
save("prices", d["prices"])
save("experiences", d["experiences"])
save("catalog", d["catalog"])
save("meta", d["meta"])
print("ok: experiences", len(X), "rows", len(R), "sources", len(S))
