#!/usr/bin/env python3
"""Phase 1 data builder: writes data.json (master dataset) from the phase-1 research capture.
Later phases should edit data.json directly (or extend this script) and then run build_app.py."""
import json, datetime, urllib.parse

CHECKED = "2026-11-06"
DATE_FMT = "%Y-%m-%d"

def d(s): return datetime.date.fromisoformat(s)

# ---------------- status vocabulary ----------------
STATUS = {
  "verified": {"label": "Verified quote", "desc": "Read on the cruise line's own booking site for this exact sailing date, 2 adults per cabin, taxes and port fees included, not logged in, no loyalty or membership discount applied."},
  "published": {"label": "Published, not date-verified", "desc": "A real published figure (aggregator listing, cruise-line policy summary or news report) that was not confirmed on the provider's own booking page for this date."},
  "estimate": {"label": "Planning estimate", "desc": "Calculated by this planner from other figures (for example, gratuities = daily rate x 4 guests x 7 nights). Not a quote."},
  "unavailable": {"label": "Not captured", "desc": "Could not be read for this date. No number is shown rather than guessing."},
}

# ---------------- photos (Wikimedia Commons) ----------------
raw = json.load(open("photos_raw.json"))
def photo(key):
    f, a, lic = raw[key]
    title = f.replace(" ", "_")
    return {
        "url": "https://commons.wikimedia.org/wiki/Special:FilePath/" + urllib.parse.quote(title) + "?width=1000",
        "page": "https://commons.wikimedia.org/wiki/File:" + urllib.parse.quote(title),
        "credit": f"{a} / Wikimedia Commons / {lic}",
        "license": lic,
    }

# ---------------- sources ----------------
sources = {}
def src(id, title, url, kind, publisher, note=""):
    sources[id] = {"id": id, "title": title, "url": url, "kind": kind, "publisher": publisher, "checked": CHECKED, "note": note}
    return id

src("cabinsaver_sea", "Seattle Cruises in 2027: Seven Cruise Lines Compared", "https://cabinsaver.com/articles/trends/seattle-cruises/", "aggregator", "CabinSaver", "Discovery: which lines/ships sail from Seattle in 2027, glacier counts.")
src("cabinsaver_ncl", "2027 Norwegian Cruise Line Alaska Cruises", "https://cabinsaver.com/articles/trends/ncl-alaska-cruises/", "aggregator", "CabinSaver", "Discovery: NCL ship days of week and June dates.")
src("hal_news_2027", "Holland America Line Unveils 2027 Alaska Season", "https://www.hollandamerica.com/en/us/news/2025/August/news-08072025-Alaska-2027", "first-party", "Holland America Line", "Eurodam and Noordam Seattle round trips; Noordam 28-day Solstice voyage departs Jun 6, 2027.")
src("carnival_news_2027", "Carnival Cruise Line Announces 2027 Alaska", "https://www.carnival-news.com/2025/07/24/carnival-cruise-line-announces-2027-alaska-adventures-and-remarkable-carnival-journeys-cruises", "first-party", "Carnival Cruise Line", "Legend and Spirit homeport in Seattle.")
src("cruisemapper_sea_jun", "Seattle cruise port schedule, June 2027", "https://www.cruisemapper.com/ports/seattle-port-6?month=2027-06", "aggregator", "CruiseMapper", "Ship arrival/departure times at Seattle and terminal-by-line note.")
src("cruisemapper_noordam", "ms Noordam itineraries", "https://www.cruisemapper.com/ships/ms-Noordam-613", "aggregator", "CruiseMapper", "Noordam 2027: May 30 and Jul 4 Alaska Explorer; Jun 6 is a 28-day voyage.")
src("ctt_msc_jun", "MSC Poesia cruises, June 2027", "https://www.cruisetimetables.com/cruisesonmscpoesia-jun2027.html", "aggregator", "CruiseTimetables", "MSC Poesia June port times.")
src("ctt_riviera", "Oceania Riviera departing 1 July 2027", "https://www.cruisetimetables.com/cruisesonoceaniariviera-01jul2027.html", "aggregator", "CruiseTimetables", "Riviera 7-night Visions of Alaska itinerary, times and sampled prices.")
src("gangwaze_riviera", "Riviera June 24, 2027 – 7 Night Visions of Alaska", "https://gangwaze.com/cruise-lines/oceania-cruises/riviera/2027-06-24/7-nights", "aggregator", "Gangwaze", "Riviera Seattle round trips start Jun 24, 2027.")
src("terminals", "Seattle cruise terminals by line (Pier 66 / Pier 91)", "https://www.cruisemapper.com/ports/seattle-port-6?month=2027-06", "aggregator", "CruiseMapper", "Pier 91 serves Carnival Corp. lines, Royal Caribbean Group, MSC, Virgin; Pier 66 serves NCL and Oceania. Confirm on your cruise documents.")
src("princess_policy", "Princess standard cancellation, refund & final payment policy", "https://www.princess.com/en-us/plan/standard-cancellation-refund-policy", "first-party", "Princess Cruises", "Final payment 120 days before departure for new bookings sailing 2027+.")
src("princess_policy_news", "Princess Cruises updates booking policies", "https://www.cruisecritic.com/news/princess-cruises-updates-booking-policies", "news", "Cruise Critic", "120-day final payment for bookings made on/after Sep 2, 2026 for 2027+ sailings.")
src("ncl_policy", "NCL cancellation policy summary", "https://pabau.com/templates/ncl-cruises-cancellation-policy/", "secondary", "Pabau (summary of NCL terms)", "Final payment 120 days; $250 pp deposit for 7+ day sailings. Verify in NCL Guest Ticket Contract.")
src("rcl_policy", "Royal Caribbean cancellation policy guide", "https://www.royalcaribbeanblog.com/2024/06/06/royal-caribbean-cancellation-policy", "secondary", "Royal Caribbean Blog", "Final payment 90 days for 5-14 night cruises; refundable vs non-refundable deposit fares.")
src("celebrity_faq", "Celebrity Cruises payments FAQ", "https://www.celebritycruises.com/gb/faqs/manage-plan", "first-party", "Celebrity Cruises (UK site)", "Final payment 90 days; cancellation scale 89-75 days 25%. UK market page; confirm US terms.")
src("grat_points", "How much to tip on a cruise (Oct 2026)", "https://thepointsparty.com/articles/how-much-to-tip-on-a-cruise-gratuities-by-line", "secondary", "The Points Party", "Carnival $17, Royal Caribbean $18.50, Norwegian $20, Princess $18 per guest per day (standard rooms).")
src("grat_hal", "Holland America raises daily gratuity (Jun 1, 2026)", "https://cruise.blog/2026/04/another-carnival-cruise-line-raises-the-daily-gratuity-charges", "news", "Cruise.Blog", "HAL standard cabins $18.00 pp/day from Jun 1, 2026.")
src("grat_moneywise", "Cruise automatic gratuities 2026", "https://moneywise.com/life/travel/cruise-automatic-gratuities-tipping-daily-fees", "news", "Moneywise", "MSC $17-23; Celebrity $19.50-24.50 pp/day after 2026 increases.")
src("grat_cruzely", "Cruise ship gratuities for 2026", "https://www.cruzely.com/full-guide-to-cruise-ship-gratuities-for-2019-amounts-etiquette-and-more/", "secondary", "Cruzely", "Virgin Voyages: gratuities included in fare.")

