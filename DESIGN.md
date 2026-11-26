# show-me 설계

Status: implemented. 구조·도구·엔진 회귀·설치는 검증했다. 새 세션의 라우팅 시험, 두 번째 사례를 새 엔진으로 다시 만들기, 발표 화면에서의 사람 판정은 unverified다(아래 "확인하지 못한 것").

한 줄 철학: 말로 설명하기 전에 실물을 보여 주는 강의 자료를 만들고, 찍은 화면으로 판정한다.

## 범위

강의·발표에서 브라우저로 여는 HTML 슬라이드 덱을 만들고 고친다. 덱은 녹화 영상, 화면 캡처, 실제 링크를 슬라이드 안에서 재생·확대·스크롤하며 보여 준다. 키보드로 넘기고, 구간별 시간 예산 타이머를 켤 수 있다.

범위 밖: PPTX·Keynote·Google Slides 파일, PDF 유인물만 만드는 일, 모션그래픽 영상 제작(Lightplay가 맡는다), 발표 대본 낭독 녹음.

## 출발 사례

| 사례 | 상태 | 쓰인 곳 |
| --- | --- | --- |
| 2026-11-25 강의 덱 v2 (`video-creator2/projects/2026-11-25-how-i-use-agents-v2/slides/`, 15장, 비전공 교수 대상 20분) | 실제 강의에 사용. 읽기 전용 원본 | 엔진 기능, 파일 구조, 검사 방법, principle 근거, 회귀 기준 |
| 2026-11-26 메이킹 강의 덱 (`video-creator2/projects/2026-11-26-making-of-lecture/`, 17장, 비전공 학생 대상 20분) | 다른 세션에서 제작 중. 이 설계의 마지막 단계에서 `engine_notes.md`, `brief.md`를 읽기 전용으로 읽었다 | 잠정 규칙 대조, 엔진 후보, 시작 팔레트 |

클라이언트 앱 화면과 개인 자료는 이 저장소의 예제·문서에 넣지 않았다. 예제는 ffmpeg·Pillow로 만든 중립 샘플(`examples/sample-deck/`)이다. v2 회귀 도구는 고객 화면을 다루므로 커밋하지 않는 `.work/regress-v2/`에 둔다.

## 결과물과 판정

| 구분 | 계약 |
| --- | --- |
| 결과물 | 덱 프로젝트 폴더. 발표에 들고 가는 `slides/`(index.html, deck.css, scenes.js, engine/, fonts/, media/)와 `talk.md`, `qa/deck/`, `제작노트.md` |
| 에이전트 완료 | `check_deck.py` 자동 검사 실패 0(페이지·콘솔 오류, 없는 파일, 깨진 미디어, 예산 합 초과, 설정·`data-chap` 형식). 경고 처리. 시트와 글이 많은 장을 Read로 연 기록. 현장 전용 목록과 재생성 명령 |
| 사람 판정 | 발표 화면의 맨 뒷줄 가독성과 색, 리허설로 잰 구간 시간, 영상 소리, 내용·말투 |
| 납품 요청 문장 | "`slides/index.html`을 발표할 화면에서 열어 F(전체 화면)·T(타이머)로 한 번 넘겨 보며 리허설해 주세요. 저는 1920×1080 스크린샷과 오류 검사로 확인했고, 현장 화면의 글자 크기와 소리, 실제 말하는 시간은 확인하지 못했습니다." |
| 재개 상태 | 프로젝트 `PAUSE.md`(끝난 것, 남은 것, 다시 시작하는 명령) |

## 기준과 결과

후보를 보기 전에 정한 기준이다(**principle-criteria-before-candidates**).

