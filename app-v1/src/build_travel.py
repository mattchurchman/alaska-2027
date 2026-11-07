#!/usr/bin/env python3
"""Phase 3: add flights[] and hotels[] to data.json (run from the folder holding data.json).
All figures were read on Google Flights / Google Hotels on 2026-11-06 (Denver) with no sign-in.
Nothing here is a booking-site quote: statuses are 'published' (a real listed price, not read on the
airline/hotel's own booking page) or 'estimate' (calculated here) or 'unavailable'."""
import json, datetime as dt, urllib.parse as up

CHECKED = "2026-11-06"
d = json.load(open("data.json"))

def gf(dep, ret, nonstop=True):
    q = f"Flights from ABQ to SEA on {dep} through {ret} for 4 adults" + (" nonstop" if nonstop else "")
    return "https://www.google.com/travel/flights?q=" + up.quote(q)

def gh(area, night, nxt):
    return "https://www.google.com/travel/search?q=" + up.quote(f"{area} {night} to {nxt} 2 guests")

# ---------- sources ----------
new_sources = [
 dict(id="gf_abq_sea", title="Google Flights: ABQ to SEA round trips, 4 adults, June 2027", url="https://www.google.com/travel/flights?q=Flights%20from%20ABQ%20to%20SEA%20on%202027-06-11%20through%202027-06-19%20for%204%20adults%20nonstop", kind="aggregator", publisher="Google Flights", checked=CHECKED,
      note="Fares and times for 4 adults, economy incl. Basic, logged out. Shows Alaska Airlines fare options; Alaska's own booking site was not queried. Each flight record links to its own date search."),
 dict(id="alaska_air", title="Alaska Airlines booking site", url="https://www.alaskaair.com/", kind="first-party", publisher="Alaska Airlines", checked=CHECKED,
      note="Where to book. Not queried: the fare figures come from the Google Flights listing of Alaska's Saver/Main/First fares. Homepage only; no deep link to the exact flights is available."),
 dict(id="gh_downtown", title="Google Hotels: downtown Seattle, Jun 11-12 2027", url=gh("hotels in downtown Seattle","June 11 2027","June 12 2027"), kind="aggregator", publisher="Google Hotels", checked=CHECKED,
      note="Nightly rate shown for 1 room, 2 guests (the 2 rooms x 4 adults setting did not carry through). Tax treatment is not stated on the list page."),
 dict(id="gh_airport", title="Google Hotels: near Seattle-Tacoma airport, Jun 11-12 2027", url=gh("hotels near Seattle-Tacoma airport SeaTac","June 11 2027","June 12 2027"), kind="aggregator", publisher="Google Hotels", checked=CHECKED,
      note="Same basis as the downtown search: 1 room, 2 guests, tax treatment not stated."),
 dict(id="gh_pier66", title="Google Hotels: waterfront / Pier 66 area, Jun 11-12 2027", url=gh("waterfront hotels Seattle Pier 66","June 11 2027","June 12 2027"), kind="aggregator", publisher="Google Hotels", checked=CHECKED,
      note="Same basis; Google lists distance to Pier 66 for each result."),
]
have = {s["id"] for s in d["sources"]}
d["sources"] += [s for s in new_sources if s["id"] not in have]

# ---------- flights ----------
OUT = [("07:00","09:12"),("16:11","18:23")]
RET = [("11:16","15:19"),("18:55","22:58")]
# (outbound date, return date, return times opened on the booking page?)
pairs = [("2027-06-11","2027-06-19",True),("2027-06-14","2027-06-22",False),("2027-06-16","2027-06-24",False),
         ("2027-06-18","2027-06-26",False),("2027-06-19","2027-06-27",False),("2027-06-24","2027-07-02",True)]