# ---------------- places (genuine coordinates; logistics are planning notes) ----------------
places = [
 {"id":"sea_p91","name":"Smith Cove Cruise Terminal (Pier 91)","short":"Seattle · Pier 91","kind":"terminal","country":"US","tz":"America/Los_Angeles","lat":47.6297,"lng":-122.3822,
  "photo":photo("pier91"),"notes":"Interbay/Magnolia, about 3 mi north of downtown. Used by Princess, Holland America, Royal Caribbean, Celebrity, Carnival, MSC and Virgin (typical assignment; confirm on cruise documents). Taxi/rideshare or cruise-line transfer to SEA airport, roughly 30-45 min."},
 {"id":"sea_p66","name":"Bell Street Cruise Terminal (Pier 66)","short":"Seattle · Pier 66","kind":"terminal","country":"US","tz":"America/Los_Angeles","lat":47.6114,"lng":-122.3479,
  "photo":photo("pier66"),"notes":"Downtown waterfront in Belltown, near Pike Place Market. Used by Norwegian and Oceania (typical assignment; confirm). Downtown hotels are a short ride away."},
 {"id":"sea_airport","name":"Seattle–Tacoma International Airport (SEA)","short":"SEA airport","kind":"airport","country":"US","tz":"America/Los_Angeles","lat":47.4502,"lng":-122.3088,"photo":None,"notes":"Arrival/departure airport for the ABQ flights (Phase 3)."},
 {"id":"juneau","name":"Juneau, Alaska","short":"Juneau","kind":"port","country":"US","tz":"America/Juneau","lat":58.2989,"lng":-134.4081,"photo":photo("juneau"),"photo2":photo("juneau_aerial"),
  "notes":"Ships normally berth at the downtown docks; the Mount Roberts Tramway base is on the waterfront. Mendenhall Glacier is about 12 miles away (bus or tour needed). Busiest port in Southeast Alaska: several ships a day in June.","dock":"Dock (downtown)"},
 {"id":"skagway","name":"Skagway, Alaska","short":"Skagway","kind":"port","country":"US","tz":"America/Juneau","lat":59.4503,"lng":-135.3260,"photo":photo("skagway"),"photo2":photo("skagway_town"),
  "notes":"Docks are at the south end of town; Broadway's historic district starts within roughly half a mile. White Pass & Yukon Route trains board near the docks. Flat, compact town; Canada (Yukon) excursions need passports.","dock":"Dock"},
 {"id":"ketchikan","name":"Ketchikan, Alaska (downtown)","short":"Ketchikan","kind":"port","country":"US","tz":"America/Juneau","lat":55.3422,"lng":-131.6461,"photo":photo("ketchikan"),
  "notes":"Downtown berths put Creek Street and the waterfront a short, flat walk from the gangway. Often rainy: Ketchikan is one of the wettest towns in the US.","dock":"Dock (downtown)"},
 {"id":"ketchikan_wc","name":"Ketchikan – Ward Cove","short":"Ketchikan (Ward Cove)","kind":"port","country":"US","tz":"America/Juneau","lat":55.4110,"lng":-131.7270,"photo":photo("ketchikan_ward_cove"),
  "notes":"Norwegian's Ketchikan calls use the Ward Cove dock about 7 miles north of downtown; reaching Creek Street needs a shuttle or taxi (allow 20-30 min each way). Adds a transfer for the parents.","dock":"Dock (Ward Cove, shuttle to town)"},
 {"id":"sitka","name":"Sitka, Alaska","short":"Sitka","kind":"port","country":"US","tz":"America/Juneau","lat":57.0531,"lng":-135.3300,"photo":photo("sitka"),
  "notes":"Most large ships use the Sitka Sound Cruise Terminal several miles north of downtown with a shuttle into town; some calls tender to downtown instead. Dock vs tender is set per call, so confirm closer to sailing.","dock":"Dock north of town with shuttle, or tender"},
 {"id":"icy_strait","name":"Icy Strait Point (Hoonah), Alaska","short":"Icy Strait Point","kind":"port","country":"US","tz":"America/Juneau","lat":58.1290,"lng":-135.4475,"photo":photo("icy_strait_point"),
  "notes":"Tlingit-owned destination built around a restored 1912 cannery near the village of Hoonah. Ships dock at the cannery complex; whale watching departs nearby; gondolas and the ZipRider are on site.","dock":"Dock"},
 {"id":"victoria","name":"Victoria, British Columbia","short":"Victoria, BC","kind":"port","country":"CA","tz":"America/Vancouver","lat":48.4139,"lng":-123.3870,"photo":photo("victoria"),
  "notes":"Ships berth at Ogden Point, roughly 1.5-2 km from the Inner Harbour. Most Seattle round trips call in the evening for a few hours (required foreign-port stop). Canada: bring passports.","dock":"Dock (Ogden Point)"},
 {"id":"glacier_bay","name":"Glacier Bay National Park","short":"Glacier Bay","kind":"scenic","country":"US","tz":"America/Juneau","lat":58.9790,"lng":-137.0510,"photo":photo("glacier_bay"),"photo2":photo("glacier_bay_ship"),
  "notes":"National Park Service limits ship entries; park rangers board for commentary. Ship cruises up to tidewater glaciers such as Margerie and Johns Hopkins (ice permitting). No going ashore.","dock":"Scenic cruising (no landing)"},
 {"id":"tracy_arm","name":"Tracy Arm Fjord","short":"Tracy Arm","kind":"scenic","country":"US","tz":"America/Juneau","lat":57.8350,"lng":-133.3500,"photo":photo("tracy_arm"),
  "notes":"Narrow fjord south of Juneau ending at the Sawyer Glaciers. Large ships often cannot reach the glacier faces when ice is heavy; lines may substitute Endicott Arm.","dock":"Scenic cruising (no landing)"},
 {"id":"endicott_arm","name":"Endicott Arm & Dawes Glacier","short":"Dawes Glacier","kind":"scenic","country":"US","tz":"America/Juneau","lat":57.5200,"lng":-132.9000,"photo":photo("dawes_glacier"),"photo2":photo("endicott_arm"),
  "notes":"Fjord next to Tracy Arm, ending at Dawes Glacier. Usually a morning scenic cruise before an afternoon Juneau call.","dock":"Scenic cruising (no landing)"},
 {"id":"hubbard","name":"Hubbard Glacier","short":"Hubbard Glacier","kind":"scenic","country":"US","tz":"America/Yakutat","lat":60.0200,"lng":-139.4700,"photo":photo("hubbard_glacier"),
  "notes":"North America's largest tidewater glacier (about 6 miles wide at the face), in Disenchantment Bay near Yakutat. Rare on 7-night Seattle round trips.","dock":"Scenic cruising (no landing)"},
 {"id":"stephens_passage","name":"Stephens Passage","short":"Stephens Passage","kind":"scenic","country":"US","tz":"America/Juneau","lat":57.95,"lng":-134.05,"photo":None,
  "notes":"Channel south of Juneau, known for humpback whales. Holland America lists it as scenic cruising on the way in to Juneau.","dock":"Scenic cruising"},
]

