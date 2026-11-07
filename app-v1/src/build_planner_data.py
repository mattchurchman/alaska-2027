#!/usr/bin/env python3
"""Phase 4: add planner data to data.json (run from the folder holding data.json).
Adds: map points of interest (pois[]) with coordinates, hotel coordinates, schematic route lines
for the map, scoring factors and default weights (subjective), planner timing assumptions,
starter-plan pick lists, 'Know before you go' notes with sources, and the 'user' price status.
No prices are added here."""
import json, math, heapq

CHECKED = "2026-11-06"
d = json.load(open("data.json"))
P = {p["id"]: p for p in d["places"]}

# ---------- sources ----------
W = "https://en.wikipedia.org/wiki/"
new_sources = [
 dict(id="wiki_coords", title="Wikipedia article coordinates (Totem Bight, Saxman, Butchart Gardens, White Pass, Mendenhall Glacier, Misty Fjords, Sitka NHP, Auke Bay)", url=W+"Totem_Bight_State_Historical_Park", kind="reference", publisher="Wikipedia", checked=CHECKED,
      note="Coordinates read from each article's infobox; used to place map pins. Other pins are approximate (marked on the map)."),
 dict(id="naturalearth", title="Natural Earth 1:10m land and boundary lines (public domain)", url="https://www.naturalearthdata.com/", kind="reference", publisher="Natural Earth", checked=CHECKED,
      note="Coastline drawn on the planner map. Generalized: small coves and piers are not shown."),
 dict(id="wx_spark", title="WeatherSpark: average weather at Juneau International Airport", url="https://weatherspark.com/y/145123/Average-Weather-at-Juneau-International-Airport-Alaska-United-States-Year-Round", kind="reference", publisher="WeatherSpark", checked=CHECKED,
      note="June averages: high 63°F, low 48°F, about 13 days with measurable precipitation, about 4.3 in of rain, mostly cloudy or overcast about 70% of the time."),
 dict(id="travel_juneau_wx", title="Travel Juneau: weather and packing tips", url="https://www.traveljuneau.com/discover-juneau/travel-tips-weather/", kind="first-party", publisher="Travel Juneau", checked=CHECKED,
      note="Summer highs generally low-to-mid 60s °F; layers, a waterproof outer layer and waterproof shoes recommended."),
 dict(id="daylight_jnu", title="Alaska.org: Juneau sunrise and sunset, June", url="https://www.alaska.org/weather/daylight-hours/juneau/june", kind="reference", publisher="ALASKA.ORG", checked=CHECKED,
      note="Jun 1: 3:58 am to 9:51 pm. Jun 21: 3:48 am to 10:09 pm. Jun 30: 3:54 am to 10:07 pm."),
 dict(id="rci_passport", title="Royal Caribbean: Do you need a passport for a cruise?", url="https://www.royalcaribbean.com/guides/do-you-need-a-passport-for-a-cruise", kind="first-party", publisher="Royal Caribbean", checked=CHECKED,
      note="Closed-loop cruises (same US port start and end, e.g. Seattle round trips via Victoria): passport recommended, not required; alternatives listed. A passport is needed to fly home from abroad if you miss the ship."),
]
have = {s["id"] for s in d["sources"]}
d["sources"] += [s for s in new_sources if s["id"] not in have]