flights = []
for o, r, opened in pairs:
    embark = (dt.date.fromisoformat(o) + dt.timedelta(days=1)).isoformat()
    sails = [s["id"] for s in d["sailings"] if s["depart"] == embark]
    assert all(s["return"] == r for s in d["sailings"] if s["depart"] == embark), (embark, r)
    flights.append(dict(
        id=f"abq_sea_ak_{o}_{r}", airline="Alaska Airlines", flightNumbers=None,
        flightNumberNote="Google Flights did not show flight numbers for these results; get them from Alaska at booking.",
        route="ABQ-SEA-ABQ", stops=0, outboundDate=o, returnDate=r, embarkDate=embark, disembarkDate=r, sailingIds=sails,
        outbound=[dict(dep=a, arr=b, durationMin=192, tz="Dep Mountain / arr Pacific") for a, b in OUT],
        returns=[dict(dep=a, arr=b, durationMin=183, tz="Dep Pacific / arr Mountain") for a, b in RET],
        returnTimesChecked=opened,
        returnTimesNote=None if opened else "Return times were read for Jun 11-19 and Jun 24-Jul 2 only; the same two nonstops (11:16 am, 6:55 pm) were not opened for this date pair. Confirm before relying on them.",
        fare=dict(
            saver=dict(total4=1588, pp=397, status="published", note="Alaska 'Saver' fare as listed on Google Flights for 4 adults, round trip, taxes and fees included. No changes, no refunds."),
            main=dict(total4=2068 if opened else None, pp=517 if opened else None, status="published" if opened else "unavailable", note="Main fare: free change (fare difference may apply), no refunds, free seat selection." if opened else "Booking options not opened for this date pair."),
            first=dict(total4=3588 if opened else None, pp=897 if opened else None, status="published" if opened else "unavailable", note="First class, 2 free checked bags each." if opened else "Booking options not opened for this date pair."),
        ),
        bags=dict(firstCheckedPerPerson=90, status="published", note="Saver and Main: 1 free carry-on each; first checked bag $90 per person each way as shown on the Google booking panel (confirm whether this is per direction at checkout). 4 bags would be about $360 if charged once, $720 if each way."),
        restrictions="Saver: no changes, no refunds. Main: free change, no refund. Prices can change daily.",
        sources=["gf_abq_sea","alaska_air"], url=gf(o, r), bookUrl="https://www.alaskaair.com/", checked=CHECKED,
        buffers=dict(
            arrive="Arrives the day before embarkation (7:00 am flight lands 9:12 am; hotel check-in is usually mid-afternoon, so plan luggage storage).",
            depart="Ship docks about 6:00-7:00 am (see each itinerary). The 11:16 am flight leaves roughly 4 to 5 hours after docking: workable with a transfer, tight if disembarkation is late or the parents need assistance. The 6:55 pm flight is the relaxed choice (needs luggage storage or a day room).",
            status="estimate")))
# connecting alternatives, one date pair (the only one searched without the nonstop filter)
flights.append(dict(
    id="abq_sea_connecting_2027-06-11_2027-06-19", airline="Not captured (carrier names not shown in the list text)", flightNumbers=None,
    route="ABQ-SEA (1 stop)", stops=1, outboundDate="2027-06-11", returnDate="2027-06-19", embarkDate="2027-06-12", disembarkDate="2027-06-19", sailingIds=[s["id"] for s in d["sailings"] if s["depart"]=="2027-06-12"],
    outbound=[dict(dep="19:35",arr="00:11+1",totalFare4=1706,durationMin=336),dict(dep="21:35",arr="01:45+1",totalFare4=1786,durationMin=310),dict(dep="09:45",arr="14:05",totalFare4=2046,durationMin=320),dict(dep="08:20",arr="12:24",totalFare4=5106,durationMin=304)],
    returns=[], returnTimesChecked=False,
    fare=dict(saver=dict(total4=None,pp=None,status="unavailable",note="Round-trip totals for 4 adults as listed with the outbound flight: $1,706 / $1,786 / $2,046 / $5,106. Return legs and airlines not captured.")),
    bags=dict(firstCheckedPerPerson=None,status="unavailable",note="Not captured."),
    restrictions="Not captured.", sources=["gf_abq_sea"], url=gf("2027-06-11","2027-06-19",False), bookUrl=None, checked=CHECKED,
    note="Only Alaska flies ABQ-SEA nonstop in the results. The connecting options cost $118 to $3,518 more for four and two of them land after midnight, so they are listed for context only."))
d["flights"] = flights