# ---------------- cruise lines ----------------
lines = [
 {"id":"princess","name":"Princess Cruises","badge":"PR","color":"#1f4e8c","terminal":"sea_p91",
  "gratuity":{"pp_day":18.0,"status":"published","source":"grat_points","note":"$18 pp/day standard staterooms (since Mar 2026). Included in the optional Princess Plus fare."},
  "fareBasis":"Princess Standard fare (site default). 'Up to 50% Off' sale pricing shown publicly. Princess Plus (drinks, Wi-Fi, gratuities) costs more.",
  "includes":"Main dining, buffet, entertainment, pools. Drinks, Wi-Fi and gratuities extra on the Standard fare.",
  "payment":{"finalPaymentDays":120,"deposit":"Non-refundable deposit by default unless you pay to upgrade to a refundable deposit (per Princess policy page).","status":"verified","source":"princess_policy","note":"Applies to new bookings made after Sep 2, 2026 for 2027 sailings."},
  "accessibility":"Accessible staterooms bookable on the line's site (check 'Accessible stateroom')."},
 {"id":"hal","name":"Holland America Line","badge":"HA","color":"#16365c","terminal":"sea_p91",
  "gratuity":{"pp_day":18.0,"status":"published","source":"grat_hal","note":"$18 pp/day standard cabins from Jun 1, 2026."},
  "fareBasis":"Standard fare shown with 'All taxes and fees included'. 'Have It All' package is an optional add-on.",
  "includes":"Main dining, Lido buffet, live music venues, 24-hour room service. Drinks, Wi-Fi and gratuities extra on the base fare.",
  "payment":{"finalPaymentDays":None,"deposit":"Not captured.","status":"unavailable","source":None,"note":"Sources disagree (75 vs 90 days). Confirm at booking."},
  "accessibility":"Booking flow has a 'Wheelchair Accessible Room' checkbox."},
 {"id":"ncl","name":"Norwegian Cruise Line","badge":"NC","color":"#0a5f8f","terminal":"sea_p66",
  "gratuity":{"pp_day":20.0,"status":"published","source":"grat_points","note":"$20 pp/day (Club Balcony Suite and below)."},
  "fareBasis":"Base fare ('Free at Sea' / More at Sea extras optional). Joy sailings showed a 'Black Friday Latitudes Sale' price to logged-out visitors.",
  "includes":"Main dining rooms, buffet, Broadway-style shows. Freestyle dining (no fixed times). Drinks, Wi-Fi and service charge extra on the base fare.",
  "payment":{"finalPaymentDays":120,"deposit":"$250 per person for 7+ day sailings (secondary source).","status":"published","source":"ncl_policy","note":"Verify in NCL Guest Ticket Contract."},
  "accessibility":"'I need an accessible stateroom' option in booking; requires affirmation of need."},
 {"id":"rci","name":"Royal Caribbean","badge":"RC","color":"#1d3f8f","terminal":"sea_p91",
  "gratuity":{"pp_day":18.5,"status":"published","source":"grat_points","note":"$18.50 pp/day non-suite."},
  "fareBasis":"Price shown with 'all taxes & fees'. Page also tagged '10% Off Resident Rate' and 'Early Booking Bonus'; no residency discount was applied.",
  "includes":"Main dining, Windjammer buffet, shows, pools. Drinks, Wi-Fi and gratuities extra.",
  "payment":{"finalPaymentDays":90,"deposit":"Refundable and non-refundable deposit fares; non-refundable fares become a cruise credit minus $100 pp if cancelled before final payment.","status":"published","source":"rcl_policy","note":"5-14 night cruises."},
  "accessibility":"Accessible staterooms available by request in booking."},
 {"id":"celebrity","name":"Celebrity Cruises","badge":"CE","color":"#22313f","terminal":"sea_p91",
  "gratuity":{"pp_day":19.5,"status":"published","source":"grat_moneywise","note":"$19.50 pp/day standard staterooms after the 2026 increase (news report)."},
  "fareBasis":"Price shown with 'all taxes & fees' and the '75% Off 2nd Guest' promotion. Default fare type (cruise-only vs All Included) not confirmed.",
  "includes":"Main dining, buffet, shows. All Included upgrade adds drinks, Wi-Fi and tips.",
  "payment":{"finalPaymentDays":90,"deposit":"Not captured for US market.","status":"published","source":"celebrity_faq","note":"Taken from Celebrity's UK FAQ; confirm US terms."},
  "accessibility":"Inside staterooms listed as including accessible options."},
 {"id":"carnival","name":"Carnival Cruise Line","badge":"CA","color":"#1b4fa0","terminal":"sea_p91",
  "gratuity":{"pp_day":17.0,"status":"published","source":"grat_points","note":"$17 pp/day standard staterooms (since Apr 2026)."},
  "fareBasis":"Public fare for 2 adults, no military/senior/past-guest discounts, 'Taxes and fees are included'.",
  "includes":"Main dining, Lido buffet, comedy and shows. Drinks, Wi-Fi and gratuities extra.",
  "payment":{"finalPaymentDays":None,"deposit":"Not captured.","status":"unavailable","source":None,"note":"Confirm on booking confirmation."},
  "accessibility":"Accessible staterooms by request."},
 {"id":"msc","name":"MSC Cruises","badge":"MS","color":"#13284a","terminal":"sea_p91",
  "gratuity":{"pp_day":17.0,"status":"published","source":"grat_moneywise","note":"$17 pp/day standard after the May 2026 increase (news report)."},
  "fareBasis":"'Price includes all fees and taxes' for 2 guests. A '10% off with Voyagers Club' member discount was shown but not applied.",
  "includes":"Main dining, buffet, shows. Drinks and Wi-Fi extra unless a package is added.",
  "payment":{"finalPaymentDays":None,"deposit":"Not captured.","status":"unavailable","source":None,"note":""},
  "accessibility":"Not captured."},
 {"id":"virgin","name":"Virgin Voyages","badge":"VV","color":"#7a1131","terminal":"sea_p91",
  "gratuity":{"pp_day":0.0,"status":"published","source":"grat_cruzely","note":"Gratuities included in fare; Wi-Fi and basic drinks also included."},
  "fareBasis":"Adults-only (18+). 'Black Friday Preview: 80% off 2nd Sailor' pricing shown per sailor.",
  "includes":"All restaurants (no buffet), gratuities, basic drinks, Wi-Fi.",
  "payment":{"finalPaymentDays":None,"deposit":"Not captured.","status":"unavailable","source":None,"note":""},
  "accessibility":"Not captured."},
 {"id":"oceania","name":"Oceania Cruises","badge":"OC","color":"#22344a","terminal":"sea_p66",
  "gratuity":{"pp_day":None,"status":"unavailable","source":None,"note":"Not captured."},
  "fareBasis":"Premium line; adults-only since Jan 2026 per European agent listing. Prices here are aggregator samples only.",
  "includes":"Specialty dining included; small ship (about 1,250 guests).",
  "payment":{"finalPaymentDays":None,"deposit":"Not captured.","status":"unavailable","source":None,"note":""},
  "accessibility":"Not captured."},
]

