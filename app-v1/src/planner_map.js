/* ===================== Phase 4: map ===================== */
var LEFT={ketchikan_wc:1,icy_strait:1,sea_p91:1,sitka:1,glacier_bay:1,hubbard:1,victoria:1},MV=null,MAPDEF={x:-80,y:10,w:1280,h:1350};
var JUMPS=[["all","Whole route",null,null,null],["seattle","Seattle",47.53,-122.33,30],["victoria","Victoria",48.48,-123.42,28],["ketchikan","Ketchikan & Misty Fjords",55.45,-131.2,90],
  ["juneau","Juneau",58.36,-134.52,30],["tracy","Tracy & Endicott Arms",57.7,-133.3,80],["skagway","Skagway & White Pass",59.6,-135.1,45],["icy","Icy Strait & Glacier Bay",58.6,-136.3,110],["sitka","Sitka",57.06,-135.33,14],["hubbard","Hubbard Glacier",59.8,-139.2,110]];
function mapLayers(){return Object.assign({route:true,all:false,spots:true,easy:false,hotels:true,mine:true},store.get("mapL",{}))}
function miles(a,b,c,d){var R=3958.8,t=Math.PI/180,x=Math.sin((c-a)*t/2),y=Math.sin((d-b)*t/2),h=x*x+Math.cos(a*t)*Math.cos(c*t)*y*y;return 2*R*Math.asin(Math.sqrt(h))}
function nearPort(pt){var pl=IDX.places[pt.place];return pl&&miles(pl.lat,pl.lng,pt.lat,pt.lng)<1.2}
function poiExps(id){return (D.excursions||[]).filter(function(e){return e.poi===id})}
function easyPoi(id){return poiExps(id).some(function(e){return e.label==="ideal_parents"||e.label==="everyone"})}
function vMap(){
  var L=mapLayers(),p=AP(),s=IDX.sail[p.sailing];
  var chips=[["route","Your cruise route"],["all","All routes"],["spots","Excursion spots"],["easy","Easy for parents only"],["mine","Your activities"],["hotels","Seattle hotels"]].map(function(c){return '<button class="chip" data-ml="'+c[0]+'" aria-pressed="'+(!!L[c[0]])+'">'+c[1]+'</button>'}).join("");
  var groups=[["Ports","port"],["Glaciers & scenic","scenic"],["Seattle","terminal"]];
  var plist=groups.map(function(g){return '<div><div class="eyebrow">'+g[0]+'</div><div class="plist">'+D.places.filter(function(x){return x.kind===g[1]||(g[1]==="terminal"&&x.kind==="airport")}).map(function(x){return '<button class="linkbtn" data-mk="place:'+esc(x.id)+'">'+esc(x.short)+'</button>'}).join("")+'</div></div>'}).join("")+
   '<div><div class="eyebrow">Excursion spots</div><div class="plist">'+(D.pois||[]).map(function(x){return '<button class="linkbtn" data-mk="poi:'+esc(x.id)+'">'+esc(x.name)+'</button>'}).join("")+'</div></div>'+
   '<div><div class="eyebrow">Hotels</div><div class="plist">'+(D.hotels||[]).map(function(x){return '<button class="linkbtn" data-mk="hotel:'+esc(x.id)+'">'+esc(x.name)+'</button>'}).join("")+'</div></div>';
  return '<section class="view"><div class="lede"><p>Your cruise is <b>'+esc(sailLabel(s))+'</b>. Drag to move, pinch or use + and − to zoom, and tap a pin for tours, times and distances.</p></div>'+
   '<div class="toolbar"><div class="chips" role="group" aria-label="Layers">'+chips+'</div><label class="sel" for="map-jump">Go to <select id="map-jump" data-mj="1">'+JUMPS.map(function(j){return '<option value="'+j[0]+'">'+esc(j[1])+'</option>'}).join("")+'</select></label></div>'+
   '<div class="mapwrap"><div class="mapbox"><svg id="amap" class="amap" viewBox="'+[MAPDEF.x,MAPDEF.y,MAPDEF.w,MAPDEF.h].join(" ")+'" role="application" aria-label="Map of the cruise region"><rect x="-500" y="-500" width="2600" height="2700" class="sea"/><path class="land" d="'+COAST.land+'"/><path class="border" d="'+COAST.border+'" vector-effect="non-scaling-stroke"/><g id="mapdyn"></g></svg>'+
   '<div class="mapctl"><button data-mz="in" aria-label="Zoom in">+</button><button data-mz="out" aria-label="Zoom out">−</button><button data-mz="reset" aria-label="Show everything">⤢</button></div>'+
   '<div class="mapkey"><span><i class="k-rt"></i>route (schematic)</span><span><i class="k-port"></i>port</span><span><i class="k-sc"></i>glacier</span><span><i class="k-poi"></i>tour spot</span><span><i class="k-ht"></i>hotel</span></div></div>'+
   '<aside class="card mappanel" id="mappanel" aria-live="polite">'+mapPanel(ui.mapSel)+'</aside></div>'+
   '<p class="note">Coastline from Natural Earth (generalized; piers and small coves are not shown). Route lines follow common channels between scheduled stops; they are not the ship’s actual track. Pins marked approximate are placed from the address or general location.</p>'+
   '<details class="card" style="padding:12px 16px"><summary>All places as a list</summary><div class="plists">'+plist+'</div></details></section>'}
