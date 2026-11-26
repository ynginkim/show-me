---
name: check-deck
description: "덱의 전 장과 상호작용 화면을 1920×1080으로 찍고, 오류·없는 파일·깨진 미디어·시간 예산·화면 밖 요소·잘린 글자를 검사해 시트와 보고서, 수정 전후 비교를 돌려주는 기술."
disable-model-invocation: true
---

# 덱 검사

Read ../resolve-show-me-tools/SKILL.md

입력은 덱 프로젝트(또는 `slides/` 폴더), 선택으로 기준 촬영본 폴더와 상호작용 목록이다. 결과는 `qa/deck/`의 촬영본, `sheet.png`, `sheet_interactions.png`, `report.md`·`report.json`, (기준이 있으면) `compare/`와, 에이전트가 직접 본 장과 발견이다. 고치는 일은 build-deck이, 몇 번 반복할지는 playbook이 정한다. 덱 파일을 고치지 않는다.

Read `../principle-judge-from-shots/SKILL.md`. **principle-judge-from-shots**를 적용한다.

## 실행

```bash
python3 $D/check_deck.py <프로젝트>                                   # 정적 검사 + 촬영 + 시트 + 보고서
python3 $D/check_deck.py <프로젝트> --baseline <기준 폴더>/shots        # + 수정 전후 비교
python3 $D/check_deck.py <프로젝트> --actions <actions.json>          # + 정해 둔 상호작용 촬영
python3 $D/check_deck.py <프로젝트> --frags                           # + 차례로 나타나는 장의 펼치기 전 상태(sNN_a.png)
python3 $D/check_deck.py <프로젝트> --no-shoot                        # 촬영 도구가 없을 때 정적 검사만
```

15장 덱의 촬영·검사는 이 저장소의 측정에서 약 1분이었다. 일부 장만 찍지 않고 전 장을 찍는다(`--only`는 원인을 좁힐 때만).

자동 상호작용은 전체 보기, 탭이 둘 이상인 장의 2번 탭, 플레이어가 있는 장의 2번 장(chapter)이다. 그 밖에 시연할 동작(특정 버튼, 확대 보기, 접힌 원문)은 actions 파일로 정한다.

```json
[{"name": "i06_lightbox", "slide": 6, "steps": [{"click": "#keypick button:nth-child(2)"}, {"wait": 700}]},
 {"name": "i09_chap3", "slide": 9, "steps": [{"press": "3"}, {"wait": 1200}, {"press": "p"}, {"wait": 300}]}]
```

촬영은 끝나지 않는 애니메이션을 0초에, 끝나는 애니메이션은 끝 상태로, 재생 중인 영상은 1초 지점에 멈춰 같은 덱이면 같은 그림이 나오게 한다(`--no-freeze`로 끈다).

## 결과 읽기

1. **exit 1**: `report.md`의 "실패"를 고친다. 페이지·콘솔 오류는 `shots/shoot.json`의 `errors[].at`(어느 장·상호작용)과 메시지로 찾는다.
2. **경고**: 처리하거나 이유를 제작노트에 남긴다. `file://` 링크는 발표 컴퓨터에서만 열린다. 엔진 버전 차이는 사용자가 갱신을 요청할 때만 고친다.
3. **슬라이드 표**: 화면 밖 요소와 잘린 글자가 있는 장을 원본 크기로 연다.
4. **시트**: `sheet.png`, `sheet_interactions.png`를 Read로 연다. 글이 많은 장, 표, 작은 글자가 있는 장은 `shots/sNN.png`를 따로 연다. 볼 것: 1920×1080에서 20px 미만 글자, 한 장에 메시지 둘 이상, 겹침, 영상 첫 프레임이 검은 화면, 청중이 모를 말, 대비가 낮은 글자.
5. **비교**(`--baseline`): `compare/compare.md`에서 바뀐 장을 확인하고, 바뀌지 않아야 할 장이 바뀌었으면 `compare/diff_*.png`를 연다. 지연 로딩 썸네일과 재생 중 영상 프레임은 원본끼리도 흔들린다. 차이 그림이 그 영역 안에만 있으면 흔들림으로 적는다.

## 돌려주는 것

명령과 exit code, 실패·경고 목록, 열어 본 장 목록과 발견, 비교에서 바뀐 장과 판단, 사람 확인 항목(발표 화면 가독성, 리허설 시간, 소리, 말투). 자동 검사 통과와 사람 판정을 하나의 통과로 쓰지 않는다.
