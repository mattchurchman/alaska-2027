/* Alaska 2027 planner (v2) — data model.
   Loads data/*.json and answers questions about it. No prices are written here:
   every number shown comes from a row in data/prices.json (or is computed from rows). */
(function () {
  'use strict';
  const FILES = ['catalog', 'prices', 'media', 'meta', 'sources'];
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
  }

  /* ---------- prices ---------- */
  M.weakest = function (statuses) {
    let w = 'verified';
    statuses.forEach(s => { if ((STATUS_RANK[s] ?? 4) > STATUS_RANK[w]) w = s; });
    return w;
  };
  M.cabinRow = function (s, cabin) {
    const id = s.priceRows && s.priceRows[cabin];
    return id ? M.rows[id] || null : null;
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
    const r = ln && ln.gratuityRow ? M.rows[ln.gratuityRow] : null;
    if (!usable(r)) return { total: null, status: 'unavailable', row: r };
    return { total: Math.round(r.usd * 4 * s.nights), status: 'estimate', row: r, rate: r.usd };
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

  window.AK = M;
})();
