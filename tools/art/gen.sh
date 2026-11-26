#!/usr/bin/env bash
# README 그림을 Codex의 내장 imagegen skill로 만든다(API 키가 필요 없다. ChatGPT 플랜 사용량이 든다).
# blackboard의 tools/art/gen.sh와 같은 방식이다.
#
#   tools/art/gen.sh            # 그림이 아직 없는 prompts/ 전부
#   tools/art/gen.sh banner     # 이것만
#
# prompts/<name>.txt 하나가 tools/art/out/<name>.png(git에 올리지 않음)가 된다. README용 자르기는 crop.sh가 한다.
# 이미 있는 그림은 건너뛴다. 하나에 1~2분쯤 걸린다. 로그는 tools/art/out/.logs/에 남는다.
set -u
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PROMPTS="$ROOT/tools/art/prompts"; OUT="$ROOT/tools/art/out"; LOGS="$OUT/.logs"
mkdir -p "$OUT" "$LOGS"
TAIL="$(cat "$PROMPTS/_style.txt")"
names=("$@"); [ ${#names[@]} -eq 0 ] && names=($(ls "$PROMPTS" | grep -v '^_' | sed 's/\.txt$//'))
for name in "${names[@]}"; do
  start=$(date +%s)
  [ -s "$OUT/$name.png" ] && { echo "SKIP $name"; continue; }
  codex exec --sandbox workspace-write --skip-git-repo-check --cd "$OUT" -o "$LOGS/$name.md" \
    "Use your imagegen skill (built-in image_gen tool) to generate exactly one image.

$(cat "$PROMPTS/$name.txt")

$TAIL

Save the final image as ./$name.png (PNG) in the current directory, then reply with the file path only." \
    > "$LOGS/$name.out" 2>&1 < /dev/null
  if [ -s "$OUT/$name.png" ]; then echo "OK   $name $(( $(date +%s) - start ))s"; else echo "FAIL $name (see $LOGS/$name.out)"; fi
done
