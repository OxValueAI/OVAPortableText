from __future__ import annotations

from typing import Literal, TypeAlias

from pydantic import Field, StrictBool, model_validator

from .base import OvaBaseModel
from .text import TextBlock
from .page_layout import PageSettings, ObjectPagination
from .chart_features import Key, V14Component


class OptionalReferenceableBlockBase(OvaBaseModel):
    id: str | None = None
    anchor: str | None = None

    @model_validator(mode="after")
    def set_default_anchor(self) -> "OptionalReferenceableBlockBase":
        if self.anchor is None and self.id is not None:
            self.anchor = self.id
        return self


class RequiredReferenceableBlockBase(OvaBaseModel):
    id: str
    anchor: str | None = None

    @model_validator(mode="after")
    def set_default_anchor(self) -> "RequiredReferenceableBlockBase":
        if self.anchor is None:
            self.anchor = self.id
        return self


class ImageBlock(OptionalReferenceableBlockBase):
    _v16_fields = ("page", "pagination")
    page: PageSettings | None = None
    pagination: ObjectPagination | None = None
    type_: Literal["image"] = Field(default="image", alias="_type", serialization_alias="_type")
    imageRef: str


class ChartBlock(OptionalReferenceableBlockBase):
    _v16_fields = ("page", "pagination")
    page: PageSettings | None = None
    pagination: ObjectPagination | None = None
    type_: Literal["chart"] = Field(default="chart", alias="_type", serialization_alias="_type")
    chartRef: str


class TableBlock(OptionalReferenceableBlockBase):
    _v16_fields = ("page", "pagination")
    page: PageSettings | None = None
    pagination: ObjectPagination | None = None
    type_: Literal["table"] = Field(default="table", alias="_type", serialization_alias="_type")
    tableRef: str


class MathBlock(OptionalReferenceableBlockBase):
    type_: Literal["math_block"] = Field(default="math_block", alias="_type", serialization_alias="_type")
    latex: str


class CalloutBlock(OptionalReferenceableBlockBase):
    type_: Literal["callout"] = Field(default="callout", alias="_type", serialization_alias="_type")
    blocks: list[TextBlock] = Field(default_factory=list)

    def append_block(self, block: TextBlock) -> "CalloutBlock":
        self.blocks.append(block)
        return self


class FigureBlock(RequiredReferenceableBlockBase, V14Component):
    _v16_fields = ("page", "pagination")
    page: PageSettings | None = None
    pagination: ObjectPagination | None = None
    type_: Literal["figure"] = Field(default="figure", alias="_type", serialization_alias="_type")
    id: Key
    anchor: Key | None = None
    layoutRef: Key
    keepTogether: StrictBool = True


BlockObject: TypeAlias = FigureBlock | ImageBlock | ChartBlock | TableBlock | MathBlock | CalloutBlock
