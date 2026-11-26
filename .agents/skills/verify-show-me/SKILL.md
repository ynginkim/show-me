---
name: verify-show-me
description: "show-me 저장소의 구조·설치·도구·엔진 회귀·실제 경로를 검증하는 내부 skill이다. 변경 뒤 최소 증거를 고를 때 쓴다."
disable-model-invocation: true
metadata:
  internal: true
---

# show-me 검증

Status: draft. 구조·도구·회귀·설치 경로는 2026-11-26에 실행했고, 새 세션의 라우팅 시험은 아직 실행하지 않았다(아래 Drive의 닫을 조건). 저장소 루트에서 쓴다. 배포 `skills/`에 포함하지 않는다.

| 변경 | 최소 검사 |
| --- | --- |
| skill 문서·DESIGN·README | `python3 scripts/check.py .` |
| 검사 키트 사본 | 위 검사와 `python3 scripts/selftest.py` |
| 스크립트(`skills/resolve-show-me-tools/scripts/`) | `python3 scripts/test_tools.py`(오류 주입 포함). 촬영 도구가 없으면 `--no-browser`와 그 사실 |
| 엔진(`assets/engine/`) | `test_tools.py`, 샘플 덱 `check_deck.py`, 로컬 v2 회귀(`.work/regress-v2/run.sh`, 있을 때만). 엔진을 바꾸면 `examples/sample-deck/slides/engine/`에도 복사한다(copies 검사) |
| 설치 자원·참조 | 커밋 뒤 깨끗한 clone에서 `python3 scripts/install_smoke.py <clone> --dest <새 빈 폴더>` |
| mode·playbook 라우팅 | 새 Claude Code 세션 경로 시험(아래) |

## Launch

`python3 scripts/check.py .` → `python3 scripts/selftest.py` → `python3 scripts/test_tools.py`. 촬영에는 `skills/resolve-show-me-tools/scripts/node_modules`의 playwright-core(`preflight.py --install`)나 `SHOWME_PLAYWRIGHT`가 필요하다. 설치 smoke는 작업 트리에 `node_modules`가 있으므로 커밋한 뒤 `git clone`한 사본에서 돌린다.

## Doctor

`python3 skills/resolve-show-me-tools/scripts/preflight.py`의 `can`과 `todo`, git status, Node·Python·ffmpeg·Chrome 버전을 읽는다. v2 원본(`video-creator2/projects/2026-11-25-how-i-use-agents-v2/`)과 Lightplay 프로젝트는 읽기만 한다.

## Drive

- **도구:** `test_tools.py`가 임시 폴더에서 새 덱, 엔진 보존·갱신, 정적 결함 4종, 장면 예외, 가짜 Lightplay 가져오기와 원본 무변경을 시험한다.
- **엔진 회귀:** `.work/regress-v2/run.sh <출력 폴더>`. 원본 v2를 두 번, 새 엔진 이식본을 한 번 찍고 비교한다. 판정: 이식본과 원본의 차이가 원본끼리의 차이(지연 로딩 썸네일, 재생 중 영상 프레임) 범위 안이고 오류 0. 이 폴더는 고객 화면·개인 자료를 다루므로 커밋하지 않는다. 출력은 scratchpad나 저장소 밖 임시 폴더에 둔다.
- **라우팅(미실행):** 새 세션에 설치본만 두고 "다음 주 ○○ 대상 20분 강의 자료를 만들어 줘. 녹화는 sources/에 있어. 단계만 옮기고 멈춰"처럼 자연스러운 요청을 준다. 기대 playbook(`create-deck`)을 실제로 Read하는지, 번호 단계 원문을 옮기는지, 조사·파일 생성을 시작하지 않는지 판정한다. 기대값은 프롬프트에 넣지 않는다. headless 세션은 비용이 들므로 실행 전에 횟수(Claude 1~2회)와 모델을 사용자에게 알리고 승인받는다. 닫을 조건: 승인 뒤 1회 실행하고 결과를 DESIGN의 검증 기록에 적는다.

## Evidence

커밋되는 요약은 DESIGN의 "검증 기록"과 `docs/regression-v2.md`에 둔다. 회귀 촬영본과 차이 그림은 고객 화면을 포함하므로 저장소에 넣지 않고 경로와 수치만 적는다. exit 0만으로 화면 품질 PASS를 쓰지 않는다.

## Cleanup

임시 설치와 촬영 출력은 위치를 기록해 둔다. 사용자가 삭제를 요청하면 정확한 경로를 확인한 뒤 지운다. v2 원본, Lightplay, meta-harness 파일에 diff가 생기면 먼저 다른 세션의 변경인지 구분하고 되돌리지 않는다.
