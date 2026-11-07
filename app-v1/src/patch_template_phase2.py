#!/usr/bin/env python3
"""Phase 2 template patch: adds the Excursions tab. Idempotent (skips if already applied)."""
t = open("template.html").read()
if "vExcursions" in t:
    print("already patched"); raise SystemExit

def rep(old, new, count=1):
    global t
    assert old in t, "missing anchor: " + old[:70]
    t = t.replace(old, new, count)

# ---- nav
rep('<a href="#ports">Ports &amp; glaciers</a>', '<a href="#ports">Ports &amp; glaciers</a><a href="#excursions">Excursions</a>')

# ---- css
CSS = """
/* excursions */
.lab{display:inline-flex;align-items:center;font-size:.74rem;font-weight:700;border-radius:999px;padding:2px 10px;white-space:nowrap}
.lab-ideal_parents{background:var(--ok-soft);color:var(--ok)} .lab-precautions{background:var(--warn-soft);color:var(--warn)}
.lab-brothers{background:var(--est-soft);color:var(--est)} .lab-everyone{background:var(--accent-soft);color:var(--accent)} .lab-not_recommended{background:var(--salmon-soft);color:var(--salmon)}
.meter{display:inline-flex;gap:3px;vertical-align:middle}
.meter i{width:10px;height:10px;border-radius:50%;background:var(--sunk);border:1px solid var(--line);display:inline-block}
.meter i.on{background:var(--accent);border-color:var(--accent)}
.ph.sm{aspect-ratio:21/8}
.xcard{overflow:hidden;display:flex;flex-direction:column;min-width:0}
.xcard .xh{padding:14px 16px 6px;display:flex;flex-direction:column;gap:8px}
.xcard h3{font-size:1.2rem}
.xrow{display:flex;flex-wrap:wrap;gap:6px 10px;align-items:center;font-size:.82rem;color:var(--muted)}
.xbox{margin:0 16px 10px;padding:9px 11px;border-radius:8px;background:var(--sunk);font-size:.86rem}
.xbox b{font-weight:600}
.xrisk{margin:0 16px 10px;padding:9px 11px;border-radius:8px;background:var(--salmon-soft);color:var(--ink);font-size:.86rem;border-left:4px solid var(--salmon)}
.xcmp{margin:0 16px 10px;font-size:.86rem}
.xo{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:3px 14px;padding:11px 16px;border-top:1px solid var(--line)}
.xo .t{min-width:0;display:flex;flex-direction:column;gap:2px}
.xo .t b{font-weight:600;font-size:.92rem}
.xo .p{text-align:right;display:flex;flex-direction:column;align-items:flex-end;gap:3px}
.xo .p .num{font-size:1.05rem;font-weight:500}
.xo .m{grid-column:1/-1;font-size:.78rem;color:var(--muted);display:flex;flex-wrap:wrap;gap:2px 12px}
.kind{display:inline-flex;font-size:.68rem;font-weight:700;letter-spacing:.04em;text-transform:uppercase;border-radius:4px;padding:1px 6px;width:fit-content;background:var(--sunk);color:var(--muted)}
.kind-cruise{background:var(--accent-soft);color:var(--accent)} .kind-free,.kind-diy{background:var(--ok-soft);color:var(--ok)}
.fit-no{color:var(--salmon);font-weight:600}
.warnb{background:var(--salmon-soft);border-left:4px solid var(--salmon);padding:10px 14px;border-radius:8px;font-size:.9rem}
"""
rep("@media (prefers-reduced-motion:no-preference)", CSS + "@media (prefers-reduced-motion:no-preference)")

# ---- default filter state
rep('var state=Object.assign({glacier:"all",line:"all",window:"june",sort:"total"},store.get("filters",{}));',
    'var state=Object.assign({glacier:"all",line:"all",window:"june",sort:"total",exPort:"all",exLabel:"all"},store.get("filters",{}));')

# ---- derived: usable shore time per excursion
rep("  D.sailings.forEach(function(s){\n    var it=IDX.itineraries[s.itinerary]",
"""  (D.excursions||[]).forEach(function(e){
    var wins=[];
    D.itineraries.forEach(function(it){var found=null;(it.days||[]).forEach(function(day){day.forEach(function(en){if(en.type==="port"&&e.ports.indexOf(en.place)>-1&&found===null){found=Math.max(0,hrs(en.arr,en.dep)-1.5)}})});if(found!==null)wins.push(found)});
    e._wins=wins;
  });
  D.sailings.forEach(function(s){
    var it=IDX.itineraries[s.itinerary]""")

