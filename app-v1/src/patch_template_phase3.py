#!/usr/bin/env python3
"""Adds the read-only 'Flights & hotels' tab to template.html (idempotent)."""
t = open("template.html").read()
if "vTravel" in t:
    print("already patched"); raise SystemExit
css = """
/* flights & hotels */
.fl{display:flex;flex-direction:column}
.fl .fh{padding:14px 16px 8px;display:flex;flex-direction:column;gap:6px}
.legs{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:10px;padding:0 16px 12px}
.leg{background:var(--sunk);border-radius:8px;padding:9px 11px;font-size:.86rem}
.leg b{font-weight:600}
.fare3{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px;padding:0 16px 12px}
.fare3>div{border:1px solid var(--line);border-radius:8px;padding:8px 10px;display:flex;flex-direction:column;gap:3px;font-size:.84rem}
.hcard{overflow:hidden;display:flex;flex-direction:column;min-width:0}
.hcard .hb{padding:14px 16px 16px;display:flex;flex-direction:column;gap:8px}
"""
t = t.replace("</style>", css + "</style>", 1)
t = t.replace('<a href="#excursions">Excursions</a>', '<a href="#excursions">Excursions</a><a href="#travel">Flights &amp; hotels</a>', 1)
js = r"""
/* ---------- flights & hotels ---------- */
function tm(t){if(!t)return"";var n=t.indexOf("+1")>-1;return t12(t.replace("+1",""))+(n?" (+1 day)":"")}
function sailNames(f){return (f.sailingIds||[]).map(function(id){var s=IDX.sail[id];return s?s._ship.name:null}).filter(Boolean).join(", ")}
function fareBox(lab,x){if(!x)return"";return '<div><span class="muted">'+esc(lab)+'</span><span class="num" style="font-size:1.1rem">'+(x.total4==null?'—':money(x.total4))+'</span><span class="note">'+(x.pp!=null?money(x.pp)+' per person · ':'')+'4 adults round trip</span>'+stTag(x.status)+'<span class="note">'+esc(x.note||"")+'</span></div>'}
function flightCard(f){
  var o=(f.outbound||[]).map(function(x){return '<div>'+tm(x.dep)+' → '+tm(x.arr)+(x.totalFare4!=null?' · '+money(x.totalFare4)+' for 4':'')+'</div>'}).join("");
  var r=(f.returns||[]).map(function(x){return '<div>'+tm(x.dep)+' → '+tm(x.arr)+'</div>'}).join("");
  var fr=f.fare||{};
  return '<article class="card fl"><div class="fh"><div class="eyebrow">Fly '+fmtD(f.outboundDate,{weekday:"short",month:"short",day:"numeric"})+' · return '+fmtD(f.returnDate,{weekday:"short",month:"short",day:"numeric"})+'</div>'+
   '<h3>'+esc(f.airline)+' · '+(f.stops===0?'nonstop':f.stops+' stop')+'</h3>'+
   '<div class="note">Cruise sails '+fmtD(f.embarkDate,{weekday:"long",month:"short",day:"numeric"})+' → ship '+esc(sailNames(f)||"none in this data")+'. Back in Seattle '+fmtD(f.disembarkDate,{weekday:"short",month:"short",day:"numeric"})+'.</div></div>'+
   '<div class="legs"><div class="leg"><b>ABQ → SEA ('+fmtD(f.outboundDate)+')</b>'+o+'<div class="note">Times as listed on Google Flights (ABQ Mountain, SEA Pacific).</div></div>'+
   (r?'<div class="leg"><b>SEA → ABQ ('+fmtD(f.returnDate)+')</b>'+r+'<div class="note">'+(f.returnTimesChecked?'Read on the booking panel.':'Not opened for this date pair; confirm.')+'</div></div>':'')+'</div>'+
   '<div class="fare3">'+(f.fare.main?fareBox("Saver",fr.saver)+fareBox("Main",fr.main)+fareBox("First",fr.first):fareBox("Round-trip total",fr.saver))+'</div>'+
   '<div class="xbox"><b>Bags:</b> '+esc((f.bags||{}).note||"")+' '+stTag((f.bags||{}).status||"unavailable")+'</div>'+
   (f.buffers?'<div class="xbox"><b>Timing for the parents:</b> '+esc(f.buffers.arrive)+' '+esc(f.buffers.depart)+' '+stTag(f.buffers.status)+'</div>':'')+
   (f.returnTimesNote?'<div class="xrisk">'+esc(f.returnTimesNote)+'</div>':'')+
   (f.note?'<div class="xcmp">'+esc(f.note)+'</div>':'')+
   '<div class="xo" style="border-top:1px solid var(--line)"><div class="t"><span class="note">'+esc(f.restrictions||"")+'</span></div><div class="m" style="grid-column:1/-1"><a href="'+esc(f.url)+'" target="_blank" rel="noopener">Source: this date search on Google Flights</a>'+(f.bookUrl?'<a href="'+esc(f.bookUrl)+'" target="_blank" rel="noopener">Book with the airline (homepage)</a>':'')+'<span>Checked '+esc(f.checked)+'</span></div></div></article>'}
var AREA={downtown:"Downtown","waterfront-adjacent":"Near the waterfront",waterfront:"Waterfront",airport:"Airport area"};
function hotelCard(h){
  var dd=h.distances||{},ds=[];if(dd.pier66Mi!=null)ds.push(dd.pier66Mi+' mi to Pier 66');if(dd.airportMi!=null)ds.push(dd.airportMi+' mi to SEA');
  return '<article class="card hcard">'+photo(h.photo,h.name)+'<div class="hb"><div class="eyebrow">'+esc(AREA[h.area]||h.area)+' · '+h.stars+'-star</div><h3>'+esc(h.name)+'</h3>'+
   '<div class="xrow"><span class="pill">★ '+h.reviewScore+' · '+h.reviewCount.toLocaleString("en-US")+' reviews</span>'+(h.accessibilityListed?'<span class="lab lab-everyone">"Accessible" listed</span>':'<span class="lab lab-precautions">No accessibility feature listed</span>')+'</div>'+
   '<div><span class="big">'+money(h.twoRooms.total)+'</span> <span class="muted" style="font-size:.85rem">2 rooms, 1 night (estimate)</span></div>'+
   '<div class="note">'+money(h.rate.perRoomNight)+' per room ('+h.rate.guests+' guests) '+stTag(h.rate.status)+' · 2-room total '+stTag(h.twoRooms.status)+' · taxes and fees '+stTag(h.taxesFees.status)+'</div>'+
   '<div class="note">Night of '+fmtD(h.stayDate,{weekday:"short",month:"short",day:"numeric"})+' (before the '+fmtD(h.checkOut,{weekday:"short",month:"short",day:"numeric"})+' sailings).'+(ds.length?' '+esc(ds.join(' · '))+'.':'')+'</div>'+
   '<div style="font-size:.9rem"><b>Good:</b> '+esc(h.pros)+'</div><div style="font-size:.9rem"><b>Watch:</b> '+esc(h.cons)+'</div>'+
   '<div class="note"><b>Getting around:</b> '+esc(h.transfers)+'</div><div class="note">Listed: '+esc(h.amenities.join(", "))+'</div>'+
   '<div class="note"><a href="'+esc(h.url)+'" target="_blank" rel="noopener">Source: Google Hotels list</a> · checked '+esc(h.checked)+'</div></div></article>'}
function vTravel(){
  var F=D.flights||[],Hs=D.hotels||[],cov=D.meta.travelCoverage||{};
  if(!F.length&&!Hs.length)return '<section class="view"><div class="card empty">No flight or hotel data in this build.</div></section>';
  var byArea={};Hs.forEach(function(h){(byArea[h.area]=byArea[h.area]||[]).push(h)});
  var order=["airport","downtown","waterfront-adjacent","waterfront"];
  return '<section class="view"><div class="lede"><p>Four adults, Albuquerque to Seattle. Only <b>Alaska Airlines</b> flies it nonstop in the results (about 3 hours), so the question is mostly which date and which return time. Hotels are for the night before the cruise.</p></div>'+
   '<div class="warnb"><b>Published listings, not booking quotes.</b> '+esc(cov.flights||"")+'</div>'+
   '<h2 style="font-size:1.4rem">Flights</h2><div class="grid g2">'+F.map(flightCard).join("")+'</div>'+
   '<h2 style="font-size:1.4rem">Seattle hotels, night of Jun 11 2027</h2><div class="warnb">'+esc(cov.hotels||"")+'</div>'+
   order.filter(function(a){return byArea[a]}).map(function(a){return '<div class="eyebrow">'+esc(AREA[a])+'</div><div class="grid g3">'+byArea[a].map(hotelCard).join("")+'</div>'}).join("")+
   '<div class="card" style="padding:16px"><div class="eyebrow" style="margin-bottom:6px">Not captured yet</div><div class="note">'+(cov.notCaptured||[]).map(esc).join(" · ")+'</div></div></section>'}
"""
t = t.replace("/* ---------- router ---------- */", js + "\n/* ---------- router ---------- */", 1)
t = t.replace("excursions:vExcursions,", "excursions:vExcursions,travel:vTravel,", 1)
t = t.replace("Flights from ABQ, Seattle hotels, the map and the day-by-day builder arrive in later phases.", "Flights from ABQ and Seattle hotels are in the Flights &amp; hotels tab. The map and the day-by-day builder arrive in Phase 4.", 1)
open("template.html", "w").write(t)
print("patched")
