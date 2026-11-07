"""P5: add Wikimedia Commons photos (author, license, file page) to data/media.json. Idempotent.

Metadata (author, license, size) was read from the Commons API on 2026-11-07.
Row: id suffix, file name as in the URL, author, license, target(s), alt text, width, height.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from common import load, save

CHECKED = "2026-11-07"
ROWS = [
 ["place-sea_airport","Sea-Tac_Airport_control_tower_with_Link_train_passing.jpg","Steve Morgan","CC BY-SA 4.0",["place:sea_airport"],"Sea-Tac Airport control tower with a Link light-rail train passing",2539,1710],
 ["place-stephens_passage","Stephens_Passage_and_Admiralty_Island%2C_AK.JPG","Jsayre64","CC BY-SA 3.0",["place:stephens_passage"],"Stephens Passage and Admiralty Island",4608,3456],
 ["place-yvr_canada_place","Vancouver_%28BC%2C_Canada%29%2C_Canada_Place_--_2022_--_2093.jpg","Dietmar Rabich","CC BY-SA 4.0",["place:yvr_canada_place"],"Canada Place cruise terminal in Vancouver",6720,3780],
 ["place-whittier","Whittier_Harbor%2C_Alaska_%282%29.jpg","127x0x0x1 at en.wikipedia","CC BY-SA 3.0",["place:whittier"],"Whittier harbor",3264,2448],
 ["place-college_fjord","Vassar_Glacier%2C_College_Fjord%2C_Alaska_06.jpg","Ken Lund","CC BY-SA 2.0",["place:college_fjord"],"Vassar Glacier in College Fjord",6000,4000],
 ["place-seward","Seward_harbor.jpg","1brownsfan","Public domain",["place:seward"],"Seward harbor",1400,1050],
 ["place-prince_rupert","Mariner_Statue_along_Waterfront_-_Prince_Rupert_-_British_Columbia_-_Canada.jpg","Adam Jones, Ph.D.","CC BY-SA 3.0",["place:prince_rupert"],"Mariner statue on the Prince Rupert waterfront",2736,3648],
 ["place-inside_passage_bc","The_Inside_Passage_in_British_Columbia_-_NOAA.jpg","Commander John Bortniak, NOAA Corps","Public domain",["place:inside_passage_bc"],"Inside Passage in British Columbia",1588,1184],
 ["place-haines","2018-09-19_01_Wide_view_of_Haines%2C_Alaska_USA.jpg","Gordon Leggett","CC BY 4.0",["place:haines"],"Wide view of Haines",8012,2030],
 ["poi-auke_bay","Juneau_Auke_Bay_Aerial_0595.jpg","Gillfoto","CC BY-SA 3.0",["poi:auke_bay"],"Aerial view of Auke Bay near Juneau",1200,796],
 ["poi-mendenhall_vc","Mendenhall_Glacier_Visitor_Center_01.jpg","Joe Mabel","CC BY-SA 4.0",["poi:mendenhall_vc"],"Mendenhall Glacier Visitor Center",6000,4000],
 ["poi-juneau_heli","Helicopter%2C_Mendenhall_Glacier%2C_Alaska.jpg","Robert Raines","CC BY-SA 2.0",["poi:juneau_heli"],"Helicopter at Mendenhall Glacier",4272,2848],
 ["poi-goldbelt_tram","Mount_Roberts_Tramway_in_Juneau%2C_Alaska.jpg","Wknight94","CC BY-SA 3.0",["poi:goldbelt_tram"],"Mount Roberts Tramway above Juneau",3072,2304],
 ["poi-white_pass","White_Pass_and_Yukon_Route_train_entering_a_tunnel.jpg","Cullen328","CC BY-SA 4.0",["poi:white_pass"],"White Pass and Yukon Route train entering a tunnel",3005,2539],
 ["poi-carcross","Carcross%2C_Yukon_Territory_2.jpg","Richard Martin","CC BY 2.0",["poi:carcross"],"Carcross, Yukon",2896,1936],
 ["poi-klgo_vc","Klondike_Gold_Rush_NHP_Skagway.JPG","Reywas92","CC BY-SA 3.0",["poi:klgo_vc"],"Klondike Gold Rush National Historical Park in Skagway",3648,2736],
 ["poi-creek_street","Calle_hist%C3%B3rica_Creek%2C_Ketchikan%2C_Alaska%2C_Estados_Unidos%2C_2017-08-16%2C_DD_54.jpg","Diego Delso","CC BY-SA 4.0",["poi:creek_street"],"Creek Street boardwalk in Ketchikan",7856,4123],
 ["poi-totem_bight","Totem_Bight_Community_House%2C_Mud_Bight_Village%2C_North_Tongass_Highway%2C_Ketchikan_vicinity_%28Ketchikan_Gateway_Borough%2C_Alaska%29.jpg","Unknown author","Public domain",["poi:totem_bight"],"Community house at Totem Bight (historic photo)",4059,3250],
 ["poi-saxman","Saxman_totem_park%28js%2901.jpg","Jerzystrzelecki","CC BY 3.0",["poi:saxman"],"Totem poles at Saxman",5648,3652],
 ["poi-misty_fjords","Misty_Fjords_National_Monument_ENBLA22.jpg","Enrico Blasutto","CC BY-SA 4.0",["poi:misty_fjords"],"Misty Fjords National Monument",5435,3623],
 ["poi-raptor_center","Handler_with_snowy_owl_at_the_Alaska_Raptor_Center.jpg","Cullen328","CC BY-SA 4.0",["poi:raptor_center"],"Handler with a snowy owl at the Alaska Raptor Center",4000,3000],
 ["poi-sitka_nhp","Sitka%2C_Alaska_-_Sitka_National_Historical_Park_-_Totem_Trail_%281%29.jpg","Jrozwado","CC BY-SA 4.0",["poi:sitka_nhp"],"Totem Trail in Sitka National Historical Park",800,1200],
 ["poi-inner_harbour","Victoria_Inner_Harbor_%285945755775%29.jpg","Roy Luck","CC BY 2.0",["poi:inner_harbour"],"Victoria Inner Harbour",4752,3168],
 ["poi-butchart","Butchart_Garden_splendor.jpg","Michelamillerdickson96","CC BY-SA 4.0",["poi:butchart"],"Butchart Gardens",4032,3024],
 ["exp-whales","Adult_Humpback_Whale_breaching.jpg","Gillfoto from Juneau, Alaska, United States","CC BY-SA 3.0",["experience:jnu_whale","experience:jnu_mdh_whale"],"Humpback whale breaching near Juneau",3648,2736],
 ["exp-lumberjack","Great_Alaskan_Lumberjack_Show_lumberjack.jpg","Wknight94","CC BY-SA 3.0",["experience:ktn_lumber"],"Great Alaskan Lumberjack Show",3072,2304],
 ["ship-emerald_princess","Emerald_Princess_cruise_ship.jpg","Quintin Soloviev","CC BY 4.0",["ship:emerald_princess"],"Emerald Princess",7311,4387],
 ["ship-crown_princess","Crown_Princess_%28ship%2C_2006%29_in_Fremantle_Harbour%2C_November_2024_03.jpg","Calistemon","CC BY-SA 4.0",["ship:crown_princess"],"Crown Princess",4543,2555],
 ["ship-discovery_princess","Discovery_Princess_docked_in_Juneau%2C_AK.jpg","Matthew Groh","CC BY-SA 4.0",["ship:discovery_princess"],"Discovery Princess docked in Juneau",6000,3375],
 ["ship-coral_princess","2026_Coral_Princess_Alaska_gf51.jpg","Gillfoto","CC BY-SA 4.0",["ship:coral_princess"],"Coral Princess in Alaska",6000,4000],
 ["ship-island_princess","Island_Princess_in_Port_Everglades.JPG","Jean-Philippe Boulet","CC BY 3.0",["ship:island_princess"],"Island Princess",4000,3000],
 ["ship-westerdam","MS_Westerdam_Skagway.jpg","PhilipRJ 89","CC BY-SA 4.0",["ship:westerdam"],"Westerdam at Skagway",4608,3456],
 ["ship-noordam","Noordam_in_Vancouver.jpg","Murgatroyd49","CC BY 4.0",["ship:noordam"],"Noordam in Vancouver",850,560],
 ["ship-serenade_of_the_seas","Serenade_of_the_Seas_in_Halifax%2C_Nova_Scotia_2024.jpg","Quintin Soloviev","CC BY 4.0",["ship:serenade_of_the_seas"],"Serenade of the Seas",8064,5176],
 ["ship-anthem_of_the_seas","Anthem_of_the_Seas_%28ship%2C_2015%29_at_Liverpool_2021-6.jpg","Rodhullandemu","CC BY-SA 4.0",["ship:anthem_of_the_seas"],"Anthem of the Seas",4721,2871],
 ["ship-celebrity_summit","Celebrity_Summit_NYC.jpg","Fritzmann2002","CC BY-SA 4.0",["ship:celebrity_summit"],"Celebrity Summit",2507,1410],
 ["ship-celebrity_solstice","Celebrity_Solstice_%28ship%2C_2008%29_001.jpg","Aah-Yeah","CC BY 2.0",["ship:celebrity_solstice"],"Celebrity Solstice",2758,1568],
 ["ship-norwegian_jade","Norwegian_Jade_%28ship%2C_2006%29_IMO_9304057%3B_in_Split%2C_2011-10-10%3B_%281%29.jpg","Ivan T.","CC BY-SA 3.0",["ship:norwegian_jade"],"Norwegian Jade",2947,1958],
 ["ship-disney_wonder","Disney_Wonder_in_Sydney_24_December_2024.jpg","Dicklyon","CC BY-SA 4.0",["ship:disney_wonder"],"Disney Wonder",4080,3072],
 ["ship-disney_magic","Disney_Magic_in_Oslo_2016_I.jpg","Smiley.toerist","CC BY-SA 4.0",["ship:disney_magic"],"Disney Magic",3648,2736],
]

# Deliberate placeholders (no suitable Commons photo found on 2026-11-07).
PLACEHOLDERS = {
    "place:stikine_icecap": "No matching Commons photo found (searched Stikine Icecap/Icefield, Shakes Glacier).",
    "poi:rainforest_sanctuary": "No matching Commons photo found for the Ketchikan Rainforest Sanctuary.",
}

if __name__ == "__main__":
    d = load()
    m = d["media"]
    have = {p["id"] for p in m["photos"]}
    n = 0
    for suffix, fn, author, lic, tgt, alt, w, h in ROWS:
        pid = "ph-" + suffix
        if pid in have:
            continue
        m["photos"].append({
            "id": pid,
            "url": f"https://commons.wikimedia.org/wiki/Special:FilePath/{fn}?width=1000",
            "page": f"https://commons.wikimedia.org/wiki/File:{fn}",
            "credit": f"{author} / Wikimedia Commons / {lic}",
            "license": lic, "for": tgt, "alt": alt, "w": w, "h": h, "checked": CHECKED,
        })
        n += 1
    m["placeholders"] = [{"for": k, "note": v, "checked": CHECKED} for k, v in PLACEHOLDERS.items()]
    save("media", m)
    print("added", n, "photos; total", len(m["photos"]))