# ---------- hotels ----------
STAY, NEXT = "2027-06-11", "2027-06-12"
def H(id, name, area, stars, rating, reviews, rate, **kw):
    base = dict(id=id, name=name, area=area, stars=stars, reviewScore=rating, reviewCount=reviews, reviewSource="Google (as shown on the Google Hotels list)",
        stayDate=STAY, checkOut=NEXT, nights=1,
        rate=dict(perRoomNight=rate, rooms=1, guests=2, status="published", note="Nightly rate for 1 room, 2 guests on the Google Hotels list. Tax and resort/parking fees are not stated."),
        twoRooms=dict(total=rate*2, status="estimate", note="Planner estimate: 2 x the one-room rate. Taxes and mandatory fees not included; Seattle hotel taxes are not shown on the list page."),
        taxesFees=dict(status="unavailable", note="Not captured on the list page."),
        photo=None, bookUrl=None, checked=CHECKED, mobilityNote=None)
    base.update(kw); return base

hotels = [
 H("hyatt_regency","Hyatt Regency Seattle","downtown",4,4.6,4300,272, sources=["gh_downtown"], url=gh("hotels in downtown Seattle","June 11 2027","June 12 2027"),
   amenities=["Free Wi-Fi","Breakfast (fee)","Parking (fee)","Fitness center","Restaurant/bar"], accessibilityListed=False, distances=dict(pier66Mi=0.8, pier91Mi=None, airportMi=None),
   transfers="Taxi, rideshare or cruise-line transfer to the terminal; costs not captured.", pros="Top score among the downtown hotels with thousands of reviews (4.6 on 4.3K).", cons="Second-highest downtown rate. No accessibility feature shown on the list page."),
 H("mayflower_park","Mayflower Park Hotel","downtown",4,4.4,1500,232, sources=["gh_downtown"], url=gh("hotels in downtown Seattle","June 11 2027","June 12 2027"),
   amenities=["Free Wi-Fi","Breakfast (fee)","Parking (fee)","Fitness center","Restaurant/bar","Room service"], accessibilityListed=False, distances=dict(pier66Mi=None, pier91Mi=None, airportMi=None),
   transfers="Downtown; terminal transfer costs not captured.", pros="Rated 4.4 on 1.5K reviews.", cons="No accessibility feature shown on the list page; Pier 66 distance not shown."),
 H("exec_pacific","Executive Hotel Pacific","downtown",3,3.6,2400,196, sources=["gh_downtown"], url=gh("hotels in downtown Seattle","June 11 2027","June 12 2027"),
   amenities=["Free Wi-Fi","Free parking (as listed)","Fitness center","Restaurant/bar","Accessible","Business center"], accessibilityListed=True, distances=dict(pier66Mi=None, pier91Mi=None, airportMi=None),
   transfers="Downtown; terminal transfer costs not captured.", pros="'Accessible' amenity listed and parking shown as free.", cons="Lowest review score of the list (3.6)."),
 H("moore","Moore Hotel","waterfront-adjacent",2,3.9,996,99, sources=["gh_pier66"], url=gh("waterfront hotels Seattle Pier 66","June 11 2027","June 12 2027"),
   amenities=["Free Wi-Fi","Breakfast","Parking (fee)","Accessible","Smoke-free"], accessibilityListed=True, distances=dict(pier66Mi=0.4, pier91Mi=None, airportMi=None),
   transfers="Short ride to Pier 66 (0.4 mi per Google); rates for taxi or rideshare not captured.", pros="Lowest downtown rate; 'Accessible' listed; breakfast included.", cons="2-star older property; review score 3.9."),
 H("hotel_max","Hotel Max","downtown",3,4.2,1600,218, sources=["gh_pier66"], url=gh("waterfront hotels Seattle Pier 66","June 11 2027","June 12 2027"),
   amenities=["Free Wi-Fi","Breakfast","Parking (fee)","Accessible","Fitness center","Laundry"], accessibilityListed=True, distances=dict(pier66Mi=0.6, pier91Mi=None, airportMi=None),
   transfers="0.6 mi to Pier 66 per Google.", pros="'Accessible' listed, mid-range rate, 4.2 on 1.6K reviews.", cons="Themed rooms may not suit everyone; no further accessibility detail captured."),
 H("edgewater","The Edgewater Hotel","waterfront",4,4.4,3300,389, sources=["gh_pier66"], url=gh("waterfront hotels Seattle Pier 66","June 11 2027","June 12 2027"),
   amenities=["Free Wi-Fi","Breakfast (fee)","Parking (fee)","Fitness center","Restaurant/bar"], accessibilityListed=False, distances=dict(pier66Mi=0.1, pier91Mi=None, airportMi=None),
   transfers="0.1 mi to Pier 66 per Google, the shortest hop of any hotel found.", pros="Closest hotel to Pier 66 in the results.", cons="Most expensive option found; no accessibility feature shown."),
 H("hampton_airport","Hampton Inn & Suites Seattle-Airport/28th Ave","airport",3,4.4,2100,152, sources=["gh_airport"], url=gh("hotels near Seattle-Tacoma airport SeaTac","June 11 2027","June 12 2027"),
   amenities=["Free breakfast","Free Wi-Fi","Free parking","Airport shuttle","Accessible","Fitness center"], accessibilityListed=True, distances=dict(pier66Mi=None, pier91Mi=None, airportMi=1.2),
   transfers="Airport shuttle listed (hours and cost not captured). Terminal is roughly 14-16 mi by road, 30-45 min (Phase 1 note); fare not captured.", pros="Best airport-area score (4.4 on 2.1K), free breakfast, parking, shuttle and 'Accessible' listed, lowest-effort arrival for the parents.", cons="Not downtown; extra ride to the pier on embarkation day."),
 H("element_airport","Element by Marriott Seattle Sea-Tac Airport","airport",3,4.5,475,132, sources=["gh_airport"], url=gh("hotels near Seattle-Tacoma airport SeaTac","June 11 2027","June 12 2027"),
   amenities=["Free breakfast","Free Wi-Fi","Parking (fee)","Indoor pool","Fitness center"], accessibilityListed=False, distances=dict(pier66Mi=None, pier91Mi=None, airportMi=2.8),
   transfers="Shuttle not shown on the list page.", pros="High score (4.5), free breakfast.", cons="Only 475 reviews; 2.8 mi from SEA; no accessibility feature shown."),
 H("doubletree_airport","DoubleTree by Hilton Seattle Airport","airport",3,3.8,6900,128, sources=["gh_airport"], url=gh("hotels near Seattle-Tacoma airport SeaTac","June 11 2027","June 12 2027"),
   amenities=["Free Wi-Fi","Breakfast (fee)","Parking (fee)","Outdoor pool","Fitness center"], accessibilityListed=False, distances=dict(pier66Mi=None, pier91Mi=None, airportMi=1.1),
   transfers="Shuttle not shown on the list page.", pros="Lowest airport-area name-brand rate in the results, 1.1 mi from SEA.", cons="Review score 3.8."),
]
d["hotels"] = hotels