function mapInit(){
  var svg=document.getElementById("amap");if(!svg)return;
  if(!MV)MV=Object.assign({},MAPDEF);
  if(ui.mapFocus){focusOn(ui.mapFocus);ui.mapSel=ui.mapFocus;ui.mapFocus=null;var pn=document.getElementById("mappanel");if(pn)pn.innerHTML=mapPanel(ui.mapSel)}
  applyMV();
  var pts={},start=null,down=null,moved=false;
  function sp(e){var pt=svg.createSVGPoint();pt.x=e.clientX;pt.y=e.clientY;return pt.matrixTransform(svg.getScreenCTM().inverse())}
  function k(){var r=svg.getBoundingClientRect();return Math.max(MV.w/r.width,MV.h/r.height)}
  svg.addEventListener("pointerdown",function(e){pts[e.pointerId]={x:e.clientX,y:e.clientY};down=e.target.closest&&e.target.closest("[data-mk]");moved=false;try{svg.setPointerCapture(e.pointerId)}catch(x){}start=Object.keys(pts).length===2?pinchState():null});
  function pinchState(){var a=Object.keys(pts).map(function(i){return pts[i]});return {d:Math.hypot(a[0].x-a[1].x,a[0].y-a[1].y),mv:Object.assign({},MV),mid:sp({clientX:(a[0].x+a[1].x)/2,clientY:(a[0].y+a[1].y)/2})}}
  svg.addEventListener("pointermove",function(e){var q=pts[e.pointerId];if(!q)return;var ids=Object.keys(pts);
    if(ids.length===1){var dx=e.clientX-q.x,dy=e.clientY-q.y;if(Math.abs(dx)+Math.abs(dy)>3)moved=true;if(moved){var kk=k();MV.x-=dx*kk;MV.y-=dy*kk;q.x=e.clientX;q.y=e.clientY;applyMV()}}
    else if(ids.length===2&&start){q.x=e.clientX;q.y=e.clientY;moved=true;var a=ids.map(function(i){return pts[i]}),d=Math.hypot(a[0].x-a[1].x,a[0].y-a[1].y);if(d>0){var f=start.d/d;MV=Object.assign({},start.mv);zoomAt(f,start.mid.x,start.mid.y)}}});
  function up(e){delete pts[e.pointerId];if(Object.keys(pts).length<2)start=null;if(!moved&&down&&e.type==="pointerup"){selectMk(down.getAttribute("data-mk"))}down=null}
  svg.addEventListener("pointerup",up);svg.addEventListener("pointercancel",up);
  svg.addEventListener("wheel",function(e){e.preventDefault();var c=sp(e);zoomAt(e.deltaY>0?1.2:1/1.2,c.x,c.y)},{passive:false});
  svg.addEventListener("keydown",function(e){var m=e.target.closest&&e.target.closest("[data-mk]");if(m&&(e.key==="Enter"||e.key===" ")){e.preventDefault();selectMk(m.getAttribute("data-mk"))}});
}
function zoomAt(f,cx,cy){var nw=Math.max(4,Math.min(1500,MV.w*f));f=nw/MV.w;MV.x=cx-(cx-MV.x)*f;MV.y=cy-(cy-MV.y)*f;MV.w*=f;MV.h*=f;applyMV()}
var mvRaf=0;
function applyMV(){MV.w=Math.min(MV.w,1500);MV.h=Math.min(MV.h,1800);MV.x=Math.max(-450,Math.min(1550-MV.w,MV.x));MV.y=Math.max(-450,Math.min(1820-MV.h,MV.y));var svg=document.getElementById("amap");if(!svg)return;svg.setAttribute("viewBox",[MV.x,MV.y,MV.w,MV.h].map(function(v){return v.toFixed(2)}).join(" "));if(!mvRaf)mvRaf=requestAnimationFrame(function(){mvRaf=0;drawDyn()})}
function mkLL(id){var t=id.split(":"),o=t[0]==="place"?IDX.places[t[1]]:t[0]==="poi"?IDX.poi[t[1]]:IDX.hotel[t[1]];return o&&o.lat!=null?{lat:o.lat,lng:o.lng,o:o,t:t[0]}:null}
function focusOn(id,w){var m=mkLL(id);if(!m)return;var q=prj(m.lat,m.lng);var W=w||(m.t==="hotel"?10:m.t==="poi"?40:m.o.kind==="scenic"?110:m.o.kind==="terminal"||m.o.kind==="airport"?28:36);var svg=document.getElementById("amap"),r=svg?svg.getBoundingClientRect():{width:4,height:3};var H=W*(r.height/Math.max(1,r.width));MV={x:q[0]-W/2,y:q[1]-H/2,w:W,h:H}}
function selectMk(id){ui.mapSel=id;var pn=document.getElementById("mappanel");if(pn){pn.innerHTML=mapPanel(id);if(window.innerWidth<900)pn.scrollIntoView({block:"nearest",behavior:"smooth"})}drawDyn()}
function drawDyn(){
  var g=document.getElementById("mapdyn"),svg=document.getElementById("amap");if(!g||!svg)return;
  var r=svg.getBoundingClientRect(),k=Math.max(MV.w/Math.max(1,r.width),MV.h/Math.max(1,r.height)),L=mapLayers(),p=AP(),s=IDX.sail[p.sailing],h="";
  var fs=12*k,rr=6*k,hitK=(window.matchMedia&&matchMedia('(pointer:coarse)').matches)?20*k:0;
  if(L.all)D.itineraries.forEach(function(it){if(it.mapLine&&it!==s._it)h+='<polyline class="rt-all" points="'+poly(it.mapLine)+'" vector-effect="non-scaling-stroke"/>'});
  if(L.route&&s._it.mapLine)h+='<polyline class="rt-on" points="'+poly(s._it.mapLine)+'" vector-effect="non-scaling-stroke"/>';
  var on={};(s._it.days||[]).forEach(function(d){d.forEach(function(e){if(e.place)on[e.place]=1})});(s._it.ports||[]).forEach(function(x){on[x]=1});
  var mine={};if(L.mine)p.acts.forEach(function(a){if(actState(p,a,s)==="ok"){var e=IDX.exc[a.x];if(e)mine[e.poi]=1}});
  function lab(x,y,t,cls,left){return '<text class="ml '+(cls||"")+'"'+(left?' text-anchor="end"':'')+' x="'+(left?x-rr*1.4:x+rr*1.4).toFixed(2)+'" y="'+(y+fs*0.35).toFixed(2)+'" style="font-size:'+fs.toFixed(2)+'px;stroke-width:'+(3*k).toFixed(2)+'px">'+esc(t)+'</text>'}
  if(L.hotels)(D.hotels||[]).forEach(function(ht){var q=prj(ht.lat,ht.lng),sel=ui.mapSel==="hotel:"+ht.id,me=p.hotel.id===ht.id;
    h+='<g class="mk" data-mk="hotel:'+esc(ht.id)+'" tabindex="0" role="button" aria-label="'+esc(ht.name)+'"><circle class="hit" cx="'+q[0].toFixed(2)+'" cy="'+q[1].toFixed(2)+'" r="'+Math.max(rr*2,hitK).toFixed(2)+'"/><rect class="m-ht'+(me?' me':'')+(sel?' sel':'')+'" x="'+(q[0]-rr*.7).toFixed(2)+'" y="'+(q[1]-rr*.7).toFixed(2)+'" width="'+(rr*1.4).toFixed(2)+'" height="'+(rr*1.4).toFixed(2)+'"/>'+(k<0.06||sel||me?lab(q[0],q[1],ht.name,"sm",q[0]>850):'')+'</g>'});
  if(L.spots)(D.pois||[]).forEach(function(pt){if(L.easy&&!easyPoi(pt.id)&&!mine[pt.id])return;var q=prj(pt.lat,pt.lng),sel=ui.mapSel==="poi:"+pt.id;
    h+='<g class="mk" data-mk="poi:'+esc(pt.id)+'" tabindex="0" role="button" aria-label="'+esc(pt.name)+'"><circle class="hit" cx="'+q[0].toFixed(2)+'" cy="'+q[1].toFixed(2)+'" r="'+Math.max(rr*2,hitK).toFixed(2)+'"/>'+(mine[pt.id]?'<circle class="m-mine" cx="'+q[0].toFixed(2)+'" cy="'+q[1].toFixed(2)+'" r="'+(rr*1.5).toFixed(2)+'"/>':'')+'<circle class="m-poi'+(sel?' sel':'')+'" cx="'+q[0].toFixed(2)+'" cy="'+q[1].toFixed(2)+'" r="'+(rr*.75).toFixed(2)+'"/>'+((k<0.12&&(k<0.03||!nearPort(pt)))||sel?lab(q[0],q[1],pt.name,"sm"):'')+'</g>'});
  D.places.forEach(function(pl){var q=prj(pl.lat,pl.lng),sel=ui.mapSel==="place:"+pl.id,cls=pl.kind==="scenic"?"m-sc":pl.kind==="port"?"m-port":"m-term",onr=on[pl.id];
    var shape=pl.kind==="scenic"?'<path class="'+cls+(sel?' sel':'')+(onr?' on':'')+'" d="M'+q[0].toFixed(2)+' '+(q[1]-rr*1.2).toFixed(2)+'l'+(rr*1.2).toFixed(2)+' '+(rr*1.2).toFixed(2)+'l'+(-rr*1.2).toFixed(2)+' '+(rr*1.2).toFixed(2)+'l'+(-rr*1.2).toFixed(2)+' '+(-rr*1.2).toFixed(2)+'z"/>':
      '<circle class="'+cls+(sel?' sel':'')+(onr?' on':'')+'" cx="'+q[0].toFixed(2)+'" cy="'+q[1].toFixed(2)+'" r="'+rr.toFixed(2)+'"/>';
    var showL=pl.kind==="port"||(pl.kind==="scenic"&&(k<1.2||onr))||(pl.kind!=="port"&&pl.kind!=="scenic"&&k<0.12)||sel;
    h+='<g class="mk" data-mk="place:'+esc(pl.id)+'" tabindex="0" role="button" aria-label="'+esc(pl.name)+'"><circle class="hit" cx="'+q[0].toFixed(2)+'" cy="'+q[1].toFixed(2)+'" r="'+Math.max(rr*2.2,hitK).toFixed(2)+'"/>'+shape+(showL?lab(q[0],q[1],pl.short.replace("Seattle · ",""),onr?"on":"",LEFT[pl.id]):'')+'</g>'});
  g.innerHTML=h}
