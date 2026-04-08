from __future__ import annotations

from typing import Any, Literal, TypeAlias

from pydantic import Field, field_validator, model_validator

from .base import OvaBaseModel
from .inline import CitationRef, FootnoteRef, GlossaryTerm, HardBreak, InlineMath, InlineObject, XRef
from .theme import BlockLayout

ALLOWED_TEXT_STYLES = {
    "normal",
    "blockquote",
    "caption",
    "figure_caption",
    "table_caption",
    "equation_caption",
    "smallprint",
    "lead",
    "quote_source",
    "subheading",
}

TextStyle: TypeAlias = Literal[
    "normal",
    "blockquote",
    "caption",
    "figure_caption",
    "table_caption",
    "equation_caption",
    "smallprint",
    "lead",
    "quote_source",
    "subheading",
]

ALLOWED_DECORATOR_MARKS = {"strong", "em", "underline", "code"}
DecoratorMark: TypeAlias = Literal["strong", "em", "underline", "code"]
ListItemStyle: TypeAlias = Literal["bullet", "number"]


class MarkDefBase(OvaBaseModel):
    key: str = Field(alias="_key", serialization_alias="_key")
    type_: str = Field(alias="_type", serialization_alias="_type")


class LinkMarkDef(MarkDefBase):
    type_: Literal["link"] = Field(default="link", alias="_type", serialization_alias="_type")
    href: str
    title: str | None = None
    openInNewTab: bool | None = None
    rel: str | None = None


class AnnotationMarkDef(MarkDefBase):
    data: dict[str, Any] = Field(default_factory=dict)


MarkDef: TypeAlias = LinkMarkDef | AnnotationMarkDef


class Span(OvaBaseModel):
    type_: Literal["span"] = Field(default="span", alias="_type", serialization_alias="_type")
    text: str
    marks: list[str] = Field(default_factory=list)

    def add_mark(self, mark: str) -> "Span":
        self.marks.append(mark)
        return self


TextChild: TypeAlias = Span | HardBreak | XRef | CitationRef | FootnoteRef | GlossaryTerm | InlineMath


class TextBlock(OvaBaseModel):
    type_: Literal["block"] = Field(default="block", alias="_type", serialization_alias="_type")
    style: TextStyle = "normal"
    children: list[TextChild] = Field(default_factory=list)
    markDefs: list[MarkDef] = Field(default_factory=list)
    listItem: ListItemStyle | None = None
    level: int | None = None
    layout: BlockLayout | None = None

    @field_validator("style")
    @classmethod
    def validate_style(cls, value: str) -> str:
        if value not in ALLOWED_TEXT_STYLES:
            allowed = ", ".join(sorted(ALLOWED_TEXT_STYLES))
            raise ValueError(f"Unsupported text block style: {value!r}. Allowed styles: {allowed}")
        return value

    @field_validator("markDefs")
    @classmethod
    def validate_mark_def_keys(cls, value: list[MarkDef]) -> list[MarkDef]:
        seen: set[str] = set()
        for item in value:
            if item.key in seen:
                raise ValueError(f"Duplicate markDef key in the same block: {item.key}")
            seen.add(item.key)
        return value

    @model_validator(mode="after")
    def validate_list_semantics(self) -> "TextBlock":
        if self.listItem is not None and self.level is None:
            self.level = 1
        if self.level is not None and self.level < 1:
            raise ValueError("Text block list level must be >= 1")
        if self.listItem is None and self.level is not None:
            raise ValueError("`level` cannot appear without `listItem`")
        return self

    @classmethod
    def from_parts(
        cls,
        *parts: str | TextChild,
        style: TextStyle = "normal",
        mark_defs: list[MarkDef] | None = None,
        list_item: ListItemStyle | None = None,
        level: int | None = None,
        layout: BlockLayout | dict[str, Any] | None = None,
    ) -> "TextBlock":
        block_layout = layout if isinstance(layout, BlockLayout) or layout is None else BlockLayout.model_validate(layout)
        block = cls(style=style, markDefs=mark_defs or [], listItem=list_item, level=level, layout=block_layout)
        for part in parts:
            block.append(part)
        return block

    @classmethod
    def paragraph(
        cls,
        text: str,
        *,
        style: TextStyle = "normal",
        mark_defs: list[MarkDef] | None = None,
        layout: BlockLayout | dict[str, Any] | None = None,
    ) -> "TextBlock":
        return cls.from_parts(text, style=style, mark_defs=mark_defs, layout=layout)

    @classmethod
    def list_block(
        cls,
        *parts: str | TextChild,
        list_item: ListItemStyle = "bullet",
        level: int = 1,
        style: TextStyle = "normal",
        mark_defs: list[MarkDef] | None = None,
        layout: BlockLayout | dict[str, Any] | None = None,
    ) -> "TextBlock":
        return cls.from_parts(
            *parts,
            style=style,
            mark_defs=mark_defs,
            list_item=list_item,
            level=level,
            layout=layout,
        )

    def append(self, part: str | TextChild) -> "TextBlock":
        if isinstance(part, str):
            self.children.append(Span(text=part))
        else:
            self.children.append(part)
        return self

    def append_text(self, text: str, *, marks: list[str] | None = None) -> "TextBlock":
        self.children.append(Span(text=text, marks=marks or []))
        return self

    def append_inline(self, inline: InlineObject) -> "TextBlock":
        self.children.append(inline)
        return self

    def add_mark_def(self, mark_def: MarkDef) -> "TextBlock":
        self.markDefs.append(mark_def)
        return self

    def add_link_def(
        self,
        *,
        key: str,
        href: str,
        title: str | None = None,
        open_in_new_tab: bool | None = None,
        rel: str | None = None,
    ) -> "TextBlock":
        self.markDefs.append(
            LinkMarkDef(
                _key=key,
                href=href,
                title=title,
                openInNewTab=open_in_new_tab,
                rel=rel,
            )
        )
        return self

    def set_list(self, *, list_item: ListItemStyle, level: int = 1) -> "TextBlock":
        self.listItem = list_item
        self.level = level
        return self