# ---- port view tweaks
rep("Dock details here are planning notes from general port knowledge, not confirmed for 2027 sailings. Phase 2 adds excursions, walking distances and accessibility for each stop.",
    "Dock details here are planning notes from general port knowledge, not confirmed for 2027 sailings. Facts found while researching excursions are listed under each port with their source; see the Excursions tab for tours and prices.")
rep("+esc(p.notes)+'</p><div class=\"note\">'+n+' of '", "+esc(p.notes)+'</p>'+portExtra(p)+'<div class=\"note\">'+n+' of '")

# ---- overview note + watch-outs
rep("'<p class=\"note\">Excursions, flights from ABQ, Seattle hotels, the map and the day-by-day builder arrive in later phases.</p></div></section>';",
    "'<p class=\"note\">Excursion research is in the Excursions tab. Flights from ABQ, Seattle hotels, the map and the day-by-day builder arrive in later phases.</p></div>'+watchouts()+'</section>';")

# ---- new functions (inserted before router)
FN = r"""
/* ---------- excursions ---------- */
function portExtra(p){
  var L=p.logistics||[],ex=(D.excursions||[]).filter(function(e){return e.ports.indexOf(p.id)>-1}).length;
  return (L.length?'<ul class="note" style="margin:0;padding-left:18px">'+L.map(function(l){var s=IDX.sources[l.source];return '<li>'+esc(l.text)+(s?' <a href="'+esc(s.url)+'" target="_blank" rel="noopener">source</a>':'')+'</li>'}).join("")+'</ul>':'')+
    (ex?'<a href="#excursions" data-expo="'+esc(p.id)+'">'+ex+' excursion idea'+(ex>1?'s':'')+'</a>':'')}
function watchouts(){
  var r=(D.excursions||[]).filter(function(e){return e.risk});if(!r.length)return"";
  return '<div class="warnb"><b>Watch-outs from excursion research</b><ul style="margin:6px 0 0;padding-left:20px">'+r.map(function(e){return '<li><b>'+esc(e.name)+':</b> '+esc(e.risk.text)+'</li>'}).join("")+'</ul></div>'}
function priceTxt(o){
  if(o.pp==null)return '<span class="muted">No price shown</span>';
  if(o.pp===0)return '<span class="num">Free</span>';
  var v=(o.pp%1===0)?String(o.pp):o.pp.toFixed(2);
  return (o.from?'<span class="muted" style="font-size:.75rem">from </span>':'')+'<span class="num">$'+Number(v).toLocaleString("en-US",{minimumFractionDigits:(o.pp%1===0?0:2)})+'</span>'+(o.unit==="vehicle"?' <span class="muted" style="font-size:.75rem">/ vehicle</span>':o.unit==="charter"?' <span class="muted" style="font-size:.75rem">/ charter</span>':' <span class="muted" style="font-size:.75rem">/ person</span>')}
var WC={accessible:"Wheelchair accessible (per page)",limited:"Limited accessibility (per page)",ambulatory:"Ambulatory accessible: collapsible wheelchairs OK, no scooters",no:"Not accessible (per page)",not_stated:"Accessibility not stated"};
var KRANK={cruise:0,independent:1,reseller:2,diy:3,free:4};
function meter(n){var h="";for(var i=1;i<=5;i++)h+='<i'+(i<=n?' class="on"':'')+'></i>';return '<span class="meter" role="img" aria-label="Exertion '+n+' of 5">'+h+'</span>'}
function fitTxt(o,e){
  if(o.hours==null||!e._wins.length)return"";
  var n=e._wins.filter(function(w){return w>=o.hours}).length,tot=e._wins.length;
  return n===0?'<span class="fit-no">Too long for every route (needs '+o.hours+' h of '+Math.max.apply(null,e._wins).toFixed(1)+' h best case)</span>':'<span>Fits '+n+' of '+tot+' routes</span>'}
function cmpLine(e){
  var c=[],ind=[];e.offers.forEach(function(o){if(o.pp==null||o.pp===0||o.unit!=="pp")return;if(o.kind==="cruise")c.push(o.pp);else if(o.kind==="independent"||o.kind==="reseller")ind.push(o.pp)});
  if(!c.length||!ind.length)return"";
  var a=Math.min.apply(null,c),b=Math.min.apply(null,ind);
  return '<div class="xcmp"><b>Option A vs B:</b> lowest cruise-line price $'+a.toFixed(0)+' vs lowest independent $'+b.toFixed(0)+' per person'+(b<a?' (about $'+Math.round((a-b)*4)+' less for four if the tours match)':a<b?' (the cruise-line option is lower)':'')+'. <span class="muted">Not like-for-like unless the inclusions match.</span></div>'}
function offerHtml(o,e){
  var kind=D.meta.offerKinds[o.kind]||o.kind,wc=o.wheelchair||"not_stated";
  return '<div class="xo"><div class="t"><span class="kind kind-'+esc(o.kind)+'">'+esc(kind)+'</span><b>'+esc(o.title)+'</b><span class="note">'+esc(o.provider)+(o.line?'':'')+'</span></div>'+
   '<div class="p">'+priceTxt(o)+stTag(o.status)+'</div>'+
   '<div class="m">'+(o.hours!=null?'<span>'+o.hours+' h</span>':'')+(o.level?'<span>Line rating: '+esc(o.level)+'</span>':'')+'<span>'+esc(WC[wc]||WC.not_stated)+'</span>'+(fitTxt(o,e)?fitTxt(o,e):'')+'</div>'+
   (o.note?'<div class="m"><span>'+esc(o.note)+'</span></div>':'')+
   '<div class="m"><span>Cancellation: '+esc(o.cancel||"not stated on the page read")+'</span>'+(o.url?'<a href="'+esc(o.url)+'" target="_blank" rel="noopener">Source / booking page</a>':'<span>No source link (planning note)</span>')+'<span>Checked '+esc(o.checked)+'</span></div></div>'}
function xcard(e,i){
  var pl=IDX.places[e.photoPlace]||{},ph=(i%2&&pl.photo2)?pl.photo2:pl.photo;
  var offers=e.offers.slice().sort(function(a,b){return (KRANK[a.kind]-KRANK[b.kind])});
  var grp={parents:"Parents",brothers:"Brothers",family:"Whole family"}[e.group]||"";
  return '<article class="card xcard" id="x-'+esc(e.id)+'">'+(function(){var h=photo(ph,pl.short||pl.name||'');return h.replace('class="ph"','class="ph sm"')})()+
   '<div class="xh"><h3>'+esc(e.name)+'</h3><div class="xrow"><span class="lab lab-'+esc(e.label)+'">'+esc(D.meta.labels[e.label])+'</span>'+(grp?'<span class="pill">Suggested: '+grp+'</span>':'')+'<span>Exertion '+meter(e.exertion)+'</span><span>Weather sensitivity: '+esc(e.weather)+'</span></div>'+
   '<p style="margin:0;font-size:.92rem">'+esc(e.blurb)+'</p></div>'+
   (e.risk?'<div class="xrisk"><b>Operating risk ('+esc(e.risk.level)+'):</b> '+esc(e.risk.text)+(IDX.sources[e.risk.source]?' <a href="'+esc(IDX.sources[e.risk.source].url)+'" target="_blank" rel="noopener">source</a>':'')+'</div>':'')+
   '<div class="xbox"><b>Mobility:</b> '+esc(e.mobility)+'<div class="note" style="margin-top:4px">Exertion score is '+esc(e.exertionBasis)+'. Low exertion is not confirmed accessibility.</div></div>'+
   (e.caveat?'<div class="xcmp"><b>Note:</b> '+esc(e.caveat)+'</div>':'')+cmpLine(e)+
   '<div>'+offers.map(function(o){return offerHtml(o,e)}).join("")+'</div></article>'}
function vExcursions(){
  var ex=D.excursions||[];
  if(!ex.length)return '<section class="view"><div class="card empty">No excursion data in this build.</div></section>';
  var withEx=D.places.filter(function(p){return ex.some(function(e){return e.port===p.id})});
  var labs=[["all","All"]].concat(Object.keys(D.meta.labels).filter(function(k){return ex.some(function(e){return e.label===k})}).map(function(k){return [k,D.meta.labels[k]]}));
  var cov=D.meta.excursionCoverage||{};
  var list=ex.filter(function(e){return (state.exPort==="all"||e.port===state.exPort)&&(state.exLabel==="all"||e.label===state.exLabel)});
  var body="";
  withEx.forEach(function(p){
    var xs=list.filter(function(e){return e.port===p.id});if(!xs.length)return;
    var w=xs[0]._wins,sum=w.length?'Usable shore time on the '+w.length+' route'+(w.length>1?'s':'')+' that stop here: '+Math.min.apply(null,w).toFixed(1)+' to '+Math.max.apply(null,w).toFixed(1)+' h':'Onboard scenic cruising: no going ashore';
    body+='<h2 style="font-size:1.4rem">'+esc(p.name)+'</h2><div class="note" style="margin-top:-12px">'+esc(sum)+(p.id==="ketchikan"?' (Norwegian calls at Ward Cove add a shuttle transfer)':'')+'</div><div class="grid g2">'+xs.map(function(e,i){return xcard(e,i)}).join("")+'</div>'});
  var nOff=0;ex.forEach(function(e){nOff+=e.offers.length});
  return '<section class="view"><div class="lede"><p>Each experience shows <b>Option A</b> (what cruise lines sell) and <b>Option B</b> (the operator direct or an independent reseller) side by side, so the family can see what a tour really costs. '+ex.length+' experiences, '+nOff+' priced or sourced options, checked '+fmtD(cov.checked||D.meta.updated,{month:"long",day:"numeric",year:"numeric"})+'.</p></div>'+
   '<div class="warnb"><b>These are published prices, not quotes.</b> '+esc(cov.summary||"")+' Cruise-line prices were read only for Princess, Carnival and Norwegian; the other lines are listed as not captured (see Sources). "Fits" compares each tour with the usable shore time (scheduled hours minus 1.5 h) on every route that stops there.</div>'+
   '<div class="toolbar"><label class="sel" for="f-export">Port <select id="f-export" data-f="exPort"><option value="all">All ports</option>'+withEx.map(function(p){return '<option value="'+p.id+'"'+(state.exPort===p.id?" selected":"")+'>'+esc(p.short||p.name)+'</option>'}).join("")+'</select></label>'+
   '<div class="chips" role="group" aria-label="Suitability">'+labs.map(function(o){return '<button class="chip" data-f="exLabel" data-v="'+esc(o[0])+'" aria-pressed="'+(state.exLabel===o[0])+'">'+esc(o[1])+'</button>'}).join("")+'</div></div>'+
   (body||'<div class="card empty">No excursions match these filters.</div>')+'</section>';
}
"""
rep("/* ---------- router ---------- */", FN + "\n/* ---------- router ---------- */")
rep("var VIEWS={overview:vOverview,sailings:vSailings,itineraries:vItins,ports:vPorts,lines:vLines,sources:vSources};",
    "var VIEWS={overview:vOverview,sailings:vSailings,itineraries:vItins,ports:vPorts,excursions:vExcursions,lines:vLines,sources:vSources};")