function expLine(e,s){var offs=e.offers.filter(function(o){return o.pp!=null&&offerOK(o,s)&&(o.hours!=null||o.kind==="free")}),lo=offs.length?Math.min.apply(null,offs.map(function(o){return o.pp})):null;
  return '<li><b>'+esc(e.name)+'</b> <span class="lab lab-'+esc(e.label)+'">'+esc(D.meta.labels[e.label])+'</span><span class="note"> exertion '+e.exertion+'/5 · '+(lo==null?'price not captured':lo===0?'free option':'from '+money(lo)+' pp')+'</span></li>'}
function mapPanel(id){
  var p=AP(),s=IDX.sail[p.sailing];
  if(!id)return '<div class="eyebrow">Tap a pin</div><p class="note">Ports show your cruise’s times there and the tours on offer; tour spots show the straight-line distance from the dock; hotels show distances to the pier and airport.</p><p class="note">Your activities are ringed. Use “Easy for parents only” to hide spots whose tours are all higher-exertion.</p>';
  var m=mkLL(id);if(!m)return"";var o=m.o,h="";
  if(m.t==="place"){
    var stops=stopsOf(s).filter(function(x){return x.place===o.id}),X=(D.excursions||[]).filter(function(e){return e.ports.indexOf(o.id)>-1});
    h=(o.photo?photo(o.photo,o.short).replace('class="ph"','class="ph sm"'):'')+'<div class="eyebrow">'+esc({port:"Port",scenic:"Scenic cruising",terminal:"Cruise terminal",airport:"Airport"}[o.kind]||o.kind)+'</div><h3>'+esc(o.name)+'</h3>'+(o.dock?'<span class="pill">'+esc(o.dock)+'</span>':'')+
     '<p class="note">'+esc(o.notes||"")+'</p>'+
     (stops.length?stops.map(function(st){return '<div class="xbox"><b>On your cruise:</b> '+dlong(st.date)+(st.arr?', '+t12(st.arr)+(st.dep?' – '+t12(st.dep):''):st.dep?', sails '+t12(st.dep):'')+(st.usable!=null?' · '+durTxt(st.usable)+' usable':'')+'</div>'}).join(""):(o.kind==="port"||o.kind==="scenic")?'<div class="note">Not on your cruise ('+esc(s._ship.name)+').</div>':'')+
     ((o.logistics||[]).length?'<ul class="note">'+o.logistics.map(function(l){var so=IDX.sources[l.source];return '<li>'+esc(l.text)+(so?' '+linkSrc(so.url,"source"):'')+'</li>'}).join("")+'</ul>':'')+
     (X.length&&o.kind==="port"?'<div class="eyebrow">Tours here</div><ul class="xl">'+X.map(function(e){return expLine(e,s)}).join("")+'</ul>':'')+
     '<div class="row-links">'+(o.kind==="port"&&stops.length?'<button class="btn sm" data-pa="plan-port" data-v="'+esc(o.id)+'">Plan this day</button>':'')+(X.length&&o.kind==="port"?'<a href="#excursions" data-expo="'+esc(o.id)+'">All tour details</a>':'')+'</div>'}
  else if(m.t==="poi"){
    var port=IDX.places[o.place],d=port?miles(port.lat,port.lng,o.lat,o.lng):null,X2=poiExps(o.id);
    h='<div class="eyebrow">Tour spot · '+esc(port?port.short:"")+'</div><h3>'+esc(o.name)+'</h3><p class="note">'+esc(o.note||"")+'</p>'+
     (d!=null?'<div class="xbox"><b>'+d.toFixed(1)+' mi</b> straight-line from the '+esc(port.short)+' cruise dock'+(d>1.5?' (road distance is longer; transport needed)':' (walkable for some; Mom’s limit is about 2 mi a day)')+'.</div>':'')+
     '<p class="note">'+(o.basis==="wikipedia"?'Location from Wikipedia.':'Approximate location.')+'</p>'+
     (X2.length?'<div class="eyebrow">Tours here</div><ul class="xl">'+X2.map(function(e){return expLine(e,s)}).join("")+'</ul>':'')+
     '<div class="row-links">'+(stopsOf(s).some(function(x){return x.place===o.place||(o.place==="ketchikan"&&x.place==="ketchikan_wc")})?'<button class="btn sm" data-pa="plan-port" data-v="'+esc(o.place)+'">Plan this day</button>':'<span class="note">Your cruise does not stop at '+esc(port?port.short:"")+'.</span>')+'</div>'}
  else{
    var term=IDX.places[s._line.terminal],dt2=miles(term.lat,term.lng,o.lat,o.lng),da=miles(IDX.places.sea_airport.lat,IDX.places.sea_airport.lng,o.lat,o.lng);
    h='<div class="eyebrow">Hotel · '+esc(AREA[o.area]||o.area)+'</div><h3>'+esc(o.name)+'</h3><div class="xrow"><span class="pill">★ '+o.reviewScore+' · '+o.reviewCount.toLocaleString("en-US")+'</span>'+(o.accessibilityListed?'<span class="lab lab-everyone">“Accessible” listed</span>':'')+'</div>'+
     '<p><span class="num big2">'+money(o.rate.perRoomNight)+'</span> <span class="note">per room, night of '+dlong(o.stayDate)+' '+stTag(o.rate.status)+'</span></p>'+
     '<div class="xbox">About <b>'+dt2.toFixed(1)+' mi</b> straight-line to '+esc(term.short)+' (your cruise) and <b>'+da.toFixed(1)+' mi</b> to SEA airport. Road distances are longer.</div>'+
     '<p class="note">'+esc(o.transfers||"")+' Approximate location.</p><div class="row-links">'+(p.hotel.id===o.id?'<span class="pill">In your plan</span>':'<button class="btn sm" data-pa="hotel" data-v="'+esc(o.id)+'">Use in my plan</button>')+linkSrc(o.url,"Google Hotels")+'</div>'}
  return h}

