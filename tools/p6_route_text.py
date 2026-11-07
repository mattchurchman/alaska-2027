"""P6: short "why this route" notes on each route family (planner summaries, no prices).
Idempotent: overwrites the same fields each run."""
from common import load, save

TEXT = {
    "SEA-GB": dict(
        short="Seattle · Glacier Bay",
        why="Fly nonstop to Seattle and sail into Glacier Bay National Park, where park rangers come aboard for the day. Only Princess, Holland America and Norwegian hold the permits, so this is the route to pick if Glacier Bay itself matters.",
        tradeoff="Usually the priciest Seattle round trip, and the open-ocean run past Vancouver Island means two sea days.",
        bestFor="The full glacier day without changing airports"),
    "SEA-DAWES": dict(
        short="Seattle · Dawes Glacier",
        why="The most sailings and lines from Seattle. The glacier day is Endicott Arm, a narrow fjord ending at Dawes Glacier with steep walls close on both sides.",
        tradeoff="Floating ice can stop big ships short of the glacier face; the captain may turn back early or go elsewhere.",
        bestFor="Most choice of ships and dates from Seattle"),
    "SEA-TRACY": dict(
        short="Seattle · Tracy Arm",
        why="Carnival and MSC sailings, often the lowest fares from Seattle. The glacier day is Tracy Arm, a long fjord with waterfalls and twin glaciers.",
        tradeoff="Large ships often cannot get close to the glacier faces in Tracy Arm, so the scenery is the fjord more than the ice.",
        bestFor="Watching the budget"),
    "SEA-HUBBARD": dict(
        short="Seattle · Hubbard Glacier",
        why="A single Norwegian sailing that reaches Hubbard Glacier, one of the largest tidewater glaciers in North America, far up the Gulf of Alaska coast.",
        tradeoff="Only one date in the window, and getting to Hubbard and back costs extra time at sea.",
        bestFor="A huge glacier face from Seattle"),
    "SEA-NONE": dict(
        short="Seattle · no glacier day",
        why="A smaller, upscale ship with port calls but no scheduled glacier cruising.",
        tradeoff="Skips the glacier day that most families come for.",
        bestFor="A quieter ship, if glaciers are not the point"),
    "YVR-RT": dict(
        short="Vancouver round trip",
        why="Starts in Vancouver and sails north through the sheltered Inside Passage, so more of the trip is calm, scenic water instead of open ocean. Glacier days vary by ship: Glacier Bay, Dawes, Tracy Arm, Hubbard or the Stikine Icecap.",
        tradeoff="No nonstop flight from Albuquerque to Vancouver, and a Canada border crossing at the start and end (passports needed).",
        bestFor="Smoother, more scenic sailing"),
    "YVR-N": dict(
        short="Vancouver → Alaska (one way)",
        why="Ends in Seward or Whittier near Anchorage, so no days are spent sailing back south. Many add a second glacier day such as College Fjord or Hubbard Glacier, and you can add Denali or Anchorage time before flying home.",
        tradeoff="Fly into one city and home from another, plus a 2 to 3 hour transfer from the ship to Anchorage. Arrival-city costs are not captured yet.",
        bestFor="The most glaciers in seven nights"),
    "YVR-S": dict(
        short="Alaska → Vancouver (one way)",
        why="The same idea in reverse: start near Anchorage (Seward or Whittier) and finish in Vancouver, usually with Hubbard Glacier early in the week.",
        tradeoff="Fly into Anchorage and home from Vancouver, plus the transfer from Anchorage to the ship. Arrival-city costs are not captured yet.",
        bestFor="Adding Anchorage or Denali before the cruise"),
}


def main():
    d = load()
    c = d["catalog"]
    for r in c["routeFamilies"]:
        t = TEXT[r["id"]]
        r.update(t)
        r["textBasis"] = "Planner summary written in P6 from the catalog and line notes; general knowledge, not a sourced figure."
    save("catalog", c)
    print("route text set for", len(c["routeFamilies"]))


if __name__ == "__main__":
    main()
