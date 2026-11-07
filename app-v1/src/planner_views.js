/* ===================== Phase 4: views ===================== */
function tagWho(w){return '<span class="who who-'+w+'">'+esc(whoTxt(w))+'</span>'}
function sailLabel(s){return s._ship.name+" · "+fmtD(s.depart,{month:"short",day:"numeric"})+"–"+fmtD(s.return,{month:"short",day:"numeric"})}
function linkSrc(u,t){return u?'<a href="'+esc(u)+'" target="_blank" rel="noopener">'+esc(t||"source")+'</a>':''}

/* ---------- overview ---------- */
function vOverview(){
  var W=weights(),june=D.sailings.filter(function(s){return s._june&&s._total!=null&&s._it.days});
  var lead=pick(june,function(s){return -score(s,W).total});
  var cheap=pick(june.filter(function(s){return s._fareStatus==="verified"}),function(s){return s._total});
  var mob=pick(june,function(s){return -factors(s).mobility*1e5+s._total});
  var gl=pick(june,function(s){return -factors(s).scenic*1e5+s._total});
  var picks=[["Leading pick (your weights)",lead,function(s){return 'Overall score <b class="num">'+Math.round(score(s,W).total)+'</b> / 100'}],
    ["Lowest June cost",cheap,function(s){return 'Two cabins + tips'}],
    ["Easiest for the parents",mob,function(s){return 'Ease score <b class="num">'+factors(s).mobility.toFixed(1)+'</b> / 10 · '+(s._it._sea)+' sea day'+(s._it._sea===1?'':'s')}],
    ["Best glacier day",gl,function(s){return esc(s._it.glacier||"")+' · scenery '+factors(s).scenic.toFixed(1)+' / 10'}]];
  var cards=picks.filter(function(x){return x[1]}).map(function(pk){var s=pk[1];
    return '<article class="card pick">'+photo(s._ship.photo,s._ship.name)+'<div class="body"><div class="eyebrow">'+esc(pk[0])+'</div><h3>'+esc(s._ship.name)+'</h3>'+
    '<div class="lineName">'+badge(s._line)+esc(s._line.name)+'</div><div class="muted">'+dlong(s.depart)+' – '+fmtD(s.return)+' · '+gpill(s._it.glacier)+'</div>'+
    '<div><span class="big">'+money(s._total)+'</span> <span class="muted" style="font-size:.85rem">cruise for 4 incl. tips</span></div><div class="note">'+pk[2](s)+'</div>'+
    '<div class="row-links"><a href="#sailings" data-goto="'+esc(s.id)+'">Details</a><button class="linkbtn" data-pa="use-sail" data-v="'+esc(s.id)+'">Use in my plan</button></div></div></article>'}).join("");
  var p=AP(),ps=IDX.sail[p.sailing],C=cost(p),n=planIssues(p);
  var mine='<article class="card mine"><div class="mine-l"><div class="eyebrow">Your active plan</div><h2>'+esc(p.name)+'</h2><div class="muted">'+esc(sailLabel(ps))+' · '+esc(ps._line.name)+'</div>'+
    '<div class="tiles">'+tile("Trip total",money(C.total))+tile("Per person",money(C.pp))+tile("Parents",money(C.parents))+tile("Brothers",money(C.brothers))+'</div>'+
    '<div class="note">'+Math.round(C.researched/Math.max(1,C.total)*100)+'% of this total is researched prices; the rest is estimates. '+(n.bad||n.warn||n.off?'<b>'+(n.bad+n.off)+' problem'+((n.bad+n.off)===1?'':'s')+', '+n.warn+' caution'+(n.warn===1?'':'s')+'</b> in the day plan.':'No schedule problems.')+'</div>'+
    '<div class="row-links"><a class="btn" href="#plan">Open the plan builder</a><a href="#compare">Compare cruises</a><a href="#map">Map</a></div></div>'+
    '<a class="mine-map" href="#map" aria-label="Open the map">'+miniMap(ps)+'</a></article>';
  return '<section class="view"><div class="lede"><p>Seattle round-trip Alaska cruises for late May to early July 2027, priced the way the family books: an <b>interior</b> cabin for the brothers and a <b>balcony</b> for the parents on the same ship. '+
    D.sailings.length+' sailings checked '+fmtD(D.meta.updated,{month:"long",day:"numeric",year:"numeric"})+'. Build and compare whole trips in the plan builder.</p></div>'+mine+
    '<div class="grid g4">'+cards+'</div>'+chartCard()+
    '<div class="card" style="padding:16px"><div class="eyebrow" style="margin-bottom:10px">How to read the price labels</div><div class="statusrow">'+
    Object.keys(D.meta.statusDefinitions).map(function(k){return '<div>'+stTag(k)+'<span class="muted">'+esc(D.meta.statusDefinitions[k].desc)+'</span></div>'}).join("")+'</div></div>'+
    watchouts()+'<div><div class="eyebrow" style="margin-bottom:8px">Planner build</div><div class="phase">'+D.meta.phases.map(function(ph){return '<span class="'+(ph.status==="done"?"done":"")+'">'+ph.n+'. '+esc(ph.name)+(ph.status==="done"?" ✓":ph.status==="next"?" (next)":"")+'</span>'}).join("")+'</div></div></section>'}
function tile(k,v,sub){return '<div class="tile"><span class="eyebrow">'+esc(k)+'</span><span class="num tv">'+v+'</span>'+(sub?'<span class="note">'+sub+'</span>':'')+'</div>'}

/* ---------- map projection ---------- */
function prj(lat,lng){return [(lng-COAST.LON0)*COAST.K*COAST.S,(COAST.LAT1-lat)*COAST.S]}
function poly(pts){return pts.map(function(q){var x=prj(q[0],q[1]);return x[0].toFixed(1)+","+x[1].toFixed(1)}).join(" ")}
function miniMap(s){var it=s._it,pts=it.mapLine||[];if(!COAST)return"";
  var xs=pts.map(function(q){return prj(q[0],q[1])}),minx=Math.min.apply(null,xs.map(function(a){return a[0]}))-30,maxx=Math.max.apply(null,xs.map(function(a){return a[0]}))+30,miny=Math.min.apply(null,xs.map(function(a){return a[1]}))-30,maxy=Math.max.apply(null,xs.map(function(a){return a[1]}))+30;
  var dots=[];(it.days||[]).forEach(function(d){d.forEach(function(e){if(e.place&&(e.type==="port"||e.type==="scenic")){var q=prj(IDX.places[e.place].lat,IDX.places[e.place].lng);dots.push('<circle cx="'+q[0].toFixed(1)+'" cy="'+q[1].toFixed(1)+'" r="'+((maxx-minx)/90).toFixed(1)+'" class="'+(e.type==="scenic"?"m-sc":"m-port")+'"/>')}})});
  return '<svg class="minimap" preserveAspectRatio="xMidYMid slice" viewBox="'+[minx,miny,maxx-minx,maxy-miny].map(function(v){return v.toFixed(0)}).join(" ")+'" role="img" aria-label="Route of '+esc(s._ship.name)+'"><rect x="'+minx+'" y="'+miny+'" width="'+(maxx-minx)+'" height="'+(maxy-miny)+'" class="sea"/><path class="land" d="'+COAST.land+'"/><polyline class="rt-on" points="'+poly(pts)+'" vector-effect="non-scaling-stroke"/>'+dots.join("")+'</svg>'}

