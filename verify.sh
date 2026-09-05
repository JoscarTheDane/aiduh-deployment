#!/usr/bin/env bash
# Post-restart verification for the llama-server systemd service.
# Wait ~15-30s after restart — a ~18GB Q4 model takes a while to
# load into VRAM. "Connection refused" early on is normal.

set -u

echo "=== 1. Service status ==="
systemctl status llama-server.service --no-pager | head -15

echo
echo "=== 2. Health check (expected: {\"status\":\"ok\"}) ==="
curl -s http://localhost:8080/health || echo "not up yet — wait 10s and retry"

echo
echo "=== 3. Model registered? ==="
curl -s http://localhost:8080/v1/models | python3 -c "import sys,json; d=json.load(sys.stdin); [print(m['id']) for m in d['data']]" 2>/dev/null || echo "model list unavailable"

echo
echo "=== 4. Port check ==="
ss -ltnp | grep :8080 && echo "port 8080 listening" || echo "port 8080 NOT listening"
