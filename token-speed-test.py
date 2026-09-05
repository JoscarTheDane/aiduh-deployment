#!/usr/bin/env python3
"""
Local TPS benchmark for llama.cpp (Qwen3.6-35B-A3B-UD-Q4_K_XL)
Run on the server itself to eliminate Tailscale/network overhead.

Usage: python3 token-speed-test.py
"""

import json
import time
import urllib.request
import sys

BASE_URL = "http://127.0.0.1:8080/v1/chat/completions"
MODEL = "Qwen3.6-35B-A3B-UD-Q4_K_XL.gguf"
PROMPT = "Count from 1 to 50. Write a detailed analysis of each number's significance in military strategy."
TOKEN_LENGTHS=*** 256, 512, 1024, 2048]

def benchmark(max_tokens):
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": PROMPT}],
        "temperature": 0.7,
        "max_tokens": max_tokens,
        "stream": True,
        "chat_template_kwargs": {"preserve_thinking": False}
    }
    data = json.dumps(payload).encode()
    req = urllib.request.Request(BASE_URL, data=data, headers={"Content-Type": "application/json"}, method="POST")

    t0 = time.time()
    ttft = None
    times = []

    with urllib.request.urlopen(req, timeout=120) as resp:
        for line in resp:
            if not line.strip():
                continue
            if line.decode('utf-8').strip().startswith("data: "):
                try:
                    chunk = json.loads(line.decode('utf-8')[6:])
                    delta = chunk.get("choices", [{}])[0].get("delta", {})
                    rt = delta.get("reasoning_content", "")
                    text = rt if rt else delta.get("content", "")
                    if text:
                        now = time.time()
                        if ttft is None:
                            ttft = now
                        times.append(now)
                except json.JSONDecodeError:
                    pass

    total = len(times)
    gen_time = times[-1] - times[0] if len(times) > 1 else (time.time() - ttft if ttft else 0.001)
    ttft_ms = (ttft - t0) * 1000
    tps = total / gen_time if gen_time > 0 else 0

    return total, ttft_ms, tps


if __name__ == "__main__":
    print("=" * 60)
    print("TOKEN SPEED TEST — LOCAL (127.0.0.1, no Tailscale)")
    print(f"Model: {MODEL}")
    print("=" * 60)

    results = []
    for n in TOKEN_LENGTHS:
        print(f"\n  Running {n}-token test...", flush=True)
        total, ttft_ms, tps = benchmark(n)
        results.append((n, total, ttft_ms, tps))
        print(f"  Generated: {total} tokens  |  TTFT: {ttft_ms:.0f}ms  |  TPS: {tps:.1f}")

    print("\n" + "=" * 60)
    print(f"{'Target':>8}  {'Actual':>8}  {'TTFT(ms)':>10}  {'TPS':>8}")
    print("-" * 60)
    for target, actual, ttft, tps in results:
        print(f"{target:>8}  {actual:>8}  {ttft:>10.0f}  {tps:>8.1f}")
    print("=" * 60)

    best = results[-1]
    if best[3] >= 180:
        status = f"OPTIMAL ({best[3]:.1f} TPS)"
    elif best[3] >= 100:
        status = f"ACCEPTABLE ({best[3]:.1f} TPS)"
    else:
        status = f"LOW THROUGHPUT ({best[3]:.1f} TPS) — investigate server config"

    print(f"STATUS: {status}")
    print("=" * 60)

    input("\nPress Enter to exit...")