/* ---------- plan builder ---------- */
function vPlan(){
  var p=AP(),s=IDX.sail[p.sailing],C=cost(p),n=planIssues(p);
  var over=p.budget&&C.total>p.budget;
  return '<section class="view plan">'+planBar(p)+
   '<div class="sumstrip card"><div class="tiles">'+tile("Trip total",money(C.total),Math.round(C.researched/Math.max(1,C.total)*100)+'% researched prices')+tile("Per person",money(C.pp))+tile("Parents (2)",money(C.parents))+tile("Brothers (2)",money(C.brothers))+
   tile(p.budget?"Budget left":"Per day",p.budget?'<span class="'+(over?'bad':'')+'">'+(over?'−':'')+money(Math.abs(p.budget-C.total))+'</span>':money(C.perDay),p.budget?(over?'Over your target of '+money(p.budget):'of '+money(p.budget)):C.days+' days, ABQ to ABQ')+'</div>'+
   (n.bad||n.off||n.warn?'<div class="note">'+(n.bad+n.off?'<span class="bad">'+(n.bad+n.off)+' problem'+((n.bad+n.off)===1?'':'s')+'</span> · ':'')+n.warn+' caution'+(n.warn===1?'':'s')+' in the day plan below.</div>':'')+
   '<nav class="stepnav" aria-label="Plan steps">'+[["st-cruise","1 Cruise"],["st-cabins","2 Cabins"],["st-flights","3 Flights"],["st-hotel","4 Hotel"],["st-days","5 Days"],["st-costs","6 Costs"],["st-share","7 Save & share"]].map(function(x){return '<a href="#plan" data-jump="'+x[0]+'">'+x[1]+'</a>'}).join("")+'</nav></div>'+
   stepCruise(p,s)+stepCabins(p,s)+stepFlights(p,s)+stepHotel(p,s)+stepDays(p,s)+stepCosts(p,s,C)+stepShare(p)+'</section>'}
function planBar(p){
  var c=ui.confirm;
  return '<div class="planbar"><label class="sel" for="pl-switch">Plan <select id="pl-switch" data-pa="switch">'+PL.list.map(function(x){return '<option value="'+esc(x.id)+'"'+(x.id===p.id?' selected':'')+'>'+esc(x.name)+'</option>'}).join("")+'</select></label>'+
   '<label class="sel grow" for="pl-name">Name <input id="pl-name" type="text" maxlength="60" value="'+esc(p.name)+'" data-pf="name"></label>'+
   '<div class="btnrow"><button class="btn sm" data-pa="dup">Duplicate</button>'+
   '<select id="pl-new" data-pa="new" aria-label="New plan"><option value="">New plan…</option><option value="blank">Blank (same cruise)</option><option value="budget">Budget Alaska</option><option value="balanced">Balanced Family Experience</option><option value="premium">Premium Scenery &amp; Wildlife</option></select>'+
   (c==="del"?'<button class="btn sm danger" data-pa="del-yes">Delete “'+esc(p.name)+'”</button><button class="btn sm ghost" data-pa="cancel">Keep</button>':'<button class="btn sm ghost" data-pa="del"'+(PL.list.length<2?' disabled title="Keep at least one plan"':'')+'>Delete</button>')+'</div></div>'}
function stepHead(id,n,t,sub){return '<div class="stephead" id="'+id+'"><span class="stepn">'+n+'</span><div><h2>'+t+'</h2>'+(sub?'<p class="note">'+sub+'</p>':'')+'</div></div>'}
function stepCruise(p,s){
  var groups={};D.sailings.forEach(function(x){(groups[x._line.id]=groups[x._line.id]||[]).push(x)});
  var opts=D.lines.filter(function(l){return groups[l.id]}).map(function(l){return '<optgroup label="'+esc(l.name)+'">'+groups[l.id].slice().sort(function(a,b){return a.depart<b.depart?-1:1}).map(function(x){return '<option value="'+esc(x.id)+'"'+(x.id===s.id?' selected':'')+'>'+esc(sailLabel(x))+' · '+(x._total==null?'price incomplete':money(x._total))+(x._it.days?'':' · no port times')+'</option>'}).join("")+'</optgroup>'}).join("");
  var it=s._it,sc=score(s,weights()),N=p.acts.filter(function(a){return actState(p,a,s)!=="ok"}).length;
  return '<div class="card step">'+stepHead("st-cruise",1,"Cruise","Pick the sailing. Changing it keeps your activities; any that do not fit the new route are flagged in step 5.")+
   '<div class="stepbody"><label class="sel stack" for="pl-sail">Sailing <select id="pl-sail" data-pa="sail">'+opts+'</select></label>'+
   '<div class="cruisepick"><div>'+photo(s._ship.photo,s._ship.name).replace('class="ph"','class="ph sm"')+'</div><div class="cp-b"><div class="lineName">'+badge(s._line)+esc(s._line.name)+'</div><h3>'+esc(s._ship.name)+'</h3><div class="muted">'+esc(it.name)+'</div>'+
   '<div class="chips-s">'+gpill(it.glacier)+'<span class="pill">'+dlong(s.depart)+' – '+dlong(s.return)+'</span>'+(it._ak!=null?'<span class="pill">'+it._ak.toFixed(1)+' h in AK ports</span>':'')+'<span class="pill">'+esc(IDX.places[s._line.terminal].short)+'</span>'+(sc.total!=null?'<span class="pill">Score '+Math.round(sc.total)+'/100</span>':'')+'</div>'+
   (s.flags.length?'<div class="note">'+s.flags.map(function(f){return {"promo":"Sale or promo price: may end","holiday":"July 4 week","adults-only":"Adults only","resident-tag":"Resident-rate tag shown (not applied)"}[f]}).filter(Boolean).map(esc).join(" · ")+'</div>':'')+
   (!it.days?'<div class="warnb">Day-by-day port times were not captured for this sailing, so activities cannot be planned or time-checked.</div>':'')+
   (N?'<div class="warnb">'+N+' activit'+(N===1?'y':'ies')+' from your previous cruise do not fit this route. See step 5.</div>':'')+
   '<div class="row-links"><a href="#sailings" data-goto="'+esc(s.id)+'">Full sailing details</a><a href="#compare">Compare with others</a><a href="'+esc(s.priceSource.url)+'" target="_blank" rel="noopener">Book / price page</a></div></div></div></div></div>'}
function choice(pa,g,v,on,dis,label,sub){return '<button class="opt" data-pa="'+pa+'"'+(g?' data-g="'+g+'"':'')+' data-v="'+esc(v)+'" aria-pressed="'+(on?"true":"false")+'"'+(dis?' disabled':'')+'><b>'+label+'</b>'+(sub?'<span>'+sub+'</span>':'')+'</button>'}
function stepCabins(p,s){
  function opts(g,cats){return cats.map(function(k){var x=s.prices[k];var ok=x&&x.pp!=null;
    return choice("cabin",g,k,p.cabins[g]===k,!ok,esc(x&&x.label||catName(k)),ok?'<span class="num">'+money(x.pp*2)+'</span> for 2 · '+money(x.pp)+' pp '+stTag(x.status):'Not captured')}).join("")}
  return '<div class="card step">'+stepHead("st-cabins",2,"Cabins","Prices include taxes and port fees, 2 adults per cabin. Gratuities are added in step 6.")+
   '<div class="stepbody two"><div><div class="eyebrow">Brothers</div><div class="opts">'+opts("brothers",["interior","oceanview"])+'</div></div>'+
   '<div><div class="eyebrow">Parents</div><div class="opts">'+opts("parents",["balcony","miniSuite"])+'</div><p class="note">'+esc(s._line.accessibility||"")+' When booking, ask for a cabin mid-ship near an elevator bank, away from the theatre and nightclub decks.</p></div></div></div>'}
