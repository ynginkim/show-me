/* 이 덱의 장면 스크립트. 엔진은 고치지 않고 여기서 ShowMe API로 더한다.
 *   ShowMe.scene('#id 또는 슬라이드 번호', { init(el, slide) {}, enter(el, slide) {}, leave(el, slide) {} })
 *   ShowMe.go(n) · ShowMe.lightbox([{ src, cap }], i) · ShowMe.$ · ShowMe.$$ · ShowMe.fmt(초)
 * 예: 들어올 때마다 다시 그리는 도식 → ShowMe.scene('#flow', { init: draw, enter: replay })
 * 같은 동작이 두 번째 덱에서도 필요해지면 엔진으로 올릴지 검토한다(principle-content-before-engine). */
(() => {
  // const { $ } = ShowMe;
})();
