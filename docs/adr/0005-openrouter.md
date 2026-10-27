# 5. OpenRouter as the LLM provider layer

Date: 2026-10-27 · Status: accepted

## Context
Capture needs one LLM call that returns structured output (a JSON list of typed items). The spec wants the provider swappable, and the data is personal, including spending.

## Decision
Call OpenRouter behind a small `LLMProvider` interface (`api/src/api/llm.py`), using strict `json_schema` output generated from the Pydantic models. Every request sets `provider.require_parameters: true` (only hosts that honour the schema) and `provider.data_collection: "deny"` (no hosts that store or train on prompts). The model is `anthropic/claude-haiku-5.5`, set by `OPENROUTER_MODEL`.

Model choice, from `scripts/try_parser.py` on the 20 samples in `fixtures/samples.jsonl`:

| Model | Matched | Avg latency | Confidence |
| --- | --- | --- | --- |
| anthropic/claude-haiku-5.5 | 20/20 | 2.5 s | Lowers confidence when it guesses (0.4 to 0.6) |
| openai/gpt-6-luna | 19/20 | 3.2 s | 0.95 to 0.98 on nearly everything, guesses included |

Haiku won on calibration more than on score: the inbox flags anything under 0.7, so a model that's always sure hides exactly the items worth checking. Both cost $0.10 / $0.50 per million tokens, roughly $0.0003 per capture.

## Alternatives considered
- **Anthropic or OpenAI APIs directly:** one less hop, but changing models means changing SDKs.
- **Azure OpenAI:** only worth it with free work credits, which don't apply here.

## Consequences
- Prompts pass through OpenRouter as well as the model host. `data_collection: "deny"` limits that, but it's still a third party.
- With `require_parameters`, any parameter a model doesn't support means no host at all (a 404). Found out the hard way with `temperature`, which neither model accepts.
- Switching models is an env change plus a rerun of `try_parser.py`.