function stepFlights(p,s){
  var fl=flightFor(s);if(!fl)return '<div class="card step">'+stepHead("st-flights",3,"Flights","")+'<div class="stepbody"><p class="note">No flight data.</p></div></div>';
  var f=fl.f,out=flightOutDate(s);
  var fares=[["saver","Saver"],["main","Main"],["first","First"]].map(function(x){var fr=f.fare[x[0]],ok=fr&&fr.total4!=null;
    return choice("fare","",x[0],p.flight.fare===x[0],!ok,x[1],ok?'<span class="num">'+money(fr.total4)+'</span> for 4 · '+(fl.proxy?stTag("estimate"):stTag(fr.status)):'Not captured for this date')}).join("");
  var outs=(f.outbound||[]).map(function(x,i){return choice("out","",i,+p.flight.out===i,false,tm(x.dep)+' → '+tm(x.arr),'ABQ '+dlong(out)+' · '+durTxt(x.durationMin/60))}).join("");
  var rets=(f.returns||[]).map(function(x,i){var rc=returnCheck(s,x.dep);return choice("ret","",i,+p.flight.ret===i,false,tm(x.dep)+' → '+tm(x.arr),'SEA '+dlong(s.return)+(rc?' · <span class="lv-'+rc.lv+'">'+(rc.lv==="ok"?"Comfortable":rc.lv==="warn"?"Tight":"Risky")+'</span>':''))}).join("");
  var r=(f.returns||[])[+p.flight.ret]||(f.returns||[])[0],rc=r&&returnCheck(s,r.dep);
  return '<div class="card step">'+stepHead("st-flights",3,"Flights","Alaska Airlines is the only ABQ–SEA nonstop found. Fly the day before the cruise.")+
   '<div class="stepbody">'+(fl.proxy?'<div class="warnb"><b>This date pair was not searched</b> ('+dlong(out)+' – '+dlong(s.return)+'). The planner uses the nonstop times and the $1,588 Saver fare seen on all six June date pairs that were searched, marked as an estimate.</div>':'')+
   '<div class="eyebrow">Fare</div><div class="opts">'+fares+'</div>'+
   '<div class="two"><div><div class="eyebrow">Outbound, '+dlong(out)+'</div><div class="opts">'+outs+'</div></div><div><div class="eyebrow">Return, '+dlong(s.return)+'</div><div class="opts">'+rets+'</div></div></div>'+
   (rc?'<div class="xbox lvbox lv-'+rc.lv+'"><b>Return-day timing:</b> ship due '+t12(rc.arr)+'; leaving the ship from about '+fmtMin(toMin(rc.arr)+cfg().disembarkH*60)+'; '+rc.tr+' min to SEA puts you at the airport about '+fmtMin(rc.atAirport)+', '+durTxt(rc.slack/60)+' before the '+tm(r.dep)+' flight. '+(rc.lv==="ok"?'Comfortable.':rc.lv==="warn"?'Tight for the parents if disembarkation runs late; the evening flight is safer.':'Too tight: pick the later flight.')+' <span class="note">Planning estimate.</span></div>':'')+
   '<div class="two"><label class="sel stack" for="pl-bags">Checked bags (total) <input id="pl-bags" type="number" min="0" max="12" inputmode="numeric" value="'+esc(p.flight.bags)+'" data-pf="flight.bags"></label>'+
   '<label class="check" for="pl-each"><input id="pl-each" type="checkbox" data-pf="flight.eachWay"'+(p.flight.eachWay?' checked':'')+'> Bag fee charged each way ($'+((f.bags||{}).firstCheckedPerPerson||"?")+' per bag)</label></div>'+
   '<p class="note">'+esc(f.restrictions||"")+' Flight numbers were not shown in the search; get them from Alaska at booking. '+linkSrc(fl.proxy?D.flights[0].url:f.url,"Google Flights search")+' · '+linkSrc(f.bookUrl,"Alaska Airlines")+' · checked '+esc(f.checked)+'</p></div></div>'}
function stepHotel(p,s){
  var night=addDays(s.depart,-1),H=(D.hotels||[]).slice().sort(function(a,b){return a.rate.perRoomNight-b.rate.perRoomNight});
  var term=s._line.terminal;
  var rows=H.map(function(h){var d=h.distances||{},on=p.hotel.id===h.id;
    return '<button class="hrow" data-pa="hotel" data-v="'+esc(h.id)+'" aria-pressed="'+on+'"><span class="hr-n"><b>'+esc(h.name)+'</b><span class="note">'+esc(AREA[h.area]||h.area)+' · ★ '+h.reviewScore+' ('+h.reviewCount.toLocaleString("en-US")+')'+(h.accessibilityListed?' · “Accessible” listed':'')+(term==="sea_p66"&&d.pier66Mi!=null?' · '+d.pier66Mi+' mi to Pier 66':'')+(d.airportMi!=null?' · '+d.airportMi+' mi to SEA':'')+'</span></span><span class="hr-p"><span class="num">'+money(h.rate.perRoomNight)+'</span><span class="note">per room</span></span></button>'}).join("");
  var h=p.hotel.id&&IDX.hotel[p.hotel.id];
  return '<div class="card step">'+stepHead("st-hotel",4,"Seattle hotel, night of "+dlong(night),"Rates were read for the night of Jun 11 only (1 room, 2 guests, before taxes). Other nights will differ.")+
   '<div class="stepbody"><div class="hlist">'+rows+'<button class="hrow" data-pa="hotel" data-v="" aria-pressed="'+(!h)+'"><span class="hr-n"><b>No hotel in the plan</b><span class="note">Arriving on cruise day is risky; the plan assumes flying in the day before.</span></span></button></div>'+
   (h?'<div class="two"><label class="sel stack" for="pl-rooms">Rooms <input id="pl-rooms" type="number" min="1" max="4" inputmode="numeric" value="'+esc(p.hotel.rooms)+'" data-pf="hotel.rooms"></label><div class="note"><b>'+esc(h.name)+':</b> '+esc(h.pros)+' <b>Watch:</b> '+esc(h.cons)+' '+esc(h.transfers)+' '+linkSrc(h.url,"Google Hotels")+'<br><button class="linkbtn" data-pa="map-hotel" data-v="'+esc(h.id)+'">Show on map</button></div></div>':'')+
   (h&&night!==h.stayDate?'<p class="note">Your night is '+dlong(night)+'; the rate shown is for '+dlong(h.stayDate)+', so the hotel total is an estimate.</p>':'')+
   '<p class="note">Your sailing uses '+esc(IDX.places[term].name)+' (usual for '+esc(s._line.name)+'; confirm on cruise documents). '+esc(IDX.places[term].notes||"")+'</p></div></div>'}

