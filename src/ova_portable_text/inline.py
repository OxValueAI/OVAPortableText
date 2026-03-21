from __future__ import annotations

"""
Inline object models for OVAPortableText.
OVAPortableText 的行内对象模型。

In the protocol, inline objects can only appear inside `block.children[]`.
根据协议，行内对象只能出现在 `block.children[]` 中。
"""

from typing import Literal, TypeAlias

from pydantic import Field, field_validator

from .base import OvaBaseModel


class HardBreak(OvaBaseModel):
    """
    Force a line break inside the same paragraph block.
    表示同一段落内部的强制换行。

    This is NOT a new paragraph.
    它不是新段落。
    """

    type_: Literal["hard_break"] = Field(default="hard_break", alias="_type", serialization_alias="_type")


class XRef(OvaBaseModel):
    """
    Cross-reference to a resolvable target, such as a section or figure.
    指向可解析目标的交叉引用，例如 section 或 figure。
    """

    type_: Literal["xref"] = Field(default="xref", alias="_type", serialization_alias="_type")
    targetType: str
    targetId: str


class CitationRef(OvaBaseModel):
    """
    Reference one or more bibliography entries.
    引用一个或多个 bibliography 条目。
    """

    type_: Literal["citation_ref"] = Field(default="citation_ref", alias="_type", serialization_alias="_type")
    refIds: list[str]
    mode: Literal["parenthetical", "narrative"] = "parenthetical"

    @field_validator("refIds")
    @classmethod
    def validate_ref_ids(cls, value: list[str]) -> list[str]:
        """
        Require at least one bibliography target.
        至少需要一个 bibliography 目标。
        """
        if not value:
            raise ValueError("citation_ref.refIds must contain at least one bibliography id")
        return value


class FootnoteRef(OvaBaseModel):
    """
    Reference a footnote entry.
    引用一个脚注条目。
    """

    type_: Literal["footnote_ref"] = Field(default="footnote_ref", alias="_type", serialization_alias="_type")
    refId: str


class GlossaryTerm(OvaBaseModel):
    """
    Reference a glossary entry or abbreviation entry.
    引用 glossary 中的术语或缩写条目。
    """

    type_: Literal["glossary_term"] = Field(default="glossary_term", alias="_type", serialization_alias="_type")
    termId: str


InlineObject: TypeAlias = HardBreak | XRef | CitationRef | FootnoteRef | GlossaryTerm
"""
Union type of all currently supported inline objects.
当前已支持的全部行内对象联合类型。
"""