| 번호 | 기준 | 확인 방법 | 결과 |
| --- | --- | --- | --- |
| C1 | 엔진과 내용이 분리된다 | 엔진 파일에 v2 내용 문자열이 없다. 덱은 엔진을 고치지 않고 scenes.js로 확장한다 | 통과. grep 0건(부분 일치 `setPointerCapture`, 토큰 `--night` 제외). v2 장면 4개를 엔진 무수정으로 scenes.js에 옮김 |
| C2 | v2 덱을 새 엔진으로 다시 만들 수 있다 | v2 내용을 새 형식으로 옮겨 15장과 상호작용 6장을 찍고 원본과 장마다 비교 | 통과. 아래 "검증 기록" |
| C3 | 강의 한 편이 끝까지 이어진다 | 새 덱·영상 에셋 덱·수정을 mode부터 따라가며 단계·입력·결과 연결 확인 | 정적 확인 통과(아래 "흐름 대입"). 새 세션 실행은 unverified |
| C4 | Lightplay 없이도 전부 동작하고, 있으면 파일 계약으로 잇는다 | Lightplay의 playwright를 쓰지 않는 촬영, 가짜 Lightplay 프로젝트 가져오기 | 통과. 원본 8개 파일 해시 전후 동일, 계약 없는 폴더는 exit 2 |
| C5 | 검사가 기계 확인과 사람 판정을 나눈다 | 보고서에 자동 검사와 "눈으로 볼 것", "사람 확인"이 따로 있다 | 통과 |
| C6 | 하네스 구조 검사를 통과한다 | `python3 scripts/check.py .`, `selftest.py` | 통과 |

## 실제 흐름

| 흐름 | 출발 파일 | 달라지는 단계 | 끝나는 파일 |
| --- | --- | --- | --- |
| A. 새 강의 자료 | 요청(청중·시간·장소), 녹화·캡처·링크 | 계획 전체, 미디어 변환 전체, 덱 새로 만들기 | 새 프로젝트 전체 |
| B. 영상 프로젝트로 슬라이드 | Lightplay 프로젝트(out/, timeline.json, storyboard.md) | 영상이 이미 말한 것과 덱이 더할 것을 나누는 계획, 계약 파일 가져오기(출처 기록) | A와 같다. media.json에 영상 출처 |
| C. 만든 자료 고치기 | 기존 덱 프로젝트, 피드백 | 수정 전 촬영본 남기기, 바뀔 장 정하기, 수정 후 비교, 엔진은 요청할 때만 갱신 | 바뀐 장과 비교 보고 |

A와 B는 출발 자료만 다르고 계획 이후 단계가 같다. 그래서 playbook을 나누지 않고 `create-deck`의 2·3단계 분기와 `link-lightplay` skill로 두었다(**principle-split-by-lifecycle**: 다시 만드는 범위와 단계가 같다). C는 기존 결과물을 읽고 무엇을 다시 찍을지부터 정하므로 따로 두었다.

흐름 대입(정적): A는 mode → create-deck 1(adapter, preflight, new_deck) → 2(plan-talk → talk.md) → 3(prepare-media → media/, media.json) → 4(build-deck → index.html·scenes.js) → 5(check-deck → report, 시트 열람) → 6(제작노트, 요청 문장)으로 이어진다. B는 2단계에서 link-lightplay의 "영상이 이미 말한 것", 3단계에서 `import_lightplay.py`가 더해진다. C는 revise-deck 2단계의 기준 촬영과 4단계의 `--baseline` 비교로 닫힌다. 각 단계의 명령은 `scripts/test_tools.py`와 샘플 덱에서 실제로 실행했다.

## 구성

