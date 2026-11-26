# 엔진 API와 부품 (show-me engine 0.1.0)

엔진은 `slides/engine/show-me.js`, `show-me.css`다. 덱은 이 문서의 속성·마크업·API만 쓴다. 원형은 2026-11-25 강의 덱 v2이며, 이 저장소의 회귀 검증에서 v2 15장과 상호작용 화면을 새 엔진으로 같은 픽셀로 다시 만들었다(원본끼리 흔들리는 영역 제외). "잠정"은 v2에 없던 것이라 두 번째 사례 확인 전이다.

## 페이지 뼈대

```html
<link rel="stylesheet" href="engine/show-me.css">
<link rel="stylesheet" href="fonts/fonts.css">
<link rel="stylesheet" href="deck.css">
…
<section class="slide" data-sky="#0b1220" data-tone="dark" data-title="표지" data-plan="20">…</section>
…
<script type="application/json" id="showme-config">{…}</script>
<script src="engine/show-me.js"></script>
<script src="scenes.js"></script>
```

엔진이 `#viewport > #stage`로 슬라이드를 감싸고, 상단 바(`#top`: 시계·라벨·구간·타이머·장 번호), 확대 보기(`#lb`), 전체 보기(`#ov`)를 만든다. 이미 마크업에 있으면 그것을 쓴다. 무대는 1920×1080이고 창 크기에 맞춰 축소·확대된다. 설정 JSON과 슬라이드 속성의 정본은 adapter(resolve-show-me-tools)의 `contract.md`다.

엔진이 만드는 요소(재생기 안쪽, 확대 보기, 전체 보기)의 클래스는 `sm-` 접두사를 쓴다. 덱 CSS는 `.bar`, `.time` 같은 짧은 이름을 써도 엔진 부품과 부딪히지 않는다. 덱 CSS로 `sm-` 클래스를 고치지 않는다. 바꿀 것은 토큰으로 바꾼다.

## 키

| 키 | 동작 |
| --- | --- |
| → PageDown Space / ← PageUp | 다음 / 이전 |
| Home / End | 처음 / 끝 |
| G | 전체 보기(누르면 이동, G·Esc 닫기) |
| F | 전체 화면 |
| T | 구간 타이머 켜기·끄기. 예산의 85%에서 주황, 넘으면 빨강 |
| 1~9 | 이 장에 탭이 있으면 탭, 플레이어가 있으면 그 장(chapter) |
| P / Z | 플레이어 재생·멈춤 / 1.7배 확대(끌어서 이동) |
| 주소 `#N` | N번째 장으로 연다 |

## 부품

**탭**: 여러 실물을 한 자리에서 바꿔 본다.

```html
<div class="tabs">
  <div class="tabbar"><button><span class="k">1</span>문서</button><button><span class="k">2</span>설계</button></div>
  <div class="pane">…</div><div class="pane">…</div>
</div>
```

**스크롤 캡처**: 긴 문서·웹페이지를 줄이지 않고 끌어서 본다. 이미지 더블클릭은 확대 보기.

```html
<div class="scroller [dark]"><div class="winbar"><i></i><i></i><i></i>창 제목<span class="zoom" data-zoom="media/doc.jpg">확대</span></div><img src="media/doc.jpg" alt=""></div>
<div class="hint">스크롤·드래그 · 더블클릭 크게</div>
```

**확대 보기**: 아무 요소에나 `data-zoom="<이미지>"`(선택 `data-cap`). 같은 `data-group` 값끼리는 ←/→로 넘긴다. scenes.js에서는 `ShowMe.lightbox([{ src, cap }], i)`.

**플레이어**: 녹화를 장(chapter)으로 나눠 튼다.

```html
<div class="player" data-src="media/rec1.mp4" data-chap='[[0,"첫 화면","보충"],[13.6,"퀴즈"],[58.8,"결과"]]'></div>
```