# ---------- points of interest ----------
# basis: "wikipedia" = infobox coordinates; "approx" = placed by the planner from the street address
# or general location, good to about a kilometre.
POIS = [
 ("auke_bay","Auke Bay harbor (whale boats)","juneau",58.38333,-134.65972,"wikipedia","Most Juneau whale tours leave from here, about 12 mi from the cruise docks by coach."),
 ("mendenhall_vc","Mendenhall Glacier Visitor Center","juneau",58.4168,-134.5456,"approx","About 12-13 mi from the docks. The Wikipedia glacier coordinates (58.4958, -134.5322) are up-glacier; the pin is at the visitor center."),
 ("juneau_heli","Juneau helicopter bases (airport area)","juneau",58.3560,-134.5780,"approx","Glacier-landing helicopters fly from near Juneau airport; exact base depends on the operator."),
 ("goldbelt_tram","Goldbelt (Mount Roberts) Tram base","juneau",58.2985,-134.4047,"approx","On the cruise docks at 490 S. Franklin St. Closed in 2026; 2027 reopening unconfirmed."),
 ("white_pass","White Pass summit (train turnaround)","skagway",59.62472,-135.13806,"wikipedia","About 20 rail miles from Skagway; the summit train turns around here."),
 ("carcross","Carcross, Yukon (bus and rail tours)","skagway",60.1667,-134.7069,"approx","Longer Yukon tours reach Carcross; Canadian border crossing (bring passports)."),
 ("klgo_vc","Klondike Gold Rush NHP visitor center","skagway",59.4553,-135.3156,"approx","Broadway & 2nd Ave, a short walk from the cruise docks."),
 ("creek_street","Creek Street","ketchikan",55.3428,-131.6425,"approx","Historic boardwalk a short walk from the downtown docks."),
 ("totem_bight","Totem Bight State Historical Park","ketchikan",55.42000,-131.77250,"wikipedia","About 10 mi north of downtown; short gravel trail to the totems and clan house."),
 ("saxman","Saxman Totem Park","ketchikan",55.32056,-131.59833,"wikipedia","About 2.5 mi south of downtown."),
 ("misty_fjords","Misty Fjords National Monument","ketchikan",55.62167,-130.60722,"wikipedia","Reached by boat (about 5 h round trip) or floatplane."),
 ("rainforest_sanctuary","Alaska Rainforest Sanctuary (Herring Cove)","ketchikan",55.3220,-131.5280,"approx","About 8 road miles from town."),
 ("raptor_center","Alaska Raptor Center","sitka",57.0545,-135.3115,"approx","1000 Raptor Way, about 1 mi from downtown Sitka."),
 ("sitka_nhp","Sitka National Historical Park (totem trail)","sitka",57.04888,-135.31596,"wikipedia","Flat, mostly gravel trail; no entrance fee."),
 ("inner_harbour","Victoria Inner Harbour","victoria",48.4216,-123.3700,"approx","About 1.5 mi from the Ogden Point cruise terminal."),
 ("butchart","Butchart Gardens","victoria",48.56528,-123.46944,"wikipedia","About 13 mi from the cruise terminal; tours run on evening calls in summer."),
]
d["pois"] = [dict(id=i, name=n, place=pl, lat=la, lng=ln, basis=b, source=("wiki_coords" if b=="wikipedia" else None), note=no) for i,n,pl,la,ln,b,no in POIS]
POI_FOR = {"jnu_whale":"auke_bay","jnu_mdh_whale":"mendenhall_vc","jnu_mdh_bus":"mendenhall_vc","jnu_tram":"goldbelt_tram","jnu_heli":"juneau_heli",
           "jnu_fjord":"tracy_arm","skg_wpyr":"white_pass","skg_wpyr_long":"white_pass","skg_bus":"carcross","skg_town":"klgo_vc",
           "ktn_city":"creek_street","ktn_lumber":"creek_street","ktn_totems":"totem_bight","ktn_misty_boat":"misty_fjords","ktn_misty_air":"misty_fjords",
           "ktn_rain":"rainforest_sanctuary","sit_town":"sitka_nhp","vic_butchart":"butchart","vic_harbour":"inner_harbour"}
for e in d["excursions"]:
    e["poi"] = POI_FOR.get(e["id"], e["port"])

# ---------- hotel coordinates (approximate) ----------
HC = {"hyatt_regency":(47.6131,-122.3334),"mayflower_park":(47.6119,-122.3383),"exec_pacific":(47.6064,-122.3330),"moore":(47.6116,-122.3418),
      "hotel_max":(47.6138,-122.3383),"edgewater":(47.6127,-122.3520),"hampton_airport":(47.4343,-122.2967),"element_airport":(47.4400,-122.2965),
      "doubletree_airport":(47.4352,-122.2952)}
for h in d["hotels"]:
    la, ln = HC[h["id"]]
    h["lat"], h["lng"], h["coordBasis"] = la, ln, "approx"

