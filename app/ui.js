/* Alaska 2027 planner (v2) — screens: Ideas, Route, Line & ship, Dates (Days, Cost and Shortlist live in plan.js).
   State lives in the URL hash (#view=…&route=…&ship=…&sailing=…) so any view can be shared. */
(function () {
  'use strict';
  const M = window.AK;
  const $ = (s, el) => (el || document).querySelector(s);
  const $$ = (s, el) => Array.from((el || document).querySelectorAll(s));
  const VIEWS = ['ideas', 'route', 'ship', 'date', 'days', 'cost', 'short'];
  const GLACIERS = ['glacier_bay', 'hubbard', 'endicott_arm', 'tracy_arm', 'college_fjord', 'stikine_icecap'];
  const LABEL_MIN = {
    sea_p91: 3, yvr_canada_place: 3, whittier: 4, seward: 5, juneau: 5, skagway: 5, ketchikan: 5, ketchikan_wc: 8,
    sitka: 5, icy_strait: 6, victoria: 5, prince_rupert: 5, haines: 6, glacier_bay: 5, hubbard: 4, college_fjord: 5,
    tracy_arm: 6, endicott_arm: 6, stephens_passage: 7, inside_passage_bc: 5, stikine_icecap: 6
  };
  const LABEL_NAME = { sea_p91: 'Seattle', yvr_canada_place: 'Vancouver', ketchikan_wc: 'Ward Cove' };
  const LS_KEY = 'ak27v2:last';

  const S = { view: 'ideas', route: null, ship: null, sailing: null, june: false, day: null };

  /* ---------------- helpers ---------------- */
  function esc(v) {
    return String(v == null ? '' : v).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  }
  function attrs(o) { return Object.keys(o).filter(k => o[k] != null && o[k] !== false).map(k => ' ' + k + '="' + esc(o[k]) + '"').join(''); }
  function statusPill(st, label) {
    return '<span class="status st-' + esc(st) + '" title="' + esc((M.meta.statusDefinitions[st] || {}).desc || '') + '">' + esc(label || M.STATUS_SHORT[st] || st) + '</span>';
  }
  function lineBadge(lid) {
    const l = M.line[lid];
    if (!l) return '';
    return '<span class="badge" style="background:' + esc(l.color) + '" title="' + esc(l.name) + '">' + esc(l.badge) + '</span>';
  }
  function routeTag(rid, act) {
    const r = M.route[rid];
    if (!r) return '';
    const inner = esc(r.short || r.name);
    if (act) return '<button type="button" class="chip" data-act="route" data-route="' + esc(rid) + '"><span class="sw" style="background:' + esc(r.color) + '"></span>' + inner + '</button>';
    return '<span class="tag route" style="background:' + esc(r.color) + '">' + inner + '</span>';
  }
  function photoHTML(p, o) {
    o = o || {};
    const ratio = o.ratio ? ' r-' + o.ratio : '';
    const label = o.label || (p && p.alt) || '';
    if (!p) {
      return '<figure class="ph noimg' + ratio + (o.cls ? ' ' + o.cls : '') + '"><div class="ph-fallback">' + esc(label) + '</div></figure>';
    }
    return '<figure class="ph' + ratio + (o.cls ? ' ' + o.cls : '') + '">' +
      '<img' + attrs({ src: p.url, alt: p.alt || label, loading: o.eager ? null : 'lazy', decoding: 'async', width: p.w, height: p.h }) + ' onerror="this.parentNode.classList.add(\'noimg\')">' +
      '<div class="ph-fallback">' + esc(label) + '</div>' +
      (o.noCredit ? '' : '<figcaption><a href="' + esc(p.page || p.url) + '" target="_blank" rel="noopener">' + esc(shortCredit(p.credit)) + '</a></figcaption>') +
      '</figure>';
  }
  function shortCredit(c) { return 'Photo: ' + String(c || 'Wikimedia Commons').replace(/\s*\/\s*Wikimedia Commons\s*/i, ' · '); }
  function placeName(pid, short) {
    const p = M.place[pid];
    if (!p) return pid;
    return short ? (p.short || p.name) : p.name;
  }
  function plural(n, w) { return n + ' ' + w + (n === 1 ? '' : 's'); }
  function toast(msg) {
    const t = $('#toast');
    t.textContent = msg;
    t.classList.add('on');
    clearTimeout(toast._t);
    toast._t = setTimeout(() => t.classList.remove('on'), 2600);
  }
  function lsGet(k) { try { return JSON.parse(localStorage.getItem(k)); } catch (e) { return null; } }
  function lsSet(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) { /* private mode */ } }

  /* ---------------- state & hash ---------------- */
  function hashOf(st) {
    const p = new URLSearchParams();
    p.set('view', st.view);
    if (st.route) p.set('route', st.route);
    if (st.ship) p.set('ship', st.ship);
    if (st.sailing) p.set('sailing', st.sailing);
    if (st.june) p.set('june', '1');
    if (st.view === 'days' && st.sailing && st.day != null) p.set('day', String(st.day));
    if (st.withPlan && st.sailing && window.AKP) { const pl = window.AKP.planFor(st.sailing); const enc = M.encodePlan(pl); if (enc) p.set('plan', enc); p.set('cab', M.encodeCab(pl.cab || {})); }
    return '#' + p.toString();
  }
  function readHash(h) {
    const p = new URLSearchParams((h || '').replace(/^#/, ''));
    const st = {};
    const v = p.get('view');
    st.view = VIEWS.includes(v) ? v : null;
    const r = p.get('route'); st.route = r && M.route[r] ? r : null;
    const sh = p.get('ship'); st.ship = sh && M.ship[sh] ? sh : null;
    const sa = p.get('sailing'); st.sailing = sa && M.sailing[sa] ? sa : null;
    st.june = p.get('june') === '1';
    const dy = p.get('day'); st.day = dy != null && /^\d+$/.test(dy) ? +dy : null;
    if (p.get('plan') != null || p.get('cab') != null) st.shared = { plan: p.get('plan') || '', cab: p.get('cab') || '' };
    if (st.sailing) st.ship = st.ship || M.sailing[st.sailing].ship; // a sailing implies its ship
    if (!st.view && (st.sailing || st.route)) st.view = st.sailing ? 'date' : 'route';
    return st;
  }
  let lastRenderedView = null;
  function go(patch, push) {
    Object.assign(S, patch);
    const h = hashOf(S);
    if (location.hash !== h) {
      if (push) history.pushState(null, '', h); else history.replaceState(null, '', h);
    }
    lsSet(LS_KEY, { route: S.route, ship: S.ship, sailing: S.sailing, june: S.june, view: S.view, day: S.day });
    render();
  }
  function fromLocation() {
    if (location.hash === hashOf(S)) return; // popstate and hashchange can both fire for one step
    const st = readHash(location.hash);
    const shared = st.shared; delete st.shared;
    Object.assign(S, { route: null, ship: null, sailing: null, june: false, shipOnly: false, day: null }, st);
    if (!S.view) S.view = 'ideas';
    if (shared && S.sailing && window.AKP) { window.AKP.receiveShared(S.sailing, shared); history.replaceState(null, '', hashOf(S)); }
    render();
  }
  window.addEventListener('popstate', fromLocation);
  window.addEventListener('hashchange', fromLocation);

  /* ---------------- render ---------------- */
  function render() {
    $$('.steps a').forEach(a => { if (a.dataset.view === S.view) a.setAttribute('aria-current', 'page'); else a.removeAttribute('aria-current'); });
    const curStep = $('.steps a[aria-current="page"]'), steps = $('.steps');
    if (curStep && steps && (curStep.offsetLeft + curStep.offsetWidth > steps.scrollLeft + steps.clientWidth || curStep.offsetLeft < steps.scrollLeft)) steps.scrollLeft = curStep.offsetLeft - 12;
    $$('.view').forEach(v => { v.hidden = v.dataset.view !== S.view; });
    const changed = lastRenderedView !== S.view;
    if (S.view === 'ideas') renderIdeas();
    if (S.view === 'route') renderRoute();
    if (S.view === 'ship') renderShip();
    if (S.view === 'date') renderDate();
    if (['days', 'cost', 'short'].includes(S.view) && window.AKP) window.AKP.render(S.view);
    if (window.AKP) window.AKP.renderShared();
    renderPickbar();
    if (changed) {
      if (lastRenderedView) window.scrollTo(0, 0);
      lastRenderedView = S.view;
      const titles = { ideas: 'Ideas', route: 'Routes', ship: 'Lines & ships', date: 'Dates', days: 'Days', cost: 'Cost', short: 'Shortlist' };
      document.title = titles[S.view] + ' · Alaska 2027 Planner';
    }
  }

  /* ---------------- Ideas ---------------- */
  function routeStats(rid) {
    const list = M.sailingsFor({ route: rid });
    const best = M.cheapest(list);
    const lines = Array.from(new Set(list.map(s => s._line)));
    const first = list[0], last = list[list.length - 1];
    return { list, best, lines, first, last };
  }
  function glacierPhotoForRoute(r) {
    const g = r.glacier || (r.id === 'YVR-N' ? 'college_fjord' : r.id === 'YVR-S' ? 'hubbard' : r.id === 'YVR-RT' ? 'inside_passage_bc' : null);
    return M.photo(['place:' + g, 'place:' + (r.gateway === 'SEA' ? 'sea_p91' : 'yvr_canada_place')]);
  }
  function renderIdeas() {
    const el = $('#v-ideas');
    if (el.dataset.built) return;
    const hero = M.photo(['place:glacier_bay']);
    const all = M.sailings;
    const cheapest = M.cheapest(all);
    const juneBest = M.cheapest(all.filter(M.inJune));
    const gbBest = M.cheapest(all.filter(s => M.stopsOf(M.itin[s.itinerary]).includes('glacier_bay')));
    let mostAshore = null, mostH = -1;
    all.forEach(s => { const f = M.itinFacts(M.itin[s.itinerary]); if (f.alaskaH != null && f.alaskaH > mostH && s._two.total != null) { mostH = f.alaskaH; mostAshore = s; } });
    const tv = M.meta.travelers || {};

    function quick(k, s, extra) {
      if (!s) return '';
      const sh = M.ship[s.ship];
      return '<button type="button" data-act="sailing" data-sailing="' + esc(s.id) + '">' +
        '<span class="k">' + esc(k) + '</span>' +
        '<span class="v">' + (extra ? esc(extra) : M.fmtUsd(s._two.total)) + '</span>' +
        '<span class="s">' + lineBadge(s._line) + ' ' + esc(sh.name) + ' · ' + esc(M.fmtDate(s.depart, true)) + '</span>' +
        '<span class="s" style="margin-top:6px">' + routeTag(s._route) + ' ' + statusPill(s._two.status) + '</span></button>';
    }

    const routeCards = M.routes.map(r => {
      const st = routeStats(r.id);
      return '<article class="card route-card">' +
        '<div class="stripe" style="background:' + esc(r.color) + '"></div>' +
        photoHTML(glacierPhotoForRoute(r), { ratio: '16x9', label: r.name }) +
        '<div class="card-body">' +
        '<h3>' + esc(r.name) + '</h3>' +
        '<div class="best">' + esc(r.bestFor || '') + '</div>' +
        '<p class="why">' + esc(r.why || '') + '</p>' +
        '<p class="trade"><b>Trade-off:</b> ' + esc(r.tradeoff || '') + '</p>' +
        '<div class="stats">' +
        '<span><b>' + st.list.length + '</b> sailings</span>' +
        '<span>' + st.lines.map(lineBadge).join(' ') + '</span>' +
        (st.best ? '<span>from <b>' + M.fmtUsd(st.best._two.total) + '</b> for two cabins ' + statusPill(st.best._two.status) + '</span>' : '<span>Two-cabin price not captured</span>') +
        (st.first ? '<span>' + esc(M.fmtDate(st.first.depart)) + ' – ' + esc(M.fmtDate(st.last.depart)) + '</span>' : '') +
        '</div>' +
        '<div class="actions"><button class="btn small" type="button" data-act="route" data-route="' + esc(r.id) + '">See it on the map</button>' +
        '<button class="btn small ghost" type="button" data-act="dates" data-route="' + esc(r.id) + '">Dates &amp; prices</button></div>' +
        '</div></article>';
    }).join('');

    const guide = M.meta.glacierGuide || {};
    const glacierCards = GLACIERS.filter(g => M.place[g]).map(g => {
      const p = M.place[g];
      const routes = M.routesForPlace(g);
      const gd = guide[g];
      return '<article class="card">' + photoHTML(M.photo(['place:' + g]), { ratio: '3x2', label: p.name }) +
        '<div class="card-body"><h3>' + esc(p.name) + '</h3>' +
        '<p class="small" style="color:var(--ink2);margin-top:6px">' + esc((gd && gd.summary) || p.notes || '') + '</p>' +
        (routes.length ? '<div class="chips" style="margin-top:8px">' + routes.map(r => routeTag(r.id, true)).join('') + '</div>' : '') +
        '</div></article>';
    }).join('');
    const guideReady = Object.keys(guide).length > 0;

    el.innerHTML =
      '<div class="hero">' + photoHTML(hero, { label: 'Glacier Bay', eager: true }) +
      '<div class="hero-text"><h1>Seven nights in Alaska, June 2027</h1>' +
      '<p>Four of us from Albuquerque: two brothers in an interior cabin and the parents in a balcony cabin. Start with the kind of route you want, then pick a line, a ship and a date.</p>' +
      '<button class="btn light" type="button" data-act="view" data-view="route">Explore the routes</button></div></div>' +

      '<div class="travelers">' +
      '<div class="trav"><span class="ico">P</span><div><b>Parents · ' + esc((tv.parents || {}).age || '') + '</b><span class="small muted">Balcony cabin, near the elevators. Mom’s walking limit is under about 2 miles a day.</span></div></div>' +
      '<div class="trav"><span class="ico">B</span><div><b>Brothers · ' + esc((tv.brothers || {}).age || '') + '</b><span class="small muted">Shared interior cabin. Budget-minded and up for adventure.</span></div></div>' +
      '<div class="trav"><span class="ico">✓</span><div><b>Flying from ' + esc(tv.homeAirport || 'ABQ') + '</b><span class="small muted">US citizens with passports. No loyalty programs.</span></div></div>' +
      '</div>' +

      '<div><div class="section-head"><div><h2>Quick answers</h2><p>Two cabins (interior + balcony, 2 adults each), cruise fare with taxes and port fees, before tips. Tap one to see it.</p></div></div>' +
      '<div class="quick">' +
      quick('Lowest two-cabin fare', cheapest) +
      quick('Lowest in June', juneBest) +
      quick('Lowest with Glacier Bay', gbBest) +
      quick('Most time ashore in Alaska', mostAshore, mostAshore ? M.fmtHours(mostH) : '') +
      '</div></div>' +

      '<div><div class="section-head"><div><h2>Eight kinds of route</h2><p>Seattle round trips are the simplest from Albuquerque. Vancouver and one-way trips add scenery or glaciers, and some travel.</p></div></div>' +
      '<div class="grid cols-3">' + routeCards + '</div></div>' +

      '<div><div class="section-head"><div><h2>The glacier day</h2><p>Most routes spend one day cruising up to a glacier. Which one you get depends on the route and the line.</p></div></div>' +
      '<div class="glaciers">' + glacierCards + '</div>' +
      (guideReady ? '' : '<p class="note-box" style="margin-top:12px">More on each glacier (how close ships usually get, whether rangers come aboard, the best viewing spots for the parents) is still being researched and will be added here.</p>') +
      '</div>' +
      '<div class="next-row"><button class="btn" type="button" data-act="view" data-view="route">Next: compare routes on the map →</button></div>';
    el.dataset.built = '1';
  }

  /* ---------------- maps ---------------- */
  function makeMap(elId) {
    if (!window.L) return null;
    const map = L.map(elId, { zoomControl: true, scrollWheelZoom: false, attributionControl: true, worldCopyJump: false, minZoom: 3, maxZoom: 12, zoomSnap: 0.5 });
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19, attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);
    map.attributionControl.setPrefix('<a href="https://leafletjs.com">Leaflet</a>');
    map.on('click', () => map.scrollWheelZoom.enable());
    map.on('mouseout', () => map.scrollWheelZoom.disable());
    return map;
  }
  function pinIcon(p, cls) {
    return L.divIcon({ className: 'pin ' + p.kind + (cls ? ' ' + cls : ''), html: '<i></i>', iconSize: [34, 34], iconAnchor: [17, 17] });
  }
  function placePopup(pid) {
    const p = M.place[pid];
    const routes = M.routesForPlace(pid);
    return '<div class="pop">' + photoHTML(M.photo(['place:' + pid]), { label: p.name, noCredit: false }) +
      '<div class="pop-body"><h4>' + esc(p.name) + '</h4>' +
      (p.dock ? '<p><b>Dock:</b> ' + esc(p.dock) + '</p>' : '') +
      (p.notes ? '<p>' + esc(p.notes) + '</p>' : '') +
      (routes.length ? '<div class="chips">' + routes.map(r => routeTag(r.id, true)).join('') + '</div>' : '') +
      '</div></div>';
  }
  function addPins(map, ids, opts) {
    opts = opts || {};
    const layer = L.layerGroup().addTo(map);
    const markers = {};
    ids.forEach(pid => {
      const p = M.place[pid];
      if (!p || p.lat == null || pid === 'sea_airport') return;
      const m = L.marker([p.lat, p.lng], { icon: pinIcon(p, opts.cls && opts.cls(pid)), keyboard: true, title: p.name, riseOnHover: true });
      m.bindPopup(() => placePopup(pid), { maxWidth: 260, minWidth: 260, autoPanPadding: [20, 70] });
      const lmin = LABEL_MIN[pid] || 6;
      if (lmin < 90) {
        m.bindTooltip(LABEL_NAME[pid] || p.short || p.name, { permanent: true, direction: p.kind === 'scenic' ? 'left' : 'right', offset: [p.kind === 'scenic' ? -8 : 8, 0], className: 'lbl', interactive: false });
      }
      m._lmin = lmin;
      m.addTo(layer);
      markers[pid] = m;
    });
    function labels() {
      const z = map.getZoom();
      Object.values(markers).forEach(m => {
        const tt = m.getTooltip();
        if (!tt) return;
        if (z >= m._lmin) { if (!m.isTooltipOpen()) m.openTooltip(); } else if (m.isTooltipOpen()) m.closeTooltip();
      });
    }
    map.on('zoomend', labels);
    setTimeout(labels, 0);
    return { layer, markers, labels };
  }
  function lineStyle(r, mode) {
    const base = { color: r.color, dashArray: r.dash || null, lineCap: 'round', lineJoin: 'round' };
    if (mode === 'on') return Object.assign(base, { weight: 5, opacity: 1 });
    if (mode === 'dim') return Object.assign(base, { weight: 2, opacity: 0.07 });
    return Object.assign(base, { weight: 3.5, opacity: 0.85 });
  }

  /* ---------------- Route ---------------- */
  let RM = null; // route map state
  function buildRouteMap() {
    const map = makeMap('routeMap');
    if (!map) { $('#routeMap').innerHTML = '<div class="cal-empty">The map could not load.</div>'; return null; }
    const lines = [];
    const bounds = L.latLngBounds([]);
    M.itins.forEach(it => {
      if (!it.mapLine || !it.mapLine.length) return;
      const r = M.route[it.routeFamily];
      const vis = L.polyline(it.mapLine, Object.assign(lineStyle(r), { interactive: false })).addTo(map);
      const hit = L.polyline(it.mapLine, { weight: 22, opacity: 0.001, color: '#000' }).addTo(map);
      hit.on('click', e => { L.DomEvent.stop(e); go({ route: it.routeFamily }, false); });
      hit.bindTooltip(r.name, { sticky: true });
      lines.push({ it, r, vis, hit });
      bounds.extend(vis.getBounds());
    });
    const ids = M.places.map(p => p.id);
    const pins = addPins(map, ids);
    map.fitBounds(bounds, { paddingTopLeft: [20, 20], paddingBottomRight: [80, 20] });
    return { map, lines, pins, bounds };
  }
  function styleRouteMap() {
    if (!RM) return;
    const sel = S.route;
    RM.lines.forEach(o => {
      const mode = !sel ? 'all' : (o.it.routeFamily === sel ? 'on' : 'dim');
      o.vis.setStyle(lineStyle(o.r, mode));
      if (mode === 'on') o.vis.bringToFront();
    });
    const stops = new Set();
    if (sel) M.itins.filter(it => it.routeFamily === sel).forEach(it => M.stopsOf(it).forEach(p => stops.add(p)));
    Object.keys(RM.pins.markers).forEach(pid => {
      const el = RM.pins.markers[pid].getElement();
      if (el) el.classList.toggle('dim', !!sel && !stops.has(pid));
    });
  }
  function fitRoute() {
    if (!RM) return;
    if (!S.route) { RM.map.fitBounds(RM.bounds, { paddingTopLeft: [20, 20], paddingBottomRight: [80, 20] }); return; }
    const b = L.latLngBounds([]);
    RM.lines.forEach(o => { if (o.it.routeFamily === S.route) b.extend(o.vis.getBounds()); });
    if (b.isValid()) RM.map.fitBounds(b, { paddingTopLeft: [24, 24], paddingBottomRight: [80, 24] });
  }
  let routeShown = null;
  function renderRoute() {
    if (!RM) RM = buildRouteMap();
    if (RM) setTimeout(() => { RM.map.invalidateSize(); if (routeShown !== S.route) { fitRoute(); routeShown = S.route; } styleRouteMap(); }, 0);
    const panel = $('#routePanel');
    const legend = M.routes.map(r => {
      const st = routeStats(r.id);
      return '<button type="button" data-act="route" data-route="' + esc(r.id) + '" aria-pressed="' + (S.route === r.id) + '">' +
        '<span class="sw' + (r.dash ? ' dash' : '') + '" style="background:' + esc(r.color) + '"></span>' +
        '<span class="nm">' + esc(r.name) + '</span>' +
        '<span class="ct">' + plural(st.list.length, 'sailing') + (st.best ? '<br>from ' + M.fmtK(st.best._two.total) : '') + '</span></button>';
    }).join('');
    let detail = '';
    if (S.route) {
      const r = M.route[S.route];
      const st = routeStats(r.id);
      const ships = M.shipsOnRoute(r.id);
      const rows = ships.map(sh => {
        const sl = M.sailingsFor({ route: r.id, ship: sh.id });
        const best = M.cheapest(sl);
        const itNames = Array.from(new Set(sl.map(s => M.itin[s.itinerary].name)));
        return '<div class="ship-row">' + photoHTML(M.photo(['ship:' + sh.id]), { label: sh.name, noCredit: true }) +
          '<div class="info"><b>' + lineBadge(sh.line) + ' ' + esc(sh.name) + '</b>' +
          '<span>' + esc(itNames.join(' · ')) + '</span>' +
          '<span>' + plural(sl.length, 'date') + (best ? ' · from ' + M.fmtUsd(best._two.total) + ' for two cabins' : ' · two-cabin price not captured') + '</span></div>' +
          '<div class="acts"><button class="btn small ghost" type="button" data-act="ship" data-ship="' + esc(sh.id) + '">Ship</button>' +
          '<button class="btn small" type="button" data-act="dates" data-route="' + esc(r.id) + '" data-ship="' + esc(sh.id) + '">Dates</button></div></div>';
      }).join('');
      detail = '<div class="card"><div class="stripe" style="height:6px;background:' + esc(r.color) + '"></div><div class="card-body">' +
        '<h3>' + esc(r.name) + '</h3>' +
        '<p class="small" style="color:var(--teal);font-weight:600;margin:4px 0 8px">' + esc(r.bestFor || '') + '</p>' +
        '<p>' + esc(r.why || '') + '</p><p class="small muted"><b>Trade-off:</b> ' + esc(r.tradeoff || '') + '</p>' +
        '<p class="small">' + plural(st.list.length, 'sailing') + ' on ' + plural(ships.length, 'ship') + (st.best ? ', from <b>' + M.fmtUsd(st.best._two.total) + '</b> for two cabins ' + statusPill(st.best._two.status) : '') + '.</p>' +
        '<div class="next-row" style="justify-content:flex-start"><button class="btn small" type="button" data-act="view" data-view="ship">Compare these ships →</button>' +
        '<button class="btn small ghost" type="button" data-act="dates" data-route="' + esc(r.id) + '">All dates</button>' +
        '<button class="btn small ghost" type="button" data-act="route" data-route="">Show all routes</button></div>' +
        '</div></div>' +
        '<div><h3 style="margin-bottom:8px">Ships on this route</h3><div class="ship-list">' + rows + '</div></div>';
    } else {
      detail = '<p class="note-box">Tap a route (or a coloured line on the map) to see which ships sail it. Tap a pin for a photo and notes on that stop.</p>';
    }
    panel.innerHTML = '<div><h2>Routes</h2><p class="muted small" style="margin-top:4px">Each colour is one kind of route. Dashed lines are one-way trips.</p></div>' +
      '<div class="legend">' + legend + '</div>' + detail;
  }

  /* ---------------- Line & ship ---------------- */
  function shipDocks(shipId, route) {
    const out = new Map();
    M.itins.filter(it => (it.ship === shipId || (it.ships || []).includes(shipId)) && (!route || it.routeFamily === route)).forEach(it => {
      M.stopsOf(it).forEach(pid => { const p = M.place[pid]; if (p && p.kind === 'port' && p.dock && M.isAlaskaPort(pid)) out.set(pid, p.dock); });
    });
    return out;
  }
  function videoHTML(v, poster) {
    return '<div class="video" data-embed="' + esc(v.embed) + '"><button type="button" class="poster" data-act="play"' +
      (poster ? ' style="background-image:url(&quot;' + esc(poster.url) + '&quot;)"' : '') +
      ' aria-label="Play video: ' + esc(v.title) + '"><span class="play"></span>' +
      '<span class="vt"><b>' + esc(v.title) + '</b><span>' + esc(v.channel) + ' · ' + esc(M.fmtDate(v.published)) + ' ' + esc(v.published.slice(0, 4)) + (v.length ? ' · ' + esc(v.length) : '') + ' · loads from YouTube</span></span></button></div>';
  }
  function renderShip() {
    const el = $('#v-ship');
    const route = S.route;
    const ships = M.shipsOnRoute(route);
    const byLine = {};
    ships.forEach(sh => { (byLine[sh.line] = byLine[sh.line] || []).push(sh); });
    const chips = '<div class="chips scroll" role="group" aria-label="Filter by route">' +
      '<button type="button" class="chip" data-act="route-filter" data-route="" aria-pressed="' + (!route) + '">All routes</button>' +
      M.routes.map(r => '<button type="button" class="chip" data-act="route-filter" data-route="' + esc(r.id) + '" aria-pressed="' + (route === r.id) + '"><span class="sw" style="background:' + esc(r.color) + '"></span>' + esc(r.short || r.name) + '</button>').join('') + '</div>';
    const groups = M.lines.filter(l => byLine[l.id]).map(l => {
      const cards = byLine[l.id].map(sh => shipCard(sh, route)).join('');
      return '<section class="line-group"><div class="line-head">' + lineBadge(l.id) + '<h3>' + esc(l.name) + '</h3>' +
        (l.glacierBayPermit ? '<span class="tag" style="background:var(--ice);color:var(--teal)">Glacier Bay permits</span>' : '') + '</div>' +
        '<details class="about"><summary>About ' + esc(l.name) + ' in Alaska</summary><div>' +
        (l.alaskaNotes ? '<p>' + esc(l.alaskaNotes) + '</p>' : '') +
        (l.includes ? '<p><b>Fare includes:</b> ' + esc(l.includes) + '</p>' : '') +
        (l.fareBasis ? '<p><b>Prices shown:</b> ' + esc(l.fareBasis) + '</p>' : '') +
        (l.payment && l.payment.deposit ? '<p><b>Deposit:</b> ' + esc(l.payment.deposit) + (l.payment.finalPaymentDays ? ' Final payment ' + esc(l.payment.finalPaymentDays) + ' days before sailing.' : '') + ' ' + statusPill(l.payment.status || 'unavailable') + '</p>' : '') +
        '</div></details>' +
        '<div class="grid cols-2">' + cards + '</div></section>';
    }).join('');
    el.innerHTML = '<div><div class="section-head"><div><h2>' + (route ? 'Ships on ' + esc(M.route[route].name) : 'All lines and ships') + '</h2>' +
      '<p>Photos, quick facts, a ship tour video and what matters for the parents. Prices are for two cabins on this route.</p></div></div>' + chips + '</div>' +
      groups +
      '<div class="next-row"><button class="btn" type="button" data-act="view" data-view="date">Next: pick a date →</button></div>';
    if (S.ship && lastShipScrolled !== S.ship + '|' + route) {
      lastShipScrolled = S.ship + '|' + route;
      const id = 'ship-' + S.ship;
      setTimeout(() => { const card = document.getElementById(id); if (card) card.scrollIntoView({ block: 'start' }); }, 80);
    }
  }
  let lastShipScrolled = null;
  function shipCard(sh, route) {
    const l = M.line[sh.line];
    const sl = M.sailingsFor({ route, ship: sh.id });
    const best = M.cheapest(sl);
    const photo = M.photo(['ship:' + sh.id]);
    const vids = (M.videosBy['ship:' + sh.id] || []).slice(0, 2);
    const links = M.linksBy['ship:' + sh.id] || [];
    const docks = shipDocks(sh.id, route);
    const routes = Array.from(new Set(M.sailingsFor({ ship: sh.id }).map(s => s._route)));
    const glaciers = new Set();
    M.itins.filter(it => it.ship === sh.id && (!route || it.routeFamily === route)).forEach(it => M.itinFacts(it).scenic.forEach(g => { if (GLACIERS.includes(g)) glaciers.add(g); }));
    const facts = [];
    if (sh.built) facts.push('<span class="tag">Built ' + esc(sh.built) + '</span>');
    if (sh.refit) facts.push('<span class="tag">Refit ' + esc(sh.refit) + '</span>');
    if (sh.guests) facts.push('<span class="tag" title="' + esc(sh.guestsSource || '') + '">' + esc(sh.guests.toLocaleString('en-US')) + ' guests</span>');
    const size = sh.guests ? (sh.guests < 1500 ? 'Smaller ship' : sh.guests < 2600 ? 'Mid-size ship' : sh.guests < 4000 ? 'Large ship' : 'Very large ship') : null;
    if (size) facts.push('<span class="tag">' + size + '</span>');
    const dates = sl.slice(0, 12).map(s => '<button type="button" data-act="sailing" data-sailing="' + esc(s.id) + '"' + (S.sailing === s.id ? ' aria-pressed="true" style="border-color:var(--ink)"' : '') + '><b>' + esc(M.fmtDate(s.depart)) + '</b>' + esc(M.fmtK(s._two.total)) + '</button>').join('');
    return '<article class="card ship-card" id="ship-' + esc(sh.id) + '"' + (S.ship === sh.id ? ' style="box-shadow:0 0 0 2px var(--ink),var(--shadow)"' : '') + '>' +
      photoHTML(photo, { ratio: '16x9', label: sh.name }) +
      '<div class="card-body">' +
      '<div style="display:flex;align-items:center;gap:8px">' + lineBadge(sh.line) + '<h3>' + esc(sh.name) + '</h3></div>' +
      '<div class="facts">' + facts.join('') + '</div>' +
      (sh.note ? '<p class="small">' + esc(sh.note) + '</p>' : '') +
      '<div class="chips">' + routes.map(r => routeTag(r, false)).join(' ') + '</div>' +
      '<div class="parents"><b>For the parents</b><ul>' +
      (l.accessibility ? '<li>' + esc(l.accessibility) + '</li>' : '') +
      (glaciers.size ? '<li>Glacier day: ' + esc(Array.from(glaciers).map(g => placeName(g)).join(', ')) + '. A balcony on the right side helps; the ship usually turns so both sides get a view.</li>' : '<li>No scheduled glacier day on this route.</li>') +
      (docks.size ? '<li>Alaska stops: ' + Array.from(docks).map(([pid, dk]) => esc(placeName(pid, true)) + ' (' + esc(dk) + ')').join('; ') + '.</li>' : '') +
      '<li>Ask for a balcony cabin near a mid-ship elevator when booking; cabin location is not in this planner’s data.</li>' +
      '</ul></div>' +
      (vids.length ? '<div class="videos">' + vids.map(v => videoHTML(v, photo)).join('') + '</div>' : '') +
      (links.length ? '<p class="small">' + links.map(k => '<a href="' + esc(k.url) + '" target="_blank" rel="noopener">' + esc(k.title) + ' ↗</a>').join(' · ') + '</p>' : '') +
      '<div><b class="small">' + (route ? 'Dates on this route' : 'Dates') + '</b> <span class="small muted">' + (best ? '(from ' + M.fmtUsd(best._two.total) + ', two cabins)' : '') + '</span>' +
      '<div class="mini-dates">' + dates + (sl.length > 12 ? '<button type="button" data-act="dates" data-ship="' + esc(sh.id) + '" data-route="' + esc(route || '') + '"><b>+' + (sl.length - 12) + ' more</b>see all</button>' : '') + '</div></div>' +
      '</div></article>';
  }

  /* ---------------- Dates ---------------- */
  let DM = null; // date map
  let calKey = null;
  function calRows() {
    const list = M.sailings.filter(s => (!S.route || s._route === S.route) && (!S.june || M.inJune(s)) && (!S.shipOnly || s.ship === S.ship));
    const groups = [];
    M.routes.forEach(r => {
      const rs = list.filter(s => s._route === r.id);
      if (!rs.length) return;
      const byShip = {};
      rs.forEach(s => { (byShip[s.ship] = byShip[s.ship] || []).push(s); });
      const rows = Object.keys(byShip).map(sid => ({ ship: M.ship[sid], sailings: byShip[sid], best: M.cheapest(byShip[sid]) }));
      rows.sort((a, b) => (a.best ? a.best._two.total : 1e9) - (b.best ? b.best._two.total : 1e9));
      groups.push({ r, rows });
    });
    return groups;
  }
  function renderCalendar() {
    const wrap = $('#calendar');
    const groups = calRows();
    const narrow = window.innerWidth < 600;
    const labelW = narrow ? 128 : 170;
    const start = M.dayNum(M.dateMin) - 2, end = M.dayNum(M.dateMax) + 3;
    const days = end - start;
    const avail = (wrap.clientWidth || 700) - labelW - 2;
    const px = Math.max(narrow ? 15 : 9.5, avail / days);
    const W = Math.ceil(labelW + days * px);
    const x = iso => labelW + (M.dayNum(iso) - start + 0.5) * px;
    let lines = '', ticks = '', months = '';
    for (let n = start; n < end; n++) {
      const iso = M.isoFromNum(n), dt = new Date(n * 86400000);
      if (dt.getUTCDate() === 1) {
        lines += '<div class="cal-gridline month" style="left:' + (labelW + (n - start) * px) + 'px"></div>';
      }
      if (dt.getUTCDay() === 0) {
        lines += '<div class="cal-gridline" style="left:' + (labelW + (n - start + 0.5) * px) + 'px"></div>';
        ticks += '<span class="cal-tick" style="left:' + (labelW + (n - start + 0.5) * px) + 'px">Sun ' + esc(M.fmtDate(iso)) + '</span>';
      }
      if (dt.getUTCDate() === 1 || n === start) {
        const mo = dt.getUTCMonth();
        months += '<span class="cal-month' + (mo === 5 ? ' pref' : '') + '" style="left:' + (labelW + (n - start) * px) + 'px">' + M.MON[mo] + ' 2027</span>';
      }
    }
    const juneA = Math.max(start, M.dayNum('2027-06-01')), juneB = Math.min(end, M.dayNum('2027-07-01'));
    const june = juneB > juneA ? '<div class="cal-june" style="left:' + (labelW + (juneA - start) * px) + 'px;width:' + ((juneB - juneA) * px) + 'px"></div>' : '';
    let body = '';
    groups.forEach(g => {
      body += '<div class="cal-group" style="width:' + W + 'px"><span class="gl"><span class="sw" style="background:' + esc(g.r.color) + '"></span>' + esc(g.r.name) + '</span></div>';
      g.rows.forEach(row => {
        body += '<div class="cal-row" style="width:' + W + 'px"><div class="cal-label" style="width:' + labelW + 'px">' + lineBadge(row.ship.line) + '<span class="nm">' + esc(row.ship.name) + '</span></div>';
        row.sailings.forEach(s => {
          const t = s._two;
          const sh = row.ship;
          const label = sh.name + ', ' + M.fmtDate(s.depart, true) + ', ' + s.nights + ' nights, ' + (t.total != null ? 'two cabins ' + M.fmtUsd(t.total) + ', ' + M.STATUS_SHORT[t.status] : 'two-cabin price not captured');
          body += '<button type="button" class="dot s-' + esc(t.status) + (S.sailing === s.id ? ' sel' : '') + '" data-act="pick" data-sailing="' + esc(s.id) + '" style="left:' + x(s.depart).toFixed(1) + 'px;--c:' + esc(g.r.color) + '" aria-label="' + esc(label) + '" title="' + esc(label) + '">' + esc(M.fmtK(t.total)) + '</button>';
        });
        body += '</div>';
      });
    });
    if (!groups.length) body = '<div class="cal-empty">No sailings match these filters.</div>';
    wrap.innerHTML = '<div class="cal-scroll"><div class="cal" style="width:' + W + 'px">' +
      '<div class="cal-head" style="width:' + W + 'px">' + months + ticks + '</div>' +
      '<div style="position:relative">' + june + lines + body + '</div></div></div>' +
      '<div class="cal-legend">' +
      '<span><span class="dot s-verified">$5.0k</span> verified on the line’s site</span>' +
      '<span><span class="dot s-published">$5.0k</span> published, not date-verified</span>' +
      '<span><span class="dot s-unavailable">?</span> a cabin price not captured</span>' +
      '<span>Label = interior + balcony cabins, 2 adults each, with taxes and port fees, before tips. Position = departure date.</span></div>';
    const sel = S.sailing && $('.dot.sel', wrap);
    if (sel) {
      const sc = $('.cal-scroll', wrap);
      const left = parseFloat(sel.style.left);
      if (left - labelW < sc.scrollLeft || left > sc.scrollLeft + sc.clientWidth - 40) sc.scrollLeft = Math.max(0, left - labelW - 60);
    }
  }
  function renderDateTop() {
    const shipChip = S.shipOnly && S.ship ? '<button type="button" class="chip" data-act="ship-only-off" aria-pressed="true">Only ' + esc(M.ship[S.ship].name) + ' ✕</button>' : '';
    $('#dateTop').innerHTML = '<div class="section-head"><div><h2>Pick a date</h2><p>Each row is a ship, grouped by route. Each pill is a departure; the label is the two-cabin fare. Tap one to see its days and prices.</p></div></div>' +
      '<div class="date-tools"><div class="chips scroll" role="group" aria-label="Filter by route">' +
      '<button type="button" class="chip" data-act="route-filter" data-route="" aria-pressed="' + (!S.route) + '">All routes</button>' +
      M.routes.map(r => '<button type="button" class="chip" data-act="route-filter" data-route="' + esc(r.id) + '" aria-pressed="' + (S.route === r.id) + '"><span class="sw" style="background:' + esc(r.color) + '"></span>' + esc(r.short || r.name) + '</button>').join('') + '</div>' +
      '<div class="chips"><label class="toggle"><input type="checkbox" data-act="june"' + (S.june ? ' checked' : '') + '> June departures only</label>' + shipChip + '</div></div>';
  }
  function renderDate() {
    renderDateTop();
    const key = [S.route, S.june, S.shipOnly && S.ship, window.innerWidth].join('|');
    if (key !== calKey) { renderCalendar(); calKey = key; }
    else $$('#calendar .dot').forEach(d => d.classList.toggle('sel', d.dataset.sailing === S.sailing));
    renderSailing();
    if (!DM && window.L) {
      const map = makeMap('dateMap');
      DM = { map, layer: L.layerGroup().addTo(map), pins: null, shown: undefined };
    }
    if (DM) setTimeout(() => { DM.map.invalidateSize(); drawDateMap(); }, 0);
  }
  function drawDateMap() {
    const key = (S.sailing || '') + '|' + (S.route || '');
    if (DM.shown === key) return;
    DM.shown = key;
    DM.layer.clearLayers();
    if (DM.pins) { DM.map.removeLayer(DM.pins.layer); DM.map.off('zoomend', DM.pins.labels); DM.pins = null; }
    const b = L.latLngBounds([]);
    let stops = new Set();
    const its = S.sailing ? [M.itin[M.sailing[S.sailing].itinerary]] : M.itins.filter(it => !S.route || it.routeFamily === S.route);
    its.forEach(it => {
      if (!it.mapLine || !it.mapLine.length) return;
      const r = M.route[it.routeFamily];
      const pl = L.polyline(it.mapLine, Object.assign(lineStyle(r, S.sailing ? 'on' : 'all'), { interactive: false })).addTo(DM.layer);
      b.extend(pl.getBounds());
      M.stopsOf(it).forEach(p => stops.add(p));
    });
    DM.pins = addPins(DM.map, Array.from(stops));
    if (b.isValid()) DM.map.fitBounds(b, { paddingTopLeft: [16, 16], paddingBottomRight: [70, 16] });
  }
  function renderSailing() {
    const el = $('#sailingPanel');
    if (!S.sailing) {
      el.innerHTML = '<div class="empty-pick">Tap a departure in the calendar to see its route, day-by-day port times and cabin prices.</div>';
      return;
    }
    const s = M.sailing[S.sailing], it = M.itin[s.itinerary], sh = M.ship[s.ship], l = M.line[s._line], r = M.route[s._route];
    const t = s._two, tips = M.tips(s);
    const ends = M.endpoints(it);
    const prices = M.CABINS.map(([k, label]) => {
      const row = M.cabinRow(s, k);
      const who = k === 'interior' ? 'Brothers' : k === 'balcony' ? 'Parents' : '';
      const url = M.sourceUrl(row);
      return '<div class="cab' + (who ? ' pick' : '') + '"><div class="cab-top"><span class="cab-n">' + esc(label) + (who ? ' <span class="who">' + who + '</span>' : '') + '</span>' +
        '<span class="cab-p">' + (row && row.status !== 'unavailable' ? M.fmtUsd(row.usd) : '—') + '</span></div>' +
        '<div class="cab-meta">' + statusPill(row ? row.status : 'unavailable') + (row && row.checked ? ' <span>checked ' + esc(M.fmtChecked(row.checked)) + '</span>' : '') +
        (url ? ' <a href="' + esc(url) + '" target="_blank" rel="noopener">source ↗</a>' : '') +
        (window.AKP && s.priceRows[k] ? ' <button type="button" class="linkbtn" data-act="quote" data-row="' + esc(s.priceRows[k]) + '" data-label="' + esc(label + ' cabin, ' + sh.name + ', ' + M.fmtDate(s.depart)) + '">' + (row && row.quoted ? 'edit my quote' : 'add my quote') + '</button>' : '') + '</div>' +
        (row && row.note ? '<div class="cab-note">' + esc(row.note) + '</div>' : '') + '</div>';
    }).join('');
    let days = '';
    if (it.days) {
      it.days.forEach((day, i) => {
        const iso = M.addDays(s.depart, i);
        day.forEach((e, j) => {
          const p = e.place ? M.place[e.place] : null;
          let what = '', cls = 'k-' + e.type;
          if (e.type === 'embark') what = '<b>Board in ' + esc(placeName(e.place, true)) + '</b> <span class="t">· sails ' + esc(M.fmtTime(e.dep)) + '</span>';
          else if (e.type === 'disembark') what = '<b>Arrive ' + esc(placeName(e.place, true)) + '</b> <span class="t">· ' + esc(M.fmtTime(e.arr)) + ', then off the ship</span>';
          else if (e.type === 'sea') what = 'At sea';
          else if (e.type === 'scenic') what = '<b>' + esc(p ? p.name : e.place) + '</b> <span class="t">· scenic cruising' + (e.arr ? ' ' + esc(M.fmtTime(e.arr)) + '–' + esc(M.fmtTime(e.dep)) : ', hours not listed') + '</span>';
          else if (e.type === 'port') {
            const u = M.usableHours(e);
            what = '<b>' + esc(p ? p.short || p.name : e.place) + '</b> <span class="t">· ' + (e.arr ? esc(M.fmtTime(e.arr)) + '–' + esc(M.fmtTime(e.dep)) : 'times not listed') + '</span>' +
              (u != null ? '<span class="u">About ' + esc(M.fmtHours(u)) + ' to explore' + (p && p.dock ? ' · ' + esc(p.dock) : '') + '</span>' : (p && p.dock ? '<span class="u">' + esc(p.dock) + '</span>' : ''));
          }
          days += '<li class="' + cls + '"><div class="d">' + (j === 0 ? '<b>Day ' + (i + 1) + '</b>' + esc(M.fmtDate(iso, true)) : '') + '</div><div class="w">' + what + '</div></li>';
        });
      });
    } else {
      days = '<li><div class="d"></div><div class="w muted">Port times were not captured for this sailing. Stops: ' + esc(M.stopsOf(it).map(p => placeName(p, true)).join(' → ')) + '.</div></li>';
    }
    const facts = M.itinFacts(it);
    const flags = (s.flags || []).map(f => '<span class="flag">' + esc(M.FLAG_LABEL[f] || f) + '</span>').join('');
    const tsrc = it.timesStatus ? 'Port times: ' + statusPill(it.timesStatus) + (it.timesSource ? ' <span class="small muted">' + esc(it.timesSource) + '</span>' : '') : '';
    el.innerHTML = '<article class="card sail">' + photoHTML(M.photo(['ship:' + sh.id]), { label: sh.name }) +
      '<div class="card-body">' +
      '<div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">' + lineBadge(l.id) + '<h3>' + esc(sh.name) + '</h3>' + routeTag(r.id) + '</div>' +
      '<div class="sub">' + esc(it.name) + '<br>' + esc(M.fmtDate(s.depart, true)) + ' → ' + esc(M.fmtDate(s.return, true)) + ' · ' + plural(s.nights, 'night') + ' · ' + esc(placeName(ends.from, true)) + (ends.to !== ends.from ? ' to ' + esc(placeName(ends.to, true)) : ' round trip') + '</div>' +
      '<div class="price-big"><b>' + (t.total != null ? M.fmtUsd(t.total) : 'Not captured') + '</b>' + statusPill(t.status) + '</div>' +
      '<p class="small muted">' + (t.total != null ? 'Interior + balcony cabin, 2 adults each, cruise fare with taxes and port fees.' : 'The ' + esc(t.missing.join(' and ')) + ' price was not captured, so no two-cabin total is shown.') + '</p>' +
      (tips.total != null ? '<p class="small">Plus about <b>' + M.fmtUsd(tips.total) + '</b> in crew tips ' + statusPill('estimate') + ' <span class="muted">(' + M.fmtUsd(tips.rate) + ' per person per day × 4 × ' + s.nights + ' nights' + (M.sourceUrl(tips.row) ? ', <a href="' + esc(M.sourceUrl(tips.row)) + '" target="_blank" rel="noopener">rate source</a>' : '') + ')</span></p>' : '') +
      (flags ? '<div class="flags">' + flags + '</div>' : '') +
      (s.note ? '<p class="small">' + esc(s.note) + '</p>' : '') +
      (s.priceSourceKind && s.priceSourceKind !== 'first-party' ? '<p class="small muted">Prices for this sailing come from a ' + esc(s.priceSourceKind) + ', not the cruise line.</p>' : '') +
      '<h3 style="font-size:1.05rem;margin-top:14px">Cabin prices <span class="small muted" style="font-family:var(--sans);font-weight:400">per cabin, 2 adults</span></h3><div class="cabs">' + prices + '</div>' +
      '<h3 style="font-size:1.05rem;margin-top:14px">Day by day</h3>' +
      '<p class="small muted" style="margin:2px 0 0">' + (facts.alaskaH != null ? 'About ' + esc(M.fmtHours(facts.alaskaH)) + ' to explore across ' + plural(facts.alaskaPorts, 'Alaska port') + ' (port hours minus 30 min to get off and 1 h back aboard). ' : '') + 'Times are local.</p>' +
      '<ul class="days">' + days + '</ul>' +
      (tsrc ? '<p class="small" style="margin-top:8px">' + tsrc + '</p>' : '') +
      '<div class="next-row" style="justify-content:flex-start;margin-top:12px">' +
      '<button class="btn small" type="button" data-act="view" data-view="days">Plan the days</button>' +
      '<button class="btn small ghost" type="button" data-act="view" data-view="cost">Trip cost</button>' +
      (window.AKP ? '<button class="btn small ghost" type="button" data-act="star" data-sailing="' + esc(s.id) + '" aria-pressed="' + window.AKP.isStarred(s.id) + '">' + (window.AKP.isStarred(s.id) ? '★ On shortlist' : '☆ Shortlist') + '</button>' : '') +
      '<button class="btn small ghost" type="button" data-act="share">Share</button>' +
      '<button class="btn small ghost" type="button" data-act="ship" data-ship="' + esc(sh.id) + '">About the ship</button></div>' +
      '</div></article>';
  }

  /* ---------------- pick bar ---------------- */
  function renderPickbar() {
    const bar = $('#pickbar');
    if (!S.sailing) { bar.hidden = true; document.body.style.removeProperty('--pick'); return; }
    const s = M.sailing[S.sailing], sh = M.ship[s.ship];
    const P = window.AKP;
    const c = P ? P.costOf(s.id) : null;
    const starred = P ? P.isStarred(s.id) : false;
    bar.hidden = false;
    const amt = c ? '<b>' + M.fmtUsd(c.totals.total) + '</b><small>' + (c.totals.missing.length ? 'trip so far · ' + c.totals.missing.length + ' not captured' : 'whole trip, 4 people') + '</small>'
      : '<b>' + (s._two.total != null ? M.fmtUsd(s._two.total) : '—') + '</b><small>2 cabins, before tips</small>';
    const next = S.view === 'days' ? ['cost', 'Cost'] : S.view === 'cost' ? ['days', 'Days'] : S.view === 'date' ? ['days', 'Plan days'] : ['date', 'Details'];
    bar.innerHTML = '<div class="in"><div class="what"><b>' + lineBadge(s._line) + ' ' + esc(sh.name) + '</b><span>' + esc(M.fmtDate(s.depart, true)) + ' · ' + esc(M.route[s._route].short || '') + '</span></div>' +
      '<button class="amt" type="button" data-act="view" data-view="cost" aria-label="Trip cost details">' + amt + '</button>' +
      (P ? '<button class="btn small star' + (starred ? ' on' : '') + '" type="button" data-act="star" data-sailing="' + esc(s.id) + '" aria-pressed="' + starred + '" aria-label="' + (starred ? 'Remove from shortlist' : 'Add to shortlist') + '">' + (starred ? '★' : '☆') + '</button>' : '') +
      '<button class="btn small go" type="button" data-act="view" data-view="' + next[0] + '">' + next[1] + '</button>' +
      '<button class="btn small x" type="button" data-act="clear" aria-label="Clear the selected sailing">✕</button></div>';
  }

  /* ---------------- share ---------------- */
  async function share() {
    const url = location.href.split('#')[0] + hashOf(Object.assign({}, S, { withPlan: !!S.sailing }));
    let text = 'Alaska 2027 ideas';
    if (S.sailing) { const s = M.sailing[S.sailing]; text = M.ship[s.ship].name + ', ' + M.fmtDate(s.depart, true) + ' (' + M.route[s._route].name + ')'; }
    else if (S.route) text = M.route[S.route].name;
    if (S.sailing && window.AKP && M.planCount(window.AKP.planFor(S.sailing))) text += ', with our day plan';
    if (navigator.share) {
      try { await navigator.share({ title: 'Alaska 2027', text, url }); return; } catch (e) { if (e && e.name === 'AbortError') return; }
    }
    try { await navigator.clipboard.writeText(url); toast('Link copied'); }
    catch (e) { window.prompt('Copy this link:', url); }
  }

  /* ---------------- events ---------------- */
  document.addEventListener('click', e => {
    const a = e.target.closest('[data-act]');
    if (!a) return;
    const act = a.dataset.act;
    if (a.tagName === 'A') e.preventDefault();
    if (act === 'view') go({ view: a.dataset.view }, true);
    else if (act === 'route') {
      const r = a.dataset.route || null;
      if (S.view === 'route' && r && r === S.route) go({ route: null }, false);
      else go({ view: 'route', route: r, sailing: r && S.sailing && M.sailing[S.sailing]._route !== r ? null : S.sailing }, S.view !== 'route');
      if (RM) RM.map.closePopup();
    }
    else if (act === 'route-filter') {
      const r = a.dataset.route || null;
      go({ route: r, sailing: r && S.sailing && M.sailing[S.sailing]._route !== r ? null : S.sailing }, false);
    }
    else if (act === 'dates') go({ view: 'date', route: a.dataset.route || S.route || null, ship: a.dataset.ship || S.ship, shipOnly: !!a.dataset.ship }, true);
    else if (act === 'ship') go({ view: 'ship', ship: a.dataset.ship }, true);
    else if (act === 'sailing' || act === 'pick') {
      const s = M.sailing[a.dataset.sailing];
      const toDate = S.view !== 'date';
      go({ view: 'date', sailing: s.id, ship: s.ship, route: S.route && S.route !== s._route ? null : S.route, shipOnly: S.shipOnly && S.ship === s.ship }, toDate);
      if (!toDate && window.innerWidth < 1100) {
        const side = $('.date-side');
        if (side) { const y = side.getBoundingClientRect().top + window.scrollY - 120; window.scrollTo({ top: y, behavior: 'smooth' }); }
      }
    }
    else if (act === 'clear') go({ sailing: null }, false);
    else if (act === 'ship-only-off') go({ shipOnly: false }, false);
    else if (act === 'share') share();
    else if (window.AKP && window.AKP.onClick(act, a, e)) { /* handled by the Days / Cost / Shortlist screens */ }
    else if (act === 'play') {
      const box = a.closest('.video');
      box.innerHTML = '<iframe src="' + esc(box.dataset.embed + '?autoplay=1&playsinline=1&rel=0') + '" title="Ship tour video" allow="autoplay; encrypted-media; picture-in-picture; fullscreen" allowfullscreen></iframe>';
    }
  });
  document.addEventListener('change', e => {
    if (e.target.matches('[data-act="june"]')) go({ june: e.target.checked }, false);
    else if (window.AKP) window.AKP.onChange(e);
  });
  let rz, lastW = window.innerWidth;
  window.addEventListener('resize', () => {
    clearTimeout(rz);
    rz = setTimeout(() => { if (window.innerWidth === lastW) return; lastW = window.innerWidth; if (S.view === 'date') renderDate(); else if (S.view === 'cost' && window.AKP) window.AKP.render('cost'); }, 200);
  });

  window.AKUI = { S, go, esc, attrs, statusPill, lineBadge, routeTag, photoHTML, placeName, plural, toast, lsGet, lsSet, render, share, hashOf };

  /* ---------------- boot ---------------- */
  M.load().then(() => {
    $('#loading').remove();
    let st = readHash(location.hash);
    if (!st.view) {
      const last = lsGet(LS_KEY);
      st = Object.assign({ view: 'ideas' }, last && last.view ? readHash(hashOf(Object.assign({ view: last.view }, last))) : {});
      if (!st.view) st.view = 'ideas';
    }
    const shared = st.shared; delete st.shared;
    if (window.AKP) window.AKP.init();
    Object.assign(S, st);
    if (shared && S.sailing && window.AKP) window.AKP.receiveShared(S.sailing, shared);
    if (S.sailing && S.view === 'date') S.shipOnly = false;
    history.replaceState(null, '', hashOf(S));
    render();
  }).catch(err => {
    console.error(err);
    $('#loading').innerHTML = '<div class="error"><b>The trip data did not load.</b><br>' + esc(err.message) + '<br>Check your connection and reload the page.</div>';
  });
})();
