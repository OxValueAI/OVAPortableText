from __future__ import annotations

"""
Text-layer models for OVAPortableText.
OVAPortableText 的文本层模型。

This module is intentionally a little richer in Step 5.
第 5 步开始，本模块会比前几步更完整一些。

Why is this module important?
为什么这个模块很重要？
Because most report-writing code spends most of its time here:
因为大多数“写报告”的代码，绝大部分时间都在操作这一层：
- paragraph-like text blocks / 类段落文本块
- inline spans / 行内文本片段
- decorators and annotations / 装饰 marks 与 annotation
- list items / 列表项

Design choice in Step 5 / 第 5 步的设计选择：
1. Keep formal document structure in `Section`, not in text styles.
   正式文档结构仍由 `Section` 表达，而不是依赖文本 style。
2. Reuse Portable Text native ideas for `marks / markDefs / listItem / level`.
   沿用 Portable Text 原生思路表达 `marks / markDefs / listItem / level`。
3. Keep the Python API ergonomic for manual report construction.
   让 Python 端手写报告对象时仍然保持顺手。
"""

from typing import Any, Literal, TypeAlias

from pydantic import Field, field_validator, model_validator

from .base import OvaBaseModel
from .inline import CitationRef, FootnoteRef, GlossaryTerm, HardBreak, InlineMath, InlineObject, XRef

# ---------------------------------------------------------------------------
# Text styles / 文本样式
# ---------------------------------------------------------------------------
# These styles are the protocol-approved styles currently allowed inside
# `content.blocks[]`, `footnotes[].blocks`, and `callout.blocks`.
# 这些是当前协议批准的文本样式，可用于
# `content.blocks[]`、`footnotes[].blocks`、`callout.blocks`。
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

# ---------------------------------------------------------------------------
# Marks / 标记
# ---------------------------------------------------------------------------
# Portable Text spans use `marks: list[str]`.
# Portable Text 的 span 通过 `marks: list[str]` 表达装饰与 annotation 引用。
# Some marks are plain decorators, such as `strong` or `em`.
# 有些 marks 是简单装饰器，例如 `strong` 或 `em`。
# Some marks are annotation references, which point to entries in `markDefs[]`.
# 有些 marks 是 annotation 引用，它们会指向 `markDefs[]` 中的定义对象。
ALLOWED_DECORATOR_MARKS = {"strong", "em", "underline", "code"}

DecoratorMark: TypeAlias = Literal["strong", "em", "underline", "code"]
ListItemStyle: TypeAlias = Literal["bullet", "number"]


class MarkDefBase(OvaBaseModel):
    """
    Common base for one mark-definition entry inside `block.markDefs[]`.
    `block.markDefs[]` 中单个 mark 定义对象的公共基类。

    Portable Text convention / Portable Text 约定：
    - `_key` is referenced by a span's `marks[]`
      `_key` 会被 span 的 `marks[]` 引用
    - `_type` describes the annotation kind
      `_type` 描述 annotation 类型

    Important distinction / 重要区分：
    decorators like `strong` do NOT live inside `markDefs[]`.
    `strong` 这类装饰器并不放在 `markDefs[]` 里。
    Only annotation-like definitions live there.
    只有 annotation 风格的定义对象才放进这里。
    """

    key: str = Field(alias="_key", serialization_alias="_key")
    type_: str = Field(alias="_type", serialization_alias="_type")


class LinkMarkDef(MarkDefBase):
    """
    Built-in link annotation definition.
    内置的链接 annotation 定义。

    This corresponds to a span mark that references this definition by `_key`.
    它会被某个 span 的 `marks[]` 通过 `_key` 进行引用。

    Example / 示例：
    - span marks: ["m-link-1"]
      span marks: ["m-link-1"]
    - markDefs: [{"_key": "m-link-1", "_type": "link", "href": "..."}]
      markDefs: [{"_key": "m-link-1", "_type": "link", "href": "..."}]
    """

    type_: Literal["link"] = Field(default="link", alias="_type", serialization_alias="_type")
    href: str
    title: str | None = None
    openInNewTab: bool | None = None
    rel: str | None = None