# ---------- meta ----------
m = d["meta"]; m["version"] = "0.3.0-phase3"; m["updated"] = CHECKED
for p in m["phases"]:
    if p["n"] == 3: p["status"] = "done"
    if p["n"] == 4: p["status"] = "next"
m["travelCoverage"] = dict(checked=CHECKED, flights=
    "Alaska Airlines is the only carrier with ABQ-SEA nonstops in the results (2 each way). Fares were read on Google Flights for 4 adults, not on Alaska's own site, so they are 'published', not verified. Six date pairs were searched (Jun 11-19, 14-22, 16-24, 18-26, 19-27, 24-Jul 2), covering the lead Saturday, Sunday, Tuesday, Thursday and Friday sailings. The same $1,588 nonstop fare appeared for every pair. Southwest, Delta, United and American showed no nonstop and were not priced separately.",
    hotels="9 hotels for the night of Jun 11 2027 (before the Sat Jun 12 sailings). Rates are 1 room, 2 guests as listed on Google Hotels; two-room totals are planner estimates (2 x rate). Taxes, fees, transfer costs and photos were not captured. Other nights (Jun 18, 19, 24 etc.) were not searched, so those rates will differ.",
    notCaptured=["Flight numbers","Alaska booking-site quotes","Southwest/Delta/United/American fares","Hotel taxes and mandatory fees","Hotel photos","Airport and terminal transfer prices","Hotel prices for nights other than Jun 11 2027","Post-cruise hotel"])
m["assumptions"].append("Flight fares are 4-adult round-trip totals from Google Flights' listing of Alaska Airlines fares; hotel rates are one room for two guests. Two-room totals are 2 x the one-room rate.")
json.dump(d, open("data.json", "w"), ensure_ascii=False, indent=1)
print("flights", len(flights), "hotels", len(hotels), "sources", len(d["sources"]))