ships = [
 {"id":"royal_princess","line":"princess","name":"Royal Princess","built":2013,"guests":3560,"guestsSource":"Princess itinerary page","photo":photo("royal_princess")},
 {"id":"star_princess","line":"princess","name":"Star Princess","built":2025,"guests":4300,"guestsSource":"CruiseTimetables listing","photo":photo("star_princess"),"note":"New Sphere-class ship (2025)."},
 {"id":"eurodam","line":"hal","name":"Eurodam","built":2008,"guests":None,"photo":photo("eurodam"),"note":"Mid-size ship; Holland America's quieter style suits the parents."},
 {"id":"norwegian_encore","line":"ncl","name":"Norwegian Encore","built":2019,"guests":3958,"guestsSource":"CruiseTimetables listing","photo":photo("norwegian_encore")},
 {"id":"norwegian_bliss","line":"ncl","name":"Norwegian Bliss","built":2018,"guests":4010,"guestsSource":"CruiseTimetables listing","photo":photo("norwegian_bliss"),"note":"Built with a large forward Observation Lounge for Alaska viewing."},
 {"id":"norwegian_joy","line":"ncl","name":"Norwegian Joy","built":2017,"guests":3776,"guestsSource":"CruiseTimetables listing","photo":photo("norwegian_joy")},
 {"id":"voyager_of_the_seas","line":"rci","name":"Voyager of the Seas","built":1999,"guests":None,"photo":photo("voyager_of_the_seas")},
 {"id":"quantum_of_the_seas","line":"rci","name":"Quantum of the Seas","built":2014,"guests":4180,"guestsSource":"CruiseTimetables listing","photo":photo("quantum_of_the_seas")},
 {"id":"celebrity_edge","line":"celebrity","name":"Celebrity Edge","built":2018,"guests":2908,"guestsSource":"CruiseTimetables listing","photo":photo("celebrity_edge")},
 {"id":"carnival_legend","line":"carnival","name":"Carnival Legend","built":2002,"guests":2134,"guestsSource":"CruiseTimetables listing","photo":photo("carnival_legend")},
 {"id":"carnival_spirit","line":"carnival","name":"Carnival Spirit","built":2001,"guests":2134,"guestsSource":"CruiseTimetables listing","photo":photo("carnival_spirit")},
 {"id":"msc_poesia","line":"msc","name":"MSC Poesia","built":2008,"guests":2446,"guestsSource":"CruiseTimetables listing","photo":photo("msc_poesia")},
 {"id":"brilliant_lady","line":"virgin","name":"Brilliant Lady","built":2025,"guests":None,"photo":photo("brilliant_lady"),"note":"Adults only (18+)."},
 {"id":"oceania_riviera","line":"oceania","name":"Oceania Riviera","built":2012,"guests":1250,"guestsSource":"Cruise Web listing","photo":photo("oceania_riviera")},
]

# ---------------- itineraries ----------------
# day: d (1-based), place, type (embark|sea|port|scenic|disembark), arr/dep "HH:MM" 24h ship-published local times
def E(place, dep): return {"type":"embark","place":place,"dep":dep}
SEA = {"type":"sea"}
def P(place, arr, dep): return {"type":"port","place":place,"arr":arr,"dep":dep}
def S(place, arr=None, dep=None): return {"type":"scenic","place":place,"arr":arr,"dep":dep}
def X(place, arr): return {"type":"disembark","place":place,"arr":arr}