- 기본은 세로 휴대폰 틀(1180:2556). `data-shape="wide"`는 16:9 틀이고 장 목록이 아래로 간다(잠정).
- `data-chap`은 `[초, 제목, 보충?]`의 JSON 배열. 진행 막대에 장 표시가 생긴다.
- `data-autoplay`를 붙이면 그 장에 들어올 때 재생하고, 떠날 때 멈춘다. `data-autoplay="restart"`는 들어올 때마다 처음부터(잠정). 일반 `<video data-autoplay>`에도 같다. 브라우저가 소리 있는 자동 재생을 막으면 조용히 멈춘 상태로 남으므로 리허설에서 확인한다.

**이야기 카드 이동**: `data-goto="N"`(1부터)을 단 요소를 누르면 N번째 장으로 간다.

**영상 썸네일**: `<video src="media/rec1.mp4#t=7" muted preload="metadata"></video>`는 7초 프레임을 카드 썸네일로 보여 준다.

## ShowMe API

엔진 뒤의 scenes.js에서 쓴다. 장 번호는 1부터다.

| API | 뜻 |
| --- | --- |
| `ShowMe.scene(대상, { init, enter, leave })` | 대상(CSS 선택자, 요소, 장 번호)이 있는 장의 장면. `init(el, slide)`은 등록할 때 한 번, `enter`는 그 장에 들어올 때마다, `leave`는 떠날 때. 대상을 못 찾으면 콘솔 오류로 남아 검사에서 잡힌다 |
| `ShowMe.go(n)`, `next()`, `prev()`, `current()` | 이동과 현재 장 |
| `ShowMe.lightbox(list, i)` | 확대 보기 열기 |
| `ShowMe.$`, `ShowMe.$$`, `ShowMe.fmt(초)` | 선택자, `m:ss` |
| `ShowMe.config`, `ShowMe.slides`, `ShowMe.version`, `ShowMe.scale` | 읽기 전용 정보 |
| `document`의 `showme:change` 이벤트 | `detail: { slide, el }` |

장면 예: 들어올 때마다 다시 그리는 도식:

```js
(() => {
  let timers = [];
  ShowMe.scene('#flow', {
    init(el) { /* SVG·DOM을 한 번 만든다 */ },
    enter(el) { timers.forEach(clearTimeout); timers = []; /* 처음 상태로 되돌리고 setTimeout으로 순서대로 움직인다 */ },
    leave() { timers.forEach(clearTimeout); },
  });
})();
```

v2의 실제 장면(24시간 순환도, 밤사이 다섯 갈래 레인, 앱 화면 갤러리, 간격 반복 띠)은 모두 이 형태로 옮겨졌다. 그런 장면은 덱의 내용이며 엔진에 넣지 않았다.

## 시작 테마(deck.css)

새 덱은 시작 테마를 받는다. 시작 팔레트는 흰 배경과 검정 명도, 검정·회색의 어두운 장, 녹색(`--accent`)·주황(`--accent2`) 강조다. 부품은 `.rail`(왼쪽 글 600px), `.stage`(오른쪽 실물), `.cover`, `.kicker`, `h1`(58px)과 `h1.title`(112px), `.chips`/`.chip.a`·`.b`·`.o`, `.cues`(말할 순서), `.tpl`(라벨-값 표), `.card`, `.lede`, `.live`(LIVE 링크), `.src`(출처), `.keys`(키 안내). 덱이 소유하므로 자유롭게 고친다.

## 엔진 토큰

| 토큰 | 쓰는 곳 | 기본 |
| --- | --- | --- |
| `--accent`, `--accent-ink`, `--accent-soft` | 재생 막대, 현재 장, 확대 배지, 전체 보기의 현재 장 | `#00704a`, `#ffffff`, 12% |
| `--clock-hand` | 시계 바늘 | `#ffb547` |
| `--night` | `data-sky`가 없을 때 배경 | `#111111` |
| `--ink-l`, `--ink-d` | dark·light 톤의 글자색 | |
| `--warn`, `--danger` | 타이머 85%, 초과 | |
| `--sans`, `--mono` | 글꼴 | 시스템 글꼴 |

`data-tone`이 `--ink`, `--ink2`, `--ink3`, `--line`, `--card`를 정한다. deck.css에서 이 값을 쓰면 톤이 바뀔 때 같이 바뀐다.