/* ---------- days ---------- */
function stepDays(p,s){
  var it=s._it;
  if(!it.days)return '<div class="card step">'+stepHead("st-days",5,"Days","")+'<div class="stepbody"><div class="warnb">Port times were not captured for this sailing (ports: '+(it.ports||[]).map(function(x){return esc(IDX.places[x].short)}).join(", ")+'). Pick a sailing with times to plan days.</div></div></div>';
  var bad=p.acts.map(function(a,i){return {a:a,i:i,st:actState(p,a,s)}}).filter(function(x){return x.st!=="ok"});
  var canMove=bad.filter(function(x){if(x.st!=="elsewhere")return false;var pl=x.a.k.split("|")[1],e=IDX.exc[x.a.x];return portStops(s).some(function(st){return st.place===pl||(e&&e.ports.indexOf(st.place)>-1)})}).length;
  var off=bad.length?'<div class="card offlist"><b>'+bad.length+' activit'+(bad.length===1?'y does':'ies do')+' not fit this cruise</b> and '+(bad.length===1?'is':'are')+' left out of the totals. '+(canMove>1?'<button class="btn sm ghost" data-pa="move-all">Move all to the same ports</button>':'')+'<ul>'+bad.map(function(x){var r=IDX.offer[x.a.o],pl=x.a.k.split("|")[1],alt=portStops(s).filter(function(st){return st.place===pl||(IDX.exc[x.a.x]&&IDX.exc[x.a.x].ports.indexOf(st.place)>-1)})[0];
     var why=x.st==="otherline"?"sold only by "+((IDX.lines[r.o.line]||{}).name||"another line"):"this route does not stop at "+(IDX.places[pl]?IDX.places[pl].short:pl)+" on that day";
     return '<li>'+esc(r.e.name)+' · '+esc(r.o.provider)+' ('+tagWho(x.a.who)+'): '+esc(why)+'. '+(alt&&x.st!=="otherline"?'<button class="linkbtn" data-pa="move" data-i="'+x.i+'" data-k="'+esc(alt.key)+'">Move to '+esc(IDX.places[alt.place].short)+' ('+dlong(alt.date)+')</button> · ':'')+'<button class="linkbtn" data-pa="rm" data-i="'+x.i+'">Remove</button></li>'}).join("")+'</ul></div>':'';
  var c=ui.confirm;
  var fill='<div class="fillbar"><span class="note">Starter picks fill each port with options that fit the time:</span>'+(c&&c.indexOf("fill:")===0?'<button class="btn sm danger" data-pa="fill-yes" data-v="'+esc(c.slice(5))+'">Replace all activities with '+esc(D.meta.presets[c.slice(5)].label)+' picks</button><button class="btn sm ghost" data-pa="cancel">Cancel</button>':
    ["budget","balanced","premium"].map(function(k){return '<button class="btn sm ghost" data-pa="fill" data-v="'+k+'">'+esc(D.meta.presets[k].label.split(" ")[0])+'</button>'}).join("")+(p.acts.length?'<button class="btn sm ghost" data-pa="fill" data-v="clear">Clear all</button>':''))+'</div>';
  var rows=stopsOf(s).map(function(st){return dayRow(p,s,st)}).join("");
  return '<div class="card step">'+stepHead("st-days",5,"Day by day","Add activities for the parents, the brothers or all four. Options that would run past all-aboard can’t be added. Usable time = port hours minus 30 min to get off and 1 h before departure. Activities are laid out from the moment you are ashore; real tour start times vary, so confirm them when booking.")+
   '<div class="stepbody">'+fill+off+'<div class="days">'+rows+'</div></div></div>'}
function dayRow(p,s,st){
  var pl=st.place?IDX.places[st.place]:null,dn='<span class="dnum">Day '+(st.day+1)+'</span> <span class="ddate">'+dlong(st.date)+'</span>',dnb='<div>'+dn+'</div>';
  if(st.type==="sea")return '<div class="dayline">'+dnb+'<span><b>At sea.</b> A rest day; onboard shows, dining and the spa. Good for the parents to recover.</span></div>';
  if(st.type==="embark"){var h=p.hotel.id&&IDX.hotel[p.hotel.id];return '<div class="dayline">'+dnb+'<span><b>Board in Seattle</b>, '+esc(pl.name)+'. Ship sails '+t12(st.dep)+'; most lines want guests aboard about 2 hours before. '+(h?'From '+esc(h.name)+': taxi, rideshare or a cruise-line transfer (costs not captured; add yours in step 6).':'')+' <button class="linkbtn" data-pa="map-place" data-v="'+esc(st.place)+'">Map</button></span></div>'}
  if(st.type==="disembark"){var fl=flightFor(s),r=fl&&(fl.f.returns||[])[+p.flight.ret],rc=r&&returnCheck(s,r.dep);
    return '<div class="dayline">'+dnb+'<span><b>Back in Seattle</b> '+(st.arr?'at '+t12(st.arr):'')+'. '+(rc?'Flight '+tm(r.dep)+': <span class="lv-'+rc.lv+'">'+(rc.lv==="ok"?"comfortable":rc.lv==="warn"?"tight":"risky")+'</span> ('+durTxt(rc.slack/60)+' at the airport before departure, estimated).':'')+(r&&toMin(r.dep)>16*60?' Plan luggage storage or a lunch for the gap.':'')+'</span></div>'}
  if(st.type==="scenic"){var x=(D.excursions||[]).filter(function(e){return e.ports.indexOf(st.place)>-1})[0];
    return '<div class="dayline scenic">'+dnb+'<span><b>'+esc(pl.name)+'</b> '+(st.arr?t12(st.arr)+'–'+t12(st.dep):'(times not published)')+'. Scenic cruising, no going ashore. '+(x?esc(x.blurb):'')+' <button class="linkbtn" data-pa="map-place" data-v="'+esc(st.place)+'">Map</button></span></div>'}
  var L=lanes(p,st),W=stopWarnings(p,st,L,s),span=st.b-st.a;
  function pct(m){return ((m-st.a)/span*100).toFixed(2)+"%"}
  function track(g){var blocks=L[g].map(function(x){return '<span class="blk w-'+x.a.who+(x.fits?'':' over')+'" style="left:'+pct(x.start)+';width:'+((Math.min(x.end,st.b+60)-x.start)/span*100).toFixed(2)+'%" title="'+esc(x.e.name+" "+fmtMin(x.start)+"–"+fmtMin(x.end))+'"></span>'}).join("");
    return '<div class="trk"><span class="tl-l">'+(g==="parents"?"Parents":"Brothers")+'</span><div class="tl-t"><span class="off" style="width:'+pct(st.start)+'"></span><span class="aboard" style="left:'+pct(st.allAboard)+'"></span>'+blocks+'</div></div>'}
  function list(g){if(!L[g].length)return '<li class="none">Nothing planned yet: free time in town or stay aboard.</li>';
    return L[g].map(function(x){var c=offerCost(x.o,x.a.who);return '<li class="'+(x.fits?'':'over')+'"><span class="tt num">'+fmtMin(x.start)+'–'+fmtMin(x.end)+'</span><span class="ti"><b>'+esc(x.e.name)+'</b> '+(x.a.who==="family"?tagWho("family"):'')+'<span class="note">'+esc(x.o.title)+' · '+esc(x.o.provider)+' · '+(c==null?'price not captured':money(c)+(x.o.from?' (from)':''))+' '+stTag(x.o.status)+(x.o.hours==null?' · duration assumed':'')+'</span></span><span class="ta"><button class="linkbtn" data-pa="map-x" data-v="'+esc(x.e.id)+'">Map</button><button class="linkbtn" data-pa="rm" data-i="'+x.i+'">Remove</button></span></li>'}).join("")}
  var dayCost=sum(p.acts.filter(function(a){return a.k===st.key}).map(function(a){return offerCost(IDX.offer[a.o].o,a.who)}));
  var open=!!ui.open[st.key];
  return '<article class="dayc" id="d-'+esc(st.key.replace("|","-"))+'">'+
   '<div class="dayh">'+(pl.photo?'<div class="dayph">'+photo(pl.photo,pl.short).replace('class="ph"','class="ph sm"')+'</div>':'')+'<div class="dayhb">'+dn+'<h3>'+esc(pl.name)+'</h3><div class="times num">'+t12(st.arr)+' – '+t12(st.dep)+' · '+durTxt(st.portH)+' in port</div><div class="note">Off by '+fmtMin(st.start)+' · back aboard by '+fmtMin(st.allAboard)+' · <b>'+durTxt(st.usable)+' usable</b> · '+esc(pl.dock||"")+'</div><div class="note">Activities today: <b class="num">'+money(dayCost)+'</b> <button class="linkbtn" data-pa="map-place" data-v="'+esc(st.place)+'">Port map</button></div></div></div>'+
   '<div class="tracks">'+track("parents")+track("brothers")+'<div class="tl-legend note"><span class="sw off"></span>getting off <span class="sw w-family"></span>all 4 <span class="sw w-parents"></span>parents <span class="sw w-brothers"></span>brothers <span class="sw ab"></span>all aboard</div></div>'+
   '<div class="two lanes"><div><div class="eyebrow">Parents</div><ul class="lane">'+list("parents")+'</ul></div><div><div class="eyebrow">Brothers</div><ul class="lane">'+list("brothers")+'</ul></div></div>'+
   (W.length?'<ul class="warns">'+W.map(function(w){return '<li class="lv-'+w.lv+'">'+esc(w.t)+'</li>'}).join("")+'</ul>':'')+
   '<details class="picker" data-stop="'+esc(st.key)+'"'+(open?' open':'')+'><summary>Add activities in '+esc(pl.short)+'</summary>'+(open?picker(p,s,st):'')+'</details></article>'}
