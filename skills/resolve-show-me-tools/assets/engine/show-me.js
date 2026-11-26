/* show-me engine 0.1.0 · MIT · https://github.com/ynginkim/show-me
 * 덱 폴더의 engine/에 복사해 쓴다. 이 파일은 고치지 않는다. 덱마다 필요한 동작은 scenes.js에서 ShowMe API로 더한다.
 * 설정은 엔진보다 앞에 둔다: <script type="application/json" id="showme-config">{ "sections": { ... } }</script>
 * 원형: 2026-11-25 강의 덱 v2의 v1 스크립트(넘김·타이머·탭·스크롤·확대·플레이어·전체 보기·키보드).
 * 엔진이 만드는 요소의 클래스는 sm- 접두사를 쓴다. 덱이 쓰는 부품 클래스(player, tabs, scroller …)는 접두사 없이 그대로다. */
(() => {
  'use strict';
  const VERSION = '0.1.0';
  const $ = (s, r = document) => r.querySelector(s), $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const NS = 'http://www.w3.org/2000/svg';
  const fmt = s => `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, '0')}`;

  // ── config ──
  let config = {};
  const cfgEl = document.getElementById('showme-config');
  if (cfgEl) {
    try { config = JSON.parse(cfgEl.textContent); }
    catch (e) { console.error('[show-me] 설정 JSON을 읽지 못했습니다: ' + e.message); }
  }
  const W = (config.stage && config.stage[0]) || 1920, H = (config.stage && config.stage[1]) || 1080;

  // ── chrome: #viewport > #stage > #top + slides, #lb, #ov ──
  const slides = $$('.slide');
  if (!slides.length) { console.error('[show-me] section.slide가 없습니다'); return; }
  let stage = $('#stage');
  if (!stage) {
    const vp = document.createElement('div'); vp.id = 'viewport';
    stage = document.createElement('div'); stage.id = 'stage';
    vp.appendChild(stage);
    slides[0].parentNode.insertBefore(vp, slides[0]);
    slides.forEach(s => stage.appendChild(s));
  }
  if (config.stage) { stage.style.width = W + 'px'; stage.style.height = H + 'px'; }
  if (!stage.dataset.tone) stage.dataset.tone = slides[0].dataset.tone || 'dark';
  const useClock = config.clock !== undefined ? !!config.clock : slides.some(s => s.dataset.h != null);
  if (!$('#top')) {
    const top = document.createElement('div'); top.id = 'top';
    top.innerHTML = (useClock ? '<svg id="clock" viewBox="-34 -34 68 68"><circle r="29" fill="none" stroke="currentColor" stroke-opacity=".3" stroke-width="3"/><g id="ticks"></g><line id="hand" x1="0" y1="0" x2="0" y2="-21" stroke-width="4" stroke-linecap="round"/><circle class="pivot" r="4"/></svg>' : '')
      + '<div id="clockLabel"></div><div id="secLabel"></div><div id="timer"></div><div id="counter"></div>';
    stage.insertBefore(top, stage.firstChild);
  }
  if (!$('#lb')) document.body.insertAdjacentHTML('beforeend', '<div id="lb"><div class="sm-box"><img alt=""></div><button class="sm-nav sm-prev">‹</button><button class="sm-nav sm-next">›</button><button class="sm-x">×</button><div class="sm-cap"></div></div>');
  if (!$('#ov')) document.body.insertAdjacentHTML('beforeend', '<div id="ov"><h2>전체 보기 <span>— 클릭해서 이동 · G/Esc 닫기</span></h2><div class="sm-g"></div></div>');

  let cur = 0, scale = 1, started = false;

  // ── fit W×H to the window ──
  const fit = () => { scale = Math.min(innerWidth / W, innerHeight / H); stage.style.transform = `scale(${scale})`; };
  addEventListener('resize', fit); fit();

  // ── clock ticks (time-of-day theme: data-h) ──
  const ticks = $('#ticks');
  if (ticks) for (let i = 0; i < 24; i++) {
    const a = i / 24 * Math.PI * 2 - Math.PI / 2, major = i % 6 === 0, l = major ? 6 : 3;
    const ln = document.createElementNS(NS, 'line');
    ln.setAttribute('x1', Math.cos(a) * (29 - l)); ln.setAttribute('y1', Math.sin(a) * (29 - l));
    ln.setAttribute('x2', Math.cos(a) * 29); ln.setAttribute('y2', Math.sin(a) * 29);
    ln.setAttribute('stroke', 'currentColor'); ln.setAttribute('stroke-width', major ? 2.4 : 1.2); ln.setAttribute('stroke-opacity', major ? .9 : .4);
    ticks.appendChild(ln);
  }
  let handDeg = 0;
  const hand = $('#hand');
  if (hand) hand.style.transformOrigin = '0 0';

  // ── sections & time-budget timer (config.sections: { key: { name, short?, color?, budget? (seconds) } }) ──
  const SEC = config.sections || {};
  const spent = {}; Object.keys(SEC).forEach(k => { spent[k] = 0; });
  let lastTick = null, timerOn = false;
  const timerEl = $('#timer');
  setInterval(() => {
    const sec = slides[cur].dataset.sec, now = performance.now();
    if (lastTick != null && sec && SEC[sec]) spent[sec] += (now - lastTick) / 1000;
    lastTick = now;
    if (!sec || !SEC[sec]) {
      timerEl.textContent = Object.keys(SEC).map(k => `${SEC[k].short || SEC[k].name} ${fmt(spent[k])}`).join(' · ');
      timerEl.className = timerOn ? 'on' : ''; return;
    }
    const s = spent[sec], b = SEC[sec].budget;
    timerEl.textContent = b ? `${SEC[sec].name} ${fmt(s)} / ${fmt(b)}` : `${SEC[sec].name} ${fmt(s)}`;
    timerEl.className = (timerOn ? 'on ' : '') + (b && s > b ? 'over' : b && s > b * 0.85 ? 'warn' : '');
  }, 250);

  // ── scenes: ShowMe.scene(target, { init, enter, leave }) ──
  const scenes = [];
  const sceneCall = (slide, kind) => scenes.forEach(sc => { if (sc.slide === slide && sc[kind]) sc[kind](sc.el, slide); });
  function scene(target, hooks = {}) {
    let el = null;
    if (typeof target === 'number') el = slides[target - 1] || null;
    else el = typeof target === 'string' ? $(target) : target;
    const slide = el && (el.classList.contains('slide') ? el : el.closest('.slide'));
    if (!el || !slide) { console.error(`[show-me] 장면 대상을 찾지 못했습니다: ${target}`); return null; }
    const sc = Object.assign({ el, slide }, hooks);
    scenes.push(sc);
    if (sc.init) sc.init(el, slide);
    if (started && slides[cur] === slide && sc.enter) sc.enter(el, slide);
    return sc;
  }

  // ── navigation ──
  function go(n, fromHash) {
    n = Math.max(0, Math.min(slides.length - 1, n));
    const changed = n !== cur || !started;
    const prev = slides[cur];
    if (changed) {
      if (started) sceneCall(prev, 'leave');
      prev.classList.remove('active');
      $$('video', prev).forEach(v => v.pause());
    }
    cur = n;
    const s = slides[cur];
    s.classList.add('active');
    if (s.dataset.sky) stage.style.setProperty('--sky', s.dataset.sky); else stage.style.removeProperty('--sky');
    stage.dataset.tone = s.dataset.tone || config.tone || 'dark';
    if (hand) {
      const h = parseFloat(s.dataset.h || 0), target = h / 24 * 360;
      // keep turning forward through the day (shortest forward path)
      let d = ((target - handDeg) % 360 + 360) % 360; if (d > 300) d -= 360;
      handDeg += d;
      hand.style.transition = 'transform .9s cubic-bezier(.83,0,.17,1)';
      hand.style.transform = `rotate(${handDeg}deg)`;
    }
    $('#clockLabel').textContent = s.dataset.label || '';
    const sec = SEC[s.dataset.sec];
    $('#secLabel').innerHTML = sec ? `<i style="background:${sec.color || 'var(--accent)'}"></i>${sec.name}${sec.budget ? ` · ${fmt(sec.budget)}` : ''}` : '';
    $('#counter').textContent = `${cur + 1} / ${slides.length}`;
    if (!fromHash) history.replaceState(null, '', '#' + (cur + 1));
    $$('.sm-ov-b').forEach((b, i) => b.classList.toggle('cur', i === cur));
    if (changed) {
      $$('video[data-autoplay]', s).forEach(v => {
        if (v.dataset.autoplay === 'restart') v.currentTime = 0;
        const p = v.play(); if (p && p.catch) p.catch(() => {});
      });
      sceneCall(s, 'enter');
      document.dispatchEvent(new CustomEvent('showme:change', { detail: { slide: cur + 1, el: s } }));
    }
  }

  // ── tabs ──
  $$('.tabs').forEach(t => {
    const btns = $$('.tabbar button', t), panes = $$(':scope > .pane', t);
    const sel = i => { btns.forEach((b, k) => b.classList.toggle('on', k === i)); panes.forEach((p, k) => p.classList.toggle('on', k === i)); };
    btns.forEach((b, i) => b.addEventListener('click', () => sel(i)));
    t._sel = (i) => { if (i < btns.length) sel(i); };
    sel(0);
  });

  // ── drag-to-scroll for scrollers and the lightbox ──
  function dragScroll(el) {
    let sx, sy, sl, st, down = false, moved = false;
    el.addEventListener('pointerdown', e => { if (e.button !== 0 || e.target.closest('.zoom')) return; down = true; moved = false; sx = e.clientX; sy = e.clientY; sl = el.scrollLeft; st = el.scrollTop; el.setPointerCapture(e.pointerId); });
    el.addEventListener('pointermove', e => { if (!down) return; const dx = (e.clientX - sx) / scale, dy = (e.clientY - sy) / scale; if (Math.abs(dx) + Math.abs(dy) > 4) moved = true; el.scrollLeft = sl - dx; el.scrollTop = st - dy; });
    el.addEventListener('pointerup', () => { down = false; });
    el.addEventListener('click', e => { if (moved) { e.stopPropagation(); e.preventDefault(); } }, true);
  }
  $$('.scroller').forEach(dragScroll);
  $$('.scroller img').forEach(im => im.addEventListener('dblclick', () => openLB([{ src: im.getAttribute('src') }], 0)));

  // ── lightbox ──
  const lb = $('#lb'), lbImg = $('img', lb), lbBox = $('.sm-box', lb), lbCap = $('.sm-cap', lb);
  let group = [], gi = 0;
  function openLB(list, i) { group = list; gi = i || 0; lb.classList.add('on'); showLB(); }
  function showLB() {
    const it = group[gi];
    lbImg.onload = () => { const tall = lbImg.naturalHeight / lbImg.naturalWidth > 1.25 && lbImg.naturalWidth > 1000; lb.classList.toggle('fit', !tall); lbImg.style.width = tall ? '1400px' : ''; lbBox.scrollTop = 0; };
    lbImg.src = it.src; lbCap.textContent = (it.cap || '') + (group.length > 1 ? `   ${gi + 1} / ${group.length}` : '');
    $$('.sm-nav', lb).forEach(b => { b.style.display = group.length > 1 ? '' : 'none'; });
  }
  const lbStep = d => { if (group.length < 2) return; gi = (gi + d + group.length) % group.length; showLB(); };
  const closeLB = () => lb.classList.remove('on');
  $('.sm-prev', lb).onclick = () => lbStep(-1); $('.sm-next', lb).onclick = () => lbStep(1); $('.sm-x', lb).onclick = closeLB;
  lb.addEventListener('click', e => { if (e.target === lb || e.target === lbBox) closeLB(); });
  dragScroll(lbBox);
  document.addEventListener('click', e => {
    const z = e.target.closest('[data-zoom]'); if (!z) return;
    const g = z.dataset.group;
    if (g) { const items = $$(`[data-group="${g}"]`).map(x => ({ src: x.dataset.zoom, cap: x.dataset.cap })); openLB(items, items.findIndex(x => x.src === z.dataset.zoom)); }
    else openLB([{ src: z.dataset.zoom, cap: z.dataset.cap }], 0);
  });

  // ── cards that jump to a slide (data-goto = 1-based slide number) ──
  $$('[data-goto]').forEach(c => c.addEventListener('click', () => go(+c.dataset.goto - 1)));

  // ── video players: .player[data-src][data-chap][data-shape=phone|wide][data-autoplay] ──
  $$('.player').forEach(P => {
    const chap = P.dataset.chap ? JSON.parse(P.dataset.chap) : [];
    if (P.dataset.shape === 'wide') P.classList.add('sm-wide');
    const auto = P.dataset.autoplay != null ? ` data-autoplay="${P.dataset.autoplay}"` : '';
    P.innerHTML = `<div class="sm-phone"><div class="sm-scr"><video src="${P.dataset.src}" preload="auto" playsinline${auto}></video></div><div class="sm-zbadge">×1.7</div></div>
      <div class="sm-ctl"><div class="sm-chap"></div><div class="sm-prog"><i></i></div><div class="sm-pbar"><button class="sm-pp">▶ 재생</button><button class="sm-sp" data-r="1">1×</button><button class="sm-sp" data-r="1.5">1.5×</button><button class="sm-sp" data-r="2">2×</button><button class="sm-zm">Z 확대</button><span class="sm-time"></span></div></div>`;
    const v = $('video', P), phone = $('.sm-phone', P), scr = $('.sm-scr', P), list = $('.sm-chap', P), bar = $('.sm-prog', P), fill = $('.sm-prog i', P), time = $('.sm-time', P), pp = $('.sm-pp', P);
    const play = () => { const p = v.play(); if (p && p.catch) p.catch(() => {}); };
    chap.forEach(([t, a, b], i) => {
      const btn = document.createElement('button');
      btn.innerHTML = `<span class="sm-n">${i + 1}</span><span class="sm-t">${fmt(t)}</span><span>${a}${b ? `<small>${b}</small>` : ''}</span>`;
      btn.onclick = () => { v.currentTime = t + 0.01; play(); };
      list.appendChild(btn);
    });
    v.addEventListener('loadedmetadata', () => { chap.forEach(([t]) => { const m = document.createElement('b'); m.style.left = (t / v.duration * 100) + '%'; bar.appendChild(m); }); });
    const upd = () => {
      fill.style.width = (v.currentTime / (v.duration || 1) * 100) + '%';
      time.textContent = `${fmt(v.currentTime)} / ${fmt(v.duration || 0)}`;
      let k = -1; chap.forEach(([t], i) => { if (v.currentTime >= t - 0.05) k = i; });
      $$('button', list).forEach((b, i) => b.classList.toggle('on', i === k));
      pp.textContent = v.paused ? '▶ 재생' : '❚❚ 멈춤';
    };
    ['timeupdate', 'play', 'pause', 'seeked', 'loadedmetadata'].forEach(ev => v.addEventListener(ev, upd));
    bar.addEventListener('click', e => { const r = bar.getBoundingClientRect(); v.currentTime = (e.clientX - r.left) / r.width * v.duration; });
    pp.onclick = () => (v.paused ? play() : v.pause());
    $$('.sm-sp', P).forEach(b => { b.onclick = () => { v.playbackRate = +b.dataset.r; $$('.sm-sp', P).forEach(x => x.classList.toggle('on', x === b)); }; });
    $('.sm-sp', P).classList.add('on');
    // zoom ×1.7 with drag-pan (start centred on the upper-middle of the screen)
    let z = 1, ox = 0, oy = 0;
    const apply = () => { v.style.transform = `translate(${ox}px, ${oy}px) scale(${z})`; phone.classList.toggle('sm-zoomed', z > 1); };
    const clampO = () => { const w = scr.clientWidth, h = scr.clientHeight; ox = Math.min(0, Math.max(w - w * z, ox)); oy = Math.min(0, Math.max(h - h * z, oy)); };
    P._zoom = () => { const w = scr.clientWidth, h = scr.clientHeight; if (z > 1) { z = 1; ox = oy = 0; } else { z = 1.7; ox = -w * 0.35; oy = -h * 0.35; clampO(); } apply(); };
    $('.sm-zm', P).onclick = P._zoom;
    scr.addEventListener('dblclick', P._zoom);
    let sx, sy, so, down = false;
    scr.addEventListener('pointerdown', e => { if (z === 1) return; down = true; sx = e.clientX; sy = e.clientY; so = [ox, oy]; scr.setPointerCapture(e.pointerId); });
    scr.addEventListener('pointermove', e => { if (!down) return; ox = so[0] + (e.clientX - sx) / scale; oy = so[1] + (e.clientY - sy) / scale; clampO(); apply(); });
    scr.addEventListener('pointerup', () => { down = false; });
    scr.addEventListener('click', () => { if (z === 1) (v.paused ? play() : v.pause()); });
    P._chap = i => { if (chap[i]) { v.currentTime = chap[i][0] + 0.01; play(); } };
    P._toggle = () => (v.paused ? play() : v.pause());
  });

  // ── overview ──
  const ov = $('#ov');
  $('.sm-g', ov).innerHTML = slides.map((s, i) => `<button class="sm-ov-b" data-i="${i}" style="background:${s.dataset.sky ? s.dataset.sky + '22' : 'var(--ov-card)'}"><span class="sm-m">${i + 1} · ${s.dataset.label || ''}</span>${s.dataset.title || ''}</button>`).join('');
  $('.sm-g', ov).addEventListener('click', e => { const b = e.target.closest('button'); if (!b) return; ov.classList.remove('on'); go(+b.dataset.i); });

  // ── keyboard (capture phase so focused video controls do not swallow keys) ──
  addEventListener('keydown', e => {
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    const k = e.key, s = slides[cur];
    if (lb.classList.contains('on')) {
      if (k === 'Escape') closeLB(); else if (k === 'ArrowRight') lbStep(1); else if (k === 'ArrowLeft') lbStep(-1); else return;
      e.preventDefault(); e.stopPropagation(); return;
    }
    if (ov.classList.contains('on') && (k === 'Escape' || k === 'g' || k === 'G')) { ov.classList.remove('on'); e.preventDefault(); return; }
    const P = $('.player', s);
    if (['ArrowRight', 'PageDown', ' '].includes(k)) go(cur + 1);
    else if (['ArrowLeft', 'PageUp'].includes(k)) go(cur - 1);
    else if (k === 'Home') go(0); else if (k === 'End') go(slides.length - 1);
    else if (k === 'g' || k === 'G') ov.classList.add('on');
    else if (k === 'f' || k === 'F') { document.fullscreenElement ? document.exitFullscreen() : document.documentElement.requestFullscreen(); }
    else if (k === 't' || k === 'T') { timerOn = !timerOn; timerEl.classList.toggle('on', timerOn); }
    else if ((k === 'p' || k === 'P') && P) P._toggle();
    else if ((k === 'z' || k === 'Z') && P) P._zoom();
    else if (/^[1-9]$/.test(k)) { const i = +k - 1, t = $('.tabs', s); if (t) t._sel(i); else if (P) P._chap(i); else return; }
    else return;
    e.preventDefault(); e.stopPropagation();
  }, true);

  // ── public API (slide numbers are 1-based, like data-goto and #N) ──
  window.ShowMe = {
    version: VERSION, config, slides, $, $$, fmt, scene,
    go: n => go(n - 1), next: () => go(cur + 1), prev: () => go(cur - 1), current: () => cur + 1,
    lightbox: openLB, get scale() { return scale; },
  };

  // ── start after scenes.js has registered its scenes ──
  function start() {
    if (started) return;
    const fromHash = parseInt(location.hash.slice(1), 10);
    slides[0].classList.add('active');
    go(Number.isFinite(fromHash) ? fromHash - 1 : 0, true);
    started = true;
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else setTimeout(start, 0);
})();