| 요소 | 이름 | 채택 이유 |
| --- | --- | --- |
| mode | `show-me-mode` | 요청을 A·B·C로 보내고, 결과물·완료·사람 판정과 정지선을 정한다 |
| playbook | `create-deck` | A와 B. 새 덱 프로젝트 |
| playbook | `revise-deck` | C. 출발 상태(기존 덱)와 다시 찍을 범위가 다르다 |
| adapter | `resolve-show-me-tools` | 엔진·템플릿·스크립트 한 벌을 소유하고 경로 `D`, 환경 점검, 새 덱, 엔진 갱신, 공유 계약을 제공한다 |
| skill | `plan-talk` | 청중·목표·구간 예산·장마다 한 문장과 실물을 `talk.md`로 돌려준다. 새 덱과 시간·순서 수정에서 쓴다 |
| skill | `prepare-media` | 녹화·캡처를 브라우저용으로 바꾸고 `media.json`에 출처를 남긴다. 새 덱과 미디어 교체에서 쓴다 |
| skill | `build-deck` | `talk.md`와 미디어로 본문·설정·테마·장면을 쓴다. 엔진 API와 부품 목록을 소유한다 |
| skill | `check-deck` | 전 장 촬영, 자동 검사, 시트, 수정 전후 비교를 돌려준다. 두 playbook의 완료 판정에 쓴다 |
| skill | `link-lightplay` | Lightplay 프로젝트의 납품 파일·장면 시각을 계약대로 읽어 가져온다. 없으면 건너뛴다 |
| principle | `principle-audience-words` | 슬라이드 글을 쓸 때 내부 이름 대신 청중의 말. v1→v2에서 작업 이름·PR 번호를 "AI 1~5"로, "실패·느림·즉시"를 "틀림·생각해서·바로"로 바꾼 결정이 근거. 두 번째 사례 brief도 "화면에 개발 용어를 쓰지 않는다" |
| principle | `principle-show-the-real-thing` | 설명 방식을 고를 때 실물 먼저, 보이지 않는 과정만 도식, 공개 범위는 현장 전용. v2 15장 중 8장이 실물, 2장이 도식. 두 번째 사례도 "내가 한 말 원문 + 그래서 나온 화면"을 짝지었다 |
| principle | `principle-content-before-engine` | 새 동작은 덱의 scenes.js에 먼저, 두 번째 덱이 필요로 할 때 엔진으로. v2 빌드가 v1 줄 번호를 잘라 붙인 문제가 근거. 두 번째 사례도 강의 전용 위젯을 엔진 밖에 두고 후보를 따로 적었다 |
| principle | `principle-judge-from-shots` | 완료와 수정 범위를 찍은 화면·검사 표·비교로 판정하고 현장 확인은 사람에게. 두 번째 사례에서 자동 검사가 놓친 빈 공간·이중 따옴표를 눈으로 고쳤다 |

기각한 후보와 대체 위치:

- playbook `slides-from-video`(흐름 B): 계획 이후 단계가 A와 같다. 사본 playbook은 어긋나기 쉽다. `create-deck` 분기와 `link-lightplay`로 둔다.
- skill `critique-deck`(독립 비평): v2에 독립 비평 기록이 없다. 판정은 `check-deck`의 시트 읽기와 `principle-judge-from-shots`에 둔다. 맥락 없는 비평이 결정을 바꾼 사례가 생기면 다시 검토한다.
- 빌드 단계(조각 HTML 합치기): v2 `build_v2.py`가 빌드 산출물과 원본을 갈라 고칠 파일을 헷갈리게 했다. `file://`에서는 HTML 조각을 불러올 수도 없다(두 번째 사례 불편 3). index.html을 직접 원본으로 둔다.
- 공용 테마를 엔진에 포함: 색·글꼴·레이아웃 부품은 덱마다 바뀐다. 새 덱을 만들 때 시작 테마를 `deck.css`로 복사하고 그 뒤로는 덱이 소유한다.
- 두 번째 mode: 사람의 역할이 바뀌지 않는다(만들기와 고치기 모두 발표자가 판정).
- 운영 adapter(resolve-capability): 운영 어휘는 백그라운드 실행, 하위 agent 둘이다.

## 엔진과 내용의 경계

| 엔진(`engine/show-me.js`, `show-me.css`) | 덱(`index.html`, `deck.css`, `scenes.js`, `media/`) |
| --- | --- |
| 1920×1080 무대 맞춤, 키보드·해시 이동, 전체 보기, 전체 화면 | 슬라이드 본문과 속성 값 |
| 구간 예산 타이머(설정 JSON의 sections) | 구간 이름·색·예산 값 |
| 슬라이드 속성 해석, 상단 바(시계·라벨·구간·타이머·장 번호) | 색 토큰, 글꼴, 레이아웃 부품 |
| 탭, 드래그 스크롤, 확대 보기, `data-goto`, 휴대폰·가로 플레이어와 장, 진입 시 자동 재생 | 장면 스크립트(도식, 갤러리, 애니메이션) |
| 장면 훅 `ShowMe.scene(대상, {init, enter, leave})`, 공개 API | 미디어와 출처 기록 |

