/* Alaska 2027 planner (v2), Phase 7 — Days, Cost and Shortlist screens.
   Plans, the shortlist, family quotes and settings live in this browser (localStorage) and can be
   exported as JSON, shared as a link, or downloaded as CSV. No price is written here: every amount
   comes from data/prices.json rows (or a family quote) through AK.cost(). */
(function () {
  'use strict';
  const M = window.AK;
  const $ = (s, el) => (el || document).querySelector(s);
  const KEYS = { plans: 'ak27v2:plans', short: 'ak27v2:short', quotes: 'ak27v2:quotes', settings: 'ak27v2:settings' };
  const GROUP_COLOR = { cruise: '#2a78d6', tips: '#eb6834', travel: '#1baf7a', hotel: '#eda100', excursions: '#e87ba4' };
  const STATUS_ORDER = ['verified', 'family-quote', 'published', 'estimate'];
  const MAX_CHART = 4;

  let U; // ui helpers, set in init
  const P = {};
  let plans = {}, short = [], pending = null;
  const offSel = {}; // chosen booking option per card, not yet added

  /* ---------------- storage ---------------- */
  function save(k, v) { U.lsSet(KEYS[k], v); }
  P.init = function () {
    U = window.AKUI;
    plans = U.lsGet(KEYS.plans) || {};
    Object.keys(plans).forEach(k => { if (!M.sailing[k]) delete plans[k]; });
    short = (U.lsGet(KEYS.short) || []).filter(id => M.sailing[id]);
    M.setQuotes(U.lsGet(KEYS.quotes) || {});
    M.settings = Object.assign({}, M.DEFAULT_SETTINGS, U.lsGet(KEYS.settings) || {});
  };
  P.planFor = function (sid) {
    const p = plans[sid];
    if (!p) return M.emptyPlan();
    p.picks = p.picks || {}; p.cab = Object.assign({ b: 'interior', p: 'balcony' }, p.cab || {});
    return p;
  };
  function editPlan(sid) {
    if (!plans[sid]) plans[sid] = M.emptyPlan();
    return P.planFor(sid);
  }
  function commit(sid) {
    if (sid && plans[sid]) plans[sid].updated = new Date().toISOString().slice(0, 10);
    save('plans', plans);
    U.render();
  }
  P.isStarred = sid => short.includes(sid);
  P.costOf = sid => M.cost(M.sailing[sid], P.planFor(sid));

  /* ---------------- shared links ---------------- */
  P.receiveShared = function (sid, shared) {
    const s = M.sailing[sid];
    const dec = M.decodePlan(shared.plan, s);
    const incoming = dec.plan;
    if (shared.cab) incoming.cab = M.decodeCab(shared.cab);
    const mine = P.planFor(sid);
    const same = M.encodePlan(mine) === M.encodePlan(incoming) && M.encodeCab(mine.cab) === M.encodeCab(incoming.cab);
    if (same) return;
    if (!M.planCount(mine) && M.encodeCab(mine.cab) === 'ib') {
      plans[sid] = incoming; save('plans', plans);
      if (M.planCount(incoming)) setTimeout(() => U.toast('Loaded the day plan from the link'), 300);
    } else pending = { sid, plan: incoming, bad: dec.bad };
  };
  P.renderShared = function () {
    const el = $('#sharedBar');
    if (!el) return;
    if (!pending || U.S.sailing !== pending.sid) { el.hidden = true; el.innerHTML = ''; return; }
    el.hidden = false;
    el.innerHTML = '<p><b>This link has a different day plan for this sailing</b> (' + acts(M.planCount(pending.plan)) + '). Yours has ' + acts(M.planCount(P.planFor(pending.sid))) + '.</p>' +
      '<div class="next-row" style="justify-content:flex-start"><button class="btn small" type="button" data-act="shared-use">Use the link’s plan</button><button class="btn small ghost" type="button" data-act="shared-keep">Keep mine</button></div>';
  };

  /* ---------------- small helpers ---------------- */
  const esc = v => U.esc(v);
  function pill(st) { return st === 'none' ? '' : U.statusPill(st); }
  function srcLink(row) {
    const url = M.sourceUrl(row);
    return url ? '<a href="' + esc(url) + '" target="_blank" rel="noopener">source ↗</a>' : '';
  }
  function quoteBtn(rowId, label, row) {
    if (!rowId) return '';
    const has = !!M.quotes[rowId];
    return '<button type="button" class="linkbtn" data-act="quote" data-row="' + esc(rowId) + '" data-label="' + esc(label) + '">' + (has ? 'edit my quote' : 'add my quote') + '</button>';
  }
  function checkedTxt(row) { return row && row.checked ? '<span>checked ' + esc(M.fmtChecked(row.checked)) + '</span>' : ''; }
  function needSailing(what) {
    return '<div class="section-head"><div><h2>' + esc(what) + '</h2></div></div><div class="empty-pick">Pick a sailing first: <a href="#view=date" data-act="view" data-view="date">choose a date</a>' + (short.length ? ' or open one from the <a href="#view=short" data-act="view" data-view="short">shortlist</a>' : '') + '.</div>';
  }
  function sailHead(s) {
    const sh = M.ship[s.ship];
    return '<div class="sail-mini">' + U.lineBadge(s._line) + '<b>' + esc(sh.name) + '</b><span>' + esc(M.fmtDate(s.depart, true)) + ' → ' + esc(M.fmtDate(s.return, true)) + ' · ' + U.plural(s.nights, 'night') + '</span>' + U.routeTag(s._route) +
      '<button class="btn small ghost star-inline" type="button" data-act="star" data-sailing="' + esc(s.id) + '" aria-pressed="' + P.isStarred(s.id) + '">' + (P.isStarred(s.id) ? '★ On shortlist' : '☆ Shortlist') + '</button></div>';
  }
  function hourLabel(m) {
    m = ((m % 1440) + 1440) % 1440;
    const h = Math.floor(m / 60), ap = h >= 12 ? 'pm' : 'am';
    return (h % 12 || 12) + ' ' + ap;
  }
  function placeShort(pid) { return U.placeName(pid, true); }
  function acts(n) { return n + (n === 1 ? ' activity' : ' activities'); }

  /* =================================================================
     DAYS
     ================================================================= */
  function firstPortDay(s) {
    const it = M.itin[s.itinerary];
    const i = (it.days || []).findIndex(d => d.some(e => e.type === 'port'));
    return i < 0 ? 0 : i;
  }
  function dayLabel(day) {
    const main = day.find(e => e.type === 'port') || day.find(e => e.type === 'scenic') || day[0];
    if (main.type === 'sea') return 'At sea';
    if (main.type === 'embark') return 'Board';
    if (main.type === 'disembark') return 'Home';
    return placeShort(main.place);
  }
  function renderDays() {
    const el = $('#v-days');
    const S = U.S;
    if (!S.sailing) { el.innerHTML = needSailing('Plan the days'); return; }
    const s = M.sailing[S.sailing], it = M.itin[s.itinerary];
    if (!it.days) {
      el.innerHTML = '<div class="section-head"><div><h2>Plan the days</h2></div></div>' + sailHead(s) +
        '<div class="empty-pick">Port times were not captured for this sailing, so its days cannot be planned here. Stops: ' + esc(M.stopsOf(it).map(placeShort).join(' → ')) + '.</div>';
      return;
    }
    let day = S.day;
    if (day == null || day < 0 || day >= it.days.length) day = firstPortDay(s);
    const plan = P.planFor(s.id);
    const strip = it.days.map((d, i) => {
      const warn = M.dayWarnings(s, i, plan);
      const n = new Set(['p', 'b'].flatMap(l => M.planPicks(plan, i, l).filter(x => x !== M.ABOARD && M.expOfOffer[x]).map(x => M.expOfOffer[x].id))).size;
      const flag = warn.some(w => w.lv === 'block') ? '<em class="dflag bad" aria-label="problem">!</em>' : warn.some(w => w.lv === 'warn') ? '<em class="dflag warn" aria-label="check">!</em>' : n ? '<em class="dflag ok" aria-label="' + n + ' planned">' + n + '</em>' : '';
      return '<button type="button" class="daychip' + (d.some(e => e.type === 'port') ? ' port' : '') + '" data-act="day" data-day="' + i + '" aria-pressed="' + (i === day) + '"><small>Day ' + (i + 1) + ' · ' + esc(M.fmtDate(M.addDays(s.depart, i), true).split(' ')[0]) + '</small><b>' + esc(dayLabel(d)) + '</b>' + flag + '</button>';
    }).join('');
    const body = it.days[day].map((e, j) => stopBlock(s, day, e, plan, j)).join('');
    const nav = '<div class="next-row daynav">' +
      (day > 0 ? '<button class="btn small ghost" type="button" data-act="day" data-day="' + (day - 1) + '">← Day ' + day + '</button>' : '<span></span>') +
      (day < it.days.length - 1 ? '<button class="btn small" type="button" data-act="day" data-day="' + (day + 1) + '">Day ' + (day + 2) + ' →</button>' : '<button class="btn small" type="button" data-act="view" data-view="cost">See the trip cost →</button>') + '</div>';
    el.innerHTML = '<div class="section-head"><div><h2>Plan the days</h2><p>Pick what the parents and the brothers do at each stop. "All 4" puts it in both plans. The planner keeps each pair’s day inside the time ashore and counts the parents’ walking.</p></div></div>' +
      sailHead(s) +
      '<div class="daystrip chips scroll" role="group" aria-label="Days of the cruise">' + strip + '</div>' +
      '<div class="dayview">' + body + '</div>' + nav;
    const cur = el.querySelector('.daychip[aria-pressed="true"]');
    if (cur && cur.scrollIntoView) { const st = cur.parentNode; st.scrollLeft = cur.offsetLeft - st.clientWidth / 2 + cur.clientWidth / 2; }
  }

  function stopBlock(s, day, e, plan, j) {
    const iso = M.addDays(s.depart, day);
    const head = '<span class="dayno">Day ' + (day + 1) + ' · ' + esc(M.fmtDate(iso, true)) + '</span>';
    const pl = e.place ? M.place[e.place] : null;
    if (e.type === 'sea') return '<article class="card stop sea"><div class="card-body">' + head + '<h3>At sea</h3><p class="muted">A full day on the ship. Nothing to book; no walking needed.</p></div></article>';
    if (e.type === 'embark') return embarkBlock(s, e, head);
    if (e.type === 'disembark') return disembarkBlock(s, e, head);
    if (e.type === 'scenic') return scenicBlock(s, e, head, pl);
    return portBlock(s, day, e, plan, head, pl);
  }

  function embarkBlock(s, e, head) {
    const ff = M.flightFor(s);
    const h = M.hotel[M.settings.hotel];
    let fl = '';
    if (ff) fl = '<p class="small">Fly the day before (' + esc(M.fmtDate(M.addDays(s.depart, -1), true)) + '): Alaska Airlines nonstop ' + ff.f.outbound.map(o => esc(M.fmtTime(o.dep)) + ' → ' + esc(M.fmtTime(o.arr))).join(' or ') + ' (Seattle time on arrival)' + (ff.exact ? '' : '; times seen for ' + esc(M.fmtDate(ff.f.outboundDate)) + ', this date was not searched') + '.' + (h ? ' Night at ' + esc(h.name) + ' (change it under Trip cost).' : '') + '</p>';
    else fl = '<p class="small muted">Flights and the hotel for this gateway are still being researched.</p>';
    return '<article class="card stop"><div class="card-body">' + head + '<h3>Board in ' + esc(placeShort(e.place)) + '</h3><p>' + esc(U.placeName(e.place)) + ' · the ship sails at <b>' + esc(M.fmtTime(e.dep)) + '</b>.</p>' + fl + '</div></article>';
  }

  function disembarkBlock(s, e, head) {
    const rc = M.returnCheck(s);
    let txt = '';
    if (rc && rc.flights.length) {
      txt = '<p class="small">Planning guess: off the ship about ' + esc(M.fmtMins(rc.offAt)) + ', ' + rc.transferMin + ' min to SEA, 2 h at the airport, so a flight at <b>' + esc(M.fmtMins(rc.earliest)) + '</b> or later is comfortable.</p><ul class="rclist">' +
        rc.flights.map(f => '<li class="' + (f.ok ? (f.slackMin < 60 ? 'tight' : 'ok') : 'bad') + '"><b>' + esc(M.fmtTime(f.dep)) + '</b> flight (lands ABQ ' + esc(M.fmtTime(f.arr)) + '): ' + (f.ok ? (f.slackMin < 60 ? 'works, but under an hour to spare' : 'relaxed, ' + M.fmtHours(f.slackMin / 60) + ' to spare') : 'too tight for the parents') + '</li>').join('') + '</ul>' +
        (rc.exact ? '' : '<p class="small muted">Flight times seen for ' + esc(M.fmtDate(M.flightFor(s).f.returnDate)) + '; this date was not searched.</p>');
    } else txt = '<p class="small muted">Flights home from this port are still being researched.</p>';
    return '<article class="card stop"><div class="card-body">' + head + '<h3>Back in ' + esc(placeShort(e.place)) + '</h3><p>The ship arrives about <b>' + esc(M.fmtTime(e.arr)) + '</b>.</p>' + txt + '</div></article>';
  }

  function scenicBlock(s, e, head, pl) {
    const x = M.exps.find(z => z.port === e.place);
    const g = (M.meta.glacierGuide || {})[e.place];
    let guide = '';
    if (g && typeof g === 'object') guide = '<dl class="gguide">' + Object.keys(g).filter(k => typeof g[k] === 'string').map(k => '<dt>' + esc(k) + '</dt><dd>' + esc(g[k]) + '</dd>').join('') + '</dl>';
    else if (typeof g === 'string') guide = '<p>' + esc(g) + '</p>';
    const ph = U.photoHTML(M.photo(['place:' + e.place]), { ratio: '16x9', label: pl ? pl.name : e.place });
    return '<article class="card stop scenic">' + ph + '<div class="card-body">' + head + '<h3>' + esc(pl ? pl.name : e.place) + '</h3>' +
      '<p>Scenic cruising' + (e.arr ? ', about ' + esc(M.fmtTime(e.arr)) + '–' + esc(M.fmtTime(e.dep)) : ' (hours not listed)') + '. Nothing to book: watch from the balcony or the open decks.</p>' +
      (x ? '<p class="small">' + esc(x.blurb) + '</p><p class="small muted">' + esc(x.mobility || '') + '</p>' : '') + guide + '</div></article>';
  }

  function portBlock(s, day, e, plan, head, pl) {
    const timed = M.timed(e);
    const lanes = { p: M.planPicks(plan, day, 'p'), b: M.planPicks(plan, day, 'b') };
    const ph = U.photoHTML(M.photo(['place:' + e.place]), { ratio: '16x9', label: pl ? pl.name : e.place });
    const u = M.usableHours(e);
    const warns = M.dayWarnings(s, day, plan);
    let top = '<article class="card stop port"><div class="stop-top">' + ph + '<div class="card-body">' + head + '<h3>' + esc(pl ? pl.short || pl.name : e.place) + '</h3>' +
      '<p>' + (timed ? 'In port <b>' + esc(M.fmtTime(e.arr)) + '–' + esc(M.fmtTime(e.dep)) + '</b>' + (u != null ? ' · about ' + esc(M.fmtHours(u)) + ' to explore' : '') : 'Port times not captured') + '</p>' +
      (pl && pl.dock ? '<p class="small muted">Where the ship ties up: ' + esc(pl.dock) + '</p>' : '') + '</div></div>' +
      (timed ? timeBar(e, lanes) : '') +
      '<div class="card-body">' + walkMeter(lanes.p) + laneLists(s, day, e, lanes) + warnList(warns) + '</div></article>';
    // option groups
    const xs = M.expsAt(e.place);
    const groups = {};
    xs.forEach(x => { const g = M.groupOf(x, s); (groups[g] = groups[g] || []).push(x); });
    let opts = '';
    if (!xs.length) opts += '<p class="note-box">Things to do in ' + esc(pl ? pl.short || pl.name : e.place) + ' are still being researched. For now the planner offers staying aboard; free time ashore needs no booking.</p>';
    M.GROUPS.forEach(([g, name, desc]) => {
      if (g === 'aboard') { opts += optGroup(name, desc, [aboardCard(s, day, e, lanes)]); return; }
      const list = (groups[g] || []).slice().sort((a, b) => bookable(a, s) - bookable(b, s) || (a.exertion || 0) - (b.exertion || 0));
      if (list.length) opts += optGroup(name, desc, list.map(x => optCard(s, day, e, x, lanes)), g);
    });
    return top + '<div class="optgroups">' + opts + '</div>';
  }
  function bookable(x, s) { return M.offersFor(x, s).length ? 0 : 1; }
  function optGroup(name, desc, cards, g) {
    return '<section class="optgroup' + (g ? ' g-' + g : '') + '"><div class="og-head"><h3>' + esc(name) + ' <span class="muted">' + cards.length + '</span></h3><p class="small muted">' + esc(desc) + '</p></div><div class="optgrid">' + cards.join('') + '</div></section>';
  }

  function timeBar(e, lanes) {
    const w = M.window(e), span = w.dep - w.arr;
    const pct = m => (Math.max(0, Math.min(1, (m - w.arr) / span)) * 100).toFixed(2) + '%';
    const wid = (a, b) => (Math.max(0, Math.min(w.dep, b) - Math.max(w.arr, a)) / span * 100).toFixed(2) + '%';
    let ticks = '';
    const first = Math.ceil(w.arr / 60) * 60;
    let k = 0;
    for (let t = first; t <= w.dep; t += 60, k++) {
      const edge = (t - w.arr) / span;
      ticks += '<span class="tk' + (k % 2 ? ' odd' : '') + (edge > 0.94 ? ' end' : edge < 0.04 ? ' start' : '') + '" style="left:' + pct(t) + '">' + esc(hourLabel(t)) + '</span>';
    }
    const zones = '<i class="tb-zone" style="left:0;width:' + wid(w.arr, w.start) + '"></i><i class="tb-zone back" style="left:' + pct(w.backBy) + ';width:' + wid(w.backBy, w.dep) + '"></i>';
    const marks = '<i class="tb-mark arr" style="left:0"></i><i class="tb-mark aa" style="left:' + pct(w.allAboard) + '"></i><i class="tb-mark dep" style="left:100%"></i>';
    const track = l => {
      const sch = M.schedule(e, lanes[l]);
      let b = '';
      if (sch.aboard) b = '<span class="tb-blk aboard" style="left:' + pct(w.start) + ';width:' + wid(w.start, w.backBy) + '">On the ship</span>';
      sch.items.forEach(it => {
        b += '<span class="tb-blk l-' + l + (it.over ? ' over' : '') + (it.indepLate ? ' late' : '') + '" style="left:' + pct(it.start) + ';width:' + wid(it.start, it.end) + '" title="' + esc(it.exp.name + ', ' + M.fmtMins(it.start) + '–' + M.fmtMins(it.end)) + '">' + esc(it.exp.name) + '</span>';
        if (it.end > w.dep) b += '<span class="tb-overflow">+' + esc(M.fmtHours((it.end - w.dep) / 60)) + '</span>';
      });
      return '<div class="tb-track">' + zones + b + marks + '</div>';
    };
    const label = 'Time ashore from ' + M.fmtTime(e.arr) + ' to ' + M.fmtTime(e.dep) + '. ' + ['p', 'b'].map(l => {
      const sch = M.schedule(e, lanes[l]);
      return (l === 'p' ? 'Parents: ' : 'Brothers: ') + (sch.aboard ? 'on the ship' : sch.items.length ? sch.items.map(i => i.exp.name + ' ' + M.fmtMins(i.start) + ' to ' + M.fmtMins(i.end)).join('; ') : 'nothing planned');
    }).join('. ');
    return '<div class="tbar" role="img" aria-label="' + esc(label) + '">' +
      '<div class="tb-grid"><span></span><div class="tb-axis">' + ticks + '</div>' +
      '<span class="tb-name">Parents</span>' + track('p') +
      '<span class="tb-name">Brothers</span>' + track('b') + '</div>' +
      '<div class="tb-legend">' +
      '<span><i class="lg-blk l-p"></i>Parents’ plan</span><span><i class="lg-blk l-b"></i>Brothers’ plan</span>' +
      '<span><i class="lg-zone"></i>Getting off / back aboard</span>' +
      '<span><i class="lg-mark arr"></i>Arrive ' + esc(M.fmtTime(e.arr)) + '</span>' +
      '<span><i class="lg-mark aa"></i>All aboard ~' + esc(M.fmtMins(w.allAboard)) + '</span>' +
      '<span><i class="lg-mark dep"></i>Sails ' + esc(M.fmtTime(e.dep)) + '</span>' +
      '</div><p class="small muted tb-note">Activities are laid end to end from ' + esc(M.fmtMins(w.start)) + ' with 15 min between. Real tour start times will differ; all aboard is usually 30 min before sailing (check the ship’s daily planner).</p></div>';
  }

  function walkMeter(pIds) {
    const wk = M.walkFor(pIds), budget = M.walkBudget();
    const over = wk.mi > budget + 1e-6;
    const scale = Math.max(budget * 1.5, wk.mi, 0.1);
    const conf = { documented: 'measured', derived: 'worked out from maps', estimate: 'estimate' }[wk.confidence] || wk.confidence;
    return '<div class="walk' + (over ? ' over' : '') + '"><div class="walk-top"><b>Parents’ walking</b><span>about <b>' + wk.mi + ' mi</b> of ' + budget + ' mi budget' + (wk.mi && pIds.some(x => x !== M.ABOARD) ? ' <span class="wconf">' + esc(conf) + '</span>' : '') + (wk.unknown ? ' <span class="wconf">+ ' + wk.unknown + ' not measured</span>' : '') + '</span></div>' +
      '<div class="walk-bar" role="meter" aria-valuemin="0" aria-valuemax="' + scale + '" aria-valuenow="' + wk.mi + '" aria-label="Parents walking ' + wk.mi + ' miles of a ' + budget + ' mile budget"><i style="width:' + Math.min(100, wk.mi / scale * 100).toFixed(1) + '%"></i><b style="left:' + (budget / scale * 100).toFixed(1) + '%" title="Budget"></b></div>' +
      '<p class="small muted">Dock to the start, on the tour and back, per person. Change the budget under <a href="#view=cost" data-act="view" data-view="cost">Trip cost → Background costs</a>.</p></div>';
  }

  function laneLists(s, day, e, lanes) {
    return '<div class="lanes">' + M.LANES.map(([l, who]) => {
      const ids = lanes[l];
      let inner;
      if (ids.includes(M.ABOARD)) inner = '<li class="aboard">Staying on the ship <button type="button" class="xbtn" data-act="unpick" data-day="' + day + '" data-lane="' + l + '" data-offer="' + M.ABOARD + '" aria-label="Remove: staying on the ship">✕</button></li>';
      else if (!ids.length) inner = '<li class="none">Nothing picked: free time ashore</li>';
      else {
        const sch = M.timed(e) ? M.schedule(e, ids) : null;
        inner = ids.map((id, i) => {
          const o = M.offer[id], x = M.expOfOffer[id];
          if (!o) return '';
          const pr = M.offerPrice(o);
          const it = sch && sch.items[i];
          return '<li' + (it && it.over ? ' class="over"' : '') + '>' + (it ? '<span class="t">' + esc(M.fmtMins(it.start)) + '–' + esc(M.fmtMins(it.end)) + '</span>' : '') +
            '<span class="n"><b>' + esc(x.name) + '</b><small>' + esc(o.provider) + ' · ' + (pr.usd == null ? 'no price captured' : pr.usd === 0 ? 'free' : esc(M.fmtUsd(pr.usd)) + ' pp, ' + esc(M.fmtUsd(pr.usd * 2)) + ' for 2') + '</small></span>' +
            '<button type="button" class="xbtn" data-act="unpick" data-day="' + day + '" data-lane="' + l + '" data-offer="' + esc(id) + '" aria-label="Remove ' + esc(x.name) + ' for the ' + who.toLowerCase() + '">✕</button></li>';
        }).join('');
      }
      return '<div class="lane l-' + l + '"><h4>' + who + '</h4><ul>' + inner + '</ul></div>';
    }).join('') + '</div>';
  }

  function warnList(ws) {
    if (!ws.length) return '';
    const icon = { block: '⛔', warn: '⚠️', info: 'ℹ️' };
    const order = { block: 0, warn: 1, info: 2 };
    return '<ul class="warns">' + ws.slice().sort((a, b) => order[a.lv] - order[b.lv]).map(w => '<li class="lv-' + w.lv + '"><span aria-hidden="true">' + icon[w.lv] + '</span><span>' + esc(w.text) + '</span></li>').join('') + '</ul>';
  }

  function optCard(s, day, e, x, lanes) {
    const offs = M.offersFor(x, s);
    const key = s.id + '|' + day + '|' + x.id;
    const picked = {};
    ['p', 'b'].forEach(l => { picked[l] = lanes[l].find(id => M.expOfOffer[id] && M.expOfOffer[id].id === x.id) || null; });
    const curId = picked.p || picked.b || (offSel[key] && offs.some(o => o.id === offSel[key]) ? offSel[key] : null) || (M.defaultOffer(x, s) || {}).id;
    const o = curId ? M.offer[curId] : null;
    const ph = U.photoHTML(M.photo(['experience:' + x.id, x.poi ? 'poi:' + x.poi : null, 'place:' + (x.photoPlace || x.port)]), { ratio: '16x9', label: x.name });
    const labelTxt = M.expLabels[x.label] || x.label;
    const walk = typeof x.walkMiles === 'number' ? '~' + x.walkMiles + ' mi walking' : 'walking not measured';
    let body = '<div class="card-body"><h4>' + esc(x.name) + '</h4><div class="xtags"><span class="xl xl-' + esc(x.label) + '">' + esc(labelTxt) + '</span><span>Effort ' + esc(x.exertion) + '/5</span><span>' + esc(walk) + '</span>' + (o ? '<span>' + esc(M.offerHours(o).assumed ? 'length not stated' : M.fmtHours(M.offerHours(o).h)) + '</span>' : '') + (x.parentsDrive ? '<span class="xl xl-ideal_parents">Easy self-drive</span>' : '') + '</div>' +
      '<p class="small">' + esc(x.blurb) + '</p>';
    if (!offs.length) {
      const lines = Array.from(new Set((x.offers || []).filter(z => z.kind === 'cruise').map(z => (M.line[z.line] || {}).name || z.line)));
      body += '<p class="small muted nob">Not bookable on this sailing: only sold by ' + esc(lines.join(', ') || 'other cruise lines') + '.</p></div>';
      return '<article class="card opt dim">' + ph + body + '</article>';
    }
    const pr = M.offerPrice(o);
    if (offs.length > 1) {
      body += '<label class="offsel"><span>Book through</span><select data-act="offer" data-key="' + esc(key) + '" data-day="' + day + '" data-exp="' + esc(x.id) + '">' +
        offs.map(z => { const zp = M.offerPrice(z); return '<option value="' + esc(z.id) + '"' + (z.id === curId ? ' selected' : '') + '>' + esc(z.provider) + ' · ' + (zp.usd == null ? 'price n/a' : zp.usd === 0 ? 'free' : M.fmtUsd(zp.usd)) + (z.hours ? ' · ' + M.fmtHours(z.hours) : '') + '</option>'; }).join('') + '</select></label>';
    } else body += '<p class="small offone">' + esc(o.provider) + (o.title && o.title !== o.provider ? ': ' + esc(o.title) : '') + '</p>';
    body += '<div class="oprice"><b>' + (pr.usd == null ? 'No price captured' : pr.usd === 0 ? 'Free' : esc(M.fmtUsd(pr.usd)) + ' <small>per person</small>') + '</b>' + pill(pr.status) + '</div>' +
      '<div class="cab-meta">' + esc((M.offerKinds[o.kind] || o.kind)) + ' ' + checkedTxt(pr.row) + ' ' + srcLink(pr.row) + ' ' + quoteBtn(o.priceRow, x.name + ' (' + o.provider + ')', pr.row) + '</div>';
    // lane buttons with time-fit
    const fit = {};
    ['p', 'b'].forEach(l => { fit[l] = picked[l] ? { ok: true } : M.canAdd(e, lanes[l], o.id); });
    const tooLong = fit.p.tooLong || fit.b.tooLong;
    const btn = (l, txt) => '<button type="button" class="pickbtn l-' + l + '" data-act="pick-lane" data-lane="' + l + '" data-day="' + day + '" data-offer="' + esc(o.id) + '" aria-pressed="' + !!picked[l] + '"' + (!picked[l] && !fit[l].ok ? ' disabled title="' + esc(fit[l].reason) + '"' : '') + '>' + (picked[l] ? '✓ ' : '+ ') + txt + '</button>';
    const both = picked.p && picked.b;
    const bothOk = both || ((picked.p || fit.p.ok) && (picked.b || fit.b.ok));
    body += '<div class="pickrow">' + btn('p', 'Parents') + btn('b', 'Brothers') +
      '<button type="button" class="pickbtn l-f" data-act="pick-all" data-day="' + day + '" data-offer="' + esc(o.id) + '" aria-pressed="' + !!both + '"' + (bothOk ? '' : ' disabled') + '>' + (both ? '✓ ' : '+ ') + 'All 4</button></div>';
    if (tooLong) body += '<p class="fitmsg">' + esc(fit.p.reason || fit.b.reason) + '</p>';
    else ['p', 'b'].forEach(l => { if (!fit[l].ok) body += '<p class="fitmsg">' + (l === 'p' ? 'Parents' : 'Brothers') + ': ' + esc(fit[l].reason.replace(/^No room left: /, 'no room left, ')) + '</p>'; });
    if (picked.p && x.label !== 'ideal_parents' && x.label !== 'everyone' && (x.label === 'brothers' || x.label === 'not_recommended' || x.exertion >= 3)) body += '<p class="fitmsg">Check the notes before booking this for the parents.</p>';
    // details
    const det = [
      ['Getting around', x.mobility], ['Stairs and hills', x.stairsHills], ['Walking', x.walkBasis ? x.walkBasis + (x.walkConfidence ? ' (' + x.walkConfidence + ')' : '') : null],
      ['Seating', x.seating], ['Weather', x.weather ? 'Weather sensitivity: ' + x.weather : null], ['Wheelchair', o.wheelchair && o.wheelchair !== 'not_stated' ? o.wheelchair : null],
      ['Cancellation', o.cancel], ['About this booking option', o.note], ['Good to know', x.caveat], ['Risk', x.risk && x.risk.text]
    ].filter(d => d[1]);
    body += '<details class="xdet"><summary>Details</summary><dl>' + det.map(d => '<dt>' + esc(d[0]) + '</dt><dd>' + esc(d[1]) + '</dd>').join('') + '</dl>' +
      (o.url ? '<p class="small"><a href="' + esc(o.url) + '" target="_blank" rel="noopener">Booking page ↗</a></p>' : '') + '</details></div>';
    return '<article class="card opt' + (picked.p || picked.b ? ' sel' : '') + '">' + ph + body + '</article>';
  }

  function aboardCard(s, day, e, lanes) {
    const on = { p: lanes.p.includes(M.ABOARD), b: lanes.b.includes(M.ABOARD) };
    const b = (l, t) => '<button type="button" class="pickbtn l-' + l + '" data-act="aboard" data-lane="' + l + '" data-day="' + day + '" aria-pressed="' + on[l] + '">' + (on[l] ? '✓ ' : '+ ') + t + '</button>';
    return '<article class="card opt aboard-card"><div class="card-body"><h4>Stay on the ship</h4><div class="xtags"><span class="xl xl-ideal_parents">Zero walking</span><span>Free</span></div><p class="small">Quiet pools, spa, the view from the balcony, or a nap. Picking this clears that pair’s other plans for the day.</p>' +
      '<div class="pickrow">' + b('p', 'Parents') + b('b', 'Brothers') + '<button type="button" class="pickbtn l-f" data-act="aboard-all" data-day="' + day + '" aria-pressed="' + (on.p && on.b) + '">' + (on.p && on.b ? '✓ ' : '+ ') + 'All 4</button></div></div></article>';
  }

  /* ---- day edits ---- */
  function laneArr(sid, day, l) {
    const plan = editPlan(sid);
    const d = plan.picks[day] = plan.picks[day] || { p: [], b: [] };
    d.p = d.p || []; d.b = d.b || [];
    return d[l];
  }
  function cleanDay(sid, day) {
    const plan = plans[sid];
    const d = plan && plan.picks[day];
    if (d && !(d.p || []).length && !(d.b || []).length) delete plan.picks[day];
  }
  function toggleLane(sid, day, l, offerId, forceOn) {
    const s = M.sailing[sid], e = M.portEntry(s, day);
    const arr = laneArr(sid, day, l);
    const x = M.expOfOffer[offerId];
    const idx = arr.findIndex(id => M.expOfOffer[id] && M.expOfOffer[id].id === x.id);
    if (idx >= 0 && forceOn !== true) { arr.splice(idx, 1); return 'removed'; }
    if (idx >= 0) return 'kept';
    const ab = arr.indexOf(M.ABOARD); if (ab >= 0) arr.splice(ab, 1);
    const fit = M.canAdd(e, arr, offerId);
    if (!fit.ok) { U.toast(fit.reason); return 'blocked'; }
    arr.push(offerId);
    return 'added';
  }

  /* =================================================================
     COST
     ================================================================= */
  function renderCost() {
    const el = $('#v-cost');
    const S = U.S;
    let html = '<div class="section-head"><div><h2>What the trip costs</h2><p>Everything for 4 people: two cabins, crew tips, flights and bags, the hotel night before, and the shore activities in your day plan. Each line shows how sure the number is.</p></div></div>';
    if (!S.sailing && !short.length) { el.innerHTML = needSailing('What the trip costs'); return; }
    if (S.sailing) {
      const s = M.sailing[S.sailing], plan = P.planFor(s.id), c = M.cost(s, plan);
      html += sailHead(s) + costSummary(s, c, plan) + costLines(s, c);
    }
    html += chartCard();
    html += assumptionsCard();
    el.innerHTML = html;
  }

  function costSummary(s, c, plan) {
    const T = c.totals;
    const cabSel = (who, opts) => '<label class="offsel"><span>' + (who === 'b' ? 'Brothers’ cabin' : 'Parents’ cabin') + '</span><select data-act="cabin" data-who="' + who + '">' + opts.map(k => {
      const r = M.cabinRow(s, k);
      const lbl = Object.fromEntries(M.CABINS)[k];
      return '<option value="' + k + '"' + (c.cab[who] === k ? ' selected' : '') + '>' + esc(lbl) + ' · ' + (r && r.status !== 'unavailable' ? M.fmtUsd(r.usd) : 'not captured') + '</option>';
    }).join('') + '</select></label>';
    return '<div class="card costsum"><div class="card-body">' +
      '<div class="cs-main"><div><span class="k">Trip total, 4 people</span><b class="big">' + M.fmtUsd(T.total) + '</b>' + U.statusPill(T.status, 'Weakest: ' + (M.STATUS_SHORT[T.status] || T.status)) + '</div>' +
      '<div class="cs-split"><div><span class="k">Parents</span><b>' + M.fmtUsd(T.parents) + '</b></div><div><span class="k">Brothers</span><b>' + M.fmtUsd(T.brothers) + '</b></div><div><span class="k">Per person</span><b>' + M.fmtUsd(T.perPerson) + '</b></div><div><span class="k">Per day (' + T.days + ' days)</span><b>' + M.fmtUsd(T.perDay) + '</b></div></div></div>' +
      (T.missing.length ? '<p class="note-box miss"><b>Not in the total yet:</b> ' + T.missing.map(m => esc(m.label)).join('; ') + '. Add your own number with “add my quote” where you have one.</p>' : '') +
      '<p class="small muted">Shared costs (tips, flights, bags, rides) are split evenly; each pair pays its own cabin, hotel room and activities. Days count from the flight to Seattle to the flight home.</p>' +
      '<div class="cabsel">' + cabSel('b', ['interior', 'oceanview']) + cabSel('p', ['balcony', 'miniSuite']) + '</div></div></div>';
  }

  function costLines(s, c) {
    const who = { parents: 'Parents', brothers: 'Brothers', shared: 'Shared' };
    const rows = c.lines.map(x => {
      const row = x.row;
      let sub = '';
      if (x.items) {
        sub = x.items.length ? '<ul class="cl-items">' + x.items.map(i => '<li><span>Day ' + (i.day + 1) + ' · ' + esc(i.exp.name) + ' <small>(' + esc(i.offer.provider) + ')</small></span><span>' + (i.pp == null ? 'no price' : i.pp === 0 ? 'free' : esc(M.fmtUsd(i.pp)) + ' × 2') + ' ' + pill(i.status) + ' ' + quoteBtn(i.offer.priceRow, i.exp.name + ' (' + i.offer.provider + ')', i.row) + '</span></li>').join('') + '</ul>'
          : '<p class="small muted">Nothing picked yet. <a href="#view=days" data-act="view" data-view="days">Plan the days →</a></p>';
      }
      const qlabel = x.label + ', ' + M.ship[s.ship].name + ' ' + M.fmtDate(s.depart);
      return '<div class="cl' + (x.usd == null ? ' gap' : '') + '"><div class="cl-what"><b>' + esc(x.label) + '</b>' + (x.note ? '<small>' + esc(x.note) + '</small>' : '') + (row && row.basis && !x.items ? '<small class="muted">Price basis: ' + esc(row.basis) + '</small>' : '') + sub + '</div>' +
        '<div class="cl-who">' + who[x.who] + '</div>' +
        '<div class="cl-amt">' + (x.usd == null ? '<span class="muted">not captured</span>' : M.fmtUsd(x.usd)) + '</div>' +
        '<div class="cl-st">' + (x.status === 'none' ? '' : U.statusPill(x.status)) + ' ' + checkedTxt(row) + ' ' + srcLink(row) + ' ' + (x.items ? '' : quoteBtn(x.rowId, qlabel, row)) + '</div></div>';
    }).join('');
    return '<div class="card"><div class="card-body"><h3 class="ch">Line by line</h3><div class="clist"><div class="cl head"><div>Item</div><div class="cl-who">Who</div><div class="cl-amt">Amount</div><div class="cl-st">How sure</div></div>' + rows +
      '<div class="cl total"><div class="cl-what"><b>Total</b></div><div class="cl-who"></div><div class="cl-amt">' + M.fmtUsd(c.totals.total) + '</div><div class="cl-st">' + (c.totals.missing.length ? '+ ' + c.totals.missing.length + ' not captured' : '') + '</div></div></div></div></div>';
  }

  function chartOptions() {
    const S = U.S;
    const ids = [];
    if (S.sailing && !short.includes(S.sailing)) ids.push(S.sailing);
    short.forEach(id => { if (ids.length < MAX_CHART) ids.push(id); });
    return ids;
  }
  function segsSorted(T) {
    const out = [];
    M.COST_GROUPS.forEach(([g]) => STATUS_ORDER.forEach(st => {
      const v = T.segs.filter(x => x.group === g && x.status === st).reduce((a, x) => a + x.usd, 0);
      if (v > 0) out.push({ group: g, status: st, usd: v });
    }));
    // statuses outside the usual order (e.g. "user") at the end of their group
    T.segs.forEach(x => { if (!STATUS_ORDER.includes(x.status)) out.push(x); });
    return out;
  }
  function chartCard() {
    const ids = chartOptions();
    const S = U.S;
    let body;
    if (!ids.length) body = '<p class="muted">Star sailings to compare up to four of them here.</p>';
    else {
      const data = ids.map(id => ({ s: M.sailing[id], c: P.costOf(id) }));
      const max = Math.max.apply(null, data.map(d => d.c.totals.total)) || 1;
      const gname = Object.fromEntries(M.COST_GROUPS);
      body = '<div class="stack" role="list">' + data.map(d => {
        const T = d.c.totals;
        const segs = segsSorted(T);
        const cur = d.s.id === S.sailing;
        const bar = segs.map(g => '<i class="seg st-' + esc(g.status) + '" style="flex:' + g.usd.toFixed(2) + ' 1 0;background-color:' + GROUP_COLOR[g.group] + '" title="' + esc(gname[g.group] + ': ' + M.fmtUsd(g.usd) + ' (' + (M.STATUS_SHORT[g.status] || g.status) + ')') + '"></i>').join('');
        const parts = M.COST_GROUPS.map(([g, n]) => T.byGroup[g] != null ? '<span><i class="sw" style="background:' + GROUP_COLOR[g] + '"></i>' + esc(n) + ' ' + M.fmtUsd(T.byGroup[g]) + '</span>' : '').join('');
        return '<div class="srow' + (cur ? ' cur' : '') + '" role="listitem"><div class="slabel"><button type="button" class="linkbtn" data-act="pick" data-sailing="' + esc(d.s.id) + '">' + U.lineBadge(d.s._line) + ' ' + esc(M.ship[d.s.ship].name) + ', ' + esc(M.fmtDate(d.s.depart, true)) + '</button>' + (short.includes(d.s.id) ? '' : ' <span class="muted small">(not starred)</span>') + '</div>' +
          '<div class="sbarrow"><div class="sbar" style="width:' + (T.total / max * 100).toFixed(1) + '%">' + bar + '</div><span class="stot">' + M.fmtUsd(T.total) + (T.missing.length ? ' <small>+ ' + T.missing.length + ' ?</small>' : '') + '</span></div>' +
          '<div class="sparts small">' + parts + ' <span>' + acts(M.planCount(P.planFor(d.s.id))) + ' planned</span></div></div>';
      }).join('') + '</div>' +
        '<div class="slegend small"><span class="lg-h">Colour = what it’s for:</span>' + M.COST_GROUPS.map(([g, n]) => '<span><i class="sw" style="background:' + GROUP_COLOR[g] + '"></i>' + esc(n) + '</span>').join('') + '</div>' +
        '<div class="slegend small"><span class="lg-h">Fill = how sure:</span><span><i class="sw st-verified"></i>Verified or family quote</span><span><i class="sw st-published"></i>Published (list or “from” price)</span><span><i class="sw st-estimate"></i>Planner estimate</span><span>“+ N ?” = items not captured, not in the bar</span></div>' +
        (short.length > MAX_CHART ? '<p class="small muted">Showing the first ' + MAX_CHART + ' starred sailings. Unstar one on the Shortlist to bring in another.</p>' : '');
    }
    return '<div class="card"><div class="card-body"><h3 class="ch">Compare the shortlist</h3><p class="small muted">Each bar is one sailing with its own day plan and cabin choice. Same flight, bag and hotel settings for all.</p>' + body + '</div></div>';
  }

  function assumptionsCard() {
    const S = U.S, set = M.settings;
    const s = S.sailing ? M.sailing[S.sailing] : null;
    const ff = s ? M.flightFor(s) : (M.flights.find(f => f.stops === 0) ? { f: M.flights.find(f => f.stops === 0), exact: false } : null);
    let fl = '';
    if (ff) {
      const f = ff.f;
      const fareOpt = ['saver', 'main', 'first'].filter(k => f.fareRows && f.fareRows[k]).map(k => {
        const r = M.row(f.fareRows[k]);
        return '<option value="' + k + '"' + (set.fare === k ? ' selected' : '') + '>' + ({ saver: 'Saver (no changes)', main: 'Main (free changes)', first: 'First (2 bags free)' }[k]) + ' · ' + (r && r.usd != null ? M.fmtUsd(r.usd) : 'n/a') + ' for 4</option>';
      }).join('');
      const bagRow = M.row(f.bagRow);
      fl = '<div class="as-block"><h4>Flights ABQ ↔ Seattle</h4>' +
        '<p class="small">Alaska Airlines is the only nonstop seen (' + f.outbound.map(o => esc(M.fmtTime(o.dep)) + '→' + esc(M.fmtTime(o.arr))).join(', ') + ' out; ' + (f.returns || []).map(o => esc(M.fmtTime(o.dep)) + '→' + esc(M.fmtTime(o.arr))).join(', ') + ' back). ' + (s ? (ff.exact ? 'Fares are for this sailing’s dates.' : 'This sailing’s dates were not searched; the planner uses the fare seen for ' + esc(M.fmtDate(f.outboundDate)) + '–' + esc(M.fmtDate(f.returnDate)) + ' (the same fare showed on all six pairs searched).') : '') + '</p>' +
        '<div class="as-ctl"><label class="offsel"><span>Fare</span><select data-act="set" data-key="fare">' + fareOpt + '</select></label>' +
        '<label class="offsel"><span>Checked bags per person</span><select data-act="set" data-key="bagsPP">' + [0, 1, 2].map(n => '<option value="' + n + '"' + (+set.bagsPP === n ? ' selected' : '') + '>' + n + '</option>').join('') + '</select></label>' +
        '<label class="toggle"><input type="checkbox" data-act="set" data-key="eachWay"' + (set.eachWay ? ' checked' : '') + '> Bag fee charged each way</label></div>' +
        '<p class="small muted">' + esc(f.restrictions || '') + ' Bag fee ' + (bagRow && bagRow.usd != null ? M.fmtUsd(bagRow.usd) : '?') + ' per person: ' + esc(bagRow ? bagRow.note || '' : '') + '</p>' +
        '<p class="small">' + U.statusPill(M.row(f.fareRows.saver) ? M.row(f.fareRows.saver).status : 'unavailable') + ' checked ' + esc(M.fmtChecked(f.checked)) + ' · <a href="' + esc(f.url) + '" target="_blank" rel="noopener">Search these dates on Google Flights ↗</a>' + (f.bookUrl ? ' · <a href="' + esc(f.bookUrl) + '" target="_blank" rel="noopener">Alaska Airlines ↗</a>' : '') + '</p></div>';
    }
    const hotels = '<div class="as-block"><h4>Hotel the night before (2 rooms)</h4><p class="small muted">Rates were read for the night of Jun 11, 2027 only, 1 room for 2, before taxes. Other nights use the same rate as an estimate.</p><div class="hotels" role="radiogroup" aria-label="Seattle hotel">' +
      M.hotels.map(h => {
        const r = M.row(h.rateRow);
        const d = h.distances || {};
        const dist = [d.pier66Mi != null ? d.pier66Mi + ' mi to Pier 66' : '', d.pier91Mi != null ? d.pier91Mi + ' mi to Pier 91' : '', d.airportMi != null ? d.airportMi + ' mi to the airport' : ''].filter(Boolean).join(' · ');
        return '<label class="hotel' + (set.hotel === h.id ? ' on' : '') + '"><input type="radio" name="hotel" data-act="set" data-key="hotel" value="' + esc(h.id) + '"' + (set.hotel === h.id ? ' checked' : '') + '><span class="h-main"><b>' + esc(h.name) + '</b><small>' + esc(h.area) + (h.reviewScore ? ' · ' + h.reviewScore + ' (' + (h.reviewCount || '?').toLocaleString('en-US') + ' reviews)' : '') + (h.accessibilityListed ? ' · accessible listed' : '') + (dist ? ' · ' + esc(dist) : '') + '</small><small class="muted">' + esc(h.pros || '') + '</small></span>' +
          '<span class="h-p"><b>' + (r && r.usd != null ? M.fmtUsd(r.usd) : '?') + '</b><small>per room</small>' + U.statusPill(r ? r.status : 'unavailable') + '</span></label>';
      }).join('') + '</div><p class="small"><a href="' + esc((M.hotel[set.hotel] || M.hotels[0] || {}).url || '#') + '" target="_blank" rel="noopener">Search this hotel area on Google Hotels ↗</a> · ' + quoteBtn('gap:transfers-SEA', 'Airport, hotel and pier rides (Seattle), total for 4', M.row('gap:transfers-SEA')) + ' for rides</p></div>';
    const walk = '<div class="as-block"><h4>Parents’ walking budget</h4><label class="offsel"><span>Miles per day</span><select data-act="set" data-key="walkBudget">' + [1, 1.5, 2, 2.5, 3, 4].map(n => '<option value="' + n + '"' + (M.walkBudget() === n ? ' selected' : '') + '>' + n + ' mi</option>').join('') + '</select></label><p class="small muted">The Days screen warns when the parents’ picks add up to more than this.</p></div>';
    const notes = (M.pl().notes || []).map(n => '<li>' + esc(n) + '</li>').join('');
    return '<div class="card" id="assumptions"><div class="card-body"><h3 class="ch">Background costs and assumptions</h3>' + fl + hotels + walk +
      '<details class="xdet"><summary>How times and totals are worked out</summary><ul class="small">' + notes + '<li>Vancouver and Anchorage flights and hotels are still being researched; those lines show as not captured until then.</li><li>Family quotes you add replace the researched number everywhere and are stored only in this browser (include them by exporting a backup).</li></ul></details></div></div>';
  }

  /* =================================================================
     SHORTLIST
     ================================================================= */
  function renderShort() {
    const el = $('#v-short');
    let html = '<div class="section-head"><div><h2>Shortlist</h2><p>Starred sailings with their day plans. Share one as a link, or save everything as a backup to move it to another phone or computer.</p></div></div>';
    if (!short.length) html += '<div class="empty-pick">Nothing starred yet. Open a sailing on <a href="#view=date" data-act="view" data-view="date">Dates</a> and tap ☆ Shortlist.</div>';
    else {
      html += '<div class="grid cols-2 shortgrid">' + short.map(id => {
        const s = M.sailing[id], sh = M.ship[s.ship], plan = P.planFor(id), c = M.cost(s, plan), T = c.totals;
        const it = M.itin[s.itinerary];
        let worst = 0, warnN = 0, blockN = 0;
        (it.days || []).forEach((d, i) => {
          worst = Math.max(worst, M.walkFor(M.planPicks(plan, i, 'p')).mi);
          M.dayWarnings(s, i, plan).forEach(w => { if (w.lv === 'warn') warnN++; if (w.lv === 'block') blockN++; });
        });
        return '<article class="card shortcard">' + U.photoHTML(M.photo(['ship:' + sh.id]), { ratio: '16x9', label: sh.name }) +
          '<div class="card-body"><div class="sc-top">' + U.lineBadge(s._line) + '<h3>' + esc(sh.name) + '</h3></div>' +
          '<p class="sub">' + esc(M.fmtDate(s.depart, true)) + ' → ' + esc(M.fmtDate(s.return, true)) + ' · ' + U.plural(s.nights, 'night') + ' ' + U.routeTag(s._route) + '</p>' +
          '<div class="price-big"><b>' + M.fmtUsd(T.total) + '</b>' + U.statusPill(T.status) + '</div>' +
          '<p class="small">Parents ' + M.fmtUsd(T.parents) + ' · Brothers ' + M.fmtUsd(T.brothers) + (T.missing.length ? ' · <span class="muted">' + T.missing.length + ' not captured</span>' : '') + '</p>' +
          '<p class="small">' + acts(M.planCount(plan)) + ' planned · parents’ longest walk ' + worst + ' mi' + (blockN ? ' · <b class="bad">' + blockN + ' timing problem' + (blockN > 1 ? 's' : '') + '</b>' : '') + (warnN ? ' · ' + warnN + ' to check' : '') + '</p>' +
          '<div class="next-row" style="justify-content:flex-start"><button class="btn small" type="button" data-act="open-days" data-sailing="' + esc(id) + '">Days</button><button class="btn small ghost" type="button" data-act="open-cost" data-sailing="' + esc(id) + '">Cost</button><button class="btn small ghost" type="button" data-act="share-opt" data-sailing="' + esc(id) + '">Share</button><button class="btn small ghost" type="button" data-act="star" data-sailing="' + esc(id) + '" aria-pressed="true" aria-label="Remove from shortlist">★ Remove</button></div></div></article>';
      }).join('') + '</div>';
    }
    // quotes
    const qk = Object.keys(M.quotes);
    html += '<div class="card"><div class="card-body"><h3 class="ch">Your quotes</h3>' + (qk.length ? '<ul class="qlist">' + qk.map(k => {
      const q = M.quotes[k], orig = M.rows[k];
      return '<li><span><b>' + esc(q.label || k) + '</b><small>' + esc(M.fmtUsd(q.usd)) + (q.basis ? ' (' + esc(q.basis) + ')' : '') + (orig && orig.usd != null ? ' · research said ' + esc(M.fmtUsd(orig.usd)) : '') + (q.date ? ' · ' + esc(M.fmtChecked(q.date)) : '') + (q.note ? ' · ' + esc(q.note) : '') + '</small></span><button type="button" class="linkbtn" data-act="quote" data-row="' + esc(k) + '" data-label="' + esc(q.label || k) + '">edit</button></li>';
    }).join('') + '</ul>' : '<p class="small muted">None yet. Use “add my quote” next to any price when someone gets a real number from a cruise line, agent, airline or hotel.</p>') + '</div></div>';
    // export / import
    html += '<div class="card"><div class="card-body"><h3 class="ch">Save and move</h3><p class="small muted">Plans, stars and quotes are kept in this browser only. A backup file carries them to another device.</p>' +
      '<div class="next-row" style="justify-content:flex-start"><button class="btn small" type="button" data-act="export-json">Save a backup (JSON)</button><button class="btn small ghost" type="button" data-act="export-cost-csv">Costs (CSV)</button><button class="btn small ghost" type="button" data-act="export-days-csv">Day plans (CSV)</button></div>' +
      '<h4 style="margin:16px 0 6px">Load a backup</h4><div class="next-row" style="justify-content:flex-start"><label class="btn small ghost filebtn">Choose a file<input type="file" accept=".json,application/json" data-act="import-file"></label></div>' +
      '<details class="xdet"><summary>Or paste the backup text</summary><textarea id="importText" rows="4" aria-label="Paste backup JSON"></textarea><button class="btn small ghost" type="button" data-act="import-text">Load pasted text</button></details></div></div>';
    el.innerHTML = html;
  }

  /* ---------------- export / import ---------------- */
  function download(name, text, type) {
    const blob = new Blob([text], { type: type || 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = name; a.rel = 'noopener';
    document.body.appendChild(a); a.click();
    setTimeout(() => { URL.revokeObjectURL(url); a.remove(); }, 1500);
  }
  const today = () => { const d = new Date(); return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0'); };
  function backup() {
    return { app: 'alaska-2027-planner', format: 1, exported: new Date().toISOString(), dataVersion: M.meta.version || null, settings: M.settings, shortlist: short, plans, quotes: M.quotes };
  }
  function csvCell(v) { v = v == null ? '' : String(v); return /[",\n]/.test(v) ? '"' + v.replace(/"/g, '""') + '"' : v; }
  function csv(rows) { return rows.map(r => r.map(csvCell).join(',')).join('\r\n') + '\r\n'; }
  function exportIds() { // shortlist first, then the open sailing, then any other sailing with a day plan
    const ids = short.slice();
    if (U.S.sailing && !ids.includes(U.S.sailing)) ids.push(U.S.sailing);
    Object.keys(plans).forEach(id => { if (!ids.includes(id) && M.sailing[id] && M.planCount(plans[id])) ids.push(id); });
    return ids;
  }
  function costCsv() {
    const head = ['sailing_id', 'starred', 'line', 'ship', 'route', 'depart', 'return', 'nights', 'brothers_cabin', 'parents_cabin'];
    const keys = ['cab-b', 'cab-p', 'tips', 'flights', 'bags', 'transfers', 'hotel', 'hoteltax', 'exc-p', 'exc-b'];
    keys.forEach(k => head.push(k + '_usd', k + '_status'));
    head.push('total_usd', 'total_status', 'parents_usd', 'brothers_usd', 'not_captured', 'activities');
    const rows = [head];
    exportIds().forEach(id => {
      const s = M.sailing[id], plan = P.planFor(id), c = M.cost(s, plan), T = c.totals;
      const r = [id, short.includes(id) ? 'yes' : 'no', (M.line[s._line] || {}).name, M.ship[s.ship].name, M.route[s._route].name, s.depart, s.return, s.nights, c.cab.b, c.cab.p];
      keys.forEach(k => { const x = c.lines.find(l => l.key === k); r.push(x && x.usd != null ? x.usd.toFixed(2) : '', x ? x.status : 'n/a'); });
      r.push(T.total.toFixed(2), T.status, T.parents.toFixed(2), T.brothers.toFixed(2), T.missing.length, M.planCount(plan));
      rows.push(r);
    });
    return csv(rows);
  }
  function daysCsv() {
    const rows = [['sailing_id', 'ship', 'day', 'date', 'place', 'in_port', 'who', 'start', 'end', 'activity', 'booked_through', 'kind', 'price_pp_usd', 'for_2_usd', 'price_status', 'walk_miles', 'source']];
    exportIds().forEach(id => {
      const s = M.sailing[id], plan = P.planFor(id), it = M.itin[s.itinerary];
      (it.days || []).forEach((d, i) => {
        const e = d.find(z => z.type === 'port');
        if (!e) return;
        ['p', 'b'].forEach(l => {
          const ids = M.planPicks(plan, i, l);
          if (!ids.length) return;
          const sch = M.timed(e) ? M.schedule(e, ids) : null;
          if (ids.includes(M.ABOARD)) { rows.push([id, M.ship[s.ship].name, i + 1, M.addDays(s.depart, i), placeShort(e.place), (e.arr || '') + '-' + (e.dep || ''), l === 'p' ? 'Parents' : 'Brothers', '', '', 'Stay on the ship', '', '', 0, 0, '', 0, '']); return; }
          ids.forEach((oid, k) => {
            const o = M.offer[oid], x = M.expOfOffer[oid]; if (!o) return;
            const pr = M.offerPrice(o), t = sch && sch.items[k];
            rows.push([id, M.ship[s.ship].name, i + 1, M.addDays(s.depart, i), placeShort(e.place), (e.arr || '') + '-' + (e.dep || ''), l === 'p' ? 'Parents' : 'Brothers', t ? M.minsToTime(t.start) : '', t ? M.minsToTime(t.end) : '', x.name, o.provider, o.kind, pr.usd == null ? '' : pr.usd, pr.usd == null ? '' : pr.usd * 2, pr.status, x.walkMiles == null ? '' : x.walkMiles, M.sourceUrl(pr.row) || '']);
          });
        });
      });
    });
    return csv(rows);
  }
  function importBackup(text) {
    let o;
    try { o = JSON.parse(text); } catch (e) { U.toast('That is not a planner backup (could not read it).'); return; }
    if (!o || o.app !== 'alaska-2027-planner' || typeof o.plans !== 'object') { U.toast('That file is not a planner backup.'); return; }
    let nP = 0, skipped = 0;
    Object.keys(o.plans || {}).forEach(sid => {
      if (!M.sailing[sid]) { skipped++; return; }
      const src = o.plans[sid] || {};
      const clean = M.emptyPlan();
      clean.cab = Object.assign(clean.cab, src.cab || {});
      Object.keys(src.picks || {}).forEach(d => {
        if (!M.portEntry(M.sailing[sid], +d)) return;
        ['p', 'b'].forEach(l => {
          const arr = ((src.picks[d] || {})[l] || []).filter(id => id === M.ABOARD || M.offer[id]);
          if (arr.length) { clean.picks[d] = clean.picks[d] || { p: [], b: [] }; clean.picks[d][l] = arr; }
        });
      });
      plans[sid] = clean; nP++;
    });
    (o.shortlist || []).forEach(id => { if (M.sailing[id] && !short.includes(id)) short.push(id); });
    const q = Object.assign({}, M.quotes);
    Object.keys(o.quotes || {}).forEach(k => { const v = o.quotes[k]; if (v && typeof v.usd === 'number' && isFinite(v.usd)) q[k] = v; });
    M.setQuotes(q);
    if (o.settings && typeof o.settings === 'object') M.settings = Object.assign({}, M.DEFAULT_SETTINGS, o.settings);
    save('plans', plans); save('short', short); save('quotes', M.quotes); save('settings', M.settings);
    U.toast('Loaded ' + U.plural(nP, 'plan') + (skipped ? ' (' + skipped + ' for sailings no longer listed were skipped)' : ''));
    U.render();
  }

  /* ---------------- quote dialog ---------------- */
  let lastFocus = null;
  function openQuote(rowId, label) {
    const dlg = $('#quoteDlg');
    const r = M.rows[rowId] || null, q = M.quotes[rowId];
    const basis = (q && q.basis) || (r && r.basis) || (rowId.startsWith('gap:') ? 'total for 4 people' : '');
    lastFocus = document.activeElement;
    dlg.innerHTML = '<div class="dlg" role="dialog" aria-modal="true" aria-labelledby="qTitle"><h3 id="qTitle">Your quote</h3><p class="small"><b>' + esc(label) + '</b></p>' +
      (basis ? '<p class="small muted">Enter it the same way: ' + esc(basis) + '.</p>' : '') +
      (r && r.usd != null ? '<p class="small muted">Researched number: ' + esc(M.fmtUsd(r.usd)) + ' (' + esc(M.STATUS_SHORT[r.status] || r.status) + (r.checked ? ', checked ' + esc(M.fmtChecked(r.checked)) : '') + ')</p>' : '') +
      '<label class="qf"><span>Amount in US dollars</span><input id="qAmt" type="text" inputmode="decimal" autocomplete="off" value="' + (q ? esc(q.usd) : '') + '" placeholder="e.g. 4120"></label>' +
      '<label class="qf"><span>Where it came from (optional)</span><input id="qNote" type="text" autocomplete="off" maxlength="160" value="' + (q ? esc(q.note || '') : '') + '" placeholder="e.g. Princess phone quote, incl. taxes"></label>' +
      '<p class="small muted">Saved in this browser only. Don’t type names, emails or booking numbers here: they would go into share links and backups.</p>' +
      '<div class="next-row" style="justify-content:flex-start"><button class="btn small" type="button" data-act="quote-save" data-row="' + esc(rowId) + '" data-label="' + esc(label) + '" data-basis="' + esc(basis) + '">Save</button>' +
      (q ? '<button class="btn small ghost" type="button" data-act="quote-del" data-row="' + esc(rowId) + '">Remove my quote</button>' : '') +
      '<button class="btn small ghost" type="button" data-act="quote-close">Cancel</button></div></div>';
    dlg.hidden = false;
    document.body.classList.add('dlg-open');
    const i = $('#qAmt'); if (i) i.focus();
  }
  function closeQuote() {
    const dlg = $('#quoteDlg');
    dlg.hidden = true; dlg.innerHTML = '';
    document.body.classList.remove('dlg-open');
    if (lastFocus && lastFocus.focus) try { lastFocus.focus(); } catch (e) { /* gone after re-render */ }
  }
  document.addEventListener('keydown', e => {
    const dlg = $('#quoteDlg');
    if (!dlg || dlg.hidden) return;
    if (e.key === 'Escape') closeQuote();
    if (e.key === 'Enter' && e.target && e.target.id && /^q(Amt|Note)$/.test(e.target.id)) { const b = dlg.querySelector('[data-act="quote-save"]'); if (b) b.click(); }
  });

  async function shareOption(sid) {
    const url = location.href.split('#')[0] + U.hashOf({ view: 'days', sailing: sid, day: null, withPlan: true });
    const s = M.sailing[sid];
    const text = M.ship[s.ship].name + ', ' + M.fmtDate(s.depart, true) + (M.planCount(P.planFor(sid)) ? ', with our day plan' : '');
    if (navigator.share) { try { await navigator.share({ title: 'Alaska 2027', text, url }); return; } catch (e) { if (e && e.name === 'AbortError') return; } }
    try { await navigator.clipboard.writeText(url); U.toast('Link copied'); } catch (e) { window.prompt('Copy this link:', url); }
  }

  /* ---------------- events (called from ui.js) ---------------- */
  P.onClick = function (act, a) {
    const S = U.S;
    const sid = a.dataset.sailing || S.sailing;
    switch (act) {
      case 'day': U.go({ day: +a.dataset.day }, false); window.scrollTo({ top: ($('.daystrip') ? $('.daystrip').getBoundingClientRect().top + window.scrollY - 130 : 0), behavior: 'smooth' }); return true;
      case 'pick-lane': {
        const r = toggleLane(S.sailing, +a.dataset.day, a.dataset.lane, a.dataset.offer);
        cleanDay(S.sailing, +a.dataset.day); commit(S.sailing);
        if (r === 'added') U.toast('Added for the ' + (a.dataset.lane === 'p' ? 'parents' : 'brothers'));
        return true;
      }
      case 'pick-all': {
        const day = +a.dataset.day, o = a.dataset.offer;
        const x = M.expOfOffer[o];
        const inP = laneArr(S.sailing, day, 'p').some(id => M.expOfOffer[id] && M.expOfOffer[id].id === x.id);
        const inB = laneArr(S.sailing, day, 'b').some(id => M.expOfOffer[id] && M.expOfOffer[id].id === x.id);
        if (inP && inB) { toggleLane(S.sailing, day, 'p', o); toggleLane(S.sailing, day, 'b', o); }
        else { toggleLane(S.sailing, day, 'p', o, true); toggleLane(S.sailing, day, 'b', o, true); U.toast('Added for all 4'); }
        cleanDay(S.sailing, day); commit(S.sailing);
        return true;
      }
      case 'unpick': {
        const arr = laneArr(S.sailing, +a.dataset.day, a.dataset.lane);
        const i = arr.indexOf(a.dataset.offer); if (i >= 0) arr.splice(i, 1);
        cleanDay(S.sailing, +a.dataset.day); commit(S.sailing);
        return true;
      }
      case 'aboard': case 'aboard-all': {
        const day = +a.dataset.day;
        const lanesTo = act === 'aboard-all' ? ['p', 'b'] : [a.dataset.lane];
        const allOn = lanesTo.every(l => laneArr(S.sailing, day, l).includes(M.ABOARD));
        lanesTo.forEach(l => { const arr = laneArr(S.sailing, day, l); arr.splice(0, arr.length); if (!allOn) arr.push(M.ABOARD); });
        cleanDay(S.sailing, day); commit(S.sailing);
        return true;
      }
      case 'star': {
        const i = short.indexOf(sid);
        if (i >= 0) short.splice(i, 1); else short.push(sid);
        save('short', short);
        U.toast(i >= 0 ? 'Removed from the shortlist' : 'Added to the shortlist');
        U.render();
        return true;
      }
      case 'open-days': U.go({ view: 'days', sailing: sid, ship: M.sailing[sid].ship, day: null }, true); return true;
      case 'open-cost': U.go({ view: 'cost', sailing: sid, ship: M.sailing[sid].ship }, true); return true;
      case 'share-opt': shareOption(sid); return true;
      case 'quote': openQuote(a.dataset.row, a.dataset.label || a.dataset.row); return true;
      case 'quote-close': closeQuote(); return true;
      case 'quote-save': {
        const raw = String($('#qAmt').value || '').replace(/[$,\s]/g, '');
        const v = Number(raw);
        if (!raw || !isFinite(v) || v < 0) { U.toast('Type the amount as a number, e.g. 4120'); return true; }
        const q = Object.assign({}, M.quotes);
        q[a.dataset.row] = { usd: Math.round(v * 100) / 100, note: String($('#qNote').value || '').slice(0, 160), date: today(), label: a.dataset.label, basis: a.dataset.basis || '' };
        M.setQuotes(q); save('quotes', M.quotes); closeQuote(); U.toast('Saved your quote'); U.render();
        return true;
      }
      case 'quote-del': {
        const q = Object.assign({}, M.quotes); delete q[a.dataset.row];
        M.setQuotes(q); save('quotes', M.quotes); closeQuote(); U.toast('Removed your quote'); U.render();
        return true;
      }
      case 'shared-use': plans[pending.sid] = pending.plan; pending = null; save('plans', plans); U.toast('Using the plan from the link'); U.render(); return true;
      case 'shared-keep': pending = null; U.render(); return true;
      case 'export-json': download('alaska-2027-plans-' + today() + '.json', JSON.stringify(backup(), null, 2), 'application/json'); return true;
      case 'export-cost-csv': download('alaska-2027-costs-' + today() + '.csv', costCsv(), 'text/csv'); return true;
      case 'export-days-csv': download('alaska-2027-day-plans-' + today() + '.csv', daysCsv(), 'text/csv'); return true;
      case 'import-text': importBackup(($('#importText') || {}).value || ''); return true;
      default: return false;
    }
  };
  P.onChange = function (e) {
    const t = e.target, act = t.dataset && t.dataset.act;
    const S = U.S;
    if (act === 'offer') {
      offSel[t.dataset.key] = t.value;
      const day = +t.dataset.day, xid = t.dataset.exp;
      const plan = plans[S.sailing];
      if (plan && plan.picks[day]) {
        const s = M.sailing[S.sailing], e2 = M.portEntry(s, day);
        let blocked = false;
        ['p', 'b'].forEach(l => {
          const arr = plan.picks[day][l] || [];
          const i = arr.findIndex(id => M.expOfOffer[id] && M.expOfOffer[id].id === xid);
          if (i < 0) return;
          const old = arr[i]; arr[i] = t.value;
          if (M.schedule(e2, arr).over) { arr[i] = old; blocked = true; }
        });
        if (blocked) U.toast('That option is too long to fit; kept the earlier one.');
        commit(S.sailing);
      } else U.render();
    } else if (act === 'cabin') {
      const plan = editPlan(S.sailing); plan.cab[t.dataset.who] = t.value; commit(S.sailing);
    } else if (act === 'set') {
      const k = t.dataset.key;
      let v = t.type === 'checkbox' ? t.checked : t.value;
      if (k === 'bagsPP' || k === 'walkBudget') v = Number(v);
      M.settings[k] = v; save('settings', M.settings); U.render();
    } else if (act === 'import-file' && t.files && t.files[0]) {
      const fr = new FileReader();
      fr.onload = () => importBackup(String(fr.result || ''));
      fr.readAsText(t.files[0]);
      t.value = '';
    }
  };
  P.render = function (view) {
    if (view === 'days') renderDays();
    else if (view === 'cost') renderCost();
    else if (view === 'short') renderShort();
  };
  P._test = { costCsv: () => costCsv(), daysCsv: () => daysCsv(), backup: () => backup(), importBackup: t => importBackup(t), plans: () => plans };

  window.AKP = P;
})();