itins = [
 {"id":"princess_royal_gb","line":"princess","ship":"royal_princess","name":"7-Day Inside Passage (with Glacier Bay National Park)","weekday":"Saturday","glacier":"Glacier Bay","glacierPlace":"glacier_bay","timesStatus":"verified","timesSource":"Princess itinerary pages, voyage codes 1717-1722",
  "days":[[E("sea_p91","15:00")],[SEA],[P("juneau","13:00","21:15")],[P("skagway","06:00","20:30")],[S("glacier_bay","06:00","14:30")],[P("ketchikan","07:00","13:15")],[P("victoria","21:00","23:59")],[X("sea_p91","07:00")]]},
 {"id":"princess_star_dawes","line":"princess","ship":"star_princess","name":"7-Day Inside Passage (Roundtrip Seattle)","weekday":"Sunday","glacier":"Endicott Arm & Dawes Glacier","glacierPlace":"endicott_arm","timesStatus":"verified","timesSource":"Princess itinerary pages, voyage codes 4722-4727",
  "days":[[E("sea_p91","15:00")],[SEA],[P("ketchikan","06:30","15:00")],[S("endicott_arm","05:00","09:00"),P("juneau","12:30","21:00")],[P("skagway","06:00","17:00")],[SEA],[P("victoria","19:00","23:59")],[X("sea_p91","07:00")]]},
 {"id":"hal_eurodam_explorer","line":"hal","ship":"eurodam","name":"7-Day Alaska Explorer","weekday":"Saturday","glacier":"Glacier Bay","glacierPlace":"glacier_bay","timesStatus":"verified","timesSource":"Holland America cruise pages d741-d747; Seattle return time from CruiseMapper",
  "days":[[E("sea_p91","15:00")],[SEA],[S("stephens_passage"),P("juneau","12:30","22:00")],[S("glacier_bay","06:00","15:00"),P("icy_strait","17:30","22:00")],[P("sitka","08:00","16:00")],[P("ketchikan","06:30","13:00")],[P("victoria","20:00","23:59")],[X("sea_p91","07:00")]]},
 {"id":"ncl_encore_gb","line":"ncl","ship":"norwegian_encore","name":"7-Day Alaska Round-Trip Seattle: Skagway, Juneau, Ketchikan & Victoria","weekday":"Sunday","glacier":"Glacier Bay","glacierPlace":"glacier_bay","timesStatus":"verified","timesSource":"NCL vacation builder (ENCORE7SEAJNUSGYKTNVICSEA); Glacier Bay times not published",
  "days":[[E("sea_p66","15:00")],[SEA],[P("juneau","13:00","22:00")],[P("skagway","06:30","20:00")],[S("glacier_bay")],[P("ketchikan_wc","07:00","13:15")],[P("victoria","20:00","23:59")],[X("sea_p66","06:00")]]},
 {"id":"ncl_bliss_dawes","line":"ncl","ship":"norwegian_bliss","name":"7-Day Alaska Round-Trip Seattle: Juneau, Sitka, Ketchikan & Victoria","weekday":"Saturday","glacier":"Endicott Arm & Dawes Glacier","glacierPlace":"endicott_arm","timesStatus":"verified","timesSource":"NCL vacation builder (BLISS7SEASITJNUICYKTNVICSEA); Seattle return from CruiseMapper",
  "days":[[E("sea_p66","15:00")],[SEA],[P("sitka","10:00","18:00")],[P("juneau","06:30","13:30"),S("endicott_arm")],[P("icy_strait","06:00","15:00")],[P("ketchikan_wc","06:00","13:15")],[P("victoria","20:00","23:59")],[X("sea_p66","06:00")]]},
 {"id":"ncl_joy_hubbard","line":"ncl","ship":"norwegian_joy","name":"7-Day Alaska Round-trip Seattle: Juneau, Ketchikan & Victoria (Hubbard Glacier)","weekday":"Friday","glacier":"Hubbard Glacier","glacierPlace":"hubbard","timesStatus":"verified","timesSource":"NCL vacation builder (JOY7SEAJNUICYKTNVICSEA)",
  "days":[[E("sea_p66","15:00")],[SEA],[P("juneau","13:00","22:00")],[S("hubbard")],[P("icy_strait","06:00","15:00")],[P("ketchikan_wc","06:00","13:15")],[P("victoria","20:00","23:59")],[X("sea_p66","06:00")]]},
 {"id":"ncl_joy_dawes","line":"ncl","ship":"norwegian_joy","name":"7-Day Alaska Round-trip Seattle: Icy Strait Point, Ketchikan & Victoria","weekday":"Friday","glacier":"Endicott Arm & Dawes Glacier","glacierPlace":"endicott_arm","timesStatus":"verified","timesSource":"NCL vacation builder (JOY7SEAICYSITKTNVICSEA); Seattle return time not captured",
  "days":[[E("sea_p66","15:00")],[SEA],[P("sitka","11:00","20:00")],[S("endicott_arm")],[P("icy_strait","06:00","15:00")],[P("ketchikan_wc","06:00","13:15")],[P("victoria","20:00","23:59")],[X("sea_p66","06:00")]]},
 {"id":"rci_voyager_dawes","line":"rci","ship":"voyager_of_the_seas","name":"7 Night Alaska Adventure Cruise","weekday":"Friday","glacier":"Endicott Arm & Dawes Glacier","glacierPlace":"endicott_arm","timesStatus":"verified","timesSource":"Royal Caribbean itinerary page (VY07A458, Jun 11 sailing)",
  "days":[[E("sea_p91","16:00")],[SEA],[P("juneau","13:00","22:00")],[P("skagway","08:00","20:00")],[S("endicott_arm","07:00","12:00")],[SEA],[P("victoria","08:00","18:00")],[X("sea_p91","06:00")]]},
 {"id":"rci_quantum_dawes","line":"rci","ship":"quantum_of_the_seas","name":"7 Night Alaska Adventure Cruise","weekday":"Monday","glacier":"Endicott Arm & Dawes Glacier","glacierPlace":"endicott_arm","timesStatus":"verified","timesSource":"Royal Caribbean itinerary page (QN07A455, Jun 14 sailing)",
  "days":[[E("sea_p91","16:00")],[SEA],[P("sitka","09:30","17:00")],[P("skagway","07:00","20:00")],[S("endicott_arm","05:00","09:30"),P("juneau","13:00","20:00")],[SEA],[P("victoria","17:00","22:00")],[X("sea_p91","06:00")]]},
 {"id":"celebrity_edge_dawes","line":"celebrity","ship":"celebrity_edge","name":"7 Night Alaska Dawes Glacier Cruise","weekday":"Friday","glacier":"Endicott Arm & Dawes Glacier","glacierPlace":"endicott_arm","timesStatus":"verified","timesSource":"Celebrity itinerary page (EG07A439, Jun 11 sailing)",
  "days":[[E("sea_p91","16:00")],[SEA],[P("ketchikan","06:00","16:00")],[S("endicott_arm","05:30","10:00"),P("juneau","13:30","22:00")],[P("skagway","06:30","18:00")],[SEA],[P("victoria","17:30","23:59")],[X("sea_p91","06:00")]]},
 {"id":"carnival_tracy","line":"carnival","ship":None,"ships":["carnival_legend","carnival_spirit"],"name":"7-Day Alaska Inside Passage & Glacier from Seattle","weekday":"Tuesday (Legend) / Thursday (Spirit)","glacier":"Tracy Arm Fjord","glacierPlace":"tracy_arm","timesStatus":"verified","timesSource":"Carnival itinerary pages (GA2, Jun 15 Legend and Jun 17 Spirit); Seattle return from CruiseMapper",
  "days":[[E("sea_p91","15:30")],[SEA],[S("tracy_arm")],[P("skagway","07:00","20:00")],[P("juneau","07:00","15:00")],[P("ketchikan","07:00","13:00")],[P("victoria","20:00","23:59")],[X("sea_p91","07:00")]]},
 {"id":"msc_poesia_tracy","line":"msc","ship":"msc_poesia","name":"7 Nights Alaska (Ketchikan, Icy Strait, Tracy Arm, Juneau, Victoria)","weekday":"Monday","glacier":"Tracy Arm Fjord","glacierPlace":"tracy_arm","timesStatus":"published","timesSource":"CruiseTimetables (aggregator); port list confirmed on msccruisesusa.com",
  "days":[[E("sea_p91","16:00")],[SEA],[P("ketchikan","07:00","17:00")],[P("icy_strait","10:00","19:00")],[S("tracy_arm"),P("juneau","14:00","22:00")],[SEA],[P("victoria","20:00","23:58")],[X("sea_p91","07:00")]]},
 {"id":"virgin_brilliant_fjords","line":"virgin","ship":"brilliant_lady","name":"Alaska: Inside Passage & Glacial Fjords","weekday":"Thursday","glacier":"Endicott Arm & Dawes Glacier","glacierPlace":"endicott_arm","timesStatus":"unavailable","timesSource":"Port order from virginvoyages.com; day-by-day times not captured",
  "ports":["ketchikan","sitka","endicott_arm","victoria"],"days":None},
 {"id":"oceania_riviera_visions","line":"oceania","ship":"oceania_riviera","name":"7 Night Visions of Alaska","weekday":"Thursday","glacier":None,"glacierPlace":None,"timesStatus":"published","timesSource":"CruiseTimetables (Jul 1, 2027 sailing)",
  "days":[[E("sea_p66","17:00")],[SEA],[P("ketchikan","09:00","17:00")],[P("icy_strait","10:00","18:00")],[P("sitka","07:00","16:00")],[SEA],[P("victoria","14:00","23:00")],[X("sea_p66","08:00")]]},
]

