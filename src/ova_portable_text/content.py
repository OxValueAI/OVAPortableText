from __future__ import annotations

"""
Body-content models for OVAPortableText.
OVAPortableText 的正文内容模型。

This module plays two roles:
本模块承担两个角色：
1. Define `ContentItem`, the body-item type for continuous content flow.
   定义 `ContentItem`，即“连续内容流”对应的 body-item 类型。
2. Re-export common text-layer classes for user convenience.
   为了方便使用者导入，顺手重新导出常见文本层类。

Why `ContentItem.blocks` is not text-only?
为什么 `ContentItem.blocks` 不再只允许文本块？
Because the protocol explicitly allows text blocks and object blocks to share
one reading order inside the same content flow.
因为协议明确允许文本块与块级对象共享同一内容流中的阅读顺序。
"""

from typing import Literal, TypeAlias

from pydantic import Field

from .base import OvaBaseModel
from .block_objects import CalloutBlock, ChartBlock, ImageBlock, MathBlock, TableBlock
from .text import (
    ALLOWED_DECORATOR_MARKS,
    ALLOWED_TEXT_STYLES,
    AnnotationMarkDef,
    CitationRefMarkDef,
    DecoratorMark,
    FootnoteRefMarkDef,
    GlossaryTermMarkDef,
    InlineMathMarkDef,
    LinkMarkDef,
    ListItemStyle,
    MarkDef,
    Span,
    XRefMarkDef,
    TextBlock,
    TextChild,
    TextStyle,
)

BlockElement: TypeAlias = TextBlock | ImageBlock | ChartBlock | TableBlock | MathBlock | CalloutBlock
"""
Any block-level element allowed inside `content.blocks[]`.
`content.blocks[]` 中允许出现的任意块级元素类型。
"""


class ContentItem(OvaBaseModel):
    """
    One continuous content-flow body item.
    一个连续内容流 body item。

    A section body may contain multiple `ContentItem`s and `SubsectionItem`s.
    一个 section 的 body 中可以混排多个 `ContentItem` 与 `SubsectionItem`。
    """

    itemType: Literal["content"] = "content"
    blocks: list[BlockElement] = Field(default_factory=list)

    def append_block(self, block: BlockElement) -> "ContentItem":
        """
        Append one block-level element.
        追加一个块级元素。
        """
        self.blocks.append(block)
        return self

    def append_text_block(self, block: TextBlock) -> "ContentItem":
        """
        Explicit helper for appending a text block.
        针对文本块的显式追加辅助方法。
        """
        self.blocks.append(block)
        return self
