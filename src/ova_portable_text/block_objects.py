from __future__ import annotations

"""
Block-object models for OVAPortableText.
OVAPortableText 的块级对象模型。

In the protocol, these block objects can appear inside `content.blocks[]`
alongside normal text blocks in reading order.
根据协议，这些块级对象可以和普通文本块一起，按阅读顺序出现在 `content.blocks[]` 中。

This module covers the first batch of block objects:
本模块覆盖第一批块级对象：
- image
- chart
- table
- math_block
- callout
"""

from typing import Literal, TypeAlias

from pydantic import Field, model_validator

from .base import OvaBaseModel
from .text import TextBlock


class ReferenceableBlockBase(OvaBaseModel):
    """
    Common base for block objects that may become cross-reference targets.
    可作为交叉引用目标的块级对象公共基类。

    Most visual objects in the body should have:
    正文中的大多数可视对象都应该具备：
    - `id`: instance identity in the body / 正文实例身份
    - `anchor`: anchor used by renderer / 渲染侧锚点

    Design note / 设计说明：
    `id` here belongs to the body instance, not the underlying registry entry.
    这里的 `id` 属于正文实例本身，不是底层 registry 条目 ID。
    """

    id: str
    anchor: str | None = None

    @model_validator(mode="after")
    def set_default_anchor(self) -> "ReferenceableBlockBase":
        """
        Reuse `id` as default anchor when anchor is omitted.
        当未提供 anchor 时，默认复用 `id`。
        """
        if self.anchor is None:
            self.anchor = self.id
        return self


class ImageBlock(ReferenceableBlockBase):
    """
    Body image instance.
    正文中的图片实例。

    `imageRef` points to an entry in `assets.images`.
    `imageRef` 指向 `assets.images` 中的图片资源条目。
    """

    type_: Literal["image"] = Field(default="image", alias="_type", serialization_alias="_type")
    imageRef: str


class ChartBlock(ReferenceableBlockBase):
    """
    Body chart instance.
    正文中的图表实例。

    `chartRef` points to an entry in `datasets.charts`.
    `chartRef` 指向 `datasets.charts` 中的图表数据条目。
    """

    type_: Literal["chart"] = Field(default="chart", alias="_type", serialization_alias="_type")
    chartRef: str


class TableBlock(ReferenceableBlockBase):
    """
    Body table instance.
    正文中的表格实例。

    `tableRef` points to an entry in `datasets.tables`.
    `tableRef` 指向 `datasets.tables` 中的表格数据条目。
    """

    type_: Literal["table"] = Field(default="table", alias="_type", serialization_alias="_type")
    tableRef: str


class MathBlock(ReferenceableBlockBase):
    """
    Embedded LaTeX math block.
    内嵌 LaTeX 公式块。

    Current v1 decision / 当前 v1 决策：
    we directly embed `latex` inside the body object.
    当前直接在正文对象里内嵌 `latex`。
    """

    type_: Literal["math_block"] = Field(default="math_block", alias="_type", serialization_alias="_type")
    latex: str


class CalloutBlock(ReferenceableBlockBase):
    """
    Callout block containing its own text blocks.
    带自有文本块数组的 callout 块。

    Boundary / 边界：
    `callout.blocks` reuses a restricted subset of the normal text-block rules.
    `callout.blocks` 复用正文文本块规则的受限子集。

    In this implementation we only allow `TextBlock` inside callout for clarity.
    当前实现为了保持清晰，只允许 `TextBlock` 作为 callout 内部的 block。
    """

    type_: Literal["callout"] = Field(default="callout", alias="_type", serialization_alias="_type")
    blocks: list[TextBlock] = Field(default_factory=list)

    def append_block(self, block: TextBlock) -> "CalloutBlock":
        """
        Append a text block into the callout.
        向 callout 中追加一个文本块。
        """
        self.blocks.append(block)
        return self


BlockObject: TypeAlias = ImageBlock | ChartBlock | TableBlock | MathBlock | CalloutBlock
"""
Union of all currently supported block objects.
当前已支持的全部块级对象联合类型。
"""
