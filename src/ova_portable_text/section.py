from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from pydantic import Field, model_validator

from .base import OvaBaseModel
from .content import ContentItem, TextBlock

if TYPE_CHECKING:
    from .document import Document


class SubsectionItem(OvaBaseModel):
    itemType: Literal["subsection"] = "subsection"
    section: "Section"


class Section(OvaBaseModel):
    id: str
    level: int
    title: str
    numbering: str = "auto"
    anchor: str | None = None
    body: list[ContentItem | SubsectionItem] = Field(default_factory=list)

    @model_validator(mode="after")
    def set_default_anchor(self) -> "Section":
        if self.anchor is None:
            self.anchor = self.id
        return self

    def append_content(self, content: ContentItem) -> "Section":
        self.body.append(content)
        return self

    def append_block(self, block: TextBlock) -> "Section":
        self.body.append(ContentItem(blocks=[block]))
        return self

    def append_paragraph(self, text: str, *, style: str = "normal") -> "Section":
        self.body.append(ContentItem(blocks=[TextBlock.paragraph(text, style=style)]))
        return self

    def append_subsection(self, section: "Section") -> "Section":
        self.body.append(SubsectionItem(section=section))
        return self
