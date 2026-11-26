---
name: prepare-media
description: "휴대폰 녹화·화면 캡처·이미지를 오프라인 브라우저가 바로 재생하는 영상과 JPEG로 바꾸고, 출처와 공개 범위를 media.json에 남기는 기술. 새 덱과 미디어 교체에 쓴다."
disable-model-invocation: true
---

# 미디어 준비

Read ../resolve-show-me-tools/SKILL.md

입력은 `talk.md`의 실물 목록, 원자료 경로, 덱 프로젝트다. 결과는 `slides/media/`의 변환본, `media.json` 항목, 변환하지 못한 자료와 이유다. 원자료는 읽기만 하고 옮기거나 지우지 않는다. 직접 불러도 이 제약은 같다.

## 변환

| 원자료 | 명령 | 이유 |
| --- | --- | --- |
| 휴대폰 녹화(HEVC, 60fps, 세로 1180×2556 등) | `python3 $D/prep_media.py video <원본> <프로젝트>/slides/media/rec1.mp4` | H.264 yuv420p·30fps·높이 1600 이하·AAC·faststart. 어느 브라우저든 `file://`에서 재생된다 |
| 가로 화면 녹화 | `… video <원본> <dst> --height 1080` | 1080p면 충분하다 |
| 앞뒤를 자를 녹화 | `… video <원본> <dst> --trim 3.5:42` | 필요한 구간만 남긴다. 장(chapter) 시각은 자른 뒤 기준 |
| 긴 웹페이지·문서 전체 캡처(2x, 세로 수만 px) | `… image <원본> <dst> --width 1600 --crop <x0>,<x1> --max-height 16000` | 읽을 열만 남기고 폭을 줄여 브라우저가 디코딩할 수 있게 한다 |
| 일반 캡처·사진 | `… image <원본> <dst> --width 1600` | |
| 여러 장의 화면 모음(갤러리) | `… image`를 장마다, 그리고 `… thumbs <원본 폴더> <프로젝트>/slides/media/<이름>_thumb` | 격자에는 썸네일, 확대 보기에는 원본 |
| 영상의 한 프레임(카드 썸네일·포스터) | `… poster <영상> <dst.jpg> --at 12.5` | 카드에는 `<video src="x.mp4#t=12.5" muted preload="metadata">`도 쓸 수 있다 |

이미 있는 출력은 건너뛴다. 다시 만들려면 `--force`. 끝나면 `python3 $D/prep_media.py list <프로젝트>/slides/media`로 목록과 합계를 확인한다.

## 지킬 것

- 공개 범위가 걸린 자료(고객·동료·가족이 보이는 화면, 사내 문서)는 `--onsite`로 기록한다. 그 자료가 든 덱은 공개 게시하지 않고, 예제나 템플릿으로 재사용하지 않는다. 판단은 **principle-show-the-real-thing**의 Stop을 따른다. Read `../principle-show-the-real-thing/SKILL.md`.
- 출처를 알 수 없는 파일을 `slides/media/`에 손으로 넣지 않는다. 손으로 넣어야 하면 `prep_media.py image|video`를 거쳐 기록을 남긴다.
- 녹화 하나가 길면(수 분) 변환을 백그라운드로 돌리고 끝나면 길이·크기를 확인한다.
- 녹화의 장(chapter) 후보 시각을 영상을 보며 정해 결과에 적는다(build-deck이 `data-chap`에 쓴다). 확인하지 못한 시각은 추정이라고 표시한다.

## 돌려주는 것

변환한 파일 목록(크기·길이·해상도), 현장 전용 목록, 장 후보 시각, 실패한 원자료와 원인.

변환 기본값(높이 1600, 30fps, CRF 22, 캡처 폭 1600)은 2026-11-25 강의 덱의 `prep_media.py`에서 왔다. 두 번째 사례 확인 전(잠정).
