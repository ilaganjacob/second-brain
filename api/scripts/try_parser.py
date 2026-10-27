"""Run fixtures/samples.jsonl against a real model and print what came back.

    uv run python scripts/try_parser.py
    uv run python scripts/try_parser.py --model openai/gpt-6-luna

"Now" is pinned to Monday Oct 26 2026, 21:00 Toronto, so relative dates are
checkable. A row marked DIFF needs your judgment; it isn't automatically wrong.
"""

import argparse
import json
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from api.llm import LLMError, OpenRouterProvider
from api.parser import OpenApplication, parse
from api.settings import get_settings

NOW = datetime(2026, 10, 26, 21, 0, tzinfo=ZoneInfo("America/Toronto"))
OPEN_APPLICATIONS = [
    OpenApplication("app_shop01", "Shopify", "Frontend Developer", "screen"),
    OpenApplication("app_wave01", "Wave", "Senior Frontend Engineer", "applied"),
    OpenApplication("app_ws01", "Wealthsimple", "Frontend Engineer", "applied"),
]
SAMPLES = Path(__file__).parent.parent / "fixtures" / "samples.jsonl"


def summarize(proposal) -> str:
    fields = ", ".join(f"{k}={v}" for k, v in proposal.payload.items() if v is not None)
    flag = " LOW" if proposal.confidence < 0.7 else ""
    day = proposal.occurred_at.astimezone(NOW.tzinfo).date()
    return f"{proposal.domain}[{day} c={proposal.confidence:.2f}{flag}] {fields}"


def check(sample, proposals) -> list[str]:
    problems = []
    if sorted(p.domain for p in proposals) != sorted(sample["expect"]):
        problems.append(f"domains {sorted(p.domain for p in proposals)} != {sorted(sample['expect'])}")
    if "application_id" in sample:
        ids = {p.payload.get("application_id") for p in proposals if p.domain == "application"}
        if sample["application_id"] not in ids:
            problems.append(f"application_id {ids} != {sample['application_id']}")
    if "date" in sample:
        days = {str(p.occurred_at.astimezone(NOW.tzinfo).date()) for p in proposals}
        if sample["date"] not in days:
            problems.append(f"date {days} != {sample['date']}")
    return problems


def main() -> None:
    settings = get_settings()
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=settings.openrouter_model)
    args = parser.parse_args()
    provider = OpenRouterProvider(settings.openrouter_api_key, args.model)

    samples = [json.loads(line) for line in SAMPLES.read_text().splitlines() if line.strip()]
    ok, seconds = 0, []
    print(f"model: {args.model}\n")
    for i, sample in enumerate(samples, 1):
        start = time.perf_counter()
        try:
            proposals = parse(sample["text"], provider, NOW, OPEN_APPLICATIONS)
        except LLMError as exc:
            print(f"{i:2}. ERROR {sample['text']!r}\n    {exc}\n")
            continue
        seconds.append(time.perf_counter() - start)
        problems = check(sample, proposals)
        ok += not problems
        print(f"{i:2}. {'OK  ' if not problems else 'DIFF'} {sample['text']!r}  ({seconds[-1]:.1f}s)")
        for p in proposals:
            print(f"      {summarize(p)}")
        for problem in problems:
            print(f"      ! {problem}")
    avg = sum(seconds) / len(seconds) if seconds else 0
    print(f"\n{ok}/{len(samples)} matched expectations · average {avg:.1f}s per capture")


if __name__ == "__main__":
    main()
