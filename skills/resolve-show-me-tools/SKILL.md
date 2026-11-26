---
name: resolve-show-me-tools
description: "show-me의 엔진·템플릿·스크립트 경로(D)를 확인하고, 환경 점검·새 덱 만들기·엔진 갱신 명령과 공유 파일 계약을 제공하는 도메인 adapter."
disable-model-invocation: true
---

# show-me 도구 경로와 공유 계약

입력은 작업 폴더와(있으면) 덱 프로젝트 폴더다. 결과는 `D`의 실제 절대 경로, 환경 점검 결과(`can`, `todo`), 만든 덱 경로 또는 엔진 갱신 결과다. 다른 leaf는 제목 바로 아래에서 이 파일을 읽고 여기서 정한 경로로 명령을 실행한다. 이 skill은 원자료를 바꾸거나 지우지 않는다.

이 폴더가 실행 자원을 한 벌 소유한다. 스크립트는 `scripts/`, 엔진과 새 덱 템플릿은 `assets/engine/`, `assets/template/`이다. `new_deck.py`·`check_deck.py`가 `scripts/../assets`에서 엔진을 찾으므로 두 폴더의 상대 배치를 바꾸지 않는다. 라이선스는 저장소의 MIT다.

## D

- **D**: 이 SKILL.md를 연 실제 경로의 폴더 안 `scripts`의 절대 경로다. `test -f "$D/check_deck.py"`로 확인한다.
- 셸 변수는 명령 사이에 남지 않는다. 명령마다 확인한 절대 경로를 그대로 쓰거나 같은 줄 앞에 `D=…`를 붙인다. leaf 문서의 `$D`는 이 값이다.
- Lightplay의 `S`, op55의 `O`와 섞지 않는다. show-me는 그 도구를 실행하지 않는다.

## 환경 점검

```bash
python3 $D/preflight.py
```

결과의 `can`이 할 수 있는 일, `todo`가 없는 도구와 설치 안내다.

| 도구 | 쓰는 곳 | 없을 때 |
| --- | --- | --- |
| Node 18 이상, 시스템 Chrome, playwright-core | `shoot.mjs`, `check_deck.py`(촬영) | 촬영 없이 `check_deck.py --no-shoot`만 가능. playwright-core는 사용자 승인 뒤 `python3 $D/preflight.py --install`(npm, 약 14 MB, 브라우저 내려받기 없음, `$D/node_modules`에 설치). 이미 설치된 사본이 있으면 `SHOWME_PLAYWRIGHT=<node_modules가 있는 폴더>`로 쓴다 |
| ffmpeg, ffprobe | `prep_media.py video·poster`, 영상 규격 검사 | 영상 변환을 못 한다. 설치 안내(macOS `brew install ffmpeg`) |
| Python Pillow, numpy | 이미지 변환, 시트, 비교 | `python3 -m pip install pillow numpy` |
| Lightplay(선택) | 없음. `lightplay_scripts`는 찾은 경로를 알려 주기만 한다 | Lightplay 프로젝트 파일은 설치 없이 읽는다 |

## 새 덱

```bash
python3 $D/new_deck.py <프로젝트> --title "제목" --kicker "20분 강의 · …" [--no-fonts]
```

`<프로젝트>/slides/`(index.html, deck.css, scenes.js, engine/, fonts/, media/)와 `<프로젝트>/qa/deck/`을 만든다. 다시 실행해도 index.html·deck.css·scenes.js를 덮어쓰지 않는다. 글꼴(Pretendard, JetBrains Mono, SIL OFL)은 로컬에 있으면 복사하고 없으면 jsdelivr에서 내려받는다(약 2.3 MB). 확보한 글꼴만 `fonts/fonts.css`에 적어 없는 파일이 요청 실패로 남지 않게 한다. `--no-fonts`는 시스템 글꼴을 쓴다.

## 엔진 갱신

덱은 만들 때의 엔진 사본(`slides/engine/`)으로 동작한다. 설치본이 새 버전이어도 사용자가 요청하지 않으면 바꾸지 않는다. 요청하면 다음 순서를 지킨다.

1. 기준 촬영: `python3 $D/check_deck.py <프로젝트> --out <프로젝트>/qa/deck/before-engine-<시각>`.
2. 갱신: `python3 $D/new_deck.py <프로젝트> --update-engine`. 이전 엔진은 `slides/engine/.prev-<버전>-<시각>/`에 남는다.
3. 비교: `python3 $D/check_deck.py <프로젝트> --baseline <기준 폴더>/shots`. 설명되지 않는 차이가 있으면 `.prev-…`의 파일을 `slides/engine/`에 되돌리고 원인을 보고한다.

## 명령

| 명령 | 하는 일 | 쓰는 leaf |
| --- | --- | --- |
| `python3 $D/preflight.py [--install]` | 환경 점검, 승인 뒤 playwright-core 설치 | 모든 playbook 1단계 |
| `python3 $D/new_deck.py <프로젝트> [--title] [--no-fonts] [--update-engine]` | 새 덱, 엔진 갱신 | create-deck, revise-deck |
| `python3 $D/prep_media.py video\|image\|thumbs\|poster\|list …` | 원자료 변환과 출처 기록 | prepare-media |
| `python3 $D/import_lightplay.py <Lightplay 프로젝트> <덱 프로젝트> [--dry-run]` | Lightplay 납품 영상·포스터·자막·장면 시각 가져오기 | link-lightplay |
| `python3 $D/check_deck.py <프로젝트> [--baseline <shots>] [--actions <json>] [--only 3,5] [--no-shoot]` | 정적 검사, 촬영, 시트, 비교, 보고서 | check-deck |
| `node $D/shoot.mjs --deck <index.html> --out <폴더>` | 촬영만(check_deck이 부른다) | check-deck |
| `python3 $D/compare_shots.py <기준> <대상> --out <폴더>` | 촬영본 비교만(check_deck이 부른다) | check-deck |

## 자료 위치

| 이름 | 경로 |
| --- | --- |
| `contract.md` | `references/contract.md`(이 폴더). 덱 프로젝트 파일, 설정 JSON, 슬라이드 속성, media.json, 검사 결과 |
| `components.md` | `../build-deck/references/components.md`. 엔진 API와 부품 |
| `talk.md` 형식 | `../plan-talk/references/talk-template.md` |
| Lightplay 파일 계약 | `../link-lightplay/references/lightplay-contract.md` |
