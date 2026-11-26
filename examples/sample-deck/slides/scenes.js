/* 샘플 덱의 장면 스크립트. 엔진은 고치지 않고 ShowMe API로 더한다. */
(() => {
  const { $ } = ShowMe;

  // ── 5장: 여러 일이 서로 다른 시각에 끝나는 막대. 들어올 때마다 다시 그린다 ──
  const JOBS = [['자료 모으기', 0.55], ['초안 쓰기', 0.8], ['그림 만들기', 0.7], ['검사', 0.95]];
  let timers = [], bars = [];
  ShowMe.scene('#bars', {
    init(el) {
      bars = JOBS.map(([name, end], i) => {
        const y = 120 + i * 130;
        el.insertAdjacentHTML('beforeend', `<div class="lab" style="top:${y + 14}px">${name}</div><div class="bar${i % 2 ? ' b2' : ''}" style="top:${y}px"></div><div class="done" style="top:${y + 18}px">끝</div>`);
        const bar = el.querySelectorAll('.bar')[i], done = el.querySelectorAll('.done')[i];
        return { bar, done, w: Math.round(860 * end) };
      });
      $('#replayBars').onclick = () => play();
    },
    enter: () => play(),
    leave: () => timers.forEach(clearTimeout),
  });
  function play() {
    timers.forEach(clearTimeout); timers = [];
    bars.forEach(b => { b.bar.style.transition = 'none'; b.bar.style.width = '0px'; b.done.style.opacity = 0; });
    void document.body.offsetWidth;
    bars.forEach((b, i) => timers.push(setTimeout(() => {
      b.bar.style.transition = ''; b.bar.style.width = b.w + 'px';
      b.done.style.left = (160 + b.w + 18) + 'px';
      timers.push(setTimeout(() => { b.done.style.opacity = 1; }, 900));
    }, 250 + i * 300)));
  }
})();
