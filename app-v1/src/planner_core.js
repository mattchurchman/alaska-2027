/* ===================== Phase 4: planner core (model, costs, schedule, scores) ===================== */
var COAST=/*__COAST__*/null;
var PL=null, NORM=null, ui={open:{},xf:"all",confirm:null,mapSel:null,mapFocus:null,cmp:store.get("cmp",[])};
function cfg(){return D.meta.planner}
function toMin(t){if(!t)return null;if(t==="23:59"||t==="23:58")return 1440;return (+t.slice(0,2))*60+(+t.slice(3,5))}
function fmtMin(m){if(m==null)return"";if(m>=1440)return"midnight";m=Math.round(m);var h=Math.floor(m/60),mm=m%60;return((h%12)||12)+":"+String(mm).padStart(2,"0")+(h<12?" am":" pm")}
function durTxt(h){if(h==null)return"";var m=Math.round(h*60),H=Math.floor(m/60),M=m%60;return (H?H+" h":"")+(M?(H?" ":"")+M+" min":"")||"0 min"}
function pick(a,f){var b=null,bv=Infinity;a.forEach(function(x){var v=f(x);if(v!=null&&v<bv){bv=v;b=x}});return b}
function sum(a){return a.reduce(function(t,x){return t+(x||0)},0)}
function dlong(s){return fmtD(s,{weekday:"short",month:"short",day:"numeric"})}
function toast(msg){var t=document.getElementById("toast");if(!t){t=document.createElement("div");t.id="toast";t.setAttribute("role","status");document.body.appendChild(t)}t.textContent=msg;t.classList.add("on");clearTimeout(t._h);t._h=setTimeout(function(){t.classList.remove("on")},2600)}

/* ---------- indexes built after prep() ---------- */
function prep4(){
  IDX.exc={};IDX.offer={};IDX.poi={};IDX.hotel={};
  (D.excursions||[]).forEach(function(e){IDX.exc[e.id]=e;e.offers.forEach(function(o){IDX.offer[o.id]={o:o,e:e}})});
  (D.pois||[]).forEach(function(p){IDX.poi[p.id]=p});
  (D.hotels||[]).forEach(function(h){IDX.hotel[h.id]=h});
  NORM=null;
}

/* ---------- stops for a sailing ---------- */
function stopsOf(s){
  if(s._stops)return s._stops;
  var it=s._it,out=[];
  (it.days||[]).forEach(function(day,i){day.forEach(function(e,j){
    var o={day:i,j:j,date:addDays(s.depart,i),type:e.type,place:e.place||null,arr:e.arr||null,dep:e.dep||null};
    if(e.type==="port"){var a=toMin(e.arr),b=toMin(e.dep);o.key=i+"|"+e.place;o.a=a;o.b=b;o.start=a+cfg().offShipH*60;o.allAboard=b-cfg().backAboardH*60;o.usable=Math.max(0,(o.allAboard-o.start)/60);o.portH=(b-a)/60}
    out.push(o)})});
  s._stops=out;return out}
function portStops(s){return stopsOf(s).filter(function(x){return x.type==="port"})}
function stopByKey(s,k){return portStops(s).filter(function(x){return x.key===k})[0]||null}
function offerOK(o,s){return o.kind!=="cruise"||o.line===s._line.id}
function offerHours(o){if(o.hours!=null)return o.hours;return (o.kind==="free"||o.kind==="diy")?cfg().selfGuidedH:3}
function ppl(who){return who==="family"?4:2}
function offerCost(o,who){if(o.pp==null)return null;return o.unit==="pp"?o.pp*ppl(who):o.pp}
function whoTxt(w){return {family:"All 4",parents:"Parents",brothers:"Brothers"}[w]||w}

/* ---------- flights ---------- */
function flightFor(s){
  var F=(D.flights||[]).filter(function(f){return f.stops===0});
  var exact=F.filter(function(f){return f.embarkDate===s.depart&&f.returnDate===s.return})[0];
  if(exact)return {f:exact,proxy:false};
  var base=F.filter(function(f){return f.returnTimesChecked})[0]||F[0];
  return base?{f:base,proxy:true}:null}
