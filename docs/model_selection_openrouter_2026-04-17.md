# OpenRouter model selection note (2026-04-17)

## Core paper panel (6 models)

1. `openai/gpt-5.4`
2. `anthropic/claude-sonnet-4.5`
3. `google/gemini-2.5-pro`
4. `x-ai/grok-4.20`
5. `deepseek/deepseek-v3.2`
6. `qwen/qwen3.6-plus`

## Why this is the recommended paper panel

- It stays inside the 4–8 model range and fits a 6-page IEEE paper.
- It covers major current vendor families instead of benchmarking only one ecosystem.
- It avoids preview / experimental IDs in the main panel.
- It is recent enough to justify the label “contemporary” in 2026.
- It balances frontier references with lower-cost repeated-run models.

## Why not reuse the previous 6-model multilingual panel as-is

Because the ICECCME paper should be centered on **human alignment**, not on reissuing the currently submitted multilingual-only comparison.

## Reserve models

- `openai/gpt-5-mini`
- `anthropic/claude-haiku-4.5`
- `x-ai/grok-4.1-fast`
- `moonshotai/kimi-k2.5`

Use the reserve list only if cost, latency, or provider availability becomes a bottleneck.
