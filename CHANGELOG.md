# 변경 기록

## Unreleased

- README를 하네스 패밀리 형식(배너, 이름의 유래, 사용법, Lightplay와 함께, 출처, 기여와 버전)으로 다시 썼다. 배너는 Codex 내장 이미지 생성(`tools/art/`)으로 만들었다.
- 커뮤니티·릴리스 문서를 더했다: CONTRIBUTING, CODE_OF_CONDUCT, SECURITY, SUPPORT, RELEASING, THIRD_PARTY.
- 엔진 0.2.0. 두 번째 사례(2026-11-26 메이킹 강의 덱)가 실제로 쓴 기능을 올렸다.
  - 올린 기능: 차례로 나타나기(`data-frag`, 같은 값은 함께), 소리 버튼(`data-audio`), B 화면 끄기, Shift+T 타이머 0으로와 전체 경과, 그라데이션 하늘의 단색(`data-sky-solid`), 장별 상단 바·시계 숨기기(`data-notop`, `data-clock="off"`).
  - 촬영과 API: 촬영은 차례로 나타나는 요소를 모두 펼쳐 찍고, `check_deck.py --frags`는 펼치기 전 상태도 찍는다. API에 `ShowMe.revealAll`·`stopAudio`·`resetTimer`, `showme:frag` 이벤트를 더했다.
  - 색: `--ink2`·`--ink3`·`--line`을 `--ink-l`·`--ink-d`에서 만들고, `--letterbox`·`--overlay` 토큰을 더했다. 기본값은 0.1.0과 같고, 시작 테마는 무채색으로 둔다.
  - v2 회귀는 원본과 같다(흔들림 영역 제외). 샘플 덱은 보조 글자색만 최대 채널 차이 15로 바뀌었다.
  - 두 번째 사례(메이킹 강의 덱)를 맥락 없는 하위 에이전트가 이 엔진으로 옮겼다. 정지 화면 25장과 크게 보기가 원본과 픽셀 동일했다. 그 시험에서 찾은 `check_deck.py`의 `data-audio` 파일 검사 누락을 고쳤고, `[data-zoom]` 커서와 전체 보기 글자색 토큰, `--frags` 명령 문서를 더했다.
- 브리프에서 의도와 계획을 나눴다. 의도(청중, 전할 것, 강조할 것·뺄 것, 공개 범위)만 확인하고, 구성·장 목록은 승인받지 않고 정한다. 사용자가 계획을 먼저 보자고 할 때만 보이고 기다린다.

## 0.1.0-dev (2026-11-26)

- 처음 만듦. meta-harness `design-skillset` 흐름으로 설계했다.
- mode 1(`show-me-mode`), playbook 2(`create-deck`, `revise-deck`), skill 6, principle 4.
- 공통 엔진 0.1.0: 2026-11-25 강의 덱 v2의 스크립트에서 넘김·타이머·탭·스크롤·확대·플레이어·전체 보기·키보드를 떼어 내고, 그 강의의 장면은 덱 쪽 장면 훅으로 옮겼다. 엔진이 만드는 요소는 `sm-` 접두사. 가로 영상 플레이어와 진입 시 자동 재생을 더했다(잠정).
- 도구: `preflight.py`, `new_deck.py`, `prep_media.py`, `import_lightplay.py`, `check_deck.py`, `shoot.mjs`, `compare_shots.py`.
- 검증: v2 15장 회귀, 도구 테스트 14건, 구조 검사, 설치 smoke.