function flightOutDate(s){return addDays(s.depart,-1)}

/* ---------- plans ---------- */
function newId(){return "p"+Date.now().toString(36)+Math.random().toString(36).slice(2,6)}
function blankPlan(name,sid){return {id:newId(),name:name,preset:null,sailing:sid,cabins:{brothers:"interior",parents:"balcony"},
  flight:{fare:"saver",out:0,ret:1,bags:4,eachWay:true},hotel:{id:null,rooms:2},acts:[],extras:{},contPct:0,budget:null,check:{},notes:"",updated:new Date().toISOString()}}
function normPlan(p){
  var b=blankPlan(p.name||"My plan",p.sailing);
  ["cabins","flight","hotel"].forEach(function(k){p[k]=Object.assign({},b[k],p[k]||{})});
  ["acts"].forEach(function(k){if(!Array.isArray(p[k]))p[k]=[]});
  ["extras","check"].forEach(function(k){if(!p[k]||typeof p[k]!=="object")p[k]={}});
  if(typeof p.contPct!=="number")p.contPct=0;
  if(!IDX.sail[p.sailing])p.sailing=(presetSailing("balanced")||D.sailings[0]).id;
  p.acts=p.acts.filter(function(a){return a&&IDX.offer[a.o]&&IDX.exc[a.x]});
  return p}
function savePlans(){store.set("plans",PL)}
function AP(){var p=PL.list.filter(function(x){return x.id===PL.active})[0];if(!p){p=PL.list[0];PL.active=p.id}return p}
function touch(p){p.updated=new Date().toISOString();savePlans()}
function loadPlans(){
  var x=store.get("plans",null);
  if(x&&Array.isArray(x.list)){x.list=x.list.filter(function(p){return p&&p.id}).map(normPlan);if(x.list.length){PL=x;AP();return}}
  PL={v:1,active:null,list:[]};
  ["balanced","budget","premium"].forEach(function(k){var p=presetPlan(k);if(p)PL.list.push(p)});
  if(!PL.list.length)PL.list.push(blankPlan("My plan",D.sailings[0].id));
  PL.active=PL.list[0].id;savePlans()}
function plannable(s){return !!(s._it.days&&s._total!=null)}
function presetSailing(k){
  var june=D.sailings.filter(function(s){return s._june&&plannable(s)});
  if(k==="budget")return pick(june,function(s){return s._total});
  if(k==="premium"){var gb=june.filter(function(s){return s._it.glacier==="Glacier Bay"});return pick(gb,function(s){return -(s._it._use||0)*1e5+s._total})||pick(june,function(s){return s._total})}
  var W=defWeights();return pick(june,function(s){return -score(s,W).total})}
function presetHotel(k){
  var H=D.hotels||[];if(!H.length)return null;
  if(k==="budget")return (pick(H.filter(function(h){return h.reviewScore>=4}),function(h){return h.rate.perRoomNight})||{}).id||null;
  if(k==="balanced")return (pick(H.filter(function(h){return h.accessibilityListed}),function(h){return -h.reviewScore*1000+h.rate.perRoomNight})||{}).id||null;
  return (pick(H,function(h){return -h.reviewScore*1000+h.rate.perRoomNight})||{}).id||null}
function presetPlan(k){
  var P=D.meta.presets[k],s=presetSailing(k);if(!s)return null;
  var p=blankPlan(P.label,s.id);p.preset=k;
  p.cabins={brothers:P.cabins.brothers,parents:(s.prices[P.cabins.parents]&&s.prices[P.cabins.parents].pp!=null)?P.cabins.parents:"balcony"};
  p.flight.fare=P.fare;p.hotel.id=presetHotel(k);autoFill(p,k);return p}
