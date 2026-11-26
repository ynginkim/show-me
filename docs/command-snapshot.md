# 명령 스냅샷

skill 문서가 그대로 실행하라고 적은 명령과, 2026-11-26 이 저장소에서 관찰한 각 스크립트의 `--help` 출력이다(macOS, Python 3.15, Node 22). `skillset.json`의 `command_snapshots`가 문서와 이 파일의 문자열 일치를 검사한다. 명령의 의미·실행 가능성은 `scripts/test_tools.py`와 회귀 기록이 확인한다.

## 문서에 적은 명령

```bash
python3 $D/preflight.py
python3 $D/new_deck.py <프로젝트> --title "제목" --kicker "20분 강의 · …" [--no-fonts]
python3 $D/new_deck.py <프로젝트> --update-engine
python3 $D/import_lightplay.py <Lightplay 프로젝트> <덱 프로젝트> --dry-run
python3 $D/check_deck.py <프로젝트> --baseline <기준 폴더>/shots
python3 $D/check_deck.py <프로젝트> --no-shoot
python3 $D/prep_media.py list <프로젝트>/slides/media
```

## preflight.py

```text
usage: preflight.py [-h] [--install]

show-me 환경 점검. JSON(caps, can, todo)을 출력한다. 아무것도 설치하지 않는다(--install 제외).

options:
  -h, --help  show this help message and exit
  --install   이 폴더에서 npm install(playwright-core, 네트워크 약 14 MB, 브라우저 내려받기 없음)
```

## new_deck.py

```text
usage: new_deck.py [-h] [--title TITLE] [--kicker KICKER] [--no-fonts]
                   [--update-engine]
                   project

positional arguments:
  project

options:
  -h, --help       show this help message and exit
  --title TITLE
  --kicker KICKER
  --no-fonts
  --update-engine
```

## import_lightplay.py

```text
usage: import_lightplay.py [-h] [--name NAME] [--use {share,master}]
                           [--slug SLUG] [--onsite] [--dry-run]
                           lightplay deck

positional arguments:
  lightplay
  deck

options:
  -h, --help            show this help message and exit
  --name NAME
  --use {share,master}
  --slug SLUG
  --onsite
  --dry-run
```

## check_deck.py

```text
usage: check_deck.py [-h] [--out OUT] [--pw PW] [--baseline BASELINE]
                     [--actions ACTIONS] [--only ONLY] [--no-shoot]
                     [--no-auto]
                     target

positional arguments:
  target

options:
  -h, --help           show this help message and exit
  --out OUT
  --pw PW
  --baseline BASELINE
  --actions ACTIONS
  --only ONLY
  --no-shoot
  --no-auto
```

## compare_shots.py

```text
usage: compare_shots.py [-h] --out OUT [--tol TOL] [--map [MAP ...]]
                        before after

positional arguments:
  before
  after

options:
  -h, --help       show this help message and exit
  --out OUT
  --tol TOL
  --map [MAP ...]  before.png=after.png pairs when names differ
```

## prep_media.py

```text
usage: prep_media.py [-h] {video,image,thumbs,poster,list} ...

positional arguments:
  {video,image,thumbs,poster,list}

options:
  -h, --help            show this help message and exit
```

## shoot.mjs

```text
usage: node shoot.mjs --deck <slides/index.html> --out <dir> [--pw <dir>] [--actions <json>]
```
