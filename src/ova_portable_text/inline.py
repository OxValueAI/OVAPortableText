from __future__ import annotations

"""
Inline reference / annotation objects for OVAPortableText.
OVAPortableText 的行内引用 / 注解对象。
"""

from typing import Literal, TypeAlias

from pydantic import Field

from .base import OvaBaseModel


class HardBreak(OvaBaseModel):
    """
    Soft line break within one logical paragraph.
    单个逻辑段落内部的换行。

    Note:
    This remains supported by the package as a lightweight extension even though
    the protocol's current formal inline-object list focuses on semantic refs.
    即便当前协议正式列举的行内对象更侧重语义引用，包仍保留这个轻量扩展能力。
    """

    type_: Literal["hard_break"] = Field(default="hard_break", alias="_type", serialization_alias="_type")


class XRef(OvaBaseModel):
    type_: Literal["xref"] = Field(default="xref", alias="_type", serialization_alias="_type")
    targetType: str
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
