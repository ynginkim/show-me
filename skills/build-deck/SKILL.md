---
name: build-deck
description: "talk.md와 준비된 미디어로 덱의 index.html 슬라이드·설정 JSON, deck.css 테마, scenes.js 장면을 쓰는 기술. 엔진 API와 부품 목록을 소유한다. 새 덱 작성과 장 수정에 쓴다."
disable-model-invocation: true
---

# 덱 만들기

Read ../resolve-show-me-tools/SKILL.md

입력은 `talk.md`, `slides/media/`와 `media.json`, 새 덱 템플릿이나 기존 `slides/`다. 결과는 고친 `slides/index.html`, `deck.css`, `scenes.js`와 엔진 후보 메모다. `slides/engine/`은 고치지 않는다. 직접 불러도 같다.

Read `references/components.md`. 엔진이 해석하는 속성, 부품, `ShowMe` API가 거기 있다.

Read `../principle-content-before-engine/SKILL.md`, Read `../principle-audience-words/SKILL.md`. **principle-content-before-engine**, **principle-audience-words**를 적용한다.

## 절차

1. **설정 JSON.** `talk.md`의 강의 길이와 구간 예산을 `#showme-config`의 `length`, `sections`로 옮긴다(초 단위). 구간 색은 deck.css의 토큰을 `var(--…)`로 가리킨다.
2. **장.** `talk.md`의 장 목록 순서대로 `<section class="slide">`를 쓴다. 장마다 `data-sec`, `data-title`, `data-plan`(예상 초)을 넣는다. 배경 `data-sky`와 톤 `data-tone`은 장의 성격(실물이 밝은 문서면 light, 영상·도식이면 dark 등)으로 정하고, 시간대로 이야기를 잇는 강의면 `data-h`로 시계를 움직인다.
3. **배치.** 실물이 있는 장은 왼쪽 글(`.rail`) + 오른쪽 실물(`.stage`)을 기본으로 한다. 실물 부품은 components.md에서 고른다: 녹화는 `.player`(세로) 또는 `.player[data-shape=wide]`, 긴 캡처는 `.scroller`, 여러 실물은 `.tabs`, 확대는 `data-zoom`, 이야기 이동은 `data-goto`, 처음부터 틀 영상은 `data-autoplay`.
4. **글.** 제목은 한 문장, 3줄 이하. 본문 글자는 20px 이상(1920×1080 기준), 장마다 메시지 하나. 내부 이름 대신 청중의 말(**principle-audience-words**). 원문을 보여 줘야 하면 `<details>`로 접는다. 출처·날짜는 `.kicker`나 `.src`에 짧게.
5. **장면.** 도식과 애니메이션은 scenes.js에 `ShowMe.scene(대상, { init, enter, leave })`로 쓴다. 들어올 때 움직이는 장면이 있으면 그 장에 `data-shot-wait`(끝나는 ms + 여유)를 넣는다. 엔진에 없는 동작이 필요하면 scenes.js에 쓰고, 다른 덱에서도 쓸 것 같으면 `제작노트.md`의 "엔진 후보"에 한 줄 남긴다(**principle-content-before-engine**).
6. **테마.** 색·글꼴·레이아웃 부품은 deck.css에서 고친다. 엔진 토큰(`--accent`, `--accent-ink`, `--accent-soft`, `--clock-hand`, `--night`, `--sans`, `--mono`)을 덮어써 엔진 부품의 색을 맞춘다.
7. **표지.** 표지에는 강의 제목, 구간과 예산, 키 안내(`.keys`)를 둔다. 발표자가 키를 잊었을 때 표지에서 확인한다.

## 나눠 만들기

장이 많으면 구간마다 하위 agent에 나눠 맡길 수 있다. 먼저 설정 JSON, deck.css 토큰, 장 번호를 확정하고, 각 agent는 자기 구간의 `<section>`과 scenes.js 블록만 쓴다. index.html과 scenes.js의 합치기는 현재 세션이 맡는다.

## 돌려주는 것

바뀐 파일, 장 수와 구간별 `data-plan` 합, scenes.js에 쓴 장면 목록, 엔진 후보, 확인하지 못한 시각(장 시작점 등).
