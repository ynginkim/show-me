# 산출물 의존 그래프

덱 프로젝트 하나의 파일이 어떻게 만들어지고, 무엇이 바뀌면 무엇을 다시 만드는지 적는다. 경로는 프로젝트 폴더 기준이다. `D`는 `resolve-show-me-tools/scripts`의 절대 경로다. 비용은 2026-11-26 이 저장소의 회귀 검증에서 잰 값이며, 측정하지 않은 것은 미측정으로 둔다.

## 노드

| 노드 | 파일 | 생성/소비 | 비용 | 근거 |
| --- | --- | --- | --- | --- |
| 계획 | `talk.md` | plan-talk가 쓴다 / build-deck, check-deck 보고, revise-deck | 모델 작업만 | 설계 |
| 원본 자료 | `sources/` 또는 사용자가 알려 준 경로, Lightplay 프로젝트 | 사용자·Lightplay / prepare-media, link-lightplay | 없음(읽기 전용) | v2 `prep_media.py`가 `sources/`·`capture/`를 읽음 |
| 미디어 | `slides/media/*`, `slides/media/media.json` | `prep_media.py`, `import_lightplay.py` / index.html, check | 영상 변환은 길이에 비례(미측정). v2 미디어 합계 약 31 MB | v2 `slides/media` |
| 엔진 사본 | `slides/engine/show-me.js`, `show-me.css` | `new_deck.py`(복사) / index.html | 없음 | 설계 |
| 글꼴 | `slides/fonts/*` | `new_deck.py`(로컬 복사 또는 내려받기) / deck.css | 내려받기 약 2.3 MB(Pretendard·JetBrains Mono) | v2 `slides/fonts` |
| 덱 본문 | `slides/index.html`(설정 JSON 포함), `slides/deck.css`, `slides/scenes.js` | build-deck / 브라우저, check | 모델 작업만 | 설계 |
| 검사 결과 | `qa/deck/shots/*.png`, `qa/deck/sheet.png`, `qa/deck/report.md`, `report.json` | `check_deck.py` / 판정, revise-deck 기준 | 15장+상호작용 6장 촬영 약 1분(아래 회귀 기록) | 회귀 검증 |
| 비교 결과 | `qa/deck/compare/*` | `check_deck.py --baseline` / revise-deck | 촬영 비용과 같음 | 설계 |

## 간선과 무효화

| 변경 | 무효화 | 재사용 조건 | 다음 확인 |
| --- | --- | --- | --- |
| 슬라이드 문구·색(표면) | 해당 장의 촬영본 | 설정 JSON과 `data-sec`·`data-plan`이 그대로면 예산 표 재사용 | 전 장 다시 촬영(1분 내외라 일부만 찍지 않는다), 수정 전 촬영본과 비교 |
| 구간 예산·`data-sec`·`data-plan`(계약) | 예산 표, 타이머 표시, `talk.md` 구간 표 | 없음 | `talk.md`와 설정 JSON을 함께 고치고 예산 검사 |
| 원본 녹화 교체 | 해당 `media/*.mp4`, 플레이어의 장(chapter) 시각 | 길이·장면 시각이 같으면 장 목록 재사용. 다르면 `data-chap` 다시 씀 | 그 장의 상호작용 촬영 |
| Lightplay 영상 다시 렌더 | 가져온 영상·포스터, 장 목록(`timeline.json` scenes) | 마스터 파일 해시가 `media.json`과 같으면 재사용 | `import_lightplay.py` 다시 실행, 해시 비교 |
| 엔진 갱신 | 전 장의 촬영본 | 덱이 엔진 API만 썼으면 내용 파일은 그대로 | 갱신 전 촬영본을 기준으로 전 장 비교. 차이가 설명되지 않으면 이전 엔진으로 되돌린다 |
| `scenes.js` 수정 | 그 장면이 있는 장 | 다른 장은 비교로 확인 | 해당 장 상호작용 촬영 |

## 흐름 대입

- **새 덱:** 계획 → 미디어 → 새 덱 폴더(엔진·글꼴 복사) → 본문 → 검사. 다시 실행할 최소 명령은 `check_deck.py` 하나다. 유료 자원은 없다.
- **영상 프로젝트에서:** Lightplay 프로젝트는 읽기만 한다. 가져온 파일의 원본 경로·SHA256을 `media.json`에 남긴다. 영상이 다시 렌더되면 해시가 달라지므로 가져오기를 다시 실행한다.
- **수정:** 수정 전에 `qa/deck/`를 `qa/deck/before-<시각>/`로 옮겨 기준으로 삼는다. 수정 뒤 `check_deck.py --baseline`으로 바뀐 장과 바뀌지 않아야 할 장을 함께 본다.

반복 검수 사이클(본문 → 검사 → 본문)은 오류 0, 화면 밖 요소 처리, 시트 열람이 끝나면 멈춘다. 같은 문제가 두 번 고쳐도 남으면 원인을 엔진·내용 중 어디에 둘지부터 다시 정한다.