# ---- click handler for port links
rep('document.addEventListener("click",function(e){\n',
    'document.addEventListener("click",function(e){\n  var xo=e.target.closest("[data-expo]");if(xo){state.exPort=xo.getAttribute("data-expo");if(state.exPort==="ketchikan_wc")state.exPort="ketchikan";state.exLabel="all";store.set("filters",state);if(location.hash==="#excursions"){e.preventDefault();render()}return}\n',1)

# ---- sources view: coverage card
rep("'<h2 style=\"font-size:1.35rem\">Cruise price pages</h2>",
    "excursionCov()+'<h2 style=\"font-size:1.35rem\">Cruise price pages</h2>")
rep("function vSources(){",
"""function excursionCov(){
  var c=D.meta.excursionCoverage;if(!c)return"";
  function dl(o){return Object.keys(o).map(function(k){return '<li><b>'+esc((IDX.lines[k]&&IDX.lines[k].name)||k)+':</b> '+esc(o[k])+'</li>'}).join("")}
  return '<div class="card" style="padding:16px"><div class="eyebrow">Excursion research coverage ('+esc(c.checked)+')</div><p style="margin:8px 0 0">'+esc(c.summary)+'</p>'+
   '<h3 style="font-size:1rem;margin:12px 0 4px">Cruise-line excursion prices captured</h3><ul style="margin:0;padding-left:20px">'+dl(c.linesWithCruiseExcursionPrices)+'</ul>'+
   '<h3 style="font-size:1rem;margin:12px 0 4px">Not captured</h3><ul style="margin:0;padding-left:20px">'+dl(c.linesNotCaptured)+'</ul>'+
   '<h3 style="font-size:1rem;margin:12px 0 4px">Pages that blocked or failed</h3><ul style="margin:0;padding-left:20px">'+c.operatorPagesBlocked.map(function(x){return '<li>'+esc(x)+'</li>'}).join("")+'</ul>'+
   '<h3 style="font-size:1rem;margin:12px 0 4px">Known gaps</h3><ul style="margin:0;padding-left:20px">'+c.gaps.map(function(x){return '<li>'+esc(x)+'</li>'}).join("")+'</ul>'+
   '<h3 style="font-size:1rem;margin:12px 0 4px">What is subjective</h3><ul style="margin:0;padding-left:20px">'+c.subjectiveFields.map(function(x){return '<li>'+esc(x)+'</li>'}).join("")+'</ul></div>'}
function vSources(){""")

# ---- touch targets: chips and selects at least 44px tall
rep("border-radius:999px;padding:7px 12px;min-height:38px;cursor:pointer","border-radius:999px;padding:8px 14px;min-height:44px;cursor:pointer")
rep("padding:8px 10px;min-height:40px;border-radius:8px","padding:8px 10px;min-height:44px;border-radius:8px")
open("template.html", "w").write(t)
print("patched")