function autoFill(p,k){
  var s=IDX.sail[p.sailing],P=D.meta.presets[k];p.acts=[];if(!s||!s._it.days)return;
  portStops(s).forEach(function(st){
    [["family",P.family],["brothers",P.brothers]].forEach(function(g){
      var list=(g[1]||{})[st.place]||[];
      for(var i=0;i<list.length;i++){var e=IDX.exc[list[i]];if(!e||e.ports.indexOf(st.place)<0)continue;var o=pickOffer(e,s,P.offer,p,st,g[0]);if(o){p.acts.push({k:st.key,x:e.id,o:o.id,who:g[0]});break}}})})}
function pickOffer(e,s,mode,p,st,who){
  var c=e.offers.filter(function(o){return offerOK(o,s)&&o.pp!=null&&(o.hours!=null||o.kind==="free")&&fitsNew(p,st,who,o)});
  c.sort(function(a,b){if(mode==="cruise-first"){var ca=a.kind==="cruise"?0:1,cb=b.kind==="cruise"?0:1;if(ca!==cb)return ca-cb}return a.pp-b.pp});
  return c[0]||null}

/* ---------- schedule ---------- */
function lanes(p,st){
  var L={parents:[],brothers:[]},tr=cfg().transitionH*60;
  ["parents","brothers"].forEach(function(g){var t=st.start;
    p.acts.forEach(function(a,i){if(a.k!==st.key||(a.who!==g&&a.who!=="family"))return;var r=IDX.offer[a.o];if(!r)return;
      var start=L[g].length?t+tr:t,end=start+offerHours(r.o)*60;L[g].push({a:a,i:i,o:r.o,e:r.e,start:start,end:end,fits:end<=st.allAboard});t=end})});
  return L}
function laneEnd(l){return l.length?l[l.length-1].end:null}
function fitsNew(p,st,who,o){var L=lanes(p,st),h=offerHours(o)*60;
  return (who==="family"?["parents","brothers"]:[who]).every(function(g){var e=laneEnd(L[g]);var s0=e==null?st.start:e+cfg().transitionH*60;return s0+h<=st.allAboard})}
function actState(p,a,s){
  var r=IDX.offer[a.o];if(!r)return "missing";
  if(!s._it.days)return "untimed";
  if(!stopByKey(s,a.k))return "elsewhere";
  if(!offerOK(r.o,s))return "otherline";
  return "ok"}
function stopWarnings(p,st,L,s){
  var W=[],seen={};
  ["parents","brothers"].forEach(function(g){
    var l=L[g];if(!l.length)return;var last=l[l.length-1];
    l.forEach(function(x){if(!x.fits&&!seen["f"+x.i]){seen["f"+x.i]=1;W.push({lv:"bad",t:x.e.name+" ends at "+fmtMin(x.end)+", after all-aboard ("+fmtMin(st.allAboard)+"). Remove something or pick a shorter option."})}});
    if(last.fits&&(last.o.kind==="independent"||last.o.kind==="reseller")&&st.allAboard-last.end<60&&!seen["t"+last.i]){seen["t"+last.i]=1;W.push({lv:"warn",t:"Tight: "+last.e.name+" ("+last.o.provider+") ends "+Math.round(st.allAboard-last.end)+" min before all-aboard. Independent tours do not hold the ship."})}
  });
  L.parents.forEach(function(x){if(seen["m"+x.e.id])return;
    if(x.e.label==="not_recommended"||x.e.label==="brothers"||x.e.exertion>=3){seen["m"+x.e.id]=1;W.push({lv:"warn",t:"Parents: "+x.e.name+" is rated "+x.e.exertion+"/5 for exertion ("+D.meta.labels[x.e.label]+"). Check against Mom's ~2-mile limit."})}});
  var walky=L.parents.filter(function(x){return x.e.seating!=="seated"});
  if(walky.length>=2)W.push({lv:"warn",t:"Parents have "+walky.length+" activities with walking or standing here. Consider one seated option."});
  if(st.place==="ketchikan_wc"){var needs=p.acts.filter(function(a){var r=IDX.offer[a.o];return a.k===st.key&&r&&r.o.kind!=="cruise"&&r.e.id!=="ktn_wc_shuttle"&&r.e.ports.indexOf("ketchikan")>-1&&r.o.kind!=="independent"}).length;
    var hasSh=p.acts.some(function(a){return a.k===st.key&&a.x==="ktn_wc_shuttle"});
    if(needs&&!hasSh)W.push({lv:"info",t:"Ward Cove is about 7 mi from downtown Ketchikan. Add the Ward Cove shuttle or confirm the tour picks up at Ward Cove."})}
  if(st.place==="sitka"&&p.acts.some(function(a){return a.k===st.key}))W.push({lv:"info",t:"Sitka: ships use a terminal north of town (shuttle) or tender. Allow extra time; confirm closer to sailing."});
  p.acts.forEach(function(a){if(a.k!==st.key)return;var r=IDX.offer[a.o];if(r&&r.e.risk&&!seen["r"+r.e.id]){seen["r"+r.e.id]=1;W.push({lv:"bad",t:r.e.name+": "+r.e.risk.text})}});
  return W}

