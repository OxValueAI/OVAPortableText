from __future__ import annotations

from typing import Literal

from pydantic import Field

from .base import OvaBaseModel


class Span(OvaBaseModel):
    type_: Literal["span"] = Field(default="span", alias="_type", serialization_alias="_type")
    text: str
    marks: list[str] = Field(default_factory=list)


class TextBlock(OvaBaseModel):
    type_: Literal["block"] = Field(default="block", alias="_type", serialization_alias="_type")
    style: str = "normal"
    children: list[Span] = Field(default_factory=list)
    markDefs: list[dict] = Field(default_factory=list)

    @classmethod
    def paragraph(cls, text: str, *, style: str = "normal") -> "TextBlock":
        return cls(style=style, children=[Span(text=text)])


class ContentItem(OvaBaseModel):
    itemType: Literal["content"] = "content"
    blocks: list[TextBlock] = Field(default_factory=list)