/* ===================== Phase 4: exports ===================== */
function exportObj(){return {app:"alaska-2027-planner",kind:"plans",dataVersion:D.meta.version,exported:new Date().toISOString(),active:PL.active,plans:PL.list}}
function csvEsc(v){v=v==null?"":String(v);return /[",\n]/.test(v)?'"'+v.replace(/"/g,'""')+'"':v}
function planCSV(p){
  var s=IDX.sail[p.sailing],C=cost(p),R=[["Section","Date","Place / item","For","Amount (USD)","Status","Detail","Source"]];
  R.push(["Plan","",p.name+" · "+sailLabel(s)+" · "+s._line.name,"","","","Exported "+new Date().toISOString().slice(0,10)+", data "+D.meta.version,""]);
  C.items.forEach(function(i){R.push(["Cost","",i.label,i.who==="split"?"split":whoTxt(i.who),Math.round(i.amt*100)/100,(D.meta.statusDefinitions[i.status]||{label:i.status}).label,i.note,i.src||""])});
  C.miss.forEach(function(i){R.push(["Cost (missing)","",i.label,"","","Not captured",i.note||"",""])});
  R.push(["Total","","Trip total","All 4",Math.round(C.total),"","Per person "+Math.round(C.pp)+"; parents "+Math.round(C.parents)+"; brothers "+Math.round(C.brothers),""]);
  portStops(s).forEach(function(st){var L=lanes(p,st),seen={};["parents","brothers"].forEach(function(g){L[g].forEach(function(x){if(x.a.who==="family"&&seen[x.i])return;seen[x.i]=1;
    R.push(["Day "+(st.day+1),st.date,IDX.places[st.place].short+": "+x.e.name,whoTxt(x.a.who),offerCost(x.o,x.a.who),(D.meta.statusDefinitions[x.o.status]||{}).label||"",fmtMin(x.start)+"-"+fmtMin(x.end)+" · "+x.o.provider+" · "+x.o.title,x.o.url||""])})})});
  PL.list.forEach(function(x){var c=cost(x);R.push(["All plans","",x.name+" · "+sailLabel(IDX.sail[x.sailing]),"All 4",Math.round(c.total),"","Per person "+Math.round(c.pp),""])});
  return R.map(function(r){return r.map(csvEsc).join(",")}).join("\r\n")}

/* ---- Phase 5: cruise comparison CSVs (same rules as make_csv.py; keep the two in step) ---- */
function nf(x){return x==null?"":String(Math.round(x*100)/100)}
function glTxt(it){return it.glacier||"No glacier day"}
function cruiseCSVs(){
  var P=function(s,k){return s.prices[k]};
  var A=[["line","ship","itinerary","sailing_id","depart","return","weekday","nights","june_2027","glacier_or_scenic","alaska_ports","alaska_port_hours","usable_shore_hours","sea_days","terminal","interior_pp_usd","interior_status","oceanview_pp_usd","oceanview_status","balcony_pp_usd","balcony_status","suite_tier_pp_usd","suite_tier_status","two_cabin_fare_usd","two_cabin_fare_status","gratuity_pp_per_day_usd","gratuity_status","gratuities_4_travelers_usd","two_cabin_fare_plus_gratuities_usd","flags","price_basis","price_source_url","price_checked","note"]];
  D.sailings.slice().sort(function(a,b){var la=a._line.name,lb=b._line.name,sa=a._ship.name,sb=b._ship.name;return a.depart<b.depart?-1:a.depart>b.depart?1:la<lb?-1:la>lb?1:sa<sb?-1:sa>sb?1:0}).forEach(function(s){
    var it=s._it,ln=s._line,g=ln.gratuity||{},ps=s.priceSource||{};
    A.push([ln.name,s._ship.name,it.name,s.id,s.depart,s.return,it.weekday,s.nights,s._june?"Yes":"No",glTxt(it),it._akPorts.length,nf(it._ak),nf(it._use),it._sea,IDX.places[ln.terminal].name,
      nf(P(s,"interior").pp),P(s,"interior").status,nf(P(s,"oceanview").pp),P(s,"oceanview").status,nf(P(s,"balcony").pp),P(s,"balcony").status,nf(P(s,"miniSuite").pp),P(s,"miniSuite").status,
      nf(s._fare),s._fareStatus,nf(g.pp_day),g.status||"",nf(s._grat),nf(s._total),(s.flags||[]).join("; "),s.priceBasis||"",ps.url||"",ps.checked||"",s.note||""])});
  var B=[["line","qualifies_seattle_round_trip","ships","sailings_captured_may_to_july","june_sailings","june_sailings_with_two_cabin_fare","cheapest_june_two_cabin_fare_usd","cheapest_june_ship","cheapest_june_depart","cheapest_june_fare_status","cheapest_june_fare_plus_gratuities_usd","gratuity_pp_per_day_usd","gratuity_status","glacier_or_scenic_options_june","most_alaska_port_hours_june","terminal","final_payment_days_before_sailing","deposit_policy","payment_rules_status","fare_basis","included_in_fare","accessibility_note","price_source_url","price_checked","limitations"]];
  D.lines.forEach(function(ln){
    var sl=D.sailings.filter(function(s){return s._line.id===ln.id});if(!sl.length)return;
    var june=sl.filter(function(s){return s._june}),pool=june.length?june:sl,wf=june.filter(function(s){return s._fare!=null}),best=null;
    wf.forEach(function(s){if(!best||s._fare<best._fare||(s._fare===best._fare&&s.depart<best.depart))best=s});
    var uniq=function(a){var o={};a.forEach(function(x){o[x]=1});return Object.keys(o).sort()};
    var ships=uniq(pool.map(function(s){return s._ship.name})),glac=uniq(pool.map(function(s){return glTxt(s._it)}));
    var akh=june.map(function(s){return s._it._ak}).filter(function(v){return v!=null}),g=ln.gratuity||{},pay=ln.payment||{},lim=[];
    if(!june.length)lim.push("No June 2027 sailing captured.");
    else if(wf.length<june.length)lim.push("Two-cabin fare not captured for "+(june.length-wf.length)+" of "+june.length+" June sailings (interior or balcony price unavailable).");
    if(g.pp_day==null)lim.push("Gratuity rate not captured.");else if(g.status!=="verified")lim.push("Gratuity rate is "+g.status+" (planning estimate).");
    if(pool.some(function(s){return !s._it.days}))lim.push("Port arrival/departure times not captured, so days cannot be planned.");
    if(pay.status!=="verified")lim.push("Deposit and final-payment rules: "+(pay.status||"not captured")+".");
    B.push([ln.name,"Yes",ships.join("; "),sl.length,june.length,wf.length,best?nf(best._fare):"",best?best._ship.name:"",best?best.depart:"",best?best._fareStatus:"",best?nf(best._total):"",nf(g.pp_day),g.status||"",glac.join("; "),akh.length?nf(Math.max.apply(null,akh)):"",IDX.places[ln.terminal].name,pay.finalPaymentDays!=null?pay.finalPaymentDays:"",pay.deposit||"",pay.status||"",ln.fareBasis||"",ln.includes||"",ln.accessibility||"",best?best.priceSource.url:"",best?best.priceSource.checked:"",lim.join(" ")])});
  (D.linesReviewed||[]).forEach(function(x){var src=x.source?IDX.sources[x.source]:null,r=B[0].map(function(){return ""});r[0]=x.line;r[1]="No";r[B[0].indexOf("price_source_url")]=src?src.url:"";r[B[0].indexOf("price_checked")]=src?src.checked:"";r[B[0].indexOf("limitations")]=x.finding;B.push(r)});
  var T=function(R){return "﻿"+R.map(function(r){return r.map(csvEsc).join(",")}).join("\r\n")};
  return {sailings:T(A),lines:T(B)}}
function planHTML(p){
  var s=IDX.sail[p.sailing],C=cost(p),fl=flightFor(s),h=p.hotel.id&&IDX.hotel[p.hotel.id];
  var days=stopsOf(s).map(function(st){var pl=st.place?IDX.places[st.place]:null,head='<h3>Day '+(st.day+1)+' · '+dlong(st.date)+' · '+(st.type==="sea"?"At sea":esc(pl.name))+'</h3>';
    if(st.type!=="port")return head+'<p>'+(st.type==="embark"?'Ship sails '+t12(st.dep)+'.':st.type==="disembark"?'Arrive '+t12(st.arr)+'.':st.type==="scenic"?'Scenic cruising '+(st.arr?t12(st.arr)+'–'+t12(st.dep):'')+'.':'Day at sea.')+'</p>';
    var L=lanes(p,st);return head+'<p>In port '+t12(st.arr)+'–'+t12(st.dep)+'. Back aboard by '+fmtMin(st.allAboard)+'.</p>'+["parents","brothers"].map(function(g){return '<p><b>'+(g==="parents"?"Parents":"Brothers")+':</b> '+(L[g].length?L[g].map(function(x){return fmtMin(x.start)+'–'+fmtMin(x.end)+' '+esc(x.e.name)+' ('+esc(x.o.provider)+')'}).join('; '):'free time')+'</p>'}).join("")}).join("");
  var r=fl&&(fl.f.returns||[])[+p.flight.ret],o=fl&&(fl.f.outbound||[])[+p.flight.out];
  return '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+esc(p.name)+' · Alaska 2027</title><style>body{font:15px/1.5 Georgia,serif;max-width:760px;margin:24px auto;padding:0 16px;color:#12212b}h1{font-size:1.6rem;margin:0}h2{font-size:1.15rem;border-bottom:1px solid #cfdadb;padding-bottom:4px;margin-top:24px}h3{font-size:1rem;margin:16px 0 2px}p{margin:2px 0}table{border-collapse:collapse;width:100%;font-size:.9rem}td,th{border-bottom:1px solid #e3eaea;padding:5px 6px;text-align:left;vertical-align:top}.r{text-align:right}.n{color:#566871;font-size:.85rem}</style></head><body>'+
   '<h1>'+esc(p.name)+'</h1><p class="n">Alaska 2027 family plan · exported '+new Date().toLocaleDateString("en-US")+' · data '+esc(D.meta.version)+'. Prices change; recheck before booking.</p>'+
   '<h2>Cruise</h2><p><b>'+esc(s._ship.name)+'</b> ('+esc(s._line.name)+'), '+esc(s._it.name)+'. '+dlong(s.depart)+' – '+dlong(s.return)+' from '+esc(IDX.places[s._line.terminal].name)+'.</p><p>Brothers: '+esc(catName(p.cabins.brothers))+'. Parents: '+esc(catName(p.cabins.parents))+'.</p>'+
   (fl?'<h2>Flights</h2><p>Alaska Airlines nonstop. Out '+dlong(flightOutDate(s))+' '+(o?tm(o.dep)+' → '+tm(o.arr):'')+'. Back '+dlong(s.return)+' '+(r?tm(r.dep)+' → '+tm(r.arr):'')+'.'+(fl.proxy?' (These dates were not searched; times and fare assumed from other June dates.)':'')+'</p>':'')+
   (h?'<h2>Hotel</h2><p>'+esc(h.name)+', night of '+dlong(addDays(s.depart,-1))+', '+p.hotel.rooms+' room(s).</p>':'')+
   '<h2>Day by day</h2>'+days+
   '<h2>Costs for four</h2><table><tr><th>Item</th><th>For</th><th class="r">USD</th><th>Status</th></tr>'+C.items.map(function(i){return '<tr><td>'+esc(i.label)+'</td><td>'+esc(i.who==="split"?"split":whoTxt(i.who))+'</td><td class="r">'+money(i.amt)+'</td><td class="n">'+esc((D.meta.statusDefinitions[i.status]||{label:i.status}).label)+'</td></tr>'}).join("")+
   '<tr><th>Total</th><th></th><th class="r">'+money(C.total)+'</th><th></th></tr></table><p class="n">Per person '+money(C.pp)+' · parents '+money(C.parents)+' · brothers '+money(C.brothers)+'.</p>'+(p.notes?'<h2>Notes</h2><p>'+esc(p.notes)+'</p>':'')+'</body></html>'}
function inFrame(){try{return window.top!==window.self}catch(e){return true}}
function saveFile(name,text,mime){
  var cl=window.claude;
  if(cl&&typeof cl.use==="function"){cl.use("downloads").then(function(dl){if(!dl){blobSave(name,text,mime);return}
    dl.save({filename:name,data:text}).then(function(){toast("Saved "+name)},function(e){var c=e&&e.code;toast(c==="declined"?"Download cancelled.":c==="rate_limited"?"A download prompt is already open.":"Downloads are not available here. Use “Copy plans as text” instead.")})},function(){blobSave(name,text,mime)});return}
  blobSave(name,text,mime)}
function blobSave(name,text,mime){if(inFrame()){toast("Downloads are not available in this view. Use “Copy plans as text” instead.");return}
  try{var b=new Blob([text],{type:mime}),u=URL.createObjectURL(b),a=document.createElement("a");a.href=u;a.download=name;document.body.appendChild(a);a.click();setTimeout(function(){URL.revokeObjectURL(u);a.remove()},2000);toast("Downloading "+name)}catch(e){toast("Could not download; use Copy instead.")}}
function slug(t){return String(t).toLowerCase().replace(/[^a-z0-9]+/g,"-").replace(/^-|-$/g,"").slice(0,40)||"plan"}
function importText(t){
  var o;try{o=JSON.parse(t)}catch(e){toast("That text is not a plans file (JSON could not be read).");return}
  var arr=Array.isArray(o)?o:Array.isArray(o.plans)?o.plans:(o&&o.sailing?[o]:null);
  if(!arr||!arr.length){toast("No plans found in that file.");return}
  var n=0,first=null;arr.forEach(function(x){if(!x||!x.sailing||!IDX.sail[x.sailing])return;x=normPlan(JSON.parse(JSON.stringify(x)));if(!x.id)x.id=newId();
    var i=PL.list.findIndex(function(y){return y.id===x.id});if(i>-1)PL.list[i]=x;else PL.list.push(x);n++;if(!first)first=x.id});
  if(!n){toast("None of those plans match sailings in this planner.");return}
  PL.active=first;savePlans();toast("Imported "+n+" plan"+(n>1?"s":"")+".");rerender()}

/* ===================== Phase 4: events ===================== */
function rerender(){var y=window.scrollY;var v=(location.hash||"#overview").slice(1);if(!VIEWS[v])v="overview";document.getElementById("app").innerHTML=VIEWS[v]();afterRender(v);window.scrollTo(0,y)}
var pendingJump=null;
function afterRender(v){
  document.querySelectorAll(".ph img").forEach(function(img){if(img.complete&&img.naturalWidth)img.parentNode.classList.add("loaded")});
  if(v==="map")mapInit();
  if(pendingJump){var el=document.getElementById(pendingJump);pendingJump=null;if(el){el.scrollIntoView({block:"start"});window.scrollBy(0,-120)}}}
function setPath(p,path,val){var k=path.split("."),o=p;for(var i=0;i<k.length-1;i++){o[k[i]]=o[k[i]]||{};o=o[k[i]]}o[k[k.length-1]]=val}
function planPort(place){var p=AP(),s=IDX.sail[p.sailing];var st=portStops(s).filter(function(x){return x.place===place||(place==="ketchikan"&&x.place==="ketchikan_wc")||(place==="ketchikan_wc"&&x.place==="ketchikan")})[0];
  if(!st){toast(s._ship.name+" does not stop at "+IDX.places[place].short+".");return}
  ui.open[st.key]=true;pendingJump="d-"+st.key.replace("|","-");if(location.hash==="#plan")rerender();else location.hash="#plan"}
document.addEventListener("click",function(e){
  var j=e.target.closest("[data-jump]");if(j){e.preventDefault();var el=document.getElementById(j.getAttribute("data-jump"));if(el){el.scrollIntoView({block:"start"});window.scrollBy(0,-110)}return}
  var mz=e.target.closest("[data-mz]");if(mz){var a=mz.getAttribute("data-mz");if(a==="reset"){MV=Object.assign({},MAPDEF);applyMV()}else zoomAt(a==="in"?1/1.6:1.6,MV.x+MV.w/2,MV.y+MV.h/2);return}
  var ml=e.target.closest("[data-ml]");if(ml){var L=mapLayers(),k=ml.getAttribute("data-ml");L[k]=!L[k];store.set("mapL",L);ml.setAttribute("aria-pressed",String(L[k]));drawDyn();return}
  var mk=e.target.closest("button[data-mk]");if(mk){focusOn(mk.getAttribute("data-mk"));applyMV();selectMk(mk.getAttribute("data-mk"));var mb=document.getElementById("amap");if(mb)mb.scrollIntoView({block:"center"});return}
  var b=e.target.closest("[data-pa]");if(!b||b.tagName==="SELECT"||b.disabled)return;
  var pa=b.getAttribute("data-pa"),v=b.getAttribute("data-v"),p=AP();
  switch(pa){
    case "dup":var c=JSON.parse(JSON.stringify(p));c.id=newId();c.name=(p.name+" (copy)").slice(0,60);c.preset=null;PL.list.push(c);PL.active=c.id;touch(c);toast("Duplicated. You are now editing the copy.");break;
    case "del":ui.confirm="del";break;
    case "del-yes":PL.list=PL.list.filter(function(x){return x.id!==p.id});if(!PL.list.length)PL.list.push(blankPlan("My plan",p.sailing));PL.active=PL.list[0].id;ui.confirm=null;savePlans();toast("Plan deleted.");break;
    case "cancel":ui.confirm=null;break;
    case "cabin":p.cabins[b.getAttribute("data-g")]=v;touch(p);break;
    case "fare":p.flight.fare=v;touch(p);break;
    case "out":p.flight.out=+v;touch(p);break;
    case "ret":p.flight.ret=+v;touch(p);break;
    case "hotel":p.hotel.id=v||null;touch(p);if(location.hash==="#map"){var pn=document.getElementById("mappanel");if(pn)pn.innerHTML=mapPanel(ui.mapSel);drawDyn();return}break;
    case "add":p.acts.push({k:b.getAttribute("data-k"),x:b.getAttribute("data-x"),o:b.getAttribute("data-o"),who:b.getAttribute("data-who")});ui.open[b.getAttribute("data-k")]=true;touch(p);break;
    case "rm":p.acts.splice(+b.getAttribute("data-i"),1);touch(p);break;
    case "move":var a1=p.acts[+b.getAttribute("data-i")];if(a1)a1.k=b.getAttribute("data-k");touch(p);break;
    case "move-all":var s3=IDX.sail[p.sailing],moved=0;p.acts.forEach(function(a){if(actState(p,a,s3)!=="elsewhere")return;var e3=IDX.exc[a.x],pl3=a.k.split("|")[1];var t3=portStops(s3).filter(function(st){return st.place===pl3})[0]||portStops(s3).filter(function(st){return e3&&e3.ports.indexOf(st.place)>-1})[0];if(t3){a.k=t3.key;moved++}});touch(p);toast("Moved "+moved+" activit"+(moved===1?"y":"ies")+". Check the day plan for time conflicts.");break;
    case "fill":if(v==="clear"||p.acts.length){ui.confirm="fill:"+v;break}autoFill(p,v);touch(p);break;
    case "fill-yes":if(v==="clear")p.acts=[];else autoFill(p,v);ui.confirm=null;touch(p);toast(v==="clear"?"Activities cleared.":"Filled with "+D.meta.presets[v].label+" picks.");break;
    case "xf":ui.xf=v;break;
    case "open":PL.active=v;ui.confirm=null;savePlans();window.scrollTo(0,0);break;
    case "use-sail":p.sailing=v;touch(p);toast("“"+p.name+"” now uses "+sailLabel(IDX.sail[v])+".");if(location.hash!=="#plan"){location.hash="#plan";return}break;
    case "w-reset":store.set("weights",{});break;
    case "cmp-clear":ui.cmp=[];store.set("cmp",[]);break;
    case "map-x":var ex=IDX.exc[v];ui.mapFocus=(IDX.poi[ex.poi]?"poi:":"place:")+ex.poi;location.hash="#map";if(location.hash==="#map")rerender();return;
    case "map-place":ui.mapFocus="place:"+v;location.hash="#map";return;
    case "map-hotel":ui.mapFocus="hotel:"+v;location.hash="#map";return;
    case "plan-port":planPort(v);return;
    case "exp-json":saveFile("alaska-2027-plans.json",JSON.stringify(exportObj(),null,1),"application/json");return;
    case "exp-cmp-all":saveFile("cruise-comparison-all-sailings.csv",cruiseCSVs().sailings,"text/csv");return;
    case "exp-cmp-lines":saveFile("cruise-comparison-by-line.csv",cruiseCSVs().lines,"text/csv");return;
    case "exp-csv":saveFile("alaska-2027-"+slug(p.name)+".csv",planCSV(p),"text/csv");return;
    case "exp-html":saveFile("alaska-2027-"+slug(p.name)+"-itinerary.html",planHTML(p),"text/html");return;
    case "copy-json":var txt=JSON.stringify(exportObj());var ta=document.getElementById("imp-text");
      if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(txt).then(function(){toast("Plans copied. Paste them into a message or note.")},function(){if(ta){ta.value=txt;ta.select();toast("Text selected below: copy it with your device’s Copy.")}})}else if(ta){ta.value=txt;ta.select();toast("Text selected below: copy it with your device’s Copy.")}return;
    case "imp-paste":var t2=(document.getElementById("imp-text")||{}).value||"";if(!t2.trim()){toast("Paste exported plans text first.");return}importText(t2);return;
    case "print":try{window.print()}catch(x){}return;
    default:return}
  rerender()});
document.addEventListener("change",function(e){
  var t=e.target,p=PL&&AP();
  if(t.id==="imp-file"&&t.files&&t.files[0]){var fr=new FileReader();fr.onload=function(){importText(String(fr.result))};fr.readAsText(t.files[0]);return}
  if(t.matches("select[data-pa]")){var pa=t.getAttribute("data-pa");
    if(pa==="switch"){PL.active=t.value;ui.confirm=null;savePlans()}
    else if(pa==="new"){if(!t.value)return;var np=t.value==="blank"?blankPlan("New plan",p.sailing):presetPlan(t.value);if(!np){toast("No sailing fits that starter.");return}if(t.value!=="blank")np.name=D.meta.presets[t.value].label;PL.list.push(np);PL.active=np.id;savePlans();toast("Created “"+np.name+"”.")}
    else if(pa==="sail"){p.sailing=t.value;touch(p)}
    rerender();return}
  if(t.matches("[data-pf]")){var path=t.getAttribute("data-pf"),val;
    if(t.type==="checkbox")val=t.checked;else if(t.type==="number"){val=t.value===""?null:Math.max(0,+t.value);if(path==="hotel.rooms"&&val<1)val=1;if(path==="contPct"||path==="flight.bags")val=val||0}else val=t.value;
    if(path==="name"){val=String(val).trim().slice(0,60)||"Untitled plan"}
    setPath(p,path,val);touch(p);if(path==="notes"||path.indexOf("check.")===0)return;rerender();return}
  if(t.matches("[data-w]")){var W=store.get("weights",{});W[t.getAttribute("data-w")]=+t.value;store.set("weights",W);rerender();return}
  if(t.matches("[data-cf]")){var cf=store.get("cmpf",{});cf[t.getAttribute("data-cf")]=t.value;store.set("cmpf",cf);rerender();return}
  if(t.matches("[data-cmp]")){var id=t.getAttribute("data-cmp");ui.cmp=ui.cmp.filter(function(x){return x!==id});if(t.checked)ui.cmp.push(id);ui.cmp=ui.cmp.slice(-4);store.set("cmp",ui.cmp);rerender();return}
  if(t.matches("[data-mj]")){var J=JUMPS.filter(function(x){return x[0]===t.value})[0];if(J){if(!J[2]){MV=Object.assign({},MAPDEF)}else{var q=prj(J[2],J[3]),svg=document.getElementById("amap"),r=svg.getBoundingClientRect(),H=J[4]*(r.height/Math.max(1,r.width));MV={x:q[0]-J[4]/2,y:q[1]-H/2,w:J[4],h:H}}applyMV()}return}
});
document.addEventListener("input",function(e){var t=e.target;if(t.matches&&t.matches("[data-w]")){var b=t.parentNode.querySelector("b");if(b)b.textContent=t.value}});
document.addEventListener("toggle",function(e){var d=e.target;if(!d.matches||!d.matches("details[data-stop]"))return;var k=d.getAttribute("data-stop");ui.open[k]=d.open;
  if(d.open&&!d.querySelector(".pk,.pk-f")){var p=AP(),s=IDX.sail[p.sailing],st=stopByKey(s,k);if(st)d.insertAdjacentHTML("beforeend",picker(p,s,st))}},true);
