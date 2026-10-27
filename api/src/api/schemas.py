"""What the parser may return. These models are also the JSON schema sent to the LLM.

Every field is required (nullable where it's optional) and extra keys are
forbidden, because strict structured output demands it. Ranges such as 1-5 are
checked by Pydantic after the reply arrives, so a bad value is caught here
rather than trusted.
"""

from datetime import date
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter

SCHEMA_VERSION = 1

SpendingCategory = Literal[
    "food", "groceries", "transport", "entertainment", "shopping", "bills", "health", "other"
]


class Item(BaseModel):
    model_config = ConfigDict(extra="forbid")

    occurred_on: date = Field(description="Local date the thing happened, YYYY-MM-DD.")
    confidence: float = Field(
        ge=0, le=1, description="0-1. Below 0.7 when you had to guess anything."
    )


class ApplicationEvent(Item):
    domain: Literal["application"]
    application_id: str | None = Field(
        description="id from the open applications list if this updates one, otherwise null."
    )
    kind: Literal["job", "freelance"]
    company: str
    role: str | None = Field(description="Job title, or null if not mentioned.")
    stage: Literal["applied", "screen", "interview", "offer", "rejected", "withdrawn"]


class Meal(Item):
    domain: Literal["meal"]
    kind: Literal["prepped", "ate_out", "home"]
    description: str | None


class CheckIn(Item):
    domain: Literal["checkin"]
    energy: int | None = Field(ge=1, le=5, description="1-5, or null if not given.")
    mood: int | None = Field(ge=1, le=5, description="1-5, or null if not given.")
    sleep: int | None = Field(ge=1, le=5, description="Sleep quality 1-5, or null.")


class Spending(Item):
    domain: Literal["spending"]
    amount: float = Field(gt=0, description="CAD.")
    category: SpendingCategory
    merchant: str | None


class Note(Item):
    domain: Literal["note"]
    text: str


ParsedItem = Annotated[
    ApplicationEvent | Meal | CheckIn | Spending | Note, Field(discriminator="domain")
]
item_adapter: TypeAdapter[ParsedItem] = TypeAdapter(ParsedItem)


class ParsedLog(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[ParsedItem]


# Keywords strict structured output doesn't accept. Pydantic still enforces them.
_UNSUPPORTED = {"minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum", "discriminator"}


def _strictify(node: Any) -> Any:
    if isinstance(node, dict):
        node = {k: _strictify(v) for k, v in node.items() if k not in _UNSUPPORTED}
        if "oneOf" in node:
            node["anyOf"] = node.pop("oneOf")
        return node
    if isinstance(node, list):
        return [_strictify(v) for v in node]
    return node


def llm_schema() -> dict[str, Any]:
    """ParsedLog's JSON schema in the shape strict structured output accepts."""
    return _strictify(ParsedLog.model_json_schema())