/* ---------- costs ---------- */
var CATS=[["cruise","Cruise fare"],["grat","Gratuities"],["air","Flights & bags"],["hotel","Seattle hotel"],["act_parents","Activities: parents"],["act_brothers","Activities: brothers"],["act_family","Activities: all 4"],["extra","Your other costs"]];
function cost(p){
  var s=IDX.sail[p.sailing],it=s._it,ln=s._line,items=[],miss=[];
  function add(cat,label,amt,status,who,note,src){if(amt==null){miss.push({cat:cat,label:label,note:note});return}items.push({cat:cat,label:label,amt:amt,status:status,who:who,note:note||"",src:src||null})}
  var cb=s.prices[p.cabins.brothers]||s.prices.interior,cp=s.prices[p.cabins.parents]||s.prices.balcony;
  add("cruise","Brothers' cabin: "+(cb.label||catName(p.cabins.brothers))+" (2 × "+money(cb.pp)+")",cb.pp==null?null:cb.pp*2,cb.status,"brothers",cb.note,s.priceSource.url);
  add("cruise","Parents' cabin: "+(cp.label||catName(p.cabins.parents))+" (2 × "+money(cp.pp)+")",cp.pp==null?null:cp.pp*2,cp.status,"parents",cp.note,s.priceSource.url);
  var g=ln.gratuity&&ln.gratuity.pp_day;
  if(g===0)items.push({cat:"grat",label:"Gratuities (included in "+ln.name+" fares)",amt:0,status:ln.gratuity.status,who:"family",note:ln.gratuity.note||""});
  else{add("grat","Gratuities, brothers ($"+(g||0).toFixed(2)+" × 2 × "+s.nights+" nights)",g==null?null:g*2*s.nights,"estimate","brothers",ln.gratuity&&ln.gratuity.note);
    add("grat","Gratuities, parents ($"+(g||0).toFixed(2)+" × 2 × "+s.nights+" nights)",g==null?null:g*2*s.nights,"estimate","parents",ln.gratuity&&ln.gratuity.note)}
  var fl=flightFor(s);
  if(fl){var fr=fl.f.fare[p.flight.fare]||fl.f.fare.saver,fare=fr&&fr.total4!=null?fr:fl.f.fare.saver,fn=(fare===fl.f.fare.main?"Main":fare===fl.f.fare.first?"First":"Saver");
    add("air","Alaska Airlines nonstop, "+fn+" fare, 4 round trips"+(fl.proxy?" (fare from other June dates)":"")+(fare!==fr?" (chosen fare not captured; Saver used)":""),fare.total4,fl.proxy?"estimate":fare.status,"family",fl.proxy?"No search for "+dlong(flightOutDate(s))+"–"+dlong(s.return)+"; the same nonstop Saver fare ($1,588 for 4) appeared on all six date pairs searched.":fare.note,fl.f.url);
    var bf=fl.f.bags&&fl.f.bags.firstCheckedPerPerson,nb=+p.flight.bags||0;
    if(nb>0)add("air","Checked bags: "+nb+" × $"+bf+(p.flight.eachWay?" × 2 directions":" (once)"),bf==null?null:nb*bf*(p.flight.eachWay?2:1),"estimate","family","Bag fee shown on the Google booking panel; whether it is charged each way was not clear.")}
  else miss.push({cat:"air",label:"Flights",note:"No flight data."});
  var h=p.hotel.id&&IDX.hotel[p.hotel.id];
  if(h){var rooms=+p.hotel.rooms||0,night=addDays(s.depart,-1);
    add("hotel",h.name+": "+rooms+" room"+(rooms===1?"":"s")+" × "+money(h.rate.perRoomNight),h.rate.perRoomNight*rooms,"estimate",rooms===2?"split":"family",(night!==h.stayDate?"Rate is for the night of "+dlong(h.stayDate)+"; your night ("+dlong(night)+") was not searched. ":"")+"Taxes and fees not included.",h.url)}
  p.acts.forEach(function(a){var r=IDX.offer[a.o];if(!r||actState(p,a,s)!=="ok")return;var c=offerCost(r.o,a.who);
    var lab=r.e.name+" · "+r.o.provider+(a.who==="family"?"":" ("+whoTxt(a.who).toLowerCase()+")");
    if(c==null)miss.push({cat:"act_"+a.who,label:lab,note:"Price not captured."});
    else items.push({cat:"act_"+a.who,label:lab+(r.o.unit==="pp"?" · "+money(r.o.pp)+" × "+ppl(a.who):" · per "+r.o.unit),amt:c,status:r.o.status,who:a.who,note:(r.o.from?"'From' price. ":"")+(r.o.note||""),src:r.o.url})});
  var EX=[["transfers","Airport and pier transfers"],["drinks","Drink packages"],["wifi","Wi-Fi"],["insurance","Travel insurance"],["onboard","Onboard spending"],["postHotel","Post-cruise hotel"],["other","Other"]];
  EX.forEach(function(x){var v=p.extras[x[0]];if(v!=null&&v!==""&&!isNaN(+v)&&+v>0)items.push({cat:"extra",label:x[1],amt:+v,status:"user",who:"family",note:""})});
  var sub=sum(items.map(function(i){return i.amt}));
  if(p.contPct>0)items.push({cat:"extra",label:"Contingency ("+p.contPct+"%)",amt:Math.round(sub*p.contPct/100),status:"user",who:"family",note:""});
  var total=sum(items.map(function(i){return i.amt}));
  function share(g){return sum(items.map(function(i){return i.who===g?i.amt:(i.who==="family"||i.who==="split")?i.amt/2:0}))}
  var by={};items.forEach(function(i){by[i.status]=(by[i.status]||0)+i.amt});
  var cat={};items.forEach(function(i){cat[i.cat]=(cat[i.cat]||0)+i.amt});
  var days=Math.round((dt(s.return)-dt(flightOutDate(s)))/864e5)+1;
  return {items:items,miss:miss,total:total,parents:share("parents"),brothers:share("brothers"),pp:total/4,days:days,perDay:total/days,by:by,cat:cat,researched:(by.verified||0)+(by.published||0)}}
