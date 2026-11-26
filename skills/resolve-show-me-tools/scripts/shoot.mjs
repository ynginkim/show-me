#!/usr/bin/env node
// Screenshot every slide of a show-me deck (file://) at 1920×1080, run interactions, and report errors.
// usage: node shoot.mjs --deck <slides/index.html> --out <dir> [--pw <dir>] [--actions <json>] [--no-auto]
//        [--no-freeze] [--wait 1300] [--wait-for 10:4600,...] [--only 3,5]
// playwright-core: --pw <dir> → env SHOWME_PLAYWRIGHT → this folder's node_modules. Uses system Chrome (channel "chrome").
import { createRequire } from 'node:module';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
const flag = k => args.includes(k);
const deck = opt('--deck'), out = opt('--out');
if (!deck || !out) { console.error('usage: node shoot.mjs --deck <slides/index.html> --out <dir> [--pw <dir>] [--actions <json>]'); process.exit(2); }

function loadPlaywright() {
  const cands = [opt('--pw'), process.env.SHOWME_PLAYWRIGHT, here].filter(Boolean);
  for (const c of cands) {
    try { return { pw: createRequire(path.join(path.resolve(c), 'x.js'))('playwright-core'), from: c }; } catch (e) { /* next */ }
  }
  console.error('playwright-core를 찾지 못했습니다. 설치: npm install --prefix "' + here + '" (package.json의 버전) 또는 --pw <node_modules가 있는 폴더>');
  process.exit(3);
}

const waitDefault = +opt('--wait', 1300);
const waitFor = Object.fromEntries((opt('--wait-for', '') || '').split(',').filter(Boolean).map(x => x.split(':').map(Number)));
const only = (opt('--only', '') || '').split(',').filter(Boolean).map(Number);
const freeze = !flag('--no-freeze');

// Make the frame deterministic: finish finite animations, park infinite ones at t=0, pause playing videos at 1s.
async function settle(page) {
  if (!freeze) return;
  await page.evaluate(async () => {
    for (const a of document.getAnimations()) {
      const it = a.effect && a.effect.getTiming ? a.effect.getTiming().iterations : 1;
      if (it === Infinity) { a.pause(); a.currentTime = 0; } else { try { a.finish(); } catch (e) { /* ignore */ } }
    }
    const vids = [...document.querySelectorAll('.slide.active video')].filter(v => !v.paused);
    await Promise.all(vids.map(v => new Promise(r => { v.pause(); const t = Math.min(1, (v.duration || 2) / 2); v.addEventListener('seeked', r, { once: true }); v.currentTime = t; setTimeout(r, 1500); })));
  });
}