class AnnotationMarkDef(MarkDefBase):
    """
    Generic custom annotation definition.
    通用自定义 annotation 定义。

    Why keep this generic?
    为什么把它设计成通用型？
    Because the protocol mentions that `markDefs` can also carry comments,
    notes, and future annotation-like semantics, not just links.
    因为协议提到 `markDefs` 不仅可以承载链接，还可以承载批注、注释
    以及未来其他 annotation 语义。

    `data` is an open object bucket for annotation payload.
    `data` 是 annotation 载荷的开放对象桶。
    """

    data: dict[str, Any] = Field(default_factory=dict)


MarkDef: TypeAlias = LinkMarkDef | AnnotationMarkDef
"""
Union of currently supported mark-definition models.
当前支持的 mark-definition 模型联合类型。
"""


class Span(OvaBaseModel):
    """
    Plain inline text span.
    普通行内文本片段。

    Notes / 说明：
    1. `_type="span"` follows Portable Text native convention.
       `_type="span"` 沿用 Portable Text 原生约定。
    2. `marks` stores both decorator marks and markDef keys.
       `marks` 同时承载装饰器 mark 与 markDef 的 key。
    3. This means `marks=["strong", "m-link-1"]` is valid.
       也就是说 `marks=["strong", "m-link-1"]` 是合法的。
    """

    type_: Literal["span"] = Field(default="span", alias="_type", serialization_alias="_type")
    text: str
    marks: list[str] = Field(default_factory=list)

    def add_mark(self, mark: str) -> "Span":
        """
        Append one mark string to the span.
        向当前 span 追加一个 mark 字符串。

        This method does not try to interpret whether the mark is a decorator
        or a markDef key. That resolution belongs to the containing block.
        这个方法不会判断该 mark 是装饰器还是 markDef key；
        真正的解释工作应由包含它的 block 完成。
        """
        self.marks.append(mark)
        return self


TextChild: TypeAlias = Span | HardBreak | XRef | CitationRef | FootnoteRef | GlossaryTerm | InlineMath
"""
All currently supported child elements inside `block.children[]`.
当前 `block.children[]` 支持的全部子元素类型。
"""


