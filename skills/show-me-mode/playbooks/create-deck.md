### 새 강의 자료 만들기

형제 skill 경로는 mode 폴더 기준이다. 원자료(녹화·캡처·링크)에서 출발하든 Lightplay 영상 프로젝트에서 출발하든 이 흐름을 쓴다. 다른 점은 2·3단계의 분기뿐이다.

1. 도구를 점검하고 덱 프로젝트를 만든다.
2. 청중과 시간 예산, 장마다 보여 줄 실물을 계획한다.
3. 보여 줄 실물을 모으고 브라우저용으로 바꾼다.
4. 덱 본문과 장면을 쓴다.
5. 전 장을 찍어 검사하고 고친다.
6. 결과물과 사람 확인 요청을 전달한다.

**1.** Read `../resolve-show-me-tools/SKILL.md`. `D`를 확인하고 `preflight.py`를 실행한다. 촬영 도구(playwright-core)가 없으면 설치 안내를 보여 주고 사용자가 정하게 한다. 작업 폴더 정책에 따라 프로젝트 폴더를 정하고 `new_deck.py`로 만든다. 자료 위치에 Lightplay 프로젝트(`project.json`, `timeline.json`, `out/`)가 있으면 그 경로를 적어 둔다.

**2.** Read `../plan-talk/SKILL.md`. `talk.md`를 쓴다. Lightplay 프로젝트가 있으면 먼저 Read `../link-lightplay/SKILL.md`의 "영상이 이미 말한 것"을 따라 영상의 장면과 메시지를 읽고, 덱은 영상이 말하지 않은 것을 맡게 한다. **principle-show-the-real-thing**으로 장마다 실물과 도식을 고르고, **principle-audience-words**로 제목과 라벨의 말을 고른다. 구간 예산 합이 강의 길이를 넘으면 장을 줄인다. 글자를 줄이거나 말을 빨리 해서 맞추지 않는다.

**3.** Read `../prepare-media/SKILL.md`. `talk.md`의 실물 목록대로 원자료를 `slides/media/`로 바꾼다. Lightplay 영상은 `link-lightplay`의 가져오기로 받는다. 공개 범위가 걸린 자료는 `--onsite`로 기록한다. 긴 영상 변환은 백그라운드로 돌리고 4단계를 시작한다.

**4.** Read `../build-deck/SKILL.md`. `talk.md`의 장 목록과 구간 예산을 index.html의 슬라이드와 설정 JSON으로 옮기고, 장면 애니메이션은 scenes.js에 쓴다. 엔진에 없는 동작은 **principle-content-before-engine**에 따라 scenes.js에 쓰고 제작노트의 "엔진 후보"에 한 줄 남긴다.

**5.** Read `../check-deck/SKILL.md`. `check_deck.py`를 돌리고 실패를 고친 뒤 다시 돌린다. 실패 0이 되면 **principle-judge-from-shots**에 따라 `sheet.png`·`sheet_interactions.png`와 글이 많은 장을 원본 크기로 열어 본다. 화면 밖 요소, 잘린 글자, 한 장에 메시지 둘 이상, 맨 뒷줄에서 못 읽을 글자 크기를 고친다. 같은 문제가 두 번 고쳐도 남으면 원인을 내용·엔진·미디어 중 어디에 둘지부터 다시 정한다. 실패 0, 경고 처리, 시트 열람이 끝나면 멈춘다.

**6.** 프로젝트에 `제작노트.md`를 쓴다: 결과물 경로, 엔진 버전, 장 수와 구간 예산, 다시 만드는 명령(`new_deck.py`, `prep_media.py`, `import_lightplay.py`, `check_deck.py`), 현장 전용 자료 목록, 적용한 principle과 바뀐 결정, 엔진 후보, 사람 확인 항목. 보고는 결과물부터 쓰고 자동 검사·에이전트가 본 것·사람이 판정할 것을 나눈다. mode의 사람 판정 요청 문장으로 끝낸다. 촬영본처럼 다시 만들 수 있는 파일의 정리는 작업 폴더 정책을 따르고, 사용자 확인 없이 지우지 않는다.