function picker(p,s,st){
  var X=(D.excursions||[]).filter(function(e){return e.ports.indexOf(st.place)>-1});
  var f=ui.xf;
  var fx=X.filter(function(e){return f==="all"||(f==="parents"&&(e.label==="ideal_parents"||e.label==="everyone"||e.label==="precautions"))||(f==="brothers"&&(e.label==="brothers"||e.label==="everyone"||e.group==="brothers"))||(f==="free"&&e.offers.some(function(o){return o.pp===0}))});
  return '<div class="pk-f chips" role="group" aria-label="Filter">'+[["all","All"],["parents","Suits parents"],["brothers","For brothers"],["free","Free options"]].map(function(o){return '<button class="chip" data-pa="xf" data-v="'+o[0]+'" aria-pressed="'+(f===o[0])+'">'+o[1]+'</button>'}).join("")+'</div>'+
   fx.map(function(e){var other=0;var offs=e.offers.filter(function(o){if(!offerOK(o,s)){other++;return false}return true}).sort(function(a,b){return (KRANK[a.kind]-KRANK[b.kind])||((a.pp==null?1e9:a.pp)-(b.pp==null?1e9:b.pp))});
    var mine=e.offers.some(function(o){return o.kind==="cruise"&&o.line===s._line.id});
    return '<div class="pk"><div class="pkh"><b>'+esc(e.name)+'</b><span class="lab lab-'+esc(e.label)+'">'+esc(D.meta.labels[e.label])+'</span><span class="note">Exertion '+meter(e.exertion)+' · '+esc(e.seating)+' · weather '+esc(e.weather)+'</span></div>'+
     '<details class="pkd"><summary>Mobility and details</summary><p class="note">'+esc(e.blurb)+' '+esc(e.mobility)+(e.caveat?' '+esc(e.caveat):'')+'</p></details>'+
     (e.risk?'<div class="xrisk">'+esc(e.risk.text)+'</div>':'')+
     offs.map(function(o){var btn=function(w){var has=p.acts.some(function(a){return a.k===st.key&&a.o===o.id&&(a.who===w||a.who==="family"||w==="family")});var fit=fitsNew(p,st,w,o);var warn=(w!=="brothers")&&(e.label==="brothers"||e.label==="not_recommended"||e.exertion>=3);
        return '<button class="addb'+(warn?' warn':'')+'" data-pa="add" data-k="'+esc(st.key)+'" data-x="'+esc(e.id)+'" data-o="'+esc(o.id)+'" data-who="'+w+'"'+(has||!fit?' disabled':'')+' title="'+(has?'Already planned':!fit?'Won’t fit before all-aboard':warn?'Higher exertion: check for the parents':'Add')+'">'+(has?'✓ ':'+ ')+whoTxt(w)+(!fit&&!has?' · no time':'')+'</button>'};
      var c4=offerCost(o,"family");
      return '<div class="pko"><div class="pko-t"><span class="kind kind-'+esc(o.kind)+'">'+esc((D.meta.offerKinds[o.kind]||o.kind).replace(/ \(Option [AB]\)/,""))+'</span><b>'+esc(o.title)+'</b><span class="note">'+esc(o.provider)+' · '+(o.hours!=null?durTxt(o.hours):'duration not stated')+(o.level?' · '+esc(o.level):'')+' · '+esc(WC[o.wheelchair||"not_stated"])+(o.cancel?' · cancel: '+esc(o.cancel):'')+' · '+linkSrc(o.url,"source")+'</span></div>'+
       '<div class="pko-p">'+priceTxt(o)+(c4!=null&&o.unit==="pp"&&o.pp>0?'<span class="note">'+money(c4/2)+' for 2 · '+money(c4)+' for 4</span>':'')+stTag(o.status)+'</div>'+
       '<div class="pko-b">'+btn("parents")+btn("brothers")+btn("family")+'</div></div>'}).join("")+
     (other?'<p class="note pk-o">'+other+' price'+(other>1?'s':'')+' from other cruise lines hidden (not sold on your ship).'+(mine?'':' Your line’s own price for this was not captured.')+'</p>':'')+'</div>'}).join("")}