# ---------------- sailings ----------------
sailings = []
def booking_url(kind, **k):
    if kind=="princess": return f"https://www.princess.com/itinerary-details/?voyageCode={k['code']}"
    if kind=="hal": return f"https://www.hollandamerica.com/en/us/find-a-cruise/a7e07b/{k['code']}"
    if kind=="ncl": return f"https://www.ncl.com/vacation-builder/planning/stateroom?itineraryCode={k['itin']}&packageId={k['code']}&guests=2&stateroomTypeCode=INSIDE"
    if kind=="rci_v": return f"https://www.royalcaribbean.com/itinerary/7-night-alaska-adventure-cruise-from-seattle-on-voyager-VY07A458?sailDate={k['date']}&packageCode=VY07A458&groupId=VY07SEA-2189415139&country=USA"
    if kind=="rci_q": return f"https://www.royalcaribbean.com/itinerary/7-night-alaska-adventure-cruise-from-seattle-on-quantum-QN07A455?sailDate={k['date']}&packageCode=QN07A455&groupId=QN07SEA-2909514434&country=USA"
    if kind=="cel": return f"https://www.celebritycruises.com/itinerary/7-night-alaska-dawes-glacier-from-seattle-on-edge-EG07A439?sailDate={k['date']}&packageCode=EG07A439&groupId=EG07SEA-4212612062&country=USA"
    if kind=="car":
        dd=d(k['date']); return f"https://www.carnival.com/itinerary/7-day-alaska-inside-passage-and-glacier-cruise/seattle/{k['ship']}/7-days/ga2?itinportcode=SEA&sailDate={dd:%m%d%Y}&numGuests=2"
    if kind=="msc": return "https://www.msccruisesusa.com/search?passengers=2%7C0%7C0%7C0&embkPort=SEA"
    if kind=="virgin": return "https://www.virginvoyages.com/book/voyage-planner/find-a-voyage?portsOfCall=SEA&fromDate=2027-05-25&toDate=2027-07-10"
    if kind=="oceania": return "https://www.cruisetimetables.com/cruisesonoceaniariviera-01jul2027.html"

def price(pp, status="verified", label=None, note=None):
    if pp is None: return {"pp":None,"status":"unavailable","label":label,"note":note}
    return {"pp":pp,"status":status,"label":label,"note":note}

def add(itin, ship, date, prices, url, srcnote, flags=None, note=None, code=None):
    dep = d(date)
    sailings.append({"id":f"{itin}_{date}", "itinerary":itin, "ship":ship, "depart":date, "return":(dep+datetime.timedelta(days=7)).isoformat(), "nights":7,
        "code":code, "prices":prices, "currency":"USD", "priceBasis":"Average per person, 2 adults sharing, cruise fare including taxes, fees and port expenses. Gratuities not included.",
        "priceSource":{"url":url,"kind":"first-party" if "cruisetimetables" not in url else "aggregator","checked":CHECKED,"note":srcnote},
        "flags":flags or [], "note":note})

# Princess Royal (Glacier Bay)
for code,date,i,b,ms in [(1717,"2027-05-29",1194,2349,2994),(1718,"2027-06-05",1474,3149,3524),(1719,"2027-06-12",1474,3049,4024),(1720,"2027-06-19",1554,2849,3574),(1721,"2027-06-26",1574,2649,3624),(1722,"2027-07-03",1624,2939,3364)]:
    add("princess_royal_gb","royal_princess",date,{"interior":price(i),"oceanview":price(None,note="No oceanview category offered on this ship."),"balcony":price(b),"miniSuite":price(ms,label="Mini-Suite")},
        booking_url("princess",code=code),"Princess itinerary page, Standard fare, 'Up to 50% Off' sale",code=str(code))