class TextBlock(OvaBaseModel):
    """
    Portable Text style text block.
    Portable Text 风格文本块。

    This is the most common block type in report writing.
    这是写报告时最常见的一类块。

    It now supports three major Portable Text abilities:
    现在它支持三组很重要的 Portable Text 原生能力：
    1. `children[]` for inline sequence
       通过 `children[]` 表达行内顺序
    2. `marks / markDefs` for decorators and annotations
       通过 `marks / markDefs` 表达装饰与 annotation
    3. `listItem / level` for list semantics
       通过 `listItem / level` 表达列表语义

    Important boundary / 重要边界：
    formal document headings are still represented by `Section`, not by `h1/h2`.
    正式文档标题仍由 `Section` 表达，而不是使用 `h1/h2`。
    """

    type_: Literal["block"] = Field(default="block", alias="_type", serialization_alias="_type")
    style: TextStyle = "normal"
    children: list[TextChild] = Field(default_factory=list)
    markDefs: list[MarkDef] = Field(default_factory=list)
    listItem: ListItemStyle | None = None
    level: int | None = None

    @field_validator("style")
    @classmethod
    def validate_style(cls, value: str) -> str:
        """
        Restrict style to the protocol-approved set.
        将 style 限制在协议批准的范围内。
        """
        if value not in ALLOWED_TEXT_STYLES:
            allowed = ", ".join(sorted(ALLOWED_TEXT_STYLES))
            raise ValueError(f"Unsupported text block style: {value!r}. Allowed styles: {allowed}")
        return value

    @field_validator("markDefs")
    @classmethod
    def validate_mark_def_keys(cls, value: list[MarkDef]) -> list[MarkDef]:
        """
        Require unique `_key` values inside one block.
        要求同一个 block 内 `markDefs[]` 的 `_key` 唯一。

        Why?
        为什么要这样？
        Because spans resolve annotation marks by key.
        因为 span 会通过 key 来解析 annotation mark。
        If keys collide, resolution becomes ambiguous.
        如果 key 冲突，解析就会产生歧义。
        """
        seen: set[str] = set()
        for item in value:
            if item.key in seen:
                raise ValueError(f"Duplicate markDef key in the same block: {item.key}")
            seen.add(item.key)
        return value

    @model_validator(mode="after")
    def validate_list_semantics(self) -> "TextBlock":
        """
        Normalize and validate list semantics.
        规范化并校验列表语义。

        Rules / 规则：
        1. If `listItem` is present but `level` is omitted, default to 1.
           若存在 `listItem` 但未提供 `level`，默认补成 1。
        2. `level` must be >= 1 when present.
           当 `level` 存在时，必须 >= 1。
        3. `level` must not appear without `listItem`.
           不能只给 `level` 而不给 `listItem`。
        """
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
    ) -> "TextBlock":
        """
        Create a block from mixed text and inline objects.
        用混合的文本与行内对象构造一个 block。

        Strings are automatically converted into `Span`.
        普通字符串会自动转换成 `Span`。

        This is the main convenience constructor used by helper functions,
        `Section.append_paragraph`, list-item APIs, and example scripts.
        这是 helper 函数、`Section.append_paragraph`、列表 API、示例脚本
        等场景最常用的便捷构造入口。
        """
        block = cls(style=style, markDefs=mark_defs or [], listItem=list_item, level=level)
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
    ) -> "TextBlock":
        """
        Quick constructor for a plain one-string paragraph.
        单字符串段落的快捷构造器。
        """
        return cls.from_parts(text, style=style, mark_defs=mark_defs)

    @classmethod
    def list_block(
        cls,
        *parts: str | TextChild,
        list_item: ListItemStyle = "bullet",
        level: int = 1,
        style: TextStyle = "normal",
        mark_defs: list[MarkDef] | None = None,
    ) -> "TextBlock":
        """
        Convenience constructor for one list item block.
        单个列表项 block 的便捷构造器。

        Even though it is called `list_block`, it is still a normal Portable
        Text `block` at the JSON level. The list semantics come from
        `listItem` + `level`.
        虽然这里叫 `list_block`，但在 JSON 层它仍然是普通 Portable Text
        的 `block`；列表语义来自 `listItem` + `level`。
        """
        return cls.from_parts(
            *parts,
            style=style,
            mark_defs=mark_defs,
            list_item=list_item,
            level=level,
        )

    def append(self, part: str | TextChild) -> "TextBlock":
        """
        Append one child into the block.
        向当前 block 追加一个子元素。

        Args / 参数：
            part:
                A plain string or a supported inline object.
                可以是普通字符串，也可以是已支持的行内对象。
        """
        if isinstance(part, str):
            self.children.append(Span(text=part))
        else:
            self.children.append(part)
        return self

    def append_text(self, text: str, *, marks: list[str] | None = None) -> "TextBlock":
        """
        Append plain text as a `Span`.
        以 `Span` 的形式追加普通文本。

        This is especially useful when you want to explicitly attach marks.
        当你希望显式绑定 marks 时，这个方法尤其方便。
        """
        self.children.append(Span(text=text, marks=marks or []))
        return self

    def append_inline(self, inline: InlineObject) -> "TextBlock":
        """
        Append a supported inline object.
        追加一个已支持的行内对象。
        """
        self.children.append(inline)
        return self

    def add_mark_def(self, mark_def: MarkDef) -> "TextBlock":
        """
        Append one mark definition into `markDefs[]`.
        向 `markDefs[]` 追加一个 mark 定义对象。
        """
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
        """
        Append one `link` mark definition into `markDefs[]`.
        向 `markDefs[]` 追加一个 `link` mark 定义。

        The caller still needs to reference this mark key from one or more spans.
        调用方仍需要在一个或多个 span 的 `marks[]` 中引用这个 key。
        """
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
        """
        Convert the current block into a list item block.
        把当前 block 转成一个列表项 block。

        This mutates the current object and returns itself for chaining.
        这个方法会原地修改当前对象，并返回自身以便链式调用。
        """
        self.listItem = list_item
        self.level = level
        return self