/* ---------- costs ---------- */
function stepCosts(p,s,C){
  var mx=Math.max.apply(null,CATS.map(function(c){return C.cat[c[0]]||0}).concat([1]));
  var bars=CATS.filter(function(c){return C.cat[c[0]]}).map(function(c){var v=C.cat[c[0]];return '<div class="cbar"><span class="cb-l">'+esc(c[1])+'</span><span class="cb-t"><span class="cb-f c-'+c[0]+'" style="width:'+(v/mx*100).toFixed(1)+'%"></span></span><span class="num cb-v">'+money(v)+'</span></div>'}).join("");
  var st=["verified","published","estimate","user"].filter(function(k){return C.by[k]});
  var stack='<div class="ststack" role="img" aria-label="Share of total by price status">'+st.map(function(k){return '<span class="sk st-'+k+'" style="width:'+(C.by[k]/C.total*100).toFixed(1)+'%"></span>'}).join("")+'</div><div class="legend">'+st.map(function(k){return '<span>'+stTag(k)+' <span class="num">'+money(C.by[k])+'</span></span>'}).join("")+'</div>';
  var rows=CATS.map(function(c){var its=C.items.filter(function(i){return i.cat===c[0]}),ms=C.miss.filter(function(i){return i.cat===c[0]});if(!its.length&&!ms.length)return"";
    return '<tr class="grp"><th colspan="4">'+esc(c[1])+'</th></tr>'+its.map(function(i){return '<tr><td>'+esc(i.label)+(i.note?'<div class="note">'+esc(i.note)+'</div>':'')+'</td><td>'+(i.who==="split"?'split':esc(whoTxt(i.who)))+'</td><td class="num r">'+money(i.amt)+'</td><td>'+stTag(i.status)+(i.src?' '+linkSrc(i.src,"source"):'')+'</td></tr>'}).join("")+
      ms.map(function(i){return '<tr class="miss"><td>'+esc(i.label)+'<div class="note">'+esc(i.note||"")+'</div></td><td></td><td class="num r">—</td><td>'+stTag("unavailable")+'</td></tr>'}).join("")}).join("");
  var EX=[["transfers","Airport and pier transfers","Taxi, rideshare or cruise-line transfers (not researched)"],["drinks","Drink packages",""],["wifi","Wi-Fi",""],["insurance","Travel insurance",""],["onboard","Onboard spending","Specialty dining, spa, souvenirs"],["postHotel","Post-cruise hotel",""],["other","Other",""]];
  var form=EX.map(function(x){return '<label class="sel stack" for="ex-'+x[0]+'">'+x[1]+' <span class="dollar"><input id="ex-'+x[0]+'" type="number" min="0" step="10" inputmode="decimal" placeholder="not set" value="'+(p.extras[x[0]]!=null?esc(p.extras[x[0]]):'')+'" data-pf="extras.'+x[0]+'"></span>'+(x[2]?'<span class="note">'+x[2]+'</span>':'')+'</label>'}).join("")+
   '<label class="sel stack" for="ex-cont">Contingency % <input id="ex-cont" type="number" min="0" max="50" step="1" inputmode="numeric" value="'+esc(p.contPct||0)+'" data-pf="contPct"></label>'+
   '<label class="sel stack" for="ex-budget">Budget target for 4 <span class="dollar"><input id="ex-budget" type="number" min="0" step="100" inputmode="decimal" placeholder="none" value="'+(p.budget!=null?esc(p.budget):'')+'" data-pf="budget"></span></label>';
  var cmp=PL.list.map(function(x){var cx=cost(x),sx=IDX.sail[x.sailing],nx=planIssues(x);return '<tr'+(x.id===p.id?' class="cur"':'')+'><td><b>'+esc(x.name)+'</b><div class="note">'+esc(sailLabel(sx))+'</div></td><td class="num r">'+money(cx.total)+'</td><td class="num r">'+money(cx.pp)+'</td><td class="num r">'+money(cx.parents)+'</td><td class="num r">'+money(cx.brothers)+'</td><td class="num r">'+money(sum(["act_parents","act_brothers","act_family"].map(function(k){return cx.cat[k]})))+'</td><td>'+(nx.bad+nx.off?'<span class="bad">'+(nx.bad+nx.off)+' problem'+((nx.bad+nx.off)>1?'s':'')+'</span>':nx.warn?nx.warn+' caution'+(nx.warn>1?'s':''):'OK')+'</td><td>'+(x.id===p.id?'<span class="note">open</span>':'<button class="linkbtn" data-pa="open" data-v="'+esc(x.id)+'">Open</button>')+'</td></tr>'}).join("");
  return '<div class="card step">'+stepHead("st-costs",6,"Costs for all four","Every line shows its status. Researched prices are published figures read on provider or aggregator pages; estimates are the planner’s arithmetic or your own numbers.")+
   '<div class="stepbody"><div class="two"><div><div class="eyebrow">Where the money goes</div><div class="cbars">'+bars+'</div></div><div><div class="eyebrow">How solid the total is</div>'+stack+
   '<dl class="kv" style="margin-top:12px"><dt>Total</dt><dd class="num">'+money(C.total)+'</dd><dt>Per person</dt><dd class="num">'+money(C.pp)+'</dd><dt>Parents</dt><dd class="num">'+money(C.parents)+'</dd><dt>Brothers</dt><dd class="num">'+money(C.brothers)+'</dd><dt>Per day</dt><dd class="num">'+money(C.perDay)+' ('+C.days+' days)</dd><dt>Cruise vs rest</dt><dd class="num">'+money((C.cat.cruise||0)+(C.cat.grat||0))+' / '+money(C.total-(C.cat.cruise||0)-(C.cat.grat||0))+'</dd></dl>'+
   '<p class="note">Shared costs (flights, bags, extras, all-4 activities) are split evenly; two hotel rooms are split one each.</p></div></div>'+
   '<div class="tablewrap"><table class="costs"><thead><tr><th>Item</th><th>For</th><th class="r">Amount</th><th>Status</th></tr></thead><tbody>'+rows+'<tr class="tot"><td>Total</td><td></td><td class="num r">'+money(C.total)+'</td><td></td></tr></tbody></table></div>'+
   '<div class="eyebrow">Your own numbers (optional)</div><div class="exform">'+form+'</div>'+
   '<div class="eyebrow">Your plans side by side</div><div class="tablewrap"><table><thead><tr><th>Plan</th><th class="r">Total</th><th class="r">Per person</th><th class="r">Parents</th><th class="r">Brothers</th><th class="r">Activities</th><th>Schedule</th><th></th></tr></thead><tbody>'+cmp+'</tbody></table></div></div></div>'}
function stepShare(p){
  var canPrint=false;try{canPrint=window.top===window.self}catch(e){}
  return '<div class="card step">'+stepHead("st-share",7,"Save & share","Plans save automatically in this browser. To share with family or move to another device, export the plans file and import it there.")+
   '<div class="stepbody"><div class="btnrow"><button class="btn" data-pa="exp-json">Export plans (.json)</button><button class="btn ghost" data-pa="exp-csv">Cost summary (.csv)</button><button class="btn ghost" data-pa="exp-html">Printable itinerary (.html)</button><button class="btn ghost" data-pa="copy-json">Copy plans as text</button>'+(canPrint?'<button class="btn ghost" data-pa="print">Print this plan</button>':'')+'</div>'+
   '<div class="two"><label class="sel stack" for="imp-file">Import a plans file <input id="imp-file" type="file" accept=".json,application/json"></label>'+
   '<label class="sel stack" for="imp-text">…or paste plans text <textarea id="imp-text" rows="3" placeholder="Paste exported plans here"></textarea><button class="btn sm ghost" data-pa="imp-paste">Import pasted text</button></label></div>'+
   '<label class="sel stack" for="pl-notes">Notes for this plan <textarea id="pl-notes" rows="3" data-pf="notes" placeholder="Questions for the cruise line, who books what…">'+esc(p.notes||"")+'</textarea></label>'+
   '<p class="note">Saved plans stay on this device and browser only. Clearing site data removes them, so export a copy once you settle on something.</p></div></div>'}

