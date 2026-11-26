---
name: link-lightplay
description: "Lightplay로 만든 영상 프로젝트의 납품 영상·포스터·자막과 장면 시각을 파일 계약대로 읽어 덱으로 가져오는 기술. Lightplay 프로젝트가 없으면 건너뛴다. 영상 에셋으로 슬라이드를 만들 때와 영상을 다시 렌더한 뒤에 쓴다."
disable-model-invocation: true
---

# Lightplay 영상 프로젝트 연결

Read ../resolve-show-me-tools/SKILL.md

입력은 Lightplay 프로젝트 경로와 덱 프로젝트다. 결과는 영상이 이미 말한 것의 요약, `slides/media/`로 가져온 파일과 `media.json` 출처, 장(chapter) 시각, 경고다. Lightplay 프로젝트는 읽기만 한다. Lightplay의 mode(showreel-mode)를 이 흐름 안에서 부르지 않는다. 영상 자체를 고쳐야 하면 사용자에게 Lightplay로 따로 고치도록 안내하고, 다시 렌더된 뒤 이 skill로 다시 가져온다.

파일 계약은 `references/lightplay-contract.md`에 있다. 읽기 전에 그 파일을 Read로 연다.

## 언제 건너뛰나

자료 위치에 Lightplay 프로젝트(`project.json`, `timeline.json`, `out/`이 함께 있는 폴더)가 없으면 이 skill은 할 일이 없다. "없음"을 돌려주고 끝낸다. Lightplay 설치 여부는 상관없다. 파일만 읽으므로 설치 없이 동작하고, `preflight.py`의 `lightplay_scripts`는 참고로만 본다.

## 영상이 이미 말한 것

plan-talk에 넘길 요약을 만든다. `concept.md`(있으면), `storyboard.md`의 장면별 메시지, `script.json`의 나레이션 줄, `timeline.json`의 `scenes[{id, start, end}]`를 읽는다. 결과는 장면마다 `시작 초 · 장면 id · 한 줄 메시지`와 영상 전체의 한 문장, 쓰인 색·시간대 같은 시각 언어 메모다. 덱은 이것을 되풀이하지 않고, 영상이 짧게 지나간 실물을 자세히 보여 주는 쪽을 맡는다.

## 가져오기

```bash
python3 $D/import_lightplay.py <Lightplay 프로젝트> <덱 프로젝트> --dry-run   # 무엇을 가져올지 먼저 본다
python3 $D/import_lightplay.py <Lightplay 프로젝트> <덱 프로젝트> [--name <납품 이름>] [--use share|master] [--slug opening] [--onsite]
```

- 기본은 공유용 영상(`_공유용.mp4`, 마스터의 약 1/3 크기)이다. 프로젝터 화질이 걱정되면 `--use master`.
- 납품 이름 후보가 둘 이상이면 exit 2와 후보 목록이 나온다. 사용자에게 고르게 하지 말고 `제작노트.md`·`qa/qa_report.md`가 가리키는 최종본을 고른다. 판단할 수 없을 때만 묻는다.
- `qa/qa_report.md`가 없다는 경고는 납품 검수 전 영상일 수 있다는 뜻이다. 보고에 적는다.
- `<slug>.chapters.json`의 장면 id를 storyboard의 장면 이름으로 바꿔 플레이어의 `data-chap`에 쓴다. 장면 수가 많으면(10개 이상) 이야기 단위로 묶는다.
- 영상이 공개 범위가 걸린 실물을 담고 있으면 `--onsite`.

## 다시 렌더된 영상

`media.json`의 `source_sha256`과 Lightplay `out/`의 현재 파일 해시를 비교한다. 같으면 할 일이 없다. 다르면 다시 가져오고, 길이와 장면 시각이 바뀌었으면 `data-chap`과 그 영상을 쓰는 장을 다시 확인한다.

## 돌려주는 것

영상 요약(장면별 한 줄), 가져온 파일과 원본 해시, 장 시각, 경고(검수 보고서 없음, 길이 불일치), 건너뛰었으면 그 이유.

계약의 파일 이름은 2026-11-25 강의 영상(Lightplay finish.py 산출물)에서 확인했다. 두 번째 사례 확인 전(잠정).
