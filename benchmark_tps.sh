#!/usr/bin/env bash
# Quick tokens-per-second benchmark against the local llama-server.
# Run ON the server host to eliminate network overhead.
#
# Usage:
#   export LLM_MODEL="name-from-/v1/models"          # e.g. Qwen3.8-27B-UD-Q4_K_XL.gguf
#   export LLM_API_KEY="***"   # optional — llama-server usually has no auth
#   ./benchmark_tps.sh

set -u
MODEL="${LLM_MODEL:?set LLM_MODEL to the model id from /v1/models}"
KEY="${LLM_API_KEY}"
AUTH=()
[ -n "$KEY" ] && AUTH=(-H "Authorization: Bearer $KEY")

for i in 1 2 3; do
  START=$(date +%s%N)
  RESPONSE=$(curl -s http://localhost:8080/v1/chat/completions \
    "${AUTH[@]}" \
    -H "Content-Type: application/json" \
    -d '{
      "model": "'"${MODEL}"'",
      "messages": [{"role":"user","content":"List 10 items one per line Number: [short description]"}],
      "max_tokens": 64,
      "temperature": 0.7
    }')
  END=$(date +%s%N)
  TOKENS=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['usage']['completion_tokens'])")
  DUR_NS=$((END - START))
  DUR_S=$(echo "scale=4;$DUR_NS/1000000000" | bc)
  TPS=$(echo "scale=2;$TOKENS/$DUR_S" | bc)
  echo "Run $i: $TOKENS tokens in ${DUR_S}s = $TPS TPS"
done