엔진이 만드는 요소의 클래스는 `sm-` 접두사를 쓴다. 두 번째 사례에서 덱 CSS의 `.bar`가 엔진 재생기 막대와 부딪혀 잘린 결함이 실제로 났다. 덱이 쓰는 부품 클래스(`player`, `tabs`, `scroller` 등)는 API라 접두사 없이 둔다.

## 파일 경계와 Lightplay

- 실행 자원(`scripts/`, `assets/engine/`, `assets/template/`)은 `resolve-show-me-tools`가 상대 배치(`scripts/../assets`) 그대로 한 벌 소유한다. 다른 leaf는 제목 바로 아래 `Read ../resolve-show-me-tools/SKILL.md`로 adapter를 읽는다.
- 공유 계약(덱 파일, 설정 JSON, 슬라이드 속성, media.json, 검사 결과)은 `resolve-show-me-tools/references/contract.md` 한 곳에 둔다. 엔진 API와 부품은 `build-deck/references/components.md`가 소유한다.
- Lightplay와는 파일 계약만으로 잇는다(`link-lightplay/references/lightplay-contract.md`). show-me는 Lightplay 프로젝트를 읽기만 하고, showreel-mode를 중첩 호출하지 않으며, Lightplay 설치를 요구하지 않는다. Lightplay가 op55를 소비하는 방식(adapter가 경로를 확인하고 leaf가 계약 파일을 받음)과 같다. 다른 점은 show-me가 Lightplay의 스크립트를 실행할 일이 없다는 것이다. 그래서 Lightplay 쪽 adapter 경로는 `preflight.py`가 참고로만 보고한다.
- 확인 기준: Lightplay `42cf8e156645b22d31c0cea031dc46981ec636ab`의 `finish.py` 산출물 이름과 v2 영상 프로젝트의 실제 `project.json`·`timeline.json`. 특정 커밋을 실행 조건으로 요구하지 않는다.

## 진입 정책과 언어

<!-- skillset:policy:start -->
| mode | 자연어 자동 호출 |
| --- | --- |
| `show-me-mode` | `true` |

leaf skill과 principle의 자동 호출은 `false`다.
<!-- skillset:policy:end -->

`show-me-mode`는 자연어 진입을 허용한다. "강의 자료", "발표 슬라이드"는 요청 표현만으로 영역이 드러나고, Lightplay의 `showreel-mode`가 "슬라이드만 만드는 작업"을 범위 밖으로 둔 자리를 맡는다. description에 PPTX·Keynote·Google Slides와 영상 제작을 범위 밖으로 적었다. leaf와 principle은 명시 호출이다. 문서와 UI는 한국어, 이름은 영어 kebab-case다.

## 검증 기록

