from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from api.llm import FakeProvider, LLMError
from api.parser import OpenApplication, build_system_prompt, parse
from api.schemas import llm_schema

TORONTO = ZoneInfo("America/Toronto")
# Monday evening in Toronto, already Tuesday in UTC.
NOW = datetime(2026, 10, 26, 21, 0, tzinfo=TORONTO)
SHOPIFY = OpenApplication("app_shop01", "Shopify", "Frontend Developer", "screen")


def item(domain, **fields):
    base = {"domain": domain, "occurred_on": "2026-10-26", "confidence": 0.95}
    return base | fields


def test_one_message_becomes_several_proposals():
    provider = FakeProvider({"items": [
        item("spending", amount=14, category="food", merchant="Freshii"),
        item("meal", kind="ate_out", description="lunch"),
    ]})

    proposals = parse("$14 lunch at Freshii", provider, NOW)

    assert [p.domain for p in proposals] == ["spending", "meal"]
    assert proposals[0].payload == {"amount": 14.0, "category": "food", "merchant": "Freshii"}
    assert proposals[0].confidence == 0.95


def test_today_keeps_the_current_time_and_other_days_get_local_noon():
    provider = FakeProvider({"items": [
        item("note", text="today"),
        item("note", text="yesterday", occurred_on="2026-10-25"),
    ]})

    today, yesterday = parse("x", provider, NOW)

    assert today.occurred_at == NOW
    assert yesterday.occurred_at == datetime(2026, 10, 25, 12, 0, tzinfo=TORONTO)


def test_out_of_range_scores_become_a_zero_confidence_note():
    provider = FakeProvider({"items": [item("checkin", energy=7, mood=3, sleep=None)]})

    [proposal] = parse("energy 7", provider, NOW)

    assert proposal.domain == "note"
    assert proposal.confidence == 0
    assert "Unreadable" in proposal.payload["text"]


def test_an_empty_reply_keeps_the_text_as_a_note():
    [proposal] = parse("lol nothing today", FakeProvider({"items": []}), NOW)

    assert proposal.domain == "note"
    assert proposal.payload["text"] == "lol nothing today"


def test_a_known_application_id_is_kept():
    provider = FakeProvider({"items": [item(
        "application", application_id="app_shop01", kind="job",
        company="Shopify", role="Frontend Developer", stage="interview",
    )]})

    [proposal] = parse("Shopify moved me to interview", provider, NOW, [SHOPIFY])

    assert proposal.payload["application_id"] == "app_shop01"
    assert proposal.confidence == 0.95


def test_a_new_application_gets_a_fresh_id():
    provider = FakeProvider({"items": [item(
        "application", application_id=None, kind="job",
        company="Stripe", role="Frontend Engineer", stage="applied",
    )]})

    [proposal] = parse("applied to Stripe", provider, NOW)

    assert proposal.payload["application_id"].startswith("app_")
    assert proposal.confidence == 0.95


@pytest.mark.parametrize(
    ("application_id", "stage"),
    [("app_made_up", "interview"), (None, "rejected")],
    ids=["invented id", "update to an unknown application"],
)
def test_suspicious_application_events_are_flagged(application_id, stage):
    provider = FakeProvider({"items": [item(
        "application", application_id=application_id, kind="job",
        company="Wave", role=None, stage=stage,
    )]})

    [proposal] = parse("Wave", provider, NOW, [SHOPIFY])

    assert proposal.payload["application_id"] not in {"app_made_up", None}
    assert proposal.confidence <= 0.5


def test_provider_errors_propagate_so_the_caller_can_retry():
    with pytest.raises(LLMError):
        parse("x", FakeProvider(LLMError("timeout")), NOW)


def test_prompt_has_local_date_and_open_applications():
    prompt = build_system_prompt(NOW, [SHOPIFY])

    assert "Monday 2026-10-26" in prompt
    assert "id=app_shop01 company=Shopify role=Frontend Developer stage=screen" in prompt


def test_schema_is_strict_friendly():
    schema = llm_schema()
    text = str(schema)

    assert "oneOf" not in text and "discriminator" not in text and "maximum" not in text
    for definition in schema["$defs"].values():
        assert definition["additionalProperties"] is False
        assert set(definition["required"]) == set(definition["properties"])