# ---------- schematic routes ----------
N = {"sea_p66":(47.611,-122.348),"sea_p91":(47.6297,-122.3822),"elliott":(47.63,-122.43),"pugetN":(47.95,-122.45),"admiralty":(48.17,-122.75),"jdfE":(48.25,-123.2),
     "victoria":(48.405,-123.39),"jdfMid":(48.30,-123.9),"jdfW":(48.45,-124.75),"flattery":(48.35,-125.4),"vi1":(49.0,-126.6),"vi2":(49.9,-128.1),"capeScott":(50.9,-129.1),
     "qcs":(51.7,-130.0),"hecateS":(52.6,-130.6),"hecateN":(53.8,-130.95),"dixon":(54.55,-131.15),"revilla":(55.08,-131.3),"ketchikan":(55.338,-131.645),
     "ketchikan_wc":(55.405,-131.735),"tongassN":(55.47,-131.86),"clarence1":(55.75,-132.2),"clarence2":(56.05,-132.75),"sumner":(56.3,-133.2),"frederick":(56.95,-133.7),
     "stephensS":(57.35,-133.78),"holkham":(57.74,-133.62),"endicott_arm":(57.52,-132.9),"tracy_arm":(57.835,-133.35),"stephens_passage":(57.95,-134.05),
     "gastineau":(58.2,-134.25),"juneau":(58.295,-134.40),"douglasW":(58.24,-134.63),"lynnS":(58.5,-134.98),"lynnM":(58.95,-135.18),"lynnN":(59.25,-135.36),
     "skagway":(59.445,-135.325),"icyE":(58.27,-135.15),"icy_strait":(58.135,-135.45),"icyW":(58.28,-135.85),"gbEntr":(58.38,-136.1),"gbMid":(58.75,-136.35),
     "glacier_bay":(58.98,-137.0),"crossSound":(58.13,-136.6),"gulf1":(58.5,-137.6),"gulf2":(59.1,-138.7),"yakutat":(59.75,-139.75),"hubbard":(60.0,-139.5),
     "outerBaranof":(57.3,-136.3),"sitkaSound":(57.0,-135.55),"sitka":(57.05,-135.34),"offBaranofS":(56.3,-135.1),"offPOW":(55.3,-133.9),"chathamS":(56.4,-134.65),
     "chathamM":(57.2,-134.65),"frederickW":(57.05,-134.2)}
E = [("sea_p66","elliott"),("sea_p91","elliott"),("elliott","pugetN"),("pugetN","admiralty"),("admiralty","jdfE"),("jdfE","victoria"),("jdfE","jdfMid"),("victoria","jdfMid"),
     ("jdfMid","jdfW"),("jdfW","flattery"),("flattery","vi1"),("vi1","vi2"),("vi2","capeScott"),("capeScott","qcs"),("qcs","hecateS"),("hecateS","hecateN"),("hecateN","dixon"),
     ("dixon","revilla"),("revilla","ketchikan"),("ketchikan","ketchikan_wc"),("ketchikan_wc","tongassN"),("tongassN","clarence1"),("clarence1","clarence2"),("clarence2","sumner"),
     ("sumner","frederick"),("frederick","stephensS"),("stephensS","holkham"),("holkham","endicott_arm"),("holkham","tracy_arm"),("holkham","stephens_passage"),
     ("stephens_passage","gastineau"),("gastineau","juneau"),("stephens_passage","douglasW"),("douglasW","lynnS"),("lynnS","lynnM"),("lynnM","lynnN"),("lynnN","skagway"),
     ("lynnS","icyE"),("icyE","icy_strait"),("icyE","icyW"),("icy_strait","icyW"),("icyW","gbEntr"),("gbEntr","gbMid"),("gbMid","glacier_bay"),("icyW","crossSound"),
     ("crossSound","gulf1"),("gulf1","gulf2"),("gulf2","yakutat"),("yakutat","hubbard"),("crossSound","outerBaranof"),("outerBaranof","sitkaSound"),("sitkaSound","sitka"),
     ("sitkaSound","offBaranofS"),("offBaranofS","offPOW"),("offPOW","dixon"),("offBaranofS","chathamS"),("chathamS","chathamM"),("chathamM","icyE"),("chathamM","frederickW"),
     ("frederickW","stephensS"),("frederickW","frederick"),("hecateN","offPOW")]
adj = {}
def dist(a, b):
    (la1, lo1), (la2, lo2) = N[a], N[b]
    return math.hypot((la1-la2), (lo1-lo2)*math.cos(math.radians((la1+la2)/2)))
for a, b in E:
    adj.setdefault(a, []).append(b); adj.setdefault(b, []).append(a)
def path(a, b):
    q = [(0, a, [a])]; seen = set()
    while q:
        c, n, p = heapq.heappop(q)
        if n == b: return p
        if n in seen: continue
        seen.add(n)
        for m in adj.get(n, []):
            if m not in seen: heapq.heappush(q, (c+dist(n, m), m, p+[m]))
    raise ValueError((a, b))