# Princess Star (Dawes)
for code,date,i,o,b,ms in [(4722,"2027-05-30",944,1624,1999,2274),(4723,"2027-06-06",1324,1624,2299,2924),(4724,"2027-06-13",1374,2174,2449,2924),(4725,"2027-06-20",1324,2034,2549,2874),(4726,"2027-06-27",1294,1924,2299,2724),(4727,"2027-07-04",1174,1554,2349,2674)]:
    add("princess_star_dawes","star_princess",date,{"interior":price(i),"oceanview":price(o),"balcony":price(b),"miniSuite":price(ms,label="Mini-Suite")},
        booking_url("princess",code=code),"Princess itinerary page, Standard fare, 'Up to 50% Off' sale",code=str(code),
        flags=(["holiday"] if date=="2027-06-27" else []))
# HAL Eurodam
for code,date,i,o,b,ss in [("d741","2027-05-29",1344,1394,2394,None),("d742","2027-06-05",1599,1649,2944,None),("d743","2027-06-12",1549,1599,3114,5069),("d746","2027-06-19",1549,1599,3114,4639),("d747","2027-06-26",1449,1599,2949,3829)]:
    add("hal_eurodam_explorer","eurodam",date,{"interior":price(i,label="Inside"),"oceanview":price(o),"balcony":price(b,label="Verandah"),"miniSuite":price(ss,label="Signature Suite",note=None if ss else "Sold out")},
        booking_url("hal",code=code),"Holland America booking page 'Choose your guests' (2 adults)",code=code)
# NCL Encore
for code,date,i,o,b,cb in [(24203314,"2027-05-30",1449,1979,2249,2399),(24203315,"2027-06-06",1629,2229,2749,2899),(24203316,"2027-06-13",1779,2379,2649,2949),(24203317,"2027-06-20",1749,2099,2729,2949),(24203318,"2027-06-27",1599,2079,2599,2699)]:
    add("ncl_encore_gb","norwegian_encore",date,{"interior":price(i,label="Inside"),"oceanview":price(o),"balcony":price(b),"miniSuite":price(cb,label="Club Balcony Suite")},
        booking_url("ncl",itin="ENCORE7SEAJNUSGYKTNVICSEA",code=code),"NCL vacation builder stateroom page, 2 guests",code=str(code),
        note=("Guarantee Inside (cabin assigned by NCL) was $1,579 pp." if code==24203315 else None))
# NCL Bliss
for code,date,i,o,b,cb in [(24218430,"2027-05-29",1039,1259,1609,1809),(24218431,"2027-06-05",1259,1789,2089,2379),(24218432,"2027-06-12",1209,1889,2039,2209),(24218433,"2027-06-19",1259,1709,2049,2239),(24218434,"2027-06-26",1259,1759,2109,2209)]:
    add("ncl_bliss_dawes","norwegian_bliss",date,{"interior":price(i,label="Inside"),"oceanview":price(o),"balcony":price(b),"miniSuite":price(cb,label="Club Balcony Suite")},
        booking_url("ncl",itin="BLISS7SEASITJNUICYKTNVICSEA",code=code),"NCL vacation builder stateroom page, 2 guests",code=str(code))
# NCL Joy
add("ncl_joy_hubbard","norwegian_joy","2027-06-25",{"interior":price(1009,label="Inside"),"oceanview":price(1459),"balcony":price(1879),"miniSuite":price(2049,label="Club Balcony Suite")},
    booking_url("ncl",itin="JOY7SEAJNUICYKTNVICSEA",code=24235224),"NCL vacation builder stateroom page, 2 guests; 'Black Friday Latitudes Sale' label",code="24235224",
    flags=["promo"],note="Sale price shown to logged-out visitors; the sale label suggests it may end after Black Friday 2026. Guarantee Inside was $959 pp.")
add("ncl_joy_dawes","norwegian_joy","2027-07-02",{"interior":price(1049,label="Inside"),"oceanview":price(1449),"balcony":price(1919),"miniSuite":price(2039,label="Club Balcony Suite")},
    booking_url("ncl",itin="JOY7SEAICYSITKTNVICSEA",code=24235225),"NCL vacation builder stateroom page, 2 guests; 'Black Friday Latitudes Sale' label",code="24235225",
    flags=["promo","holiday"],note="Guarantee Inside was $999 pp.")
# RCI Voyager
for date,i,o,b,s in [("2027-05-28",751,860,1400,2725),("2027-06-04",978,1217,1800,2860),("2027-06-11",960,1213,1830,3030),("2027-06-18",908,1170,1740,3260),("2027-06-25",867,1110,1650,2606)]:
    add("rci_voyager_dawes","voyager_of_the_seas",date,{"interior":price(i),"oceanview":price(o,label="Outside View"),"balcony":price(b),"miniSuite":price(s,label="Suite")},
        booking_url("rci_v",date=date),"Royal Caribbean search results date panel, 2 guests",flags=["resident-tag"])
# RCI Quantum
for date,i,o,b,s in [("2027-05-31",1205,1304,1510,3867),("2027-06-07",1352,1534,1885,3447),("2027-06-14",1380,1835,2006,3997),("2027-06-21",1342,1594,1801,3887),("2027-06-28",1259,1391,1716,3786)]:
    add("rci_quantum_dawes","quantum_of_the_seas",date,{"interior":price(i),"oceanview":price(o,label="Outside View"),"balcony":price(b),"miniSuite":price(s,label="Suite")},
        booking_url("rci_q",date=date),"Royal Caribbean search results date panel, 2 guests",flags=["resident-tag"])
# Celebrity Edge
for date,i,o,b,c in [("2027-05-28",1221,1429,2177,2377),("2027-06-04",1263,1753,2003,2341),("2027-06-11",1116,1720,2520,2590),("2027-06-18",1203,1606,2300,2300),("2027-06-25",1248,1798,2023,2222)]:
    add("celebrity_edge_dawes","celebrity_edge",date,{"interior":price(i,label="Inside"),"oceanview":price(o),"balcony":price(b,label="Veranda"),"miniSuite":price(c,label="Concierge Class")},
        booking_url("cel",date=date),"Celebrity search results date panel, 2 guests, '75% Off 2nd Guest' promotion",flags=["promo"])