// Facts about the active slide: attributes, broken media, elements outside the stage, clipped text.
const inspect = () => {
  const stage = document.getElementById('stage'), s = document.querySelector('.slide.active');
  if (!stage || !s) return { missing: true };
  const sr = stage.getBoundingClientRect(), k = sr.width / stage.offsetWidth || 1;
  const name = el => { let n = el.tagName.toLowerCase(); if (el.id) n += '#' + el.id; else if (el.classList.length) n += '.' + [...el.classList].slice(0, 2).join('.'); const t = (el.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 40); return t ? `${n} "${t}"` : n; };
  const clippedByAncestor = el => { for (let p = el.parentElement; p && p !== s; p = p.parentElement) { const cs = getComputedStyle(p); if (cs.overflowX !== 'visible' || cs.overflowY !== 'visible') return true; } return false; };
  const outside = [], clipped = [];
  for (const el of s.querySelectorAll('*')) {
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden') continue;
    const r = el.getBoundingClientRect();
    if (r.width < 1 || r.height < 1) continue;
    const x0 = (r.left - sr.left) / k, y0 = (r.top - sr.top) / k, x1 = (r.right - sr.left) / k, y1 = (r.bottom - sr.top) / k;
    if ((x0 < -2 || y0 < -2 || x1 > stage.offsetWidth + 2 || y1 > stage.offsetHeight + 2) && !clippedByAncestor(el)) outside.push({ el: name(el), box: [x0, y0, x1, y1].map(Math.round) });
    const ownText = [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
    if (ownText && (cs.overflowX === 'hidden' || cs.overflowY === 'hidden' || cs.textOverflow === 'ellipsis') && (el.scrollWidth > el.clientWidth + 1 || el.scrollHeight > el.clientHeight + 1)) clipped.push({ el: name(el), over: [el.scrollWidth - el.clientWidth, el.scrollHeight - el.clientHeight] });
  }
  const brokenImg = [...s.querySelectorAll('img')].filter(i => i.complete && i.getAttribute('src') && i.naturalWidth === 0).map(i => i.getAttribute('src'));
  const vids = [...s.querySelectorAll('video')].map(v => ({ src: v.getAttribute('src'), ready: v.readyState, err: v.error ? v.error.code : null }));
  return { title: s.dataset.title || '', sec: s.dataset.sec || '', plan: s.dataset.plan ? +s.dataset.plan : null, label: s.dataset.label || '',
    outside: outside.slice(0, 12), outsideCount: outside.length, clipped: clipped.slice(0, 12), clippedCount: clipped.length, brokenImg, vids };
};

(async () => {
  const { pw, from } = loadPlaywright();
  fs.mkdirSync(out, { recursive: true });
  const browser = await pw.chromium.launch({ channel: 'chrome', headless: true, args: ['--autoplay-policy=no-user-gesture-required'] });
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  const errs = [];
  let where = 'load';
  page.on('pageerror', e => errs.push({ at: where, kind: 'pageerror', text: e.message }));
  page.on('console', m => { if (m.type() === 'error') errs.push({ at: where, kind: 'console', text: m.text() }); });
  page.on('requestfailed', r => { const f = r.failure(); if (!f || !f.errorText.includes('ABORTED')) errs.push({ at: where, kind: 'requestfailed', text: r.url() + ' ' + (f && f.errorText) }); });
  const url = pathToFileURL(path.resolve(deck)).href;
  await page.goto(url);
  await page.waitForTimeout(1200);
  const meta = await page.evaluate(() => ({ n: document.querySelectorAll('.slide').length, engine: window.ShowMe ? window.ShowMe.version : null,
    config: window.ShowMe ? window.ShowMe.config : null, waits: [...document.querySelectorAll('.slide')].map(s => s.dataset.shotWait ? +s.dataset.shotWait : null) }));
  const slides = [];
  const shotName = i => `s${String(i).padStart(2, '0')}.png`;
  for (let i = 1; i <= meta.n; i++) {
    if (only.length && !only.includes(i)) continue;
    where = 's' + i;
    await page.goto(url + '#' + i); await page.reload();
    await page.waitForTimeout(waitFor[i] || meta.waits[i - 1] || waitDefault);
    await settle(page);
    await page.screenshot({ path: path.join(out, shotName(i)) });
    slides.push(Object.assign({ n: i, shot: shotName(i) }, await page.evaluate(inspect)));
  }

  // interactions: explicit (--actions) and automatic (overview, 2nd tab, 2nd chapter)
  let actions = [];
  if (opt('--actions')) actions = JSON.parse(fs.readFileSync(opt('--actions'), 'utf8'));
  if (!flag('--no-auto')) {
    const auto = await page.evaluate(() => [...document.querySelectorAll('.slide')].map((s, i) => ({ i: i + 1, tabs: s.querySelectorAll('.tabs .tabbar button').length, player: !!s.querySelector('.player') })));
    actions.push({ name: 'auto_overview', slide: 1, steps: [{ press: 'g' }, { wait: 400 }] });
    for (const a of auto) {
      if (only.length && !only.includes(a.i)) continue;
      if (a.tabs > 1) actions.push({ name: `auto_s${String(a.i).padStart(2, '0')}_tab2`, slide: a.i, steps: [{ press: '2' }, { wait: 500 }] });
      if (a.player) actions.push({ name: `auto_s${String(a.i).padStart(2, '0')}_chap2`, slide: a.i, steps: [{ press: '2' }, { wait: 1000 }, { press: 'p' }, { wait: 300 }] });
    }
  }
  const shots = [];
  for (const a of actions) {
    where = a.name;
    await page.goto(url + '#' + a.slide); await page.reload(); await page.waitForTimeout(a.wait || 1200);
    for (const st of a.steps || []) {
      if (st.press) await page.keyboard.press(st.press === ' ' ? 'Space' : st.press);
      if (st.click) await page.click(st.click);
      if (st.wait) await page.waitForTimeout(st.wait);
    }
    await settle(page);
    await page.screenshot({ path: path.join(out, a.name + '.png') });
    shots.push({ name: a.name, slide: a.slide, shot: a.name + '.png' });
  }

  // timer: press T on the first slide that belongs to a section and read what it shows
  let timer = null;
  const firstSec = slides.find(s => s.sec);
  if (firstSec) {
    where = 'timer';
    await page.goto(url + '#' + firstSec.n); await page.reload(); await page.waitForTimeout(400);
    await page.keyboard.press('t'); await page.waitForTimeout(1600);
    timer = await page.evaluate(() => { const t = document.getElementById('timer'); return t ? { text: t.textContent, cls: t.className, visible: getComputedStyle(t).display !== 'none' } : null; });
  }
  await browser.close();
  const res = { deck: path.resolve(deck), playwright: from, engine: meta.engine, config: meta.config, count: meta.n, slides, interactions: shots, timer, errors: errs };
  fs.writeFileSync(path.join(out, 'shoot.json'), JSON.stringify(res, null, 1));
  console.log(`slides ${slides.length}/${meta.n} · interactions ${shots.length} · errors ${errs.length}`);
  for (const e of errs) console.log(`  [${e.at}] ${e.kind}: ${e.text}`);
})().catch(e => { console.error(e); process.exit(1); });