function catName(k){return {interior:"Interior",oceanview:"Oceanview",balcony:"Balcony",miniSuite:"Suite tier"}[k]||k}
function planIssues(p){var s=IDX.sail[p.sailing],n={bad:0,warn:0,off:0};
  p.acts.forEach(function(a){if(actState(p,a,s)!=="ok")n.off++});
  portStops(s).forEach(function(st){stopWarnings(p,st,lanes(p,st),s).forEach(function(w){if(w.lv==="bad")n.bad++;else if(w.lv==="warn")n.warn++})});
  return n}
function returnCheck(s,dep){
  var dis=stopsOf(s).filter(function(x){return x.type==="disembark"})[0];if(!dis||!dis.arr)return null;
  var term=s._line.terminal,tr=(cfg().airportTransferMin[term]||45);
  var atAirport=toMin(dis.arr)+cfg().disembarkH*60+tr,slack=toMin(dep)-atAirport;
  var lv=slack>=120?"ok":slack>=75?"warn":"bad";
  return {atAirport:atAirport,slack:slack,lv:lv,arr:dis.arr,tr:tr}}

/* ---------- scores ---------- */
function defWeights(){var w={};D.meta.scoring.factors.forEach(function(f){w[f.id]=f.weight});return w}
function weights(){var w=Object.assign(defWeights(),store.get("weights",{}));return w}
function norms(){if(NORM)return NORM;var t=D.sailings.map(function(s){return s._total}).filter(function(v){return v!=null}),u=D.itineraries.map(function(i){return i._use}).filter(function(v){return v!=null});
  NORM={tMin:Math.min.apply(null,t),tMax:Math.max.apply(null,t),uMin:Math.min.apply(null,u),uMax:Math.max.apply(null,u)};return NORM}
