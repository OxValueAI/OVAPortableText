from __future__ import annotations

from typing import Literal, TypeAlias

from pydantic import Field

from .base import OvaBaseModel


class HardBreak(OvaBaseModel):
    type_: Literal["hard_break"] = Field(default="hard_break", alias="_type", serialization_alias="_type")


class XRef(OvaBaseModel):
    type_: Literal["xref"] = Field(default="xref", alias="_type", serialization_alias="_type")
    targetType: str | None = None
    targetId: str


class CitationRef(OvaBaseModel):
    type_: Literal["citation_ref"] = Field(default="citation_ref", alias="_type", serialization_alias="_type")
    targetId: str


class FootnoteRef(OvaBaseModel):
    type_: Literal["footnote_ref"] = Field(default="footnote_ref", alias="_type", serialization_alias="_type")
    targetId: str


class GlossaryTerm(OvaBaseModel):
    type_: Literal["glossary_term"] = Field(default="glossary_term", alias="_type", serialization_alias="_type")
    targetId: str


class InlineMath(OvaBaseModel):
    type_: Literal["inline_math"] = Field(default="inline_math", alias="_type", serialization_alias="_type")
    latex: str


InlineObject: TypeAlias = HardBreak | XRef | CitationRef | FootnoteRef | GlossaryTerm | InlineMath
