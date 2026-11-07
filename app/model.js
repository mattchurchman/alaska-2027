/* Alaska 2027 planner (v2) — data model.
   Loads data/*.json and answers questions about it. No prices are written here:
   every number shown comes from a row in data/prices.json (or is computed from rows). */
(function () {
  'use strict';
  const FILES = ['catalog', 'prices', 'media', 'meta', 'sources', 'experiences', 'travel'];
  const STATUS_RANK = { verified: 0, 'family-quote': 1, published: 2, estimate: 3, unavailable: 4 };
  const STATUS_SHORT = { verified: 'Verified', 'family-quote': 'Family quote', published: 'Published', estimate: 'Estimate', unavailable: 'Not captured' };
  const FLAG_LABEL = {
    promo: 'Sale or promo price: may end', holiday: 'July 4 week', 'family-line': 'Family-focused line',
    'resident-tag': 'Resident-rate tag shown (not applied)', 'adults-only': 'Adults only (18+)'
  };
  const CABINS = [
    ['interior', 'Interior'], ['oceanview', 'Ocean view'], ['balcony', 'Balcony'], ['miniSuite', 'Mini-suite']
  ];

  const M = { ready: false, STATUS_RANK, STATUS_SHORT, FLAG_LABEL, CABINS };

  M.load = async function () {
    const parts = await Promise.all(FILES.map(f =>
      fetch('data/' + f + '.json', { cache: 'no-cache' }).then(r => {
        if (!r.ok) throw new Error('Could not load data/' + f + '.json (' + r.status + ')');
        return r.json();
      })));
    const d = {};
    FILES.forEach((f, i) => { d[f] = parts[i]; });
    index(d);
    M.ready = true;
    return M;
  };

  function byId(list) { const o = {}; (list || []).forEach(x => { o[x.id] = x; }); return o; }

  function index(d) {
    const c = d.catalog;
    M.d = d;
    M.meta = d.meta;
    M.routes = c.routeFamilies;
    M.route = byId(c.routeFamilies);
    M.lines = c.lines; M.line = byId(c.lines);
    M.ships = c.ships; M.ship = byId(c.ships);
    M.itins = c.itineraries; M.itin = byId(c.itineraries);
    M.sailings = c.sailings.slice().sort((a, b) => a.depart < b.depart ? -1 : a.depart > b.depart ? 1 : 0);
    M.sailing = byId(c.sailings);
    M.places = c.places; M.place = byId(c.places);
    M.pois = c.pois || [];
    M.rows = byId(d.prices.rows);
    M.source = byId(d.sources.sources);
    M.photos = d.media.photos || [];
    M.videos = d.media.videos || [];
    M.links = d.media.officialLinks || [];
    M.placeholders = d.media.placeholders || [];
    // photo lookup by "kind:id"
    M.photoBy = {};
    M.photos.forEach(p => (p.for || []).forEach(k => { if (!M.photoBy[k]) M.photoBy[k] = p; }));
    M.videosBy = {};
    M.videos.forEach(v => (v.for || []).forEach(k => { (M.videosBy[k] = M.videosBy[k] || []).push(v); }));
    M.linksBy = {};
    M.links.forEach(l => (l.for || []).forEach(k => { (M.linksBy[k] = M.linksBy[k] || []).push(l); }));
    // derived per-sailing facts
    M.sailings.forEach(s => {
      const it = M.itin[s.itinerary];
      s._route = it.routeFamily;
      s._line = it.line;
      s._two = twoCabin(s);
    });
    M.dateMin = M.sailings[0].depart;
    M.dateMax = M.sailings[M.sailings.length - 1].depart;
    // experiences and offers (Phase 7)
    M.exps = (d.experiences && d.experiences.experiences) || [];
    M.exp = byId(M.exps);
    M.expLabels = (d.experiences && d.experiences.labels) || {};
    M.offerKinds = (d.experiences && d.experiences.offerKinds) || {};
    M.offer = {}; M.expOfOffer = {};
    M.exps.forEach(x => (x.offers || []).forEach(o => { M.offer[o.id] = o; M.expOfOffer[o.id] = x; }));
    M.travel = d.travel || {};
    M.hotels = M.travel.hotels || []; M.hotel = byId(M.hotels);
    M.flights = M.travel.flights || [];
  }

  /* ---------- prices ---------- */
  M.weakest = function (statuses) {
    let w = 'verified';
    statuses.forEach(s => { if ((STATUS_RANK[s] ?? 4) > STATUS_RANK[w]) w = s; });
    return w;
  };
  M.cabinRow = function (s, cabin) {
    const id = s.priceRows && s.priceRows[cabin];
    return id ? M.row(id) : null;
  };
  /* Family quotes overlay research rows. A quote replaces the amount everywhere it is used and
     carries status "family-quote". Quotes can also fill gaps that have no research row ("gap:…"). */
  M.quotes = {};
  M.row = function (id) {
    if (!id) return null;
    const r = M.rows[id] || null, q = M.quotes[id];
    if (!q || typeof q.usd !== 'number') return r;
    return Object.assign({}, r || { id: id, for: id, item: 'price', basis: q.basis || '' }, {
      usd: q.usd, amount: q.usd, currency: 'USD', fx: null, status: 'family-quote',
      note: q.note || '', checked: q.date || null, url: null, source: null, quoted: true, orig: r
    });
  };
  M.setQuotes = function (q) {
    M.quotes = q && typeof q === 'object' ? q : {};
    M.sailings.forEach(s => { s._two = twoCabin(s); });
  };
  function usable(r) { return r && r.status !== 'unavailable' && typeof r.usd === 'number'; }
  function twoCabin(s) {
    const a = M.cabinRow(s, 'interior'), b = M.cabinRow(s, 'balcony');
    if (!usable(a) || !usable(b)) {
      return { total: null, status: 'unavailable', rows: [a, b], missing: [!usable(a) && 'interior', !usable(b) && 'balcony'].filter(Boolean) };
    }
    return { total: a.usd + b.usd, status: M.weakest([a.status, b.status]), rows: [a, b], missing: [] };
  }
  M.twoCabin = twoCabin;
  /* Gratuities: line daily rate x 4 guests x nights. A planner estimate built from a row. */
  M.tips = function (s) {
    const ln = M.line[s._line];
    const r = ln && ln.gratuityRow ? M.row(ln.gratuityRow) : null;
    if (!usable(r)) return { total: null, status: 'unavailable', row: r };
    return { total: Math.round(r.usd * 4 * s.nights), status: r.status === 'family-quote' ? 'family-quote' : 'estimate', row: r, rate: r.usd };
  };
  M.fmtUsd = function (n) {
    if (n == null) return '—';
    return '$' + Math.round(n).toLocaleString('en-US');
  };
  M.fmtK = function (n) {
    if (n == null) return '?';
    return '$' + (n / 1000).toFixed(1) + 'k';
  };

  /* ---------- dates & times ---------- */
  const MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const DOW = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  M.MON = MON; M.DOW = DOW;
  M.dayNum = function (iso) { // days since epoch, timezone-safe
    const [y, m, d] = iso.split('-').map(Number);
    return Math.round(Date.UTC(y, m - 1, d) / 86400000);
  };
  M.isoFromNum = function (n) {
    const dt = new Date(n * 86400000);
    return dt.getUTCFullYear() + '-' + String(dt.getUTCMonth() + 1).padStart(2, '0') + '-' + String(dt.getUTCDate()).padStart(2, '0');
  };
  M.fmtDate = function (iso, withDow) {
    const n = M.dayNum(iso), dt = new Date(n * 86400000);
    return (withDow ? DOW[dt.getUTCDay()] + ' ' : '') + MON[dt.getUTCMonth()] + ' ' + dt.getUTCDate();
  };
  M.fmtChecked = function (iso) {
    if (!/^\d{4}-\d{2}-\d{2}$/.test(iso || '')) return iso || '';
    return M.fmtDate(iso) + ', ' + iso.slice(0, 4);
  };
  M.addDays = function (iso, k) { return M.isoFromNum(M.dayNum(iso) + k); };
  M.fmtTime = function (t) {
    if (!t) return '';
    let [h, m] = t.split(':').map(Number);
    if (h === 23 && m === 59) return 'midnight';
    const ap = h >= 12 ? 'pm' : 'am';
    h = h % 12 || 12;
    return h + (m ? ':' + String(m).padStart(2, '0') : '') + ' ' + ap;
  };
  function mins(t) { const [h, m] = t.split(':').map(Number); return h === 23 && m === 59 ? 1440 : h * 60 + m; }
  M.portHours = function (e) {
    if (!e || !e.arr || !e.dep) return null;
    let d = mins(e.dep) - mins(e.arr);
    if (d < 0) d += 1440;
    return d / 60;
  };
  M.usableHours = function (e) {
    const h = M.portHours(e);
    if (h == null) return null;
    const p = M.meta.planner || {};
    return Math.max(0, h - (p.offShipH ?? 0.5) - (p.backAboardH ?? 1));
  };
  M.fmtHours = function (h) {
    if (h == null) return '';
    const hh = Math.floor(h + 1e-6), mm = Math.round((h - hh) * 60);
    return hh + ' h' + (mm ? ' ' + mm + ' m' : '');
  };

  /* ---------- itineraries ---------- */
  M.stopsOf = function (it) {
    const out = [];
    (it.days || []).forEach(day => day.forEach(e => { if (e.place) out.push(e.place); }));
    if (!out.length && it.ports) out.push.apply(out, it.ports);
    return out;
  };
  const ALASKA_PORTS = new Set(['juneau', 'skagway', 'ketchikan', 'ketchikan_wc', 'sitka', 'icy_strait', 'haines']);
  M.isAlaskaPort = id => ALASKA_PORTS.has(id);
  M.itinFacts = function (it) {
    let alaskaH = 0, alaskaPorts = 0, seaDays = 0, scenic = [];
    (it.days || []).forEach(day => day.forEach(e => {
      if (e.type === 'sea') seaDays++;
      if (e.type === 'scenic') scenic.push(e.place);
      if (e.type === 'port' && ALASKA_PORTS.has(e.place)) {
        alaskaPorts++;
        const u = M.usableHours(e);
        if (u != null) alaskaH += u;
      }
    }));
    if (!it.days && it.ports) {
      it.ports.forEach(p => { if (ALASKA_PORTS.has(p)) alaskaPorts++; if (M.place[p] && M.place[p].kind === 'scenic') scenic.push(p); });
    }
    return { alaskaH: it.days ? alaskaH : null, alaskaPorts, seaDays, scenic, timesKnown: !!it.days };
  };
  M.endpoints = function (it) {
    const st = M.stopsOf(it);
    return { from: st[0], to: st[st.length - 1] };
  };

  /* ---------- groupings ---------- */
  M.sailingsFor = function (filter) {
    return M.sailings.filter(s =>
      (!filter.route || s._route === filter.route) &&
      (!filter.ship || s.ship === filter.ship) &&
      (!filter.line || s._line === filter.line));
  };
  M.cheapest = function (list) {
    let best = null;
    list.forEach(s => { if (s._two.total != null && (!best || s._two.total < best._two.total)) best = s; });
    return best;
  };
  M.inJune = s => s.depart.slice(5, 7) === '06';
  M.shipsOnRoute = function (route) {
    const seen = new Set(), out = [];
    M.sailings.forEach(s => { if ((!route || s._route === route) && !seen.has(s.ship)) { seen.add(s.ship); out.push(M.ship[s.ship]); } });
    return out;
  };
  M.routesForPlace = function (pid) {
    const out = new Set();
    M.itins.forEach(it => { if (M.stopsOf(it).includes(pid)) out.add(it.routeFamily); });
    return M.routes.filter(r => out.has(r.id));
  };
  M.photo = function (keys) {
    for (const k of keys) {
      if (!k) continue;
      if (M.photoBy[k]) return M.photoBy[k];
      if (k.startsWith('place:')) {
        const p = M.place[k.slice(6)];
        if (p && p.photo2) return Object.assign({ alt: p.name }, p.photo2);
      }
    }
    return null;
  };
  M.sourceUrl = function (row) {
    if (!row) return null;
    if (row.url) return row.url;
    const s = row.source && M.source[row.source];
    return s ? s.url : null;
  };

  /* =================================================================
     Phase 7: day plans, time fit, walking, trip cost
     A plan belongs to one sailing: { picks: { "<day index>": { p: [offerId…], b: [offerId…] } },
     cab: { b: 'interior'|'oceanview', p: 'balcony'|'miniSuite' } }. "p" = parents, "b" = brothers.
     The offer id "aboard" means that pair stays on the ship that day.
     ================================================================= */
  M.ABOARD = 'aboard';
  M.LANES = [['p', 'Parents'], ['b', 'Brothers']];
  M.pl = function () {
    const p = Object.assign({ offShipH: 0.5, backAboardH: 1, transitionH: 0.25, selfGuidedH: 1.5, unpricedH: 3, allAboardBeforeH: 0.5, indepBufferH: 1, walkBudgetMi: 2, disembarkH: 2, airportBeforeH: 2, airportTransferMin: {} }, M.meta.planner || {});
    return p;
  };
  M.DEFAULT_SETTINGS = { fare: 'saver', bagsPP: 1, eachWay: true, hotel: 'hampton_airport', walkBudget: null, retFlight: 1 };
  M.settings = Object.assign({}, M.DEFAULT_SETTINGS);
  M.walkBudget = function () { const b = M.settings.walkBudget; return typeof b === 'number' && b > 0 ? b : M.pl().walkBudgetMi; };

  M.emptyPlan = function () { return { picks: {}, cab: { b: 'interior', p: 'balcony' } }; };
  M.planPicks = function (plan, day, lane) {
    const d = plan && plan.picks && plan.picks[day];
    return (d && d[lane]) || [];
  };
  M.planCount = function (plan) {
    const seen = new Set(); // an "All 4" pick counts once
    Object.keys((plan && plan.picks) || {}).forEach(k => ['p', 'b'].forEach(l => M.planPicks(plan, k, l).forEach(o => {
      if (o !== M.ABOARD && M.expOfOffer[o]) seen.add(k + '|' + M.expOfOffer[o].id);
    })));
    return seen.size;
  };

  /* every entry of a sailing, flattened, with its day index and date */
  M.stops = function (s) {
    const it = M.itin[s.itinerary], out = [];
    (it.days || []).forEach((day, i) => day.forEach((e, j) => out.push({ day: i, j, iso: M.addDays(s.depart, i), e, type: e.type, place: e.place || null })));
    return out;
  };
  M.portEntry = function (s, day) {
    const it = M.itin[s.itinerary];
    const d = it.days && it.days[day];
    return d ? d.find(e => e.type === 'port') || null : null;
  };
  M.timed = e => !!(e && e.arr && e.dep);

  /* experiences that start from a port (scenic-cruising items are shown separately) */
  M.expsAt = function (place) { return M.exps.filter(x => (x.ports || [x.port]).includes(place)); };
  /* offers someone on this sailing can actually book: other lines' shore excursions are excluded */
  M.offersFor = function (x, s) {
    return (x.offers || []).filter(o => o.kind !== 'cruise' || o.line === s._line);
  };
  M.offerPrice = function (o) { // per-person price row (with family quote) or null
    const r = M.row(o.priceRow);
    return { row: r, usd: usable(r) ? r.usd : null, status: r ? r.status : 'unavailable' };
  };
  M.defaultOffer = function (x, s) {
    const offs = M.offersFor(x, s);
    if (!offs.length) return null;
    let best = null, bestP = Infinity;
    offs.forEach(o => {
      const p = M.offerPrice(o).usd;
      const key = p == null ? Infinity : p - (o.kind === 'cruise' ? 0.01 : 0); // tie goes to the cruise line
      if (key < bestP) { best = o; bestP = key; }
    });
    return best || offs[0];
  };
  M.offerHours = function (o) {
    if (!o || o.id === M.ABOARD) return { h: 0, assumed: false };
    if (typeof o.hours === 'number' && o.hours > 0) return { h: o.hours, assumed: false };
    const self = o.kind === 'free' || o.kind === 'diy';
    return { h: self ? M.pl().selfGuidedH : M.pl().unpricedH, assumed: true };
  };
  M.groupOf = function (x, s) {
    if (x.label === 'brothers' || x.label === 'not_recommended' || x.category === 'adventure') return 'adventure';
    const offs = s ? M.offersFor(x, s) : x.offers;
    if (offs.length && offs.every(o => o.kind === 'free' || M.offerPrice(o).usd === 0)) return 'free';
    if (x.diy) return 'diy';
    return 'easy';
  };
  M.GROUPS = [
    ['easy', 'Easy for parents', 'Low-effort tours. "With precautions" means some steps, uneven ground or standing; read the notes.'],
    ['adventure', 'Adventure', 'More active choices, mostly for the brothers.'],
    ['diy', 'DIY & budget', 'Do it yourself: buses, rental cars, self-guided routes.'],
    ['free', 'Free', 'No ticket needed. Walking distance still counts.'],
    ['aboard', 'Stay aboard', 'A quiet day on the ship: no walking, no cost.']
  ];

  /* ---- time fit for one pair on one port call ---- */
  M.window = function (e) {
    const p = M.pl();
    const arr = mins(e.arr);
    let dep = mins(e.dep);
    if (dep <= arr) dep += 1440;
    return {
      arr, dep,
      start: arr + p.offShipH * 60,          // first time you can be off the ship
      backBy: dep - p.backAboardH * 60,       // planner's "back at the ship" time
      allAboard: dep - p.allAboardBeforeH * 60,
      indepBy: dep - p.allAboardBeforeH * 60 - p.indepBufferH * 60
    };
  };
  M.schedule = function (e, offerIds) {
    const w = M.window(e), p = M.pl();
    let t = w.start;
    const items = [];
    let aboard = false;
    (offerIds || []).forEach(id => {
      if (id === M.ABOARD) { aboard = true; return; }
      const o = M.offer[id];
      if (!o) return;
      const hh = M.offerHours(o);
      const it = { id, offer: o, exp: M.expOfOffer[id], start: t, end: t + hh.h * 60, hours: hh.h, assumed: hh.assumed };
      it.over = it.end > w.backBy + 0.01;
      it.indepLate = (o.kind === 'independent' || o.kind === 'reseller') && it.end > w.indepBy + 0.01;
      items.push(it);
      t = it.end + p.transitionH * 60;
    });
    const used = items.length ? items[items.length - 1].end : w.start;
    return { w, items, aboard, over: items.some(i => i.over), freeMin: Math.max(0, w.backBy - (items.length ? used + p.transitionH * 60 : w.start)) };
  };
  /* can this offer be added to a pair's day? returns {ok, reason, need, left} */
  M.canAdd = function (e, laneIds, offerId) {
    if (!M.timed(e)) return { ok: false, reason: 'Port times were not captured for this call, so the planner cannot check the fit.' };
    const ids = (laneIds || []).filter(x => x !== M.ABOARD && x !== offerId);
    const base = M.schedule(e, ids);
    const sch = M.schedule(e, ids.concat([offerId]));
    const last = sch.items[sch.items.length - 1];
    const usableMin = sch.w.backBy - sch.w.start;
    if (!last) return { ok: true };
    if (last.hours * 60 > usableMin + 0.01) return { ok: false, tooLong: true, reason: 'Too long for this stop: about ' + M.fmtHours(last.hours) + ' needed, ' + M.fmtHours(usableMin / 60) + ' ashore.', need: last.hours, left: usableMin / 60 };
    if (last.over) return { ok: false, reason: 'No room left: about ' + M.fmtHours(last.hours) + ' needed, ' + M.fmtHours(base.freeMin / 60) + ' free after the other picks.', need: last.hours, left: base.freeMin / 60 };
    return { ok: true };
  };
  M.minsToTime = function (m) {
    m = Math.round(m) % 1440; if (m < 0) m += 1440;
    return String(Math.floor(m / 60)).padStart(2, '0') + ':' + String(m % 60).padStart(2, '0');
  };
  M.fmtMins = m => M.fmtTime(M.minsToTime(m));

  /* ---- walking ---- */
  M.walkFor = function (offerIds) {
    let mi = 0, unknown = 0, seen = new Set(), weakest = 'documented';
    const rank = { documented: 0, derived: 1, estimate: 2 };
    (offerIds || []).forEach(id => {
      if (id === M.ABOARD) return;
      const x = M.expOfOffer[id];
      if (!x || seen.has(x.id)) return;
      seen.add(x.id);
      if (typeof x.walkMiles === 'number') {
        mi += x.walkMiles;
        const c = x.walkConfidence || 'estimate';
        if ((rank[c] ?? 2) > rank[weakest]) weakest = c;
      } else unknown++;
    });
    return { mi: Math.round(mi * 10) / 10, unknown, confidence: weakest };
  };

  /* ---- warnings for one port day ---- */
  M.dayWarnings = function (s, day, plan) {
    const e = M.portEntry(s, day);
    const out = [];
    if (!e) return out;
    const place = M.place[e.place] || {};
    const lanes = { p: M.planPicks(plan, day, 'p'), b: M.planPicks(plan, day, 'b') };
    if (!M.timed(e)) {
      if (lanes.p.length || lanes.b.length) out.push({ lv: 'warn', lane: null, text: 'Port times for this call were not captured, so the fit could not be checked.' });
      return out;
    }
    ['p', 'b'].forEach(l => {
      const who = l === 'p' ? 'Parents' : 'Brothers';
      const sch = M.schedule(e, lanes[l]);
      sch.items.forEach(it => {
        if (it.over) out.push({ lv: 'block', lane: l, text: who + ': ' + it.exp.name + ' would end at ' + M.fmtMins(it.end) + ', after the ' + M.fmtMins(sch.w.backBy) + ' back-at-the-ship time. Remove something or pick a shorter option.' });
        else if (it.indepLate) out.push({ lv: 'warn', lane: l, text: who + ': ' + it.exp.name + ' (' + it.offer.provider + ') is not a cruise-line tour and ends about ' + M.fmtMins(it.end) + ', less than an hour before all aboard (' + M.fmtMins(sch.w.allAboard) + '). The ship will not wait.' });
        if (it.assumed) out.push({ lv: 'info', lane: l, text: who + ': ' + it.exp.name + ' has no stated length; planned at ' + M.fmtHours(it.hours) + '.' });
        const pr = M.offerPrice(it.offer);
        if (pr.usd == null) out.push({ lv: 'info', lane: l, text: who + ': no price captured for ' + it.exp.name + ' (' + it.offer.provider + '), so it adds nothing to the total.' });
        if (it.exp.risk && it.exp.risk.text) out.push({ lv: 'warn', lane: l, text: who + ': ' + it.exp.risk.text });
      });
    });
    // parents' suitability and walking
    const pIds = lanes.p.filter(x => x !== M.ABOARD);
    const seen = new Set();
    pIds.forEach(id => {
      const x = M.expOfOffer[id];
      if (!x || seen.has(x.id)) return; seen.add(x.id);
      if (x.label === 'brothers' || x.label === 'not_recommended') out.push({ lv: 'warn', lane: 'p', text: 'Parents: ' + x.name + ' is marked "' + (M.expLabels[x.label] || x.label) + '".' });
      else if ((x.exertion || 0) >= 3) out.push({ lv: 'warn', lane: 'p', text: 'Parents: ' + x.name + ' is rated ' + x.exertion + ' of 5 for effort.' });
    });
    const wk = M.walkFor(lanes.p), budget = M.walkBudget();
    if (wk.mi > budget + 1e-6) out.push({ lv: 'warn', lane: 'p', walk: true, text: 'Parents: about ' + wk.mi + ' mi of walking, over the ' + budget + ' mi daily budget.' });
    if (wk.unknown) out.push({ lv: 'info', lane: 'p', walk: true, text: 'Parents: walking distance not measured yet for ' + wk.unknown + (wk.unknown === 1 ? ' pick' : ' picks') + ', so the meter may read low.' });
    if (pIds.length >= 2 && !out.some(w => w.walk && w.lv === 'warn')) {
      const walky = pIds.map(id => M.expOfOffer[id]).filter(x => x && (x.walkMiles || 0) >= 1).length;
      if (walky >= 2) out.push({ lv: 'info', lane: 'p', text: 'Parents: two picks with a mile or more of walking on the same day.' });
    }
    if (e.place === 'ketchikan_wc' && (lanes.p.length || lanes.b.length) && place.dock) out.push({ lv: 'info', lane: null, text: 'Ward Cove: ' + place.dock });
    return out;
  };

  /* ---- arrival travel, flights and hotel ---- */
  const SEA_TERMINALS = new Set(['sea_p91', 'sea_p66']);
  const GATEWAY_OF = { sea_p91: 'SEA', sea_p66: 'SEA', yvr_canada_place: 'YVR', seward: 'ANC', whittier: 'ANC' };
  M.gateways = function (s) {
    const it = M.itin[s.itinerary], ends = M.endpoints(it);
    return { from: GATEWAY_OF[ends.from] || null, to: GATEWAY_OF[ends.to] || null, fromPlace: ends.from, toPlace: ends.to, seattle: SEA_TERMINALS.has(ends.from) && SEA_TERMINALS.has(ends.to) };
  };
  M.flightFor = function (s) {
    if (!M.gateways(s).seattle) return null;
    const nonstop = M.flights.filter(f => f.stops === 0);
    const exact = nonstop.find(f => (f.sailingIds || []).includes(s.id));
    if (exact) return { f: exact, exact: true };
    const want = M.dayNum(s.depart) - 1;
    let best = null, bd = Infinity;
    nonstop.forEach(f => { const dd = Math.abs(M.dayNum(f.outboundDate) - want); if (dd < bd) { bd = dd; best = f; } });
    return best ? { f: best, exact: false } : null;
  };
  M.returnCheck = function (s) {
    const ff = M.flightFor(s);
    const it = M.itin[s.itinerary];
    if (!it.days) return null;
    const last = it.days[it.days.length - 1].find(e => e.type === 'disembark');
    if (!last || !last.arr) return null;
    const p = M.pl();
    const tr = (p.airportTransferMin || {})[last.place] || 45;
    const earliest = mins(last.arr) + p.disembarkH * 60 + tr + p.airportBeforeH * 60;
    const flights = ff ? (ff.f.returns || []).map((r, i) => ({ i, dep: r.dep, arr: r.arr, ok: mins(r.dep) >= earliest, slackMin: mins(r.dep) - earliest })) : [];
    return { arr: last.arr, place: last.place, transferMin: tr, earliest, offAt: mins(last.arr) + p.disembarkH * 60, flights, exact: ff ? ff.exact : false, timesChecked: ff ? ff.f.returnTimesChecked : false };
  };

  /* ---- trip cost ---- */
  function line(o) { return Object.assign({ usd: null, status: 'unavailable', rowId: null, row: null, who: 'shared', note: '' }, o); }
  function fromRow(id, mult, o) {
    const r = M.row(id);
    const ok = usable(r);
    return line(Object.assign({ rowId: id, row: r, usd: ok ? Math.round(r.usd * mult * 100) / 100 : null, status: r ? r.status : 'unavailable' }, o));
  }
  M.cost = function (s, plan) {
    plan = plan || M.emptyPlan();
    const cab = Object.assign({ b: 'interior', p: 'balcony' }, plan.cab || {});
    const label = Object.fromEntries(CABINS);
    const L = [];
    // cruise fare: one cabin for each pair (rows are per cabin, 2 adults, taxes and fees included)
    L.push(fromRow(s.priceRows[cab.b], 1, { key: 'cab-b', group: 'cruise', who: 'brothers', label: 'Brothers’ cabin (' + label[cab.b] + ')', basisNote: 'per cabin, 2 adults' }));
    L.push(fromRow(s.priceRows[cab.p], 1, { key: 'cab-p', group: 'cruise', who: 'parents', label: 'Parents’ cabin (' + label[cab.p] + ')', basisNote: 'per cabin, 2 adults' }));
    // crew tips
    const ln = M.line[s._line], tips = M.tips(s);
    L.push(line({ key: 'tips', group: 'tips', label: 'Crew tips (' + (tips.rate != null ? M.fmtUsd(tips.rate) : '?') + ' pp/day × 4 × ' + s.nights + ' nights)', rowId: ln && ln.gratuityRow, row: tips.row, usd: tips.total, status: tips.total != null ? tips.status : 'unavailable', note: tips.total == null ? 'Daily tip rate not captured for this line.' : '' }));
    // arrival travel
    const gw = M.gateways(s);
    if (gw.seattle) {
      const ff = M.flightFor(s);
      const set = M.settings;
      const fare = (ff && ff.f.fareRows && ff.f.fareRows[set.fare]) ? set.fare : 'saver';
      if (ff) {
        const fl = fromRow(ff.f.fareRows[fare], 1, { key: 'flights', group: 'travel', label: 'Flights ABQ ↔ Seattle, 4 round trips (' + ({ saver: 'Saver', main: 'Main', first: 'First' }[fare]) + ')', flight: ff.f.id });
        if (!ff.exact && fl.status !== 'family-quote' && fl.usd != null) { fl.status = 'estimate'; fl.note = 'Fare seen for ' + M.fmtDate(ff.f.outboundDate) + '–' + M.fmtDate(ff.f.returnDate) + '; this date pair was not searched.'; }
        L.push(fl);
        const bagN = fare === 'first' ? 0 : 4 * (set.bagsPP || 0) * (set.eachWay ? 2 : 1);
        const bl = fromRow(ff.f.bagRow, bagN, { key: 'bags', group: 'travel', label: 'Checked bags (' + (fare === 'first' ? 'included in First' : (set.bagsPP || 0) + ' per person, ' + (set.eachWay ? 'each way' : 'one charge')) + ')' });
        if (bl.usd != null && bl.status !== 'family-quote') bl.status = bagN ? 'estimate' : bl.status;
        if (bagN === 0 && bl.usd != null) bl.usd = 0;
        L.push(bl);
      } else L.push(line({ key: 'flights', group: 'travel', label: 'Flights ABQ ↔ Seattle', rowId: 'gap:flights-SEA', row: M.row('gap:flights-SEA'), note: 'No flight search covers this sailing.' }));
      const g = M.row('gap:transfers-SEA');
      L.push(line({ key: 'transfers', group: 'travel', label: 'Airport, hotel and pier rides', rowId: 'gap:transfers-SEA', row: g, usd: g && usable(g) ? g.usd : null, status: g ? g.status : 'unavailable', note: g ? '' : 'Taxi, rideshare or shuttle prices were not captured.' }));
      // pre-cruise hotel: 2 rooms, the night before
      const h = M.hotel[set.hotel] || M.hotels[0];
      if (h) {
        const night = M.addDays(s.depart, -1);
        const hl = fromRow(h.rateRow, 2, { key: 'hotel', group: 'hotel', label: h.name + ', 2 rooms, night of ' + M.fmtDate(night), hotel: h.id });
        if (h.stayDate !== night && hl.status !== 'family-quote' && hl.usd != null) { hl.status = 'estimate'; hl.note = 'Rate listed for the night of ' + M.fmtDate(h.stayDate) + '; this night was not searched.'; }
        L.push(hl);
        const tx = M.row(h.taxRow);
        L.push(line({ key: 'hoteltax', group: 'hotel', label: 'Hotel taxes and fees (2 rooms)', rowId: h.taxRow, row: tx, usd: usable(tx) ? Math.round(tx.usd * 2 * 100) / 100 : null, status: tx ? tx.status : 'unavailable', note: usable(tx) ? '' : 'Not shown on the hotel list page.' }));
      }
    } else {
      const k = (gw.from || '?') + '-' + (gw.to || '?');
      const name = { SEA: 'Seattle', YVR: 'Vancouver', ANC: 'Anchorage' };
      const fid = 'gap:flights-' + k, hid = 'gap:hotel-' + (gw.from || '?');
      const fr = M.row(fid), hr = M.row(hid);
      L.push(line({ key: 'flights', group: 'travel', label: 'Flights ABQ → ' + (name[gw.from] || '?') + (gw.to !== gw.from ? ', ' + (name[gw.to] || '?') + ' → ABQ' : ' and back') + ', 4 people', rowId: fid, row: fr, usd: usable(fr) ? fr.usd : null, status: fr ? fr.status : 'unavailable', note: fr ? '' : 'Arrival-city costs for this route are still being researched.' }));
      L.push(line({ key: 'hotel', group: 'hotel', label: 'Hotel before the cruise in ' + (name[gw.from] || '?') + ', 2 rooms', rowId: hid, row: hr, usd: usable(hr) ? hr.usd : null, status: hr ? hr.status : 'unavailable', note: hr ? '' : 'Still being researched.' }));
    }
    // shore activities
    ['p', 'b'].forEach(l => {
      const items = [];
      Object.keys(plan.picks || {}).forEach(day => {
        if (!M.portEntry(s, +day)) return;
        M.planPicks(plan, day, l).forEach(id => {
          if (id === M.ABOARD || !M.offer[id]) return;
          const pr = M.offerPrice(M.offer[id]);
          items.push({ day: +day, id, exp: M.expOfOffer[id], offer: M.offer[id], pp: pr.usd, status: pr.status, row: pr.row, usd: pr.usd != null ? pr.usd * 2 : null });
        });
      });
      const priced = items.filter(i => i.usd != null);
      L.push(line({
        key: 'exc-' + l, group: 'excursions', who: l === 'p' ? 'parents' : 'brothers',
        label: (l === 'p' ? 'Parents’' : 'Brothers’') + ' shore activities (' + items.length + ')',
        usd: items.length ? Math.round(priced.reduce((a, i) => a + i.usd, 0) * 100) / 100 : 0,
        status: items.length ? (priced.length ? M.weakest(priced.map(i => i.status)) : 'unavailable') : 'none',
        items, unpriced: items.length - priced.length,
        note: items.length - priced.length ? (items.length - priced.length) + ' with no price captured' : ''
      }));
    });
    // totals
    const T = { total: 0, parents: 0, brothers: 0, missing: [], statuses: [], byGroup: {}, segs: [] };
    L.forEach(x => {
      if (x.usd == null) { T.missing.push(x); return; }
      T.total += x.usd;
      if (x.status !== 'none' && x.usd > 0) T.statuses.push(x.status);
      if (x.who === 'parents') T.parents += x.usd; else if (x.who === 'brothers') T.brothers += x.usd; else { T.parents += x.usd / 2; T.brothers += x.usd / 2; }
      T.byGroup[x.group] = (T.byGroup[x.group] || 0) + x.usd;
      if (x.usd > 0) {
        // split shore activities by their own row statuses so shading is honest
        if (x.items) {
          const by = {};
          x.items.forEach(i => { if (i.usd != null && i.usd > 0) by[i.status] = (by[i.status] || 0) + i.usd; });
          Object.keys(by).forEach(st => T.segs.push({ group: x.group, status: st, usd: by[st] }));
        } else T.segs.push({ group: x.group, status: x.status, usd: x.usd });
      }
    });
    L.forEach(x => { if (x.unpriced) T.missing.push({ label: x.label + ': ' + x.note, key: x.key + '-unpriced' }); });
    T.status = T.statuses.length ? M.weakest(T.statuses) : 'unavailable';
    T.perPerson = T.total / 4;
    T.days = s.nights + 2;
    T.perDay = T.total / T.days;
    return { lines: L, totals: T, cab, gateways: gw };
  };
  M.COST_GROUPS = [['cruise', 'Cruise fare'], ['tips', 'Crew tips'], ['travel', 'Getting there'], ['hotel', 'Hotel'], ['excursions', 'Shore activities']];

  /* ---- share-link encoding of a plan ---- */
  M.encodePlan = function (plan) {
    const parts = [];
    Object.keys((plan && plan.picks) || {}).sort((a, b) => a - b).forEach(d => ['p', 'b'].forEach(l => M.planPicks(plan, d, l).forEach(id => parts.push(d + l + id))));
    return parts.join(',');
  };
  M.decodePlan = function (str, s) {
    const plan = M.emptyPlan();
    let bad = 0;
    String(str || '').split(',').filter(Boolean).forEach(tok => {
      const m = /^(\d+)([pb])(.+)$/.exec(tok);
      if (!m || (m[3] !== M.ABOARD && !M.offer[m[3]]) || (s && !M.portEntry(s, +m[1]))) { bad++; return; }
      const d = plan.picks[m[1]] = plan.picks[m[1]] || { p: [], b: [] };
      if (!d[m[2]].includes(m[3])) d[m[2]].push(m[3]);
    });
    return { plan, bad };
  };
  M.encodeCab = cab => ({ interior: 'i', oceanview: 'o', balcony: 'b', miniSuite: 'm' }[cab.b] || 'i') + ({ interior: 'i', oceanview: 'o', balcony: 'b', miniSuite: 'm' }[cab.p] || 'b');
  M.decodeCab = function (str) {
    const v = String(str || '');
    return { b: v[0] === 'o' ? 'oceanview' : 'interior', p: v[1] === 'm' ? 'miniSuite' : 'balcony' };
  };

  window.AK = M;
})();
