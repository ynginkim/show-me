# show-me

> 말로 설명하기 전에 실물을 보여 주는 강의 자료를 만들고, 찍은 화면으로 판정한다.

강의·발표에서 브라우저로 넘기는 HTML 슬라이드 덱을 만들고 고치는 하네스입니다. 녹화 영상은 장(chapter)으로 나눠 슬라이드 안에서 틀고, 긴 문서 캡처는 줄이지 않고 스크롤하며, 실제 링크는 LIVE 버튼으로 엽니다. 구간별 시간 예산 타이머와 장면 애니메이션을 넣고, 끝나면 전 장을 1920×1080으로 찍어 오류·없는 파일·시간 예산을 검사합니다.

[Lightplay](https://github.com/ynginkim/lightplay)로 만든 영상 프로젝트가 있으면 그 납품 영상·포스터·자막과 장면 시각을 파일 계약대로 가져옵니다. Lightplay 설치는 필요 없고, 영상 도구 전체를 함께 설치하지 않습니다.

## 구성

<!-- skillset:summary:start -->
mode 1개, playbook 2개, skill 6개, principle 4개 (설치 단위 11개).

검사: `python3 scripts/check.py .`
<!-- skillset:summary:end -->

| 종류 | 이름 | 하는 일 |
| --- | --- | --- |
| mode | `show-me-mode` | 요청을 새 덱·수정으로 보내고, 결과물·완료·사람 판정을 정한다. 자연어로 진입한다 |
| playbook | `create-deck` | 새 강의 자료. 원자료에서 출발하든 Lightplay 영상에서 출발하든 같은 흐름 |
| playbook | `revise-deck` | 만든 덱 고치기. 수정 전 촬영본과 비교한다 |
| skill | `resolve-show-me-tools` | 엔진·템플릿·스크립트 경로(D), 환경 점검, 새 덱, 공유 계약 |
| skill | `plan-talk` | 청중·목표·구간 예산·장마다 보여 줄 실물 → `talk.md` |
| skill | `prepare-media` | 휴대폰 녹화·캡처 → 브라우저용 영상·JPEG, 출처 기록 |
| skill | `build-deck` | 슬라이드 본문·설정·테마·장면. 엔진 API와 부품 목록 |
| skill | `check-deck` | 전 장 촬영, 자동 검사, 시트, 수정 전후 비교 |
| skill | `link-lightplay` | Lightplay 영상 프로젝트 연결(없으면 건너뜀) |
| principle | `principle-audience-words` | 내부 이름 대신 청중의 말 |
| principle | `principle-show-the-real-thing` | 실물 먼저, 보이지 않는 과정만 도식, 공개 범위 |
| principle | `principle-content-before-engine` | 새 동작은 덱의 scenes.js에 먼저 |
| principle | `principle-judge-from-shots` | 찍은 화면과 비교로 판정, 현장 확인은 사람 |

## 덱 한 벌

```text
<프로젝트>/
  talk.md                 청중·구간 예산·장 목록
  slides/                 발표에 들고 가는 폴더(file://로 연다)
    index.html            슬라이드 본문과 설정 JSON. 덱의 정본(빌드 없음)
    deck.css  scenes.js   이 덱의 테마와 장면
    engine/               show-me 엔진 사본(고치지 않음)
    fonts/  media/        글꼴, 변환한 미디어와 media.json(출처)
  qa/deck/                촬영본, sheet.png, report.md
  제작노트.md
```

키: ←/→ 넘기기 · G 전체 보기 · F 전체 화면 · T 구간 타이머 · 1~9 탭/장 · P 재생 · Z 확대.

## 설치

GitHub 게시 전에는 로컬 경로로 프로젝트에 설치한다.

```bash
npx skills@1.7.4 add ~/Documents/harness/show-me -a claude-code -a codex
```

게시 뒤에는 `npx skills@1.7.4 add ynginkim/show-me -a claude-code -a codex`. 촬영 검사에는 Node 18 이상, 시스템 Chrome, playwright-core가 필요하다. 설치된 skill에서 한 번 `python3 <설치 위치>/resolve-show-me-tools/scripts/preflight.py --install`을 실행한다(npm, 약 14 MB, 브라우저는 내려받지 않음). 영상 변환에는 ffmpeg, 이미지·시트에는 Python Pillow·numpy가 필요하다. 글꼴(Pretendard, JetBrains Mono, SIL OFL)은 새 덱을 만들 때 로컬에서 복사하거나 내려받는다.

## 시작 프롬프트

- "다음 주 목요일 신입 직원 대상 20분 사내 강의 자료 만들어 줘. 녹화는 `sources/`에 있고, 현장에서만 보여 줄 거야."
- "이 Lightplay 영상 프로젝트(`projects/…`)로 강의 오프닝을 틀고 이어지는 슬라이드도 만들어 줘."
- "어제 만든 덱에서 2구간을 3분 줄이고, 6번 장의 캡처를 새 걸로 바꿔 줘."

## 검증 수준

- 구조: `python3 scripts/check.py .`, `python3 scripts/selftest.py`
- 도구: `python3 scripts/test_tools.py`(새 덱, 엔진 보존, 결함 주입 5종, Lightplay 가져오기와 원본 무변경)
- 엔진 회귀: 2026-11-25 강의 덱 v2(15장)를 새 엔진으로 다시 만들어 원본과 장마다 비교했다. 결과는 [회귀 기록](docs/regression-v2.md)
- 설치: 깨끗한 clone에서 install smoke
- 미확인: 새 세션의 라우팅 시험, 두 번째 사례(메이킹 강의 덱)를 새 엔진으로 다시 만들기, 발표 화면에서의 사람 확인. 자세한 표는 [DESIGN](DESIGN.md)의 "확인하지 못한 것"

구조·도구 검사 통과는 덱의 품질을 뜻하지 않는다. 발표 화면의 가독성, 리허설 시간, 소리는 사람이 확인한다.

## 더 읽기

[사용 가이드](docs/guide/README.md) · [설계](DESIGN.md) · [의존 그래프](docs/artifact-graph.md) · [명령 스냅샷](docs/command-snapshot.md) · [회귀 기록](docs/regression-v2.md)

이 하네스는 [harness-family](https://github.com/ynginkim/harness-family)의 세 basis(playbook·skill·principle)와 mode 구조를 따르며 [meta-harness](https://github.com/ynginkim/meta-harness)의 `design-skillset` 흐름으로 만들었다. 라이선스는 [MIT](LICENSE).