for it in d["itineraries"]:
    stops = []
    if it.get("days"):
        for day in it["days"]:
            for e in day:
                if e.get("place"): stops.append(e["place"])
    elif it.get("ports"):
        ln = next(l for l in d["lines"] if l["id"] == it["line"])
        stops = [ln["terminal"]] + it["ports"] + [ln["terminal"]]
    pts = []
    for a, b in zip(stops, stops[1:]):
        seg = path(a, b)
        for n in (seg if not pts else seg[1:]): pts.append([round(N[n][0], 3), round(N[n][1], 3)])
    it["mapLine"] = pts
    it["mapLineBasis"] = "schematic"

# ---------- planner settings ----------
m = d["meta"]
m["statusDefinitions"]["user"] = {"label": "Your estimate", "desc": "A number you typed into the planner (for example transfers or travel insurance). Not researched."}
m["planner"] = {
 "offShipH": 0.5, "backAboardH": 1.0, "transitionH": 0.25, "selfGuidedH": 1.5,
 "disembarkH": 2.0, "airportBeforeH": 2.0, "airportTransferMin": {"sea_p91": 45, "sea_p66": 40},
 "bagFeeEachWayDefault": True,
 "notes": [
  "Usable shore time = scheduled port hours minus 30 min to get off and 1 h to be back aboard before departure.",
  "Activities for the same people are laid end to end with 15 min between them. Self-guided options without a stated duration are planned at 1.5 h.",
  "Return-flight timing assumes leaving the ship starts about 2 h after the scheduled arrival, 45 min (Pier 91) or 40 min (Pier 66) to SEA, and 2 h at the airport before departure. Transfer times are planning estimates.",
  "Cruise-line tours wait for late-running tours or get you to the next port; independent tours do not. The planner flags independent tours that end less than an hour before all-aboard."]}
m["scoring"] = {
 "note": "Scores are the planner's judgment, built from the sourced facts with the rules below. Change the weights to match what the family cares about.",
 "factors": [
  {"id":"scenic","label":"Glaciers and scenery","weight":25,"rule":"Glacier Bay 10, Hubbard Glacier 9, Endicott Arm & Dawes Glacier 8, Tracy Arm 7 (large ships often cannot reach the glacier face), no glacier day 3; +0.5 for a second scenic passage."},
  {"id":"mobility","label":"Easy for the parents","weight":25,"rule":"Start at 10. -1.5 for each Ward Cove call (7 mi shuttle to Ketchikan), -1 for each Sitka call (shuttle or tender), -0.5 for each Alaska port with under 4 usable hours, +0.5 per full sea day (max +1). Port times not captured: -2."},
  {"id":"value","label":"Value","weight":20,"rule":"Two cabins + gratuities. Lowest in the window scores 10, highest scores 0, straight line between. No score when a cabin price is missing."},
  {"id":"excursions","label":"Excursion choice","weight":15,"rule":"2 points per distinct Alaska port (Juneau, Skagway, Ketchikan, Sitka, Icy Strait Point), max 10."},
  {"id":"portTime","label":"Time ashore","weight":10,"rule":"Usable hours in Alaska ports. Fewest in the window scores 0, most scores 10."},
  {"id":"comfort","label":"Ship comfort","weight":5,"rule":"Ship built 2017 or later 10, 2008-2016 7, older 4. A rough stand-in; not a review score."}],
 "glacier": {"Glacier Bay":10,"Hubbard Glacier":9,"Endicott Arm & Dawes Glacier":8,"Tracy Arm Fjord":7,"none":3}}
