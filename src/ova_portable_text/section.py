from __future__ import annotations

"""
Section-related models for OVAPortableText.
OVAPortableText 的 section 相关模型。

A section is the formal document-structure node.
section 是正式文档结构节点。

This version strengthens the ergonomics further.
这一版继续强化易用性。

The goal is to let report-writing code read naturally, e.g.:
目标是让写报告的代码读起来更自然，例如：

    sec = doc.new_section(...)
    sec.append_paragraph("Hello")
    sec.append_image_with_caption(...)
    sub = sec.new_subsection(...)
    sub.append_bullet_item("Point A")

without constantly constructing nested body-item wrappers by hand.
而不必不断手动构造嵌套 body-item 包装对象。
"""

from typing import Literal, TypeAlias

from pydantic import Field, model_validator

from .base import OvaBaseModel
from .block_objects import CalloutBlock, ChartBlock, ImageBlock, MathBlock, TableBlock
from .content import BlockElement, ContentItem, MarkDef, TextBlock, TextChild, TextStyle
from .text import ListItemStyle


NumberingMode: TypeAlias = Literal["auto", "none", "manual"]


class SubsectionItem(OvaBaseModel):
    """
    Wrapper item used inside `section.body` to hold a nested section.
    用于 `section.body` 中承载嵌套 section 的包装 item。
    """

    itemType: Literal["subsection"] = "subsection"
    section: "Section"


