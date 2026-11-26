# 변경 기록

## 0.1.0-dev (2026-11-26)

- 처음 만듦. meta-harness `design-skillset` 흐름으로 설계했다.
- mode 1(`show-me-mode`), playbook 2(`create-deck`, `revise-deck`), skill 6, principle 4.
- 공통 엔진 0.1.0: 2026-11-25 강의 덱 v2의 스크립트에서 넘김·타이머·탭·스크롤·확대·플레이어·전체 보기·키보드를 떼어 내고, 그 강의의 장면은 덱 쪽 장면 훅으로 옮겼다. 엔진이 만드는 요소는 `sm-` 접두사. 가로 영상 플레이어와 진입 시 자동 재생을 더했다(잠정).
- 도구: `preflight.py`, `new_deck.py`, `prep_media.py`, `import_lightplay.py`, `check_deck.py`, `shoot.mjs`, `compare_shots.py`.
- 검증: v2 15장 회귀, 도구 테스트 14건, 구조 검사, 설치 smoke.