/* ---------- compare ---------- */
function vCompare(){
  var W=weights(),F=D.meta.scoring.factors,cf=Object.assign({window:"june",line:"all",glacier:"all",size:"all",max:"",minMob:""},store.get("cmpf",{}));
  var list=D.sailings.filter(function(s){
    if(cf.window==="june"&&!s._june)return false;if(cf.line!=="all"&&s._line.id!==cf.line)return false;
    if(cf.glacier!=="all"&&(cf.glacier==="none"?!!s._it.glacier:s._it.glacier!==cf.glacier))return false;
    if(cf.size!=="all"&&shipSize(s)!==cf.size)return false;if(cf.max&&(s._total==null||s._total>+cf.max))return false;if(cf.minMob&&factors(s).mobility<+cf.minMob)return false;return true});
  var rows=list.map(function(s){return {s:s,sc:score(s,W)}}).sort(function(a,b){return (b.sc.total||-1)-(a.sc.total||-1)});
  var tw=sum(Object.keys(W).map(function(k){return W[k]}))||1;
  var COL={scenic:"var(--g-bay)",mobility:"var(--ok)",value:"var(--warn)",excursions:"var(--est)",portTime:"var(--g-hubbard)",comfort:"var(--na)"};
  var sliders=F.map(function(f){return '<label class="slider" for="w-'+f.id+'"><span><i style="background:'+COL[f.id]+'"></i>'+esc(f.label)+' <b class="num">'+W[f.id]+'</b></span><input id="w-'+f.id+'" type="range" min="0" max="50" step="5" value="'+W[f.id]+'" data-w="'+f.id+'"></label>'}).join("");
  var rules='<details class="rules"><summary>How each score is worked out</summary><ul>'+F.map(function(f){return '<li><b>'+esc(f.label)+':</b> '+esc(f.rule)+'</li>'}).join("")+'</ul><p class="note">'+esc(D.meta.scoring.note)+'</p></details>';
  var sel=ui.cmp.filter(function(id){return IDX.sail[id]});
  var lines=D.lines.filter(function(l){return D.sailings.some(function(s){return s._line===l})});
  function sf(k,opts){return '<select id="cf-'+k+'" data-cf="'+k+'">'+opts.map(function(o){return '<option value="'+esc(o[0])+'"'+(String(cf[k])===String(o[0])?' selected':'')+'>'+esc(o[1])+'</option>'}).join("")+'</select>'}
  var body=rows.map(function(r,i){var s=r.s,it=s._it,tb=tripBase(s),on=sel.indexOf(s.id)>-1;
    var segs=F.map(function(f){var v=r.sc.f[f.id];if(v==null||!W[f.id])return"";return '<span style="width:'+(v*W[f.id]/tw*10).toFixed(2)+'%;background:'+COL[f.id]+'" title="'+esc(f.label+": "+v.toFixed(1)+"/10")+'"></span>'}).join("");
    return '<article class="card crow'+(on?' sel':'')+'"><div class="cr-rank num">'+(i+1)+'</div><div class="cr-who"><div class="lineName">'+badge(s._line)+esc(s._line.name)+'</div><b>'+esc(s._ship.name)+'</b><span class="note">'+dlong(s.depart)+' – '+fmtD(s.return)+'</span>'+gpill(it.glacier)+'</div>'+
     '<div class="cr-facts"><div><span class="k">Two cabins + tips</span><span class="num">'+money(s._total)+'</span>'+stTag(s._fareStatus)+'</div><div><span class="k">Trip base</span><span class="num">'+money(tb.amt)+'</span><span class="note">+ flights &amp; hotel</span></div><div><span class="k">AK ports</span><span>'+it._akPorts.map(function(x){return IDX.places[x].short}).join(", ")+'</span></div><div><span class="k">Usable ashore</span><span class="num">'+(it._use!=null?it._use.toFixed(1)+' h':'—')+'</span></div><div><span class="k">Sea days · pier · guests</span><span>'+it._sea+' · '+esc(IDX.places[s._line.terminal].short.replace("Seattle · ",""))+' · '+(s._ship.guests?s._ship.guests.toLocaleString("en-US"):'n/a')+'</span></div></div>'+
     '<div class="cr-score"><span class="eyebrow">Planner score</span><span class="num big2">'+(r.sc.total==null?'—':Math.round(r.sc.total))+'</span><div class="sbar">'+segs+'</div>'+(r.sc.miss.length?'<span class="note">No '+r.sc.miss.join(", ")+' score</span>':'')+'</div>'+
     '<div class="cr-act"><label class="check" for="cmp-'+esc(s.id)+'"><input id="cmp-'+esc(s.id)+'" type="checkbox" data-cmp="'+esc(s.id)+'"'+(on?' checked':'')+(!on&&sel.length>=4?' disabled':'')+'> Compare</label><button class="linkbtn" data-pa="use-sail" data-v="'+esc(s.id)+'">Use in my plan</button></div></article>'}).join("");
  return '<section class="view"><div class="lede"><p>Rank every sailing by what matters to the family. <b>Facts</b> (prices, ports, hours) come from the research; the <b>score</b> is the planner’s judgment using the rules beside each slider. Tick up to four sailings to see them side by side.</p></div>'+
   (sel.length>=2?cmpTable(sel,W):sel.length===1?'<div class="note">Tick one more sailing to compare side by side.</div>':'')+
   '<div class="card weights"><div class="eyebrow">What matters most (weights)</div><div class="sliders">'+sliders+'</div><div class="btnrow"><button class="btn sm ghost" data-pa="w-reset">Reset weights</button></div>'+rules+'</div>'+
   scatter(rows)+
   '<div class="toolbar">'+'<label class="sel" for="cf-window">Dates '+sf("window",[["june","June departures"],["all","Late May – early July"]])+'</label><label class="sel" for="cf-line">Line '+sf("line",[["all","All lines"]].concat(lines.map(function(l){return [l.id,l.name]})))+'</label>'+
   '<label class="sel" for="cf-glacier">Glacier '+sf("glacier",[["all","Any"]].concat(Object.keys(GLAC).map(function(k){return [k,GSHORT[k]]})).concat([["none","No glacier day"]]))+'</label><label class="sel" for="cf-size">Ship '+sf("size",[["all","Any size"],["small","Under 2,600 guests"],["mid","2,600–3,999"],["large","4,000+"],["unknown","Size not listed"]])+'</label>'+
   '<label class="sel" for="cf-max">Max cruise cost '+sf("max",[["","Any"],["5500","$5,500"],["6500","$6,500"],["7500","$7,500"],["9000","$9,000"]])+'</label><label class="sel" for="cf-minMob">Ease for parents '+sf("minMob",[["","Any"],["7","7+ / 10"],["8","8+ / 10"],["9","9+ / 10"]])+'</label></div>'+
   '<div class="btnrow"><button class="btn sm ghost" data-pa="exp-cmp-lines">Download cruise-line summary (CSV)</button><button class="btn sm ghost" data-pa="exp-cmp-all">Download all sailings (CSV)</button></div>'+
   '<p class="note">'+rows.length+' sailings. Trip base = two cabins + gratuities + 4 Saver flights + 2 rooms at your plan’s hotel ('+esc(tripBase(D.sailings[0]).hname)+'). Excursions not included.</p><div class="sl">'+(body||'<div class="card empty">No sailings match these filters.</div>')+'</div></section>'}
function cmpTable(ids,W){
  var S=ids.map(function(id){return IDX.sail[id]}),F=D.meta.scoring.factors;
  function row(k,f){return '<tr><th>'+k+'</th>'+S.map(function(s){return '<td>'+f(s)+'</td>'}).join("")+'</tr>'}
  return '<div class="card cmpcard"><div class="cmph"><div class="eyebrow">Side by side</div><button class="linkbtn" data-pa="cmp-clear">Clear</button></div><div class="tablewrap"><table class="cmpt"><thead><tr><th></th>'+S.map(function(s){return '<th><div class="lineName">'+badge(s._line)+esc(s._ship.name)+'</div><span class="note">'+dlong(s.depart)+'</span></th>'}).join("")+'</tr></thead><tbody>'+
   '<tr class="grp"><th colspan="'+(S.length+1)+'">Facts (sourced)</th></tr>'+
   row("Interior, 2 people",function(s){return money(s.prices.interior.pp==null?null:s.prices.interior.pp*2)+' '+stTag(s.prices.interior.status)})+
   row("Balcony, 2 people",function(s){return money(s.prices.balcony.pp==null?null:s.prices.balcony.pp*2)+' '+stTag(s.prices.balcony.status)})+
   row("Gratuities (est.)",function(s){return money(s._grat)})+row("Two cabins + tips",function(s){return '<b class="num">'+money(s._total)+'</b>'})+
   row("Trip base",function(s){var t=tripBase(s);return money(t.amt)+(t.proxy?' <span class="note">(flight fare estimated)</span>':'')})+
   row("Glacier",function(s){return gpill(s._it.glacier)})+row("Alaska ports",function(s){return esc(s._it._akPorts.map(function(x){return IDX.places[x].short}).join(", "))})+
   row("Hours in AK ports",function(s){return s._it._ak!=null?s._it._ak.toFixed(1)+' h (~'+s._it._use.toFixed(1)+' usable)':'—'})+row("Sea days",function(s){return s._it._sea})+
   row("Seattle pier",function(s){return esc(IDX.places[s._line.terminal].short)})+row("Ship built · guests",function(s){return (s._ship.built||"—")+' · '+(s._ship.guests?s._ship.guests.toLocaleString("en-US"):"n/a")})+
   row("Final payment",function(s){var d=s._line.payment.finalPaymentDays;return d?d+' days before ('+fmtD(addDays(s.depart,-d),{month:"short",day:"numeric",year:"numeric"})+') '+stTag(s._line.payment.status):'Not confirmed'})+
   row("Watch",function(s){return '<span class="note">'+esc(s._it._notes.join(" "))+'</span>'})+
   '<tr class="grp"><th colspan="'+(S.length+1)+'">Planner scores (judgment, /10)</th></tr>'+
   F.map(function(f){return row(esc(f.label),function(s){var v=factors(s)[f.id];return v==null?'—':v.toFixed(1)})}).join("")+
   row("Overall (/100)",function(s){var t=score(s,W).total;return '<b class="num">'+(t==null?'—':Math.round(t))+'</b>'})+
   row("",function(s){return '<button class="btn sm" data-pa="use-sail" data-v="'+esc(s.id)+'">Use in my plan</button>'})+'</tbody></table></div></div>'}