m["presets"] = {
 "note": "Starter plans fill each port with the first experience on these lists that fits the usable time. Edit freely; nothing here is a recommendation backed by reviews.",
 "budget": {"label":"Budget Alaska","sailing":"cheapest June two-cabin total","cabins":{"brothers":"interior","parents":"balcony"},"fare":"saver","hotel":"cheapest hotel rated 4.0+",
            "family":{"juneau":["jnu_mdh_bus","jnu_city"],"skagway":["skg_town"],"ketchikan":["ktn_city"],"ketchikan_wc":["ktn_city"],"sitka":["sit_town"],"icy_strait":[],"victoria":["vic_harbour"]},
            "brothers":{}, "offer":"cheapest"},
 "balanced": {"label":"Balanced Family Experience","sailing":"highest overall score in June (default weights)","cabins":{"brothers":"interior","parents":"balcony"},"fare":"saver","hotel":"best-rated hotel with 'Accessible' listed",
            "family":{"juneau":["jnu_whale","jnu_mdh_bus"],"skagway":["skg_wpyr","skg_town"],"ketchikan":["ktn_totems","ktn_lumber","ktn_city"],"ketchikan_wc":["ktn_totems","ktn_lumber","ktn_city"],"sitka":["sit_town"],"icy_strait":["isp_culture"],"victoria":["vic_harbour"]},
            "brothers":{"skagway":["skg_bike","skg_adventure"],"ketchikan":["ktn_active"],"ketchikan_wc":["ktn_active"],"sitka":["sit_active"],"icy_strait":["isp_zip"],"juneau":["jnu_active"]}, "offer":"cheapest-priced"},
 "premium": {"label":"Premium Scenery & Wildlife","sailing":"June Glacier Bay sailing with the most Alaska port hours","cabins":{"brothers":"interior","parents":"miniSuite"},"fare":"main","hotel":"highest-rated hotel",
            "family":{"juneau":["jnu_mdh_whale","jnu_whale"],"skagway":["skg_wpyr"],"ketchikan":["ktn_misty_boat","ktn_totems"],"ketchikan_wc":["ktn_misty_boat","ktn_totems"],"sitka":["sit_wildlife","sit_town"],"icy_strait":["isp_wildlife","isp_culture"],"victoria":["vic_harbour"]},
            "brothers":{"juneau":["jnu_heli"],"skagway":["skg_heli","skg_adventure"],"ketchikan":["ktn_active"],"ketchikan_wc":["ktn_active"],"sitka":["sit_active"],"icy_strait":["isp_zip"]}, "offer":"cruise-first"}}
m["essentials"] = {
 "weather": {"title":"June weather","points":[
   "Juneau in June averages a high of about 63°F and a low of about 48°F, with measurable rain on roughly 13 days of the month and mostly cloudy skies about 70% of the time.",
   "Summer highs are generally in the low to mid 60s °F and can top 75°F. Expect rain at some point: pack layers, a waterproof outer layer and waterproof shoes.",
   "Glacier and fjord days on deck feel colder because of wind off the ice. Bring a warm hat and gloves for the parents on the balcony."],
  "sources":["wx_spark","travel_juneau_wx"], "caveat":"Typical conditions only; nobody can forecast June 2027."},
 "daylight": {"title":"Long days","points":["In Juneau the sun rises about 4 am and sets about 10 pm in June (Jun 21: 3:48 am to 10:09 pm), so evening port calls are still light.","Bring an eye mask if anyone sleeps badly in light; interior cabins are dark."],"sources":["daylight_jnu"]},
 "documents": {"title":"Documents","points":[
   "Seattle round trips stop in Victoria, Canada, which makes them closed-loop cruises. Passports are recommended but not required for US citizens on these sailings.",
   "Everyone in the family has a passport: take them. If someone misses the ship or needs to fly home from Victoria, a passport is required to fly.",
   "Check that names on cruise and flight bookings match the passports, and that passports are valid through the trip.",
   "Yukon tours from Skagway (Carcross, Fraser) cross into Canada: carry passports on those days."],
  "sources":["rci_passport"]},
 "congestion": {"title":"Busy ports","points":[
   "Juneau, Skagway and Ketchikan often host several ships on the same day in June. Book popular tours early and expect lines at the tram, the Mendenhall buses and the Skagway train.",
   "This planner does not have 2027 ship-by-ship port schedules, so it cannot say which days are busiest."],"sources":[]},
 "mobility": {"title":"For the parents","points":[
   "When booking the balcony, ask for a cabin mid-ship near an elevator bank, and away from the theatre, galley and nightclub decks.",
   "Lines offer accessible cabins and wheelchair or scooter rentals; book these early, they are limited.",
   "Tender ports (sometimes Sitka) need steps into a small boat. Ward Cove (Ketchikan on Norwegian) needs a shuttle into town.",
   "Mom's limit is under about 2 miles of walking a day. Seated boat tours, the White Pass train and coach tours fit that best; town walks are self-paced."],"sources":[]}}
for p in m["phases"]:
    if p["n"] == 4: p["status"] = "done"
    if p["n"] == 5: p["status"] = "next"
m["version"] = "0.4.0-phase4"; m["updated"] = CHECKED
a = "Map pins use Wikipedia coordinates where marked; others (and all hotels) are approximate. Cruise route lines are schematic, drawn along common channels, not actual ship tracks."
if a not in m["assumptions"]: m["assumptions"].append(a)
json.dump(d, open("data.json", "w"), ensure_ascii=False, indent=1)
print("pois", len(d["pois"]), "sources", len(d["sources"]), "routes", sum(1 for i in d["itineraries"] if i.get("mapLine")))
