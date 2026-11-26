### 만든 자료 고치기

형제 skill 경로는 mode 폴더 기준이다. `slides/index.html`이 있는 덱 프로젝트와 수정 요청·피드백이 있을 때 쓴다. 수정 전 촬영본을 기준으로 남겨 바뀐 장과 바뀌지 않아야 할 장을 함께 확인한다.

1. 기존 덱과 수정 요청을 확인한다.
2. 수정 전 촬영본을 기준으로 남기고 바뀔 범위를 정한다.
3. 필요한 leaf로 고친다.
4. 전 장을 다시 찍어 기준과 비교한다.
5. 바뀐 것과 사람 확인 요청을 전달한다.

**1.** Read `../resolve-show-me-tools/SKILL.md`. `D`를 확인하고 `preflight.py`를 실행한다. 프로젝트의 `talk.md`, `제작노트.md`, `PAUSE.md`, `qa/deck/report.md`, `slides/media/media.json`을 읽는다. `check_deck.py --no-shoot`으로 덱 엔진 버전과 설치본 버전을 본다. 다르더라도 사용자가 엔진 갱신을 요청하지 않았으면 덱의 엔진을 그대로 쓴다.

**2.** 수정하기 전에 `check_deck.py <프로젝트> --out <프로젝트>/qa/deck/before-<YYYYmmdd-HHMM>`으로 기준 촬영본을 만든다(이전 촬영 뒤로 덱이 바뀌지 않았으면 기존 `qa/deck/shots/`를 그 폴더로 옮겨도 된다). 아래 표에서 이번 변경이 닿는 행을 고르고, 바뀔 장과 바뀌지 않아야 할 장을 적는다. **principle-judge-from-shots**를 적용한다.

| 변경 | 다시 할 것 | 그대로 둘 것 |
| --- | --- | --- |
| 문구·색·배치 | 해당 장의 본문(build-deck) | `talk.md`의 구간 예산, 미디어 |
| 시간 줄이기·늘리기, 장 순서·추가·삭제 | `talk.md` 구간 예산과 장 목록(plan-talk) → 본문과 설정 JSON(build-deck). `data-goto` 번호와 장면 대상 확인 | 미디어 |
| 녹화·캡처 교체 | 변환(prepare-media) → 플레이어 장(`data-chap`) 시각 → 해당 장 | 다른 장 |
| Lightplay 영상을 다시 렌더함 | 가져오기(link-lightplay)와 해시 비교 → 장 시각 | 해시가 같으면 미디어 전체 |
| 엔진 갱신(요청했을 때만) | `new_deck.py --update-engine` → 전 장 비교 | 내용 파일 |
| 새 동작이 필요함 | scenes.js(**principle-content-before-engine**) | 엔진 |

**3.** 표에서 고른 순서대로 Read `../plan-talk/SKILL.md`, Read `../prepare-media/SKILL.md`, Read `../link-lightplay/SKILL.md`, Read `../build-deck/SKILL.md` 중 필요한 것만 따른다. 고치는 동안 **principle-audience-words**로 새 문구를 고른다.

**4.** Read `../check-deck/SKILL.md`. `check_deck.py <프로젝트> --baseline <기준 폴더>/shots`를 돌린다. 비교 표에서 바뀐 장이 2단계에 적은 장과 같은지 본다. 바뀌지 않아야 할 장이 바뀌었으면 차이 그림을 열어 원인을 찾고 고친다. 원본끼리도 흔들리는 영역(지연 로딩 썸네일, 재생 중인 영상 프레임)은 차이 그림에서 확인하고 이유를 적는다. 바뀐 장은 원본 크기로 열어 본다.

**5.** `제작노트.md`에 수정 이력(요청, 바뀐 장, 비교 결과, 다시 만든 명령)을 더한다. 보고에는 바뀐 장 목록과 비교 수치, 그대로 둔 것과 이유, 사람 확인 항목을 넣고 mode의 사람 판정 요청 문장으로 끝낸다. 기준 촬영본 폴더는 사용자가 정리를 승인할 때까지 남긴다.
