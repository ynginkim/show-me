# Lightplay → show-me 파일 계약

show-me가 Lightplay 영상 프로젝트에서 읽는 파일과 필드다. Lightplay 쪽 정본은 Lightplay의 `resolve-showreel-tools/references/contract.md`("프로젝트 파일")와 `finish.py`다. show-me는 그 파일을 읽기만 하고 Lightplay 프로젝트에 아무것도 쓰지 않는다. Lightplay 설치는 필요 없다.

확인 기준: Lightplay 저장소 `42cf8e156645b22d31c0cea031dc46981ec636ab`(2026-11-26)의 `finish.py`(`<name>.mp4`, `<name>_공유용.mp4`, `<name>_포스터.jpg`, `<name>.srt`)와 2026-11-25 강의 영상 프로젝트의 실제 `project.json`, `timeline.json`, `script.json`. 특정 커밋을 실행 조건으로 요구하지 않는다. 이름이 바뀌면 `import_lightplay.py`가 exit 2로 멈추고 찾은 후보를 보여 준다.

| Lightplay 파일 | 필드 | show-me에서 쓰는 곳 | 없거나 다를 때 |
| --- | --- | --- | --- |
| `project.json` | `width`, `height`, `fps`, `duration` | 플레이어 모양(16:9면 `data-shape="wide"`), 길이 확인 | 계약 아님 → exit 2 |
| `timeline.json` | `duration`, `scenes[].id`, `scenes[].start`, `scenes[].end` | `<slug>.chapters.json` → `data-chap` 시각 | 계약 아님 → exit 2. `project.json`과 길이가 0.5초 넘게 다르면 경고 |
| `out/<name>.mp4` | 마스터(H.264, 1920×1080, AAC) | `--use master` | 납품 전 → 후보가 없으면 exit 2 |
| `out/<name>_공유용.mp4` | 공유용(CRF 23, 최대 8 Mbps) | 기본 가져오기 | 없으면 마스터를 쓰고 경고 |
| `out/<name>_포스터.jpg` | 포스터 프레임 | `<slug>_poster.jpg`(카드 썸네일, 영상 장 배경) | 없으면 건너뛴다 |
| `out/<name>.srt` | 나레이션 자막 | `<slug>.srt`(자막 표시나 원문 보기에 쓸 수 있다) | 없으면 건너뛴다 |
| `qa/qa_report.md` | 자동 납품 검수 | 납품된 영상인지 판단 | 없으면 경고 |
| `storyboard.md`, `concept.md`, `script.json` | 장면 메시지, 시각 언어, 나레이션 | "영상이 이미 말한 것" 요약(에이전트가 읽음) | 없으면 장면 id만 쓴다 |

`out/video.mp4`(무음 렌더), `out/draft*.mp4`(초안)는 납품본이 아니므로 가져오지 않는다.

가져온 파일은 `slides/media/media.json`에 `from: "lightplay"`, `lightplay_project`, `source`, `source_sha256`과 함께 기록한다. 다시 렌더 여부는 이 해시로 판단한다.
