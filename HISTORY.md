# Deployment History — how "Aiduh" (the Hermes Agent) has lived

This is the paper trail of a single persistent AI assistant being
re-housed across three generations of hardware. The agent (Hermes Agent
by Nous Research, https://github.com/NousResearch/hermes-agent) carries
its own memory, skills, and cron fleet between machines — migrating the
whole brain rather than re-installing.

## Generation 1 — RTX 5090 home rig (desktop, Linux)
- Full local inference: a 24GB-class GPU serving ~27B-parameter GGUF
  models via llama.cpp.
- The agent ran with its terminal, cron scheduler, and gateway on the
  same box as the LLM.
- This is where the llama.cpp serving stack (systemd unit, flash
  attention, MTP speculative decoding, q8_0 KV cache) was developed and
  tuned.

## Generation 2 — Samsung phone, Termux (Android, Linux userland)
- The rig became unavailable; the brain was migrated to Termux on a
  Samsung phone. ~83 Termux API commands made the phone a sensor
  platform (GPS, WiFi scan, heart rate, barometer, camera, mic, TTS/STT,
  torch, NFC, IR).
- No local model serving on the phone — llama.cpp stayed on the home PC,
  reachable over Tailscale. Hermes config pointed the `custom` provider
  at `http://<home-pc-tailnet>:8080/v1`.
- Search tooling: Firecrawl-backed web tools broke (dead API key); the
  working chain became **geckodriver + headless Firefox** (WebDriver
  REST API on port 4444) with Bing-HTML curl as fallback.
- Everything else — cron jobs, skills, memory, the client campaign, the
  solar-seismic pipeline — ran on the phone.

## Generation 3 — Windows 11 tablet (current, as of Sept 2026)
- The brain was migrated to a Windows 11 tablet. Hermes home on Windows
  is `%LOCALAPPDATA%\hermes` (NOT `C:\Users\<user>\.hermes` — that path
  is ignored by Windows Hermes; merging a Linux-style brain into the
  wrong home makes the gateway show no platforms and zero cron jobs).
- Migration method: `robocopy` additive merge of the whole home dir
  (~663MB, seconds), then verify vitals (platforms, cron list, model
  config) and keep the previous host alive until the new one proves
  itself over days.
- No geckodriver/Firefox on the tablet; the headless search chain became
  **Brave search via plain curl** (parse `<div class="snippet fdb`
  blocks) with DuckDuckGo-HTML as a secondary that captcha-locks fresh
  IPs fast.
- The LLM server remains on the home PC (llama.cpp, systemd, port 8080)
  — the tablet is a client, not a host.

## Model generations served

| Era | Model | Quant | Notes |
|-----|-------|-------|-------|
| 2025–Aug 2026 | Qwen3.6-35B-A3B (MoE) | UD-Q4_K_XL | ~98-102 TPS measured; MTP draft; superseded |
| Aug 20 – Sept 2026 | Qwen3.8-27B | UD-Q4_K_XL (17.9GB) | 27.3B dense, n_embd 5120, vocab 248,320; served with thinking/reasoning content; n_ctx 163,840 |
| (parallel, Windows) | LM Studio, same Qwen3.8 GGUF | Q4_K_XL | desktop GUI host, local API on the Windows box |

## Key operating lessons
1. **Never point the agent config at a model by a name the server
   ignores.** llama.cpp serves whatever file was loaded; the "model"
   field in Hermes config must be the full GGUF path.
2. **STT is load-bearing.** Voice-note transcription (Groq Whisper) is a
   separate provider from chat — never touch it when swapping the chat
   model.
3. **Cron model pins go stale.** Every agent-driven cron job pins a
   model+provider; when the served model changes, re-pin every job or
   stale pins fall back to a provider that 402s.
4. **Migrate the brain, not the install.** `robocopy`/`rsync` the whole
   Hermes home; verify cron, platforms, and memory survived before
   decommissioning the old host.