function factors(s){
  if(s._fac)return s._fac;var it=s._it,N=norms(),sc=D.meta.scoring,f={};
  var scen=0;(it.days||[]).forEach(function(d){d.forEach(function(e){if(e.type==="scenic")scen++})});if(!it.days)scen=(it.ports||[]).filter(function(p){return IDX.places[p].kind==="scenic"}).length;
  f.scenic=Math.min(10,(sc.glacier[it.glacier||"none"]||3)+(scen>=2?0.5:0));
  var m=10,wc=0,sit=0,short=0,sea=it._sea||0;
  if(it.days){it.days.forEach(function(d){d.forEach(function(e){if(e.type!=="port")return;if(e.place==="ketchikan_wc")wc++;if(e.place==="sitka")sit++;var pl=IDX.places[e.place];if(pl.country==="US"&&hrs(e.arr,e.dep)-1.5<4)short++})})}
  else{m-=2;(it.ports||[]).forEach(function(p){if(p==="ketchikan_wc")wc++;if(p==="sitka")sit++})}
  m+=-1.5*wc-sit-0.5*short+Math.min(1,0.5*sea);f.mobility=Math.max(0,Math.min(10,m));
  f.value=s._total==null?null:(N.tMax===N.tMin?10:10*(N.tMax-s._total)/(N.tMax-N.tMin));
  var set={};(it._akPorts||[]).forEach(function(p){set[p==="ketchikan_wc"?"ketchikan":p]=1});f.excursions=Math.min(10,2*Object.keys(set).length);
  f.portTime=it._use==null?null:(N.uMax===N.uMin?10:10*(it._use-N.uMin)/(N.uMax-N.uMin));
  var b=s._ship.built;f.comfort=b==null?null:b>=2017?10:b>=2008?7:4;
  s._fac=f;return f}
function score(s,W){var f=factors(s),t=0,w=0,miss=[];Object.keys(W).forEach(function(k){if(!W[k])return;if(f[k]==null){miss.push(k);return}t+=f[k]*W[k];w+=W[k]});return {f:f,total:w?t/w*10:null,miss:miss}}
function shipSize(s){var g=s._ship.guests;return g==null?"unknown":g<2600?"small":g<4000?"mid":"large"}
function tripBase(s){var p=AP(),fl=flightFor(s),h=(p.hotel.id&&IDX.hotel[p.hotel.id])||IDX.hotel.hampton_airport;
  var air=fl?(fl.f.fare.saver.total4):null;var hot=h?h.rate.perRoomNight*2:0;
  return {amt:s._total==null||air==null?null:s._total+air+hot,air:air,hot:hot,hname:h?h.name:"",proxy:fl&&fl.proxy}}