# Carnival
for ship,slug,rows in [("carnival_legend","legend",[("2027-05-25",809,989,1394,2667),("2027-06-01",1004,1234,1564,2924),("2027-06-08",1014,1244,1594,2995),("2027-06-15",1044,1264,1604,2757),("2027-06-22",1044,1314,1624,2894),("2027-06-29",1075,1275,1605,2878)]),
                       ("carnival_spirit","spirit",[("2027-05-27",869,1134,1454,3044),("2027-06-03",1004,1294,1604,2864),("2027-06-10",1014,1304,1604,3077),("2027-06-17",1034,1284,1614,2917),("2027-06-24",1095,1405,1615,2978),("2027-07-01",1106,1366,1766,3216)])]:
    for date,i,o,b,s in rows:
        add("carnival_tracy",ship,date,{"interior":price(i),"oceanview":price(o,label="Ocean View"),"balcony":price(b),"miniSuite":price(s,label="Suite")},
            booking_url("car",date=date,ship=slug),"Carnival cruise search, 2 adults, no discounts",flags=(["holiday"] if date in ("2027-06-29","2027-07-01") else []))
# MSC
for date,i in [("2027-06-07",898),("2027-06-14",899),("2027-06-21",889),("2027-06-28",899)]:
    add("msc_poesia_tracy","msc_poesia",date,{"interior":price(i),"oceanview":price(None),"balcony":price(None,note="Category prices for this date did not open on msccruisesusa.com."),"miniSuite":price(None)},
        booking_url("msc"),"MSC search results, date list (interior 'from' price), 2 guests",note="Balcony price not captured, so the two-cabin total cannot be calculated yet.")
# Virgin
for date,sv in [("2027-06-03",1043),("2027-06-10",1182)]:
    add("virgin_brilliant_fjords","brilliant_lady",date,{"interior":price(None,label="Insider",note="Insider cabins not listed for this date."),"oceanview":price(sv,label="Sea View"),"balcony":price(None,label="Sea Terrace"),"miniSuite":price(None)},
        booking_url("virgin"),"Virgin Voyages search results, per sailor, 'Black Friday Preview: 80% off 2nd Sailor'",flags=["promo","adults-only"],
        note="Only the lowest Sea View price was captured; Sea Terrace (balcony) and Insider (interior) prices are not captured. Virgin fares include gratuities, Wi-Fi and basic drinks.")
# Oceania (aggregator)
add("oceania_riviera_visions","oceania_riviera","2027-07-01",{"interior":price(2252,"published",label="Inside"),"oceanview":price(2635,"published"),"balcony":price(3017,"published",label="Veranda"),"miniSuite":price(4165,"published",label="Suite")},
    booking_url("oceania"),"CruiseTimetables sampled 'from' prices (aggregator). Not checked on oceaniacruises.com.",flags=["holiday","adults-only"],
    note="Premium small ship. Seattle round trips start Jun 24 (price for Jun 24 not captured). No glacier day.")

# ---------------- lines reviewed but not offering a qualifying June sailing ----------------
reviewed = [
 {"line":"Holland America – Noordam","finding":"No 7-night Seattle round trip in June 2027: Noordam sails the 28-day Arctic Circle Solstice voyage Jun 6–Jul 4. Its 7-day Alaska Explorer runs May 30 and from Jul 4.","source":"cruisemapper_noordam"},
 {"line":"Royal Caribbean – Voyager 'Alaska Experience'","finding":"Juneau/Skagway/Sitka version without a glacier day runs only in May and September 2027.","source":None},
 {"line":"Norwegian Joy – 9- and 10-day","finding":"9-day round trips depart Jun 7 and Jun 16, 2027. Excluded as longer than 8 nights.","source":"cabinsaver_ncl"},
 {"line":"Carnival Luminosa, Princess Ruby/Coral/Island/Crown/Discovery","finding":"Sail from San Francisco, Vancouver or Whittier, not round trip from Seattle.","source":"cabinsaver_sea"},
 {"line":"Princess, Royal Caribbean, Celebrity, HAL Vancouver sailings","finding":"Out of scope (not Seattle departures).","source":None},
]

data = {
 "meta":{"title":"Alaska 2027 Family Cruise Planner","version":"0.1.0-phase1","updated":CHECKED,"currency":"USD",
   "travelers":{"parents":{"count":2,"age":"~65","cabin":"balcony","notes":"Mom's walking limit under ~2 miles/day; balcony near elevators."},
                "brothers":{"count":2,"age":"~35","cabin":"interior","notes":"Budget-minded, adventurous."},
                "homeAirport":"ABQ","documents":"All US citizens with passports.","loyalty":"None"},
   "window":{"from":"2027-05-25","to":"2027-07-10","preferred":"June 2027"},
   "phases":[{"n":1,"name":"Cruises + port schedules","status":"done"},{"n":2,"name":"Excursions","status":"next"},{"n":3,"name":"Flights + Seattle hotels","status":"todo"},{"n":4,"name":"Full planner app","status":"todo"},{"n":5,"name":"Testing, CSV, report","status":"todo"}],
   "assumptions":[
     "Cruise prices are per person for 2 adults sharing a cabin and already include taxes, fees and port expenses as shown on each site.",
     "Two-cabin cruise fare = 2 x interior + 2 x balcony per-person price for the same sailing.",
     "Estimated gratuities = line's published daily rate x 4 guests x 7 nights (estimate; may be prepaid or included in some fares).",
     "Usable shore time = scheduled port hours minus 1.5 hours (30 min to get off, back aboard 1 hour before departure). Planning assumption only.",
     "Seattle terminal is the line's usual pier; confirm on cruise documents.",
     "Prices change daily and sales end; refresh before booking."],
   "statusDefinitions":STATUS},
 "sources":list(sources.values()),
 "places":places, "lines":lines, "ships":ships, "itineraries":itins, "sailings":sailings, "linesReviewed":reviewed,
 "excursions":[], "flights":[], "hotels":[],
 "photoPolicy":"Photos are Wikimedia Commons images linked by URL with author and license credit. Pages show a styled placeholder when a photo cannot load."
}
json.dump(data, open("data.json","w"), indent=1, ensure_ascii=False)
print("sailings", len(sailings), "itineraries", len(itins), "places", len(places))