| 검사 | 명령·방법 | 결과 |
| --- | --- | --- |
| 구조 | `python3 scripts/check.py .` | exit 0 |
| 검사기 오류 주입 | `python3 scripts/selftest.py` | exit 0 |
| 도구 | `python3 scripts/test_tools.py` | 14/14. 새 덱 생성·보존, 엔진 보존·갱신 백업, 정적 결함 4종(없는 미디어, 설정에 없는 구간, 예산 초과, `data-chap` 형식), 장면 예외, Lightplay 가져오기·출처·원본 무변경·계약 없는 폴더 |
| 엔진 회귀(v2) | `.work/regress-v2/run.sh`: 원본 2회, 이식본 1회 촬영, 장마다 비교. 자세한 수치는 [회귀 기록](docs/regression-v2.md) | 통과. 2차 실행에서 이식본과 원본 21장 중 19장 픽셀 동일, 다른 2장(지연 로딩 썸네일, 시계 1픽셀)은 원본끼리도 달라지는 영역. 오류 0, 타이머 동일. 엔진 접두사·팔레트 변경 전후 이식본 차이는 1픽셀 |
| 샘플 덱 | `check_deck.py examples/sample-deck` | 실패 0, 경고 0, 7장 + 상호작용 4장, 시트 열람 |
| Lightplay 없는 촬영 | 이 저장소의 playwright-core 1.65.1(`preflight.py --install`)로 가져온 영상 덱 검사 | 실패 0 |
| 설치 smoke | 커밋 후 clone에서 `python3 scripts/install_smoke.py` | 통과. 커밋 `15c4c4c`를 clone해 skills@1.7.4로 설치, skill 11개와 playbook·참조 72개를 `.agents`·`.claude` 두 경로에서 열었다. 설치본의 `new_deck.py`·`check_deck.py`로 새 덱을 만들고 검사(실패 0) |
| CI(GitHub Actions) | 첫 push의 `check` 워크플로: 구조 검사, 자체 테스트 49건, 설치 smoke | 통과(run 45763925455) |
| GitHub 경로 설치 | 빈 Git 폴더에서 `npx skills@1.7.4 add ynginkim/show-me` 후 설치본의 `new_deck.py`·`check_deck.py --no-shoot` | 통과. skill 11개 |
| 라우팅(새 세션) | 미실행 | unverified |

## 잠정 규칙과 두 번째 사례 대조

한 사례(v2)에서 나온 규칙은 문서에 "두 번째 사례 확인 전(잠정)"으로 표시했다. 두 번째 사례의 `engine_notes.md`·`brief.md`(제작 중 시점)로 대조한 결과다. 그 덱이 끝나면 새 엔진으로 다시 만들어 다시 대조한다.

| 규칙 | 위치 | 두 번째 사례 | 상태 |
| --- | --- | --- | --- |
| 청중의 말로(개발 용어 빼기) | principle-audience-words | brief에 같은 규칙 | 두 사례 일치. 문서의 잠정 표시는 그 덱 완료 뒤 지운다 |
| 실물 먼저, 현장 전용 | principle-show-the-real-thing | 원문 + 결과 화면 짝, 현장 전용 | 두 사례 일치(같음) |
| 빌드 없음, 엔진·내용 분리, 엔진이 상단 바·확대·전체 보기를 만듦 | 엔진, contract | 독립적으로 같은 구조 | 두 사례 일치 |
| 장면 훅 init/enter/leave | 엔진 | `Deck.widget(name, {init, enter, leave})` | 두 사례 일치 |
| 설정에 구간·예산 | 엔진, plan-talk | `window.DECK.sections` | 두 사례 일치(형식만 다름: show-me는 JSON 블록) |
| 장당 60~120초, 한 장에 메시지 하나 | plan-talk | 17장/20분(장당 약 70초) | 범위 안. 메시지 수는 미확인 |
| 가로 16:9 플레이어 | 엔진 `data-shape="wide"` | `.vplayer`를 새로 만듦 | 필요는 확인. show-me 구현은 그 덱에서 쓰이지 않아 잠정 |
| 진입 시 자동 재생 `data-autoplay` | 엔진 | 쓰지 않음(P·클릭 재생) | 잠정 |
| 시계 `data-h` | 엔진 | 썼지만 이야기 시각이 없는 장에서 끄고 싶어 함 | 잠정. 장별 끄기 후보 |
| 변환 기본값(높이 1600, 30fps, CRF 22, 폭 1600) | prepare-media | 정보 없음 | 잠정 |
| Lightplay 파일 이름 계약 | link-lightplay | v2 영상을 슬라이드에서 틀었음(복사) | 필요는 확인. 계약 파일 이름은 잠정 |
| 시작 팔레트(v2 네이비·청록) | 시작 테마 | 사용자가 그 팔레트를 이어 쓴 덱을 마음에 들어 하지 않음 | 바꿈: 무채색 + 녹색·주황 강조로 시작(기본값, 아래) |

## 엔진 후보(두 번째 사례 요구, 아직 넣지 않음)

**principle-content-before-engine**에 따라 한 덱에서만 나온 요구는 후보로 둔다. 그 덱을 새 엔진으로 다시 만들 때 필요하면 덱의 scenes.js로 먼저 구현하고, 다른 덱에서도 필요하면 엔진으로 올린다.

