#!/usr/bin/env bash
# Run the disclosure lab against a local MLX model: start the server, wait for it, run the
# trials, stop the server. Keeps the model's lifetime inside this one script so nothing is
# left holding memory afterwards.
#   cd <repo> && lab/local-run.sh [model-repo] [trials]
set -uo pipefail
MODEL=${1:-mlx-community/Qwen3-4B-Instruct-2507-4bit}
TRIALS=${2:-8}
PORT=8099
LOG=${TMPDIR:-/tmp}/smallprint-lab-mlx.log
PY=python

nice -n 5 "$PY" -m mlx_lm server --model "$MODEL" --port "$PORT" --host 127.0.0.1 \
  --log-level WARNING > "$LOG" 2>&1 &
SRV=$!
trap 'kill $SRV 2>/dev/null' EXIT
for _ in $(seq 1 60); do
  curl -s -m 3 -o /dev/null "http://127.0.0.1:$PORT/v1/models" && break
  kill -0 $SRV 2>/dev/null || { echo "server died:"; tail -20 "$LOG"; exit 1; }
  sleep 3
done
echo "model server up on $PORT ($MODEL)"

lab/run.py --base "http://127.0.0.1:$PORT/v1" --model "$MODEL" \
  --label "$(basename "$MODEL")" --trials "$TRIALS"
rc=$?
exit $rc