function scatter(rows){
  var pts=rows.filter(function(r){return r.s._total!=null&&r.sc.total!=null});if(pts.length<2)return"";
  var Wd=880,H=280,L=56,R=16,T=14,B=40,xs=pts.map(function(r){return r.s._total}),lo=Math.floor(Math.min.apply(null,xs)/1000)*1000,hi=Math.ceil(Math.max.apply(null,xs)/1000)*1000;
  var ys=pts.map(function(r){return r.sc.total}),ylo=Math.max(0,Math.floor(Math.min.apply(null,ys)/10)*10),yhi=Math.min(100,Math.ceil(Math.max.apply(null,ys)/10)*10);if(yhi===ylo)yhi=ylo+10;
  function x(v){return L+(v-lo)/(hi-lo)*(Wd-L-R)}function y(v){return T+(yhi-v)/(yhi-ylo)*(H-T-B)}
  var g="";for(var v=lo;v<=hi;v+=1000)g+='<line class="gl" x1="'+x(v)+'" x2="'+x(v)+'" y1="'+T+'" y2="'+(H-B)+'"/><text x="'+x(v)+'" y="'+(H-B+16)+'" text-anchor="middle">$'+(v/1000)+'k</text>';
  for(var u=ylo;u<=yhi;u+=10)g+='<line class="gl" x1="'+L+'" x2="'+(Wd-R)+'" y1="'+y(u)+'" y2="'+y(u)+'"/><text x="'+(L-8)+'" y="'+(y(u)+4)+'" text-anchor="end">'+u+'</text>';
  g+='<text x="'+((L+Wd-R)/2)+'" y="'+(H-6)+'" text-anchor="middle">Two cabins + gratuities</text><text x="14" y="'+((T+H-B)/2)+'" text-anchor="middle" transform="rotate(-90 14 '+((T+H-B)/2)+')">Score</text>';
  var d=pts.map(function(r){var s=r.s,c=s._it.glacier?"var("+GLAC[s._it.glacier]+")":"var(--g-none)";return '<circle class="dot" cx="'+x(s._total).toFixed(1)+'" cy="'+y(r.sc.total).toFixed(1)+'" r="6.5" fill="'+c+'"><title>'+esc(s._ship.name+" "+fmtD(s.depart)+": "+money(s._total)+", score "+Math.round(r.sc.total))+'</title></circle>'}).join("");
  return '<div class="card chartcard"><div class="eyebrow">Score against cost</div><p class="note" style="margin:4px 0 10px">Up and to the left is better value for what you weighted. Colors show the glacier day.</p><div class="chartwrap"><svg class="chart" viewBox="0 0 '+Wd+' '+H+'" style="min-width:560px;width:100%" role="img" aria-label="Score against cost">'+g+d+'</svg></div><div class="legend">'+Object.keys(GLAC).map(function(k){return '<span class="pill" style="--c:var('+GLAC[k]+')"><i></i>'+esc(GSHORT[k])+'</span>'}).join("")+'<span class="pill" style="--c:var(--g-none)"><i></i>No glacier day</span></div></div>'}

/* ---------- know before you go ---------- */
function vKnow(){
  var E=D.meta.essentials||{},p=AP(),s=IDX.sail[p.sailing],ln=s._line;
  var cards=["weather","daylight","documents","mobility","congestion"].filter(function(k){return E[k]}).map(function(k){var x=E[k];
    return '<article class="card kcard"><h3>'+esc(x.title)+'</h3><ul>'+x.points.map(function(t){return '<li>'+esc(t)+'</li>'}).join("")+'</ul>'+(x.caveat?'<p class="note">'+esc(x.caveat)+'</p>':'')+(x.sources&&x.sources.length?'<p class="note">Sources: '+x.sources.map(function(id){var so=IDX.sources[id];return so?linkSrc(so.url,so.publisher):""}).join(" · ")+'</p>':'<p class="note">Planner guidance.</p>')+'</article>'}).join("");
  var fp=ln.payment.finalPaymentDays,fpd=fp?addDays(s.depart,-fp):null,fl=flightFor(s),h=p.hotel.id&&IDX.hotel[p.hotel.id];
  var hasInd=p.acts.some(function(a){var r=IDX.offer[a.o];return r&&r.o.kind!=="cruise"&&r.o.pp>0}),hasCr=p.acts.some(function(a){var r=IDX.offer[a.o];return r&&r.o.kind==="cruise"});
  var C=[["passports","Check all four passports are valid through "+fmtD(s.return,{month:"long",day:"numeric",year:"numeric"})+" and names match the bookings."],
   ["book","Book both cabins on "+s._ship.name+" ("+dlong(s.depart)+") together, same booking or linked. Ask for the parents’ balcony mid-ship near an elevator."],
   ["deposit","Deposit: "+(ln.payment.deposit||"check terms at booking")],
   ["final","Final payment: "+(fpd?fmtD(fpd,{weekday:"short",month:"long",day:"numeric",year:"numeric"})+" ("+fp+" days before sailing). After this, cancelling costs the full fare.":"not confirmed for "+ln.name+"; ask at booking.")],
   ["promo",s.flags.indexOf("promo")>-1?"This fare carries a sale label that may end: recheck the price before booking.":null],
   ["access","Request accessible-cabin features, wheelchair or scooter rental, and boarding assistance if the parents want them."],
   ["flights","Book the Alaska Airlines nonstops ("+(fl&&fl.proxy?"fare estimated for these dates":"fare as researched")+"). Google’s insight: cheapest time to book is usually Feb 27 – May 28. Saver fares cannot be changed."],
   ["hotel",h?"Book "+h.name+" for "+dlong(addDays(s.depart,-1))+" with free cancellation; confirm luggage storage and the airport shuttle.":"Choose a Seattle hotel for the night before."],
   ["shore",hasCr?"Cruise-line excursions open for booking after the cruise is paid or in the cruise planner; popular tours sell out.":null],
   ["indep",hasInd?"Independent tours: book directly, note each one’s cancellation rule and meeting point, and keep the operator’s phone number.":null],
   ["insurance","Decide on travel insurance (medical evacuation cover matters in Alaska)."],
   ["return","Return day: "+(fl&&fl.f.returns?"you’re on the "+tm((fl.f.returns[+p.flight.ret]||fl.f.returns[0]).dep)+" flight; ":"")+"choose self-assist or assisted disembarkation and arrange the transfer to SEA."]].filter(function(x){return x[1]});
  var list=C.map(function(c){return '<li><label class="check" for="ck-'+c[0]+'"><input id="ck-'+c[0]+'" type="checkbox" data-pf="check.'+c[0]+'"'+(p.check[c[0]]?' checked':'')+'> <span>'+esc(c[1])+'</span></label></li>'}).join("");
  return '<section class="view"><div class="lede"><p>Weather, documents and practical notes, plus a booking checklist built from your active plan (<b>'+esc(p.name)+'</b>).</p></div>'+
   '<div class="card step"><div class="stephead"><span class="stepn">✓</span><div><h2>Booking checklist</h2><p class="note">'+esc(sailLabel(s))+' · ticks save with the plan.</p></div></div><div class="stepbody"><ul class="checklist">'+list+'</ul></div></div>'+
   '<div class="grid g2">'+cards+'</div></section>'}