class Section(OvaBaseModel):
    """
    Formal section node of the report structure.
    报告结构中的正式 section 节点。

    Body can contain:
    body 中可以包含：
    - `ContentItem` for continuous content flow / 连续内容流
    - `SubsectionItem` for nested formal sections / 嵌套正式子章节
    """

    id: str
    level: int
    title: str
    numbering: NumberingMode = "auto"
    anchor: str | None = None
    body: list[ContentItem | SubsectionItem] = Field(default_factory=list)

    @model_validator(mode="after")
    def set_default_anchor(self) -> "Section":
        """
        If anchor is omitted, reuse the section id.
        如果未显式提供 anchor，则默认复用 section id。
        """
        if self.anchor is None:
            self.anchor = self.id
        return self

    def append_content(self, content: ContentItem) -> "Section":
        """
        Append a prepared `ContentItem`.
        追加一个已经构造好的 `ContentItem`。
        """
        self.body.append(content)
        return self

    def _get_or_create_last_content(self) -> ContentItem:
        """
        Return the last body item when it is a `ContentItem`, otherwise create one.
        若当前最后一个 body item 是 `ContentItem` 则直接复用，否则新建一个。

        Why is this helper useful?
        为什么这个 helper 有用？
        The protocol says a `content` item represents one continuous reading flow.
        In authoring code, users often want to keep appending related blocks into
        that same flow, instead of accidentally creating many tiny one-block items.
        协议规定 `content` 表示一段连续阅读流。在编写代码时，用户经常希望把
        一组相关 block 继续追加到同一个 flow 中，而不是无意中拆成很多单块 item。
        """
        if self.body and isinstance(self.body[-1], ContentItem):
            return self.body[-1]
        content = ContentItem()
        self.body.append(content)
        return content

    def append_to_last_content(self, block: BlockElement) -> "Section":
        """
        Append one block into the current trailing `ContentItem` when possible.
        尽量把一个 block 追加到当前末尾的 `ContentItem` 中。

        If the section currently ends with a subsection or is empty, a new
        `ContentItem` is created automatically.
        如果当前 section 为空，或者末尾是 subsection，则会自动新建一个
        `ContentItem` 再追加。
        """
        self._get_or_create_last_content().append_block(block)
        return self

    def append_blocks_to_last_content(self, *blocks: BlockElement) -> "Section":
        """
        Append multiple blocks into the current trailing `ContentItem`.
        把多个 block 追加到当前末尾的 `ContentItem` 中。

        This is especially useful for preserving one continuous content flow across
        several authoring calls.
        这特别适合在多次 authoring 调用之间，继续保持同一个连续内容流。
        """
        content = self._get_or_create_last_content()
        for block in blocks:
            content.append_block(block)
        return self

    def append_text_block_to_last_content(self, block: TextBlock) -> "Section":
        """
        Append a prepared text block to the current trailing `ContentItem`.
        把一个现成文本块追加到当前末尾的 `ContentItem` 中。
        """
        self._get_or_create_last_content().append_text_block(block)
        return self

    def append_paragraph_to_last_content(
        self,
        *parts: str | TextChild,
        style: TextStyle = "normal",
        mark_defs: list[MarkDef] | None = None,
    ) -> "Section":
        """
        Append one paragraph-style text block to the current trailing `ContentItem`.
        把一个段落型文本块追加到当前末尾的 `ContentItem` 中。
        """
        return self.append_text_block_to_last_content(
            TextBlock.from_parts(*parts, style=style, mark_defs=mark_defs)
        )

    def append_block(self, block: BlockElement) -> "Section":
        """
        Append one block-level element as a new content body item.
        将一个块级元素作为新的 content body item 追加到当前 section。

        Why wrap one block into a new `ContentItem`?
        为什么要把单个 block 包成一个新的 `ContentItem`？
        Because `section.body[]` stores content-flow chunks, and the most natural
        append-style API is still "add one visible thing at a time".
        因为 `section.body[]` 存储的是内容流片段，而最自然的 append 风格
        仍然是“每次加一个可见内容单元”。
        """
        self.body.append(ContentItem(blocks=[block]))
        return self

    def append_blocks(self, *blocks: BlockElement) -> "Section":
        """
        Append multiple blocks into one continuous `ContentItem`.
        把多个 block 作为一个连续的 `ContentItem` 一次性追加。

        This helper matters when adjacent blocks are semantically continuous,
        e.g. an object immediately followed by its caption.
        当多个相邻 block 在语义上属于同一连续片段时，这个 helper 很有用，
        例如对象块后面紧跟题注。
        """
        self.body.append(ContentItem(blocks=list(blocks)))
        return self

    def append_text_block(self, block: TextBlock) -> "Section":
        """
        Append a prepared text block as one new content item.
        以新的 content item 形式追加一个现成文本块。
        """
        self.body.append(ContentItem(blocks=[block]))
        return self

    def append_paragraph(
        self,
        *parts: str | TextChild,
        style: TextStyle = "normal",
        mark_defs: list[MarkDef] | None = None,
    ) -> "Section":
        """
        Append one paragraph-style text block.
        追加一个段落型文本块。
        """
        self.body.append(
            ContentItem(
                blocks=[
                    TextBlock.from_parts(*parts, style=style, mark_defs=mark_defs)
                ]
            )
        )
        return self

    def append_list_item(
        self,
        *parts: str | TextChild,
        list_item: ListItemStyle = "bullet",
        level: int = 1,
        mark_defs: list[MarkDef] | None = None,
    ) -> "Section":
        """
        Append one list-item block.
        追加一个列表项 block。
        """
        return self.append_text_block(
            TextBlock.list_block(*parts, list_item=list_item, level=level, mark_defs=mark_defs)
        )

    def append_bullet_item(
        self,
        *parts: str | TextChild,
        level: int = 1,
        mark_defs: list[MarkDef] | None = None,
    ) -> "Section":
        """
        Append one bullet-list item.
        追加一个无序列表项。
        """
        return self.append_list_item(*parts, list_item="bullet", level=level, mark_defs=mark_defs)

    def append_number_item(
        self,
        *parts: str | TextChild,
        level: int = 1,
        mark_defs: list[MarkDef] | None = None,
    ) -> "Section":
        """
        Append one numbered-list item.
        追加一个有序列表项。
        """
        return self.append_list_item(*parts, list_item="number", level=level, mark_defs=mark_defs)

    def append_paragraphs(self, *paragraphs: str) -> "Section":
        """
        Append multiple plain paragraphs in order.
        按顺序追加多个普通段落。

        Why provide this small helper?
        为什么增加这个小 helper？
        In real report authoring, users often already have text split into several
        paragraph strings. Writing ``append_paragraph`` repeatedly is fine, but a
        batch helper makes migration code cleaner and easier to read.
        在真实报告编写中，用户经常已经拿到若干段落字符串。逐个调用
        ``append_paragraph`` 当然可以，但批量 helper 会让迁移代码更干净、
        更容易阅读。
        """
        for paragraph in paragraphs:
            self.append_paragraph(paragraph)
        return self

    def append_bullet_items(self, *items: str, level: int = 1) -> "Section":
        """
        Append multiple bullet-list items in order.
        按顺序追加多个无序列表项。
        """
        for item in items:
            self.append_bullet_item(item, level=level)
        return self

    def append_number_items(self, *items: str, level: int = 1) -> "Section":
        """
        Append multiple numbered-list items in order.
        按顺序追加多个有序列表项。
        """
        for item in items:
            self.append_number_item(item, level=level)
        return self

    def append_subheading(self, text: str) -> "Section":
        """
        Append a non-formal subheading inside this section.
        在当前 section 内追加一个非正式小标题。
        """
        return self.append_paragraph(text, style="subheading")

    def append_blockquote(self, *parts: str | TextChild, mark_defs: list[MarkDef] | None = None) -> "Section":
        """
        Append a blockquote-style text block.
        追加一个 blockquote 风格文本块。
        """
        return self.append_paragraph(*parts, style="blockquote", mark_defs=mark_defs)

    def append_lead(self, *parts: str | TextChild, mark_defs: list[MarkDef] | None = None) -> "Section":
        """
        Append a lead paragraph.
        追加一个导语段落。
        """
        return self.append_paragraph(*parts, style="lead", mark_defs=mark_defs)

    def append_smallprint(self, *parts: str | TextChild, mark_defs: list[MarkDef] | None = None) -> "Section":
        """
        Append a smallprint paragraph.
        追加一个 smallprint 段落。
        """
        return self.append_paragraph(*parts, style="smallprint", mark_defs=mark_defs)

    def append_caption(self, *parts: str | TextChild, mark_defs: list[MarkDef] | None = None) -> "Section":
        """
        Append a generic caption block.
        追加一个通用 caption 文本块。
        """
        return self.append_paragraph(*parts, style="caption", mark_defs=mark_defs)

    def append_figure_caption(self, *parts: str | TextChild, mark_defs: list[MarkDef] | None = None) -> "Section":
        """
        Convenience method for `figure_caption` text blocks.
        `figure_caption` 文本块的便捷方法。
        """
        return self.append_paragraph(*parts, style="figure_caption", mark_defs=mark_defs)

    def append_table_caption(self, *parts: str | TextChild, mark_defs: list[MarkDef] | None = None) -> "Section":
        """
        Convenience method for `table_caption` text blocks.
        `table_caption` 文本块的便捷方法。
        """
        return self.append_paragraph(*parts, style="table_caption", mark_defs=mark_defs)

    def append_equation_caption(self, *parts: str | TextChild, mark_defs: list[MarkDef] | None = None) -> "Section":
        """
        Convenience method for `equation_caption` text blocks.
        `equation_caption` 文本块的便捷方法。
        """
        return self.append_paragraph(*parts, style="equation_caption", mark_defs=mark_defs)

    def append_image(self, *, id: str, image_ref: str, anchor: str | None = None) -> "Section":
        """
        Create and append an image block in one step.
        一步创建并追加一个 image 块。
        """
        return self.append_block(ImageBlock(id=id, anchor=anchor, imageRef=image_ref))

    def append_chart(self, *, id: str, chart_ref: str, anchor: str | None = None) -> "Section":
        """
        Create and append a chart block in one step.
        一步创建并追加一个 chart 块。
        """
        return self.append_block(ChartBlock(id=id, anchor=anchor, chartRef=chart_ref))

    def append_table(self, *, id: str, table_ref: str, anchor: str | None = None) -> "Section":
        """
        Create and append a table block in one step.
        一步创建并追加一个 table 块。
        """
        return self.append_block(TableBlock(id=id, anchor=anchor, tableRef=table_ref))

    def append_math(self, *, id: str, latex: str, anchor: str | None = None) -> "Section":
        """
        Create and append a math block in one step.
        一步创建并追加一个 math_block。
        """
        return self.append_block(MathBlock(id=id, anchor=anchor, latex=latex))

    def append_callout(self, callout: CalloutBlock) -> "Section":
        """
        Append a prepared callout block.
        追加一个已经构造好的 callout 块。
        """
        return self.append_block(callout)

    def append_image_with_caption(
        self,
        *,
        id: str,
        image_ref: str,
        caption: str,
        anchor: str | None = None,
    ) -> "Section":
        """
        Append an image block followed by a figure-caption block.
        追加一个 image 块，并紧接着追加 figure_caption 块。

        Why does this helper exist if the protocol keeps caption adjacent rather than embedded?
        为什么协议既然强调 caption 与对象相邻而不是内嵌，还要做这个 helper？
        Because this helper only automates the recommended adjacent pattern;
        it does not change the underlying protocol shape.
        因为这个 helper 只是自动化协议推荐的“相邻模式”，
        并没有改变底层协议结构。
        """
        return self.append_blocks(
            ImageBlock(id=id, anchor=anchor, imageRef=image_ref),
            TextBlock.from_parts(caption, style="figure_caption"),
        )

    def append_chart_with_caption(
        self,
        *,
        id: str,
        chart_ref: str,
        caption: str,
        anchor: str | None = None,
    ) -> "Section":
        """
        Append a chart block followed by a figure-caption block.
        追加一个 chart 块，并紧接着追加 figure_caption 块。
        """
        return self.append_blocks(
            ChartBlock(id=id, anchor=anchor, chartRef=chart_ref),
            TextBlock.from_parts(caption, style="figure_caption"),
        )

    def append_table_with_caption(
        self,
        *,
        id: str,
        table_ref: str,
        caption: str,
        anchor: str | None = None,
    ) -> "Section":
        """
        Append a table block followed by a table-caption block.
        追加一个 table 块，并紧接着追加 table_caption 块。
        """
        return self.append_blocks(
            TableBlock(id=id, anchor=anchor, tableRef=table_ref),
            TextBlock.from_parts(caption, style="table_caption"),
        )

    def append_math_with_caption(
        self,
        *,
        id: str,
        latex: str,
        caption: str,
        anchor: str | None = None,
    ) -> "Section":
        """
        Append a math block followed by an equation-caption block.
        追加一个 math_block，并紧接着追加 equation_caption 块。
        """
        return self.append_blocks(
            MathBlock(id=id, anchor=anchor, latex=latex),
            TextBlock.from_parts(caption, style="equation_caption"),
        )

    def append_subsection(self, section: "Section") -> "Section":
        """
        Append a nested formal subsection.
        追加一个嵌套正式子章节。
        """
        self.body.append(SubsectionItem(section=section))
        return self

    def new_subsection(
        self,
        *,
        id: str,
        title: str,
        numbering: NumberingMode = "auto",
        anchor: str | None = None,
        append: bool = True,
    ) -> "Section":
        """
        Create a new direct child section.
        创建一个新的直接子章节。

        The child level defaults to `self.level + 1`, which matches the protocol's
        recommended parent/child level relation.
        子章节层级默认使用 `self.level + 1`，这与协议建议的父子层级关系一致。
        """
        child = Section(
            id=id,
            level=self.level + 1,
            title=title,
            numbering=numbering,
            anchor=anchor,
        )
        if append:
            self.append_subsection(child)
        return child
