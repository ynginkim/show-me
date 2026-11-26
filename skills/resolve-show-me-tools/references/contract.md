# show-me 공유 계약

여러 leaf가 함께 쓰는 파일과 필드의 정본이다. 출처는 2026-11-25 강의 덱 v2(15장)와 이 저장소의 회귀 검증이다. 한 사례에서만 나온 항목은 "두 번째 사례 확인 전(잠정)"으로 표시한다.

## 덱 프로젝트 파일

| 파일 | 만드는 쪽 | 쓰는 쪽 |
| --- | --- | --- |
| `talk.md` | plan-talk | build-deck(장 목록·예산), check-deck(보고), revise-deck |
| `sources/`(선택) | 사용자 | prepare-media(읽기만) |
| `slides/index.html` | new_deck(템플릿) → build-deck | 브라우저, check-deck. 덱의 정본. 빌드 산출물이 아니다 |
| `slides/deck.css`, `slides/scenes.js` | new_deck(시작본) → build-deck | 브라우저 |
| `slides/engine/show-me.{js,css}` | new_deck(복사) | 브라우저. 덱에서 고치지 않는다 |
| `slides/fonts/` | new_deck | deck.css |
| `slides/media/*`, `slides/media/media.json` | prepare-media, link-lightplay | index.html, check-deck |
| `qa/deck/shots/`, `sheet.png`, `sheet_interactions.png`, `report.md`, `report.json`, `compare/` | check_deck.py | 판정, revise-deck 기준 |
| `제작노트.md` | create-deck 6단계, revise-deck 5단계 | 다음 수정 |

발표에 들고 가는 것은 `slides/` 폴더 하나다. 모든 경로는 `slides/` 기준 상대 경로로 쓴다(`file://`로 열기 때문). 다른 컴퓨터에서 열 `file://` 절대 링크는 check-deck이 경고한다.

## 설정 JSON

엔진보다 앞에 둔다. 엔진과 `check_deck.py`가 같은 블록을 읽는다.

```html
<script type="application/json" id="showme-config">
{"title": "…", "length": 1200,
 "sections": {"c": {"name": "01 회사", "short": "회사", "color": "var(--accent)", "budget": 240}},
 "clock": true, "tone": "dark", "stage": [1920, 1080]}
</script>
```

| 필드 | 뜻 | 기본 |
| --- | --- | --- |
| `length` | 강의 길이(초). 구간 예산 합과 슬라이드 예상 합을 대조한다 | 없으면 경고 |
| `sections.<키>` | `name`(상단·타이머 표시), `short`(구간 밖 장에서 타이머가 쓰는 짧은 이름), `color`, `budget`(초) | 없으면 타이머가 시간만 잰다 |
| `clock` | 상단 24시간 시계. 없으면 `data-h`가 있는 장이 하나라도 있을 때 켠다 | 자동 |
| `tone` | `data-tone`이 없는 장의 글자 톤 | `dark` |
| `stage` | 무대 크기. 1920×1080 외는 두 번째 사례 확인 전(잠정) | `[1920, 1080]` |

## 슬라이드 속성

`<section class="slide" …>` 하나가 한 장이다.

| 속성 | 뜻 |
| --- | --- |
| `data-sky` | 무대 배경. 색 또는 그라데이션. `--sky` 변수로도 쓰인다 |
| `data-sky-solid` | `data-sky`가 그라데이션일 때의 단색. 탭·버튼의 반전 글자색과 전체 보기 카드가 쓴다(0.2.0). 없으면 `data-sky` |
| `data-notop` | 이 장에서 상단 바를 숨긴다(0.2.0) |
| `data-clock` | `off`면 이 장에서 시계만 숨긴다(0.2.0) |
| `data-tone` | `dark` 또는 `light`. 글자·선·카드 색 토큰이 바뀐다 |
| `data-h` | 시계 바늘 시각(0~24). 하루의 시간대로 이야기를 이어 갈 때 쓴다. 두 번째 사례 확인 전(잠정) |
| `data-label` | 상단 왼쪽 라벨 |
| `data-sec` | 구간 키(설정 JSON의 `sections`). 없으면 구간 밖(표지·마무리) |
| `data-title` | 전체 보기(G)와 검사 보고의 제목 |
| `data-plan` | 이 장의 예상 시간(초). 구간 예산 대조에 쓴다 |
| `data-shot-wait` | 촬영 전 대기(ms). 들어올 때 움직이는 장면이 끝나는 시간 |

## media.json

`slides/media/media.json`의 `files[]`. `prep_media.py`와 `import_lightplay.py`가 쓰고, 손으로 고치지 않는다.

| 필드 | 뜻 |
| --- | --- |
| `file` | `slides/` 기준 경로 |
| `kind` | `video`, `image`, `thumb`, `poster`, `subtitles` |
| `source`, `source_sha256` | 원본 경로(프로젝트 안이면 상대 경로)와 해시. 원본이 바뀌었는지 판단한다 |
| `share` | `ok` 또는 `onsite-only`(현장에서 보여 줄 수 있지만 공개·예제 재사용 금지) |
| `from`, `lightplay_project` | Lightplay에서 가져온 파일일 때 |
| `cmd` | 만든 명령. 다시 만들 때 그대로 쓴다 |

## 검사 결과

`check_deck.py`의 exit 1은 자동 검사 실패(페이지·콘솔 오류, 없는 파일, 깨진 미디어, 예산 합이 강의 길이 초과, 설정·`data-chap` 형식 오류)다. exit 0은 덱이 좋다는 뜻이 아니다. `report.md`의 경고, 슬라이드 표(화면 밖 요소, 잘린 글자), "눈으로 볼 것", "사람 확인"을 읽는다. 촬영본 비교는 원본끼리도 흔들리는 영역(지연 로딩 썸네일 디코딩, 재생 중 영상 프레임)이 있으므로 차이 그림을 열어 판단한다.