| 후보 | 그 덱의 이유 |
| --- | --- |
| 차례로 나타나기(`data-frag`, 같은 값 함께), 촬영용 전부 펼치기 | 원문을 먼저 보이고 결과 화면을 다음 →에 보여야 했다 |
| 소리 버튼(`data-audio`, 한 번에 하나) | 녹음 줄을 그 자리에서 들려줬다 |
| B 화면 끄기, Shift+T 타이머 0으로, 전체 경과 시간 | 현장 운영. 타이머가 페이지를 연 순간부터 잰다 |
| 그라데이션 하늘 + 단색 대체(`data-sky-solid`) | 탭 글자색이 `var(--sky)`라 그라데이션에서 깨진다 |
| 상단 바 숨기기, 장별 시계 끄기 | 꽉 채우는 장, 이야기 시각이 없는 장 |
| 발표자 노트 | 장마다 말할 거리 |
| 왼쪽 글·오른쪽 화면 레이아웃, 사람·AI 말풍선 | 두 사례 모두 썼다. show-me는 시작 테마(덱 소유)에 `.rail`/`.stage`를 둔다. 엔진으로 올릴지는 그 덱 재빌드 때 정한다 |

## 이름

사용자가 후보(lectern, deckhand, limelight) 대신 `show-me`를 직접 정했다. 위치는 `~/Documents/harness/show-me`.

## 기본값과 사용자 결정

| 항목 | 이번 기본값 | 사용자가 정할 것 |
| --- | --- | --- |
| 진입 | 자연어 자동 진입 | 명시 호출(`/show-me-mode`)로 바꿀지 |
| 시작 팔레트 | 흰 배경·검정 명도, 검정·회색 어두운 장, 녹색 `#00704a`·주황 `#ffb547` 강조. 2026-11-26 피드백(작업 폴더 메모리에도 있음)을 따른 기본값이며 덱마다 deck.css에서 바꾼다 | 다른 시작 팔레트 |
| 플레이어 | 공유용 Lightplay 영상을 가져옴 | 프로젝터 화질이 중요하면 마스터 |
| 글꼴 | Pretendard + JetBrains Mono를 로컬 복사 또는 내려받기 | 다른 글꼴 |
| 공개 | 2026-11-26 사용자 요청으로 `github.com/ynginkim/show-me`에 public으로 게시했다(main만, 커밋 작성자 ynginkim@gmail.com) | 릴리스 태그 발행 시점 |
| harness-family 등재 | 하지 않음 | README 표와 호환성 표에 넣을지 |

## 확인하지 못한 것

| 항목 | 상태 | 닫을 조건 |
| --- | --- | --- |
| 두 번째 사례(메이킹 강의 덱)를 새 엔진으로 다시 만들기 | unverified | 그 덱이 끝나면 내용을 show-me 형식으로 옮겨 원본과 장마다 비교하고, 위 "엔진 후보"를 scenes.js로 둘지 엔진으로 올릴지 정한다. 잠정 표시를 갱신한다 |
| 새 세션 라우팅(mode → create-deck 읽기, 원문 단계) | unverified | 사용자 승인 뒤 Claude Code 새 세션 1회, `.agents/skills/verify-show-me`의 Drive 절차로 실행하고 이 문서의 검증 기록에 적는다 |
| 실제 강의 한 편을 show-me로 처음부터 만들기 | unverified | 다음 강의에서 `create-deck`으로 만들고 제작노트의 막힌 단계를 absorb-feedback으로 반영한다 |
| 가로 플레이어·자동 재생의 현장 동작(소리 있는 자동 재생 정책) | unverified | 발표 컴퓨터의 Chrome에서 키로 넘겨 들어갔을 때 소리와 함께 재생되는지 사람이 확인한다 |
| Windows·Linux 촬영 | unverified | 그 환경에서 `preflight.py`와 `test_tools.py`를 실행한다(Chrome 경로와 한글 시트 글꼴) |
