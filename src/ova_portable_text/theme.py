from __future__ import annotations

from typing import Literal

from pydantic import ConfigDict, Field, field_validator

from .base import OvaBaseModel


class LengthValue(OvaBaseModel):
    unit: Literal["em", "pt"]
    value: int | float

    @field_validator("value")
    @classmethod
    def validate_non_negative_value(cls, value: int | float) -> int | float:
        if value < 0:
            raise ValueError("Length `value` must be >= 0.")
        return value


class BlockLayout(OvaBaseModel):
    textAlign: Literal["left", "center", "right", "justify"] | None = None
    firstLineIndent: LengthValue | None = None
    spaceBefore: LengthValue | None = None
    spaceAfter: LengthValue | None = None


class BlockStyleDefault(OvaBaseModel):
    layout: BlockLayout | None = None


class ThemeConfig(OvaBaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="allow")

    # v1.1 formal field
    blockStyleDefaults: dict[str, BlockStyleDefault] = Field(default_factory=dict)

    # backward-compatible legacy / extension-friendly fields
    name: str | None = None
    styleTemplate: str | None = None
    pageTemplateFamily: str | None = None
    brandAssetRefs: list[str] | None = None
    coverTemplateRef: str | None = None
