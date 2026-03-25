from __future__ import annotations

"""
Top-level document models for OVAPortableText.
OVAPortableText 的顶层文档模型。

This module intentionally keeps the document object as the primary user entry.
本模块刻意让 document 对象成为用户的主入口。

Why design it this way?
为什么这样设计？
Because the target usage style of this package is close to common document libraries:
因为本包希望尽量接近常见文档库的使用方式：
- create one top-level document object / 先创建一个顶层 document 对象
- keep appending sections and resources / 再不断 append section 与资源
- finally validate, resolve, number, and export / 最后统一校验、解析、编号、导出

This file therefore contains:
因此本文件同时承载：
1. top-level document state / 顶层文档状态
2. typed-but-extensible metadata / 强类型但可扩展的元信息模型
3. convenience methods for append-style authoring / 便于 append 风格写作的快捷方法
"""

from collections import Counter
from typing import Any, Iterable

from pydantic import ConfigDict, Field

from .base import OvaBaseModel
from .block_objects import CalloutBlock, ChartBlock, ImageBlock, MathBlock, TableBlock
from .content import ContentItem
from .numbering import DocumentNumbering, NumberingConfig
from .registry import (
    AssetsRegistry,
    AttachmentAsset,
    BackgroundAsset,
    BibliographyEntry,
    DatasetsRegistry,
    FootnoteEntry,
    GlossaryEntry,
    IconAsset,
    ImageAsset,
    LogoAsset,
    MetricDataset,
    ChartDataset,
    TableDataset,
)
from .section import NumberingMode, Section, SubsectionItem
from .theme import ThemeConfig


class DocumentMeta(OvaBaseModel):
    """
    Top-level document metadata.
    文档顶层元数据。

    Why keep this model "typed but extensible"?
    为什么把它设计成“强类型但可扩展”？
    Because the protocol explicitly lists common metadata directions,
    but also states that the full detailed field table is not frozen in v1.0.
    因为协议已经明确列出了常见元信息方向，
    但同时也说明 v1.0 尚未冻结完整字段表。

    Therefore / 因此：
    - common fields get typed access / 常见字段提供强类型访问
    - unknown extra fields are still allowed / 仍允许附加未知扩展字段
    """

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    title: str | None = None
    subtitle: str | None = None
    language: str | None = None
    author: str | None = None
    date: str | None = None
    reportNumber: str | None = None
    documentType: str | None = None
    confidentiality: str | None = None
    generatedBy: str | None = None
    generatedAt: str | None = None
    clientId: str | None = None
    projectId: str | None = None

    # Protocol-mentioned likely extension directions.
    # 协议中明确提到、后续大概率会继续使用的扩展方向。
    reportType: str | None = None
    clientName: str | None = None
    locale: str | None = None
    source: str | None = None


class Document(OvaBaseModel):
    """
    Top-level report document.
    顶层报告文档对象。

    Important protocol alignment / 关键协议对齐点：
    - `schemaVersion` defaults to `report.v1`
      `schemaVersion` 默认值为 `report.v1`
    - `theme` is preserved as a placeholder, but now has a lightweight typed model
      `theme` 仍然是占位层，但现在有一个轻量强类型模型
    - top-level registries should always exist, even when empty
      顶层 registry 即使为空也应存在
    """

    schemaVersion: str = "report.v1.0"
    strict_ids: bool = Field(default=False, exclude=True, repr=False)
    meta: DocumentMeta = Field(default_factory=DocumentMeta)
    theme: ThemeConfig = Field(default_factory=ThemeConfig)
    assets: AssetsRegistry = Field(default_factory=AssetsRegistry)
    datasets: DatasetsRegistry = Field(default_factory=DatasetsRegistry)
    bibliography: list[BibliographyEntry] = Field(default_factory=list)
    footnotes: list[FootnoteEntry] = Field(default_factory=list)
    glossary: list[GlossaryEntry] = Field(default_factory=list)
    sections: list[Section] = Field(default_factory=list)

    def _iter_section_target_ids(self, section: Section) -> Iterable[str]:
        """
        Yield all globally-resolvable target IDs inside one section subtree.
        产出一个 section 子树内部所有“全局可解析目标”的 ID。

        The scope intentionally mirrors the resolver's duplicate-id coverage:
        这个范围刻意与 resolver 的 duplicate-id 覆盖保持一致：
        - section ids
        - block object ids currently indexed by the resolver
        - nested subsection targets recursively
        """
        yield section.id
        for item in section.body:
            if isinstance(item, ContentItem):
                for block in item.blocks:
                    if isinstance(block, (ImageBlock, ChartBlock, TableBlock, MathBlock, CalloutBlock)):
                        yield block.id
            elif isinstance(item, SubsectionItem):
                yield from self._iter_section_target_ids(item.section)

    def _iter_global_target_ids(self) -> Iterable[str]:
        """
        Yield all currently registered global target IDs in the document.
        产出当前 document 中所有已注册的全局目标 ID。
        """
        for section in self.sections:
            yield from self._iter_section_target_ids(section)

        for asset in self.assets.images:
            yield asset.id
        for asset in self.assets.logos:
            yield asset.id
        for asset in self.assets.backgrounds:
            yield asset.id
        for asset in self.assets.icons:
            yield asset.id
        for asset in self.assets.attachments:
            yield asset.id

        for chart in self.datasets.charts:
            yield chart.id
        for table in self.datasets.tables:
            yield table.id
        for metric in self.datasets.metrics:
            yield metric.id

        for item in self.bibliography:
            yield item.id
        for item in self.footnotes:
            yield item.id
        for item in self.glossary:
            yield item.id

    def _ensure_ids_are_available(self, ids: Iterable[str], *, context: str) -> None:
        """
        Fail early when `strict_ids=True` and incoming IDs are not globally unique.
        当 `strict_ids=True` 时，若即将加入的 ID 不是全局唯一，则尽早失败。
        """
        if not self.strict_ids:
            return

        incoming_ids = list(ids)
        incoming_counts = Counter(incoming_ids)
        duplicate_incoming = [id_value for id_value, count in incoming_counts.items() if count > 1]
        if duplicate_incoming:
            rendered = ", ".join(repr(id_value) for id_value in duplicate_incoming)
            raise ValueError(f"Duplicate id(s) inside {context}: {rendered}")

        existing_ids = set(self._iter_global_target_ids())
        conflicts = [id_value for id_value in incoming_ids if id_value in existing_ids]
        if conflicts:
            rendered = ", ".join(repr(id_value) for id_value in dict.fromkeys(conflicts))
            raise ValueError(
                f"Duplicate global id(s) detected while appending {context}: {rendered}. "
                "Disable strict_ids to defer this to document validation."
            )

    def append_section(self, section: Section) -> "Document":
        """
        Append one top-level section.
        追加一个顶层 section。
        """
        self._ensure_ids_are_available(
            self._iter_section_target_ids(section),
            context=f"section {section.id!r}",
        )
        self.sections.append(section)
        return self

    def append_sections(self, *sections: Section) -> "Document":
        """
        Append multiple top-level sections in one call.
        一次追加多个顶层 section。
        """
        for section in sections:
            self.append_section(section)
        return self

    def new_section(
        self,
        *,
        id: str,
        level: int,
        title: str,
        numbering: NumberingMode = "auto",
        anchor: str | None = None,
        append: bool = True,
    ) -> Section:
        """
        Create a new top-level section and optionally append it immediately.
        创建一个新的顶层 section，并可选择立刻 append 到 document。

        Why return the section object?
        为什么返回 section 对象？
        So callers can immediately continue writing content like:
        这样调用者可以立刻继续写内容，例如：

            sec = doc.new_section(...)
            sec.append_paragraph(...)
        """
        section = Section(id=id, level=level, title=title, numbering=numbering, anchor=anchor)
        if append:
            self.append_section(section)
        return section

    # ------------------------------------------------------------------
    # Asset registry helpers / 资源 registry helper
    # ------------------------------------------------------------------
    def add_image_asset(self, asset: ImageAsset) -> "Document":
        """
        Append an `assets.images` entry.
        追加一个 `assets.images` 条目。
        """
        self._ensure_ids_are_available([asset.id], context=f"image asset {asset.id!r}")
        self.assets.append_image(asset)
        return self

    def add_logo_asset(self, asset: LogoAsset) -> "Document":
        """
        Append an `assets.logos` entry.
        追加一个 `assets.logos` 条目。
        """
        self._ensure_ids_are_available([asset.id], context=f"logo asset {asset.id!r}")
        self.assets.append_logo(asset)
        return self

    def add_background_asset(self, asset: BackgroundAsset) -> "Document":
        """
        Append an `assets.backgrounds` entry.
        追加一个 `assets.backgrounds` 条目。
        """
        self._ensure_ids_are_available([asset.id], context=f"background asset {asset.id!r}")
        self.assets.append_background(asset)
        return self

    def add_icon_asset(self, asset: IconAsset) -> "Document":
        """
        Append an `assets.icons` entry.
        追加一个 `assets.icons` 条目。
        """
        self._ensure_ids_are_available([asset.id], context=f"icon asset {asset.id!r}")
        self.assets.append_icon(asset)
        return self

    def add_attachment_asset(self, asset: AttachmentAsset) -> "Document":
        """
        Append an `assets.attachments` entry.
        追加一个 `assets.attachments` 条目。
        """
        self._ensure_ids_are_available([asset.id], context=f"attachment asset {asset.id!r}")
        self.assets.append_attachment(asset)
        return self

    # ------------------------------------------------------------------
    # Dataset registry helpers / 数据 registry helper
    # ------------------------------------------------------------------
    def add_table_dataset(self, table: TableDataset) -> "Document":
        """
        Append a `datasets.tables` entry.
        追加一个 `datasets.tables` 条目。
        """
        self._ensure_ids_are_available([table.id], context=f"table dataset {table.id!r}")
        self.datasets.append_table(table)
        return self

    def add_chart_dataset(self, chart: ChartDataset) -> "Document":
        """
        Append a `datasets.charts` entry.
        追加一个 `datasets.charts` 条目。
        """
        self._ensure_ids_are_available([chart.id], context=f"chart dataset {chart.id!r}")
        self.datasets.append_chart(chart)
        return self

    def add_metric_dataset(self, metric: MetricDataset) -> "Document":
        """
        Append a `datasets.metrics` entry.
        追加一个 `datasets.metrics` 条目。
        """
        self._ensure_ids_are_available([metric.id], context=f"metric dataset {metric.id!r}")
        self.datasets.append_metric(metric)
        return self

    # ------------------------------------------------------------------
    # Academic / auxiliary registry helpers / 学术与辅助 registry helper
    # ------------------------------------------------------------------
    def add_bibliography_entry(self, entry: BibliographyEntry) -> "Document":
        """
        Append one bibliography entry.
        追加一个 bibliography 条目。
        """
        self._ensure_ids_are_available([entry.id], context=f"bibliography entry {entry.id!r}")
        self.bibliography.append(entry)
        return self

    def add_footnote(self, entry: FootnoteEntry) -> "Document":
        """
        Append one footnote entry.
        追加一个 footnote 条目。
        """
        self._ensure_ids_are_available([entry.id], context=f"footnote {entry.id!r}")
        self.footnotes.append(entry)
        return self

    def add_glossary_entry(self, entry: GlossaryEntry) -> "Document":
        """
        Append one glossary entry.
        追加一个 glossary 条目。
        """
        self._ensure_ids_are_available([entry.id], context=f"glossary entry {entry.id!r}")
        self.glossary.append(entry)
        return self

    def build_resolver(self):
        """
        Build a global resolver / index for the current document.
        为当前文档构建全局 resolver / 索引器。
        """
        from .resolver import DocumentResolver
        return DocumentResolver.from_document(self)

    def build_numbering(self, config: NumberingConfig | None = None) -> DocumentNumbering:
        """
        Build logical numbering hints for sections / figures / tables / equations.
        为 sections / figures / tables / equations 构建逻辑编号辅助。

        Important boundary / 重要边界：
        this method only computes logical display-number hints.
        这个方法只计算逻辑层 display number 辅助。
        It does NOT decide final renderer wording such as "Figure 3" vs "Fig. 3".
        它不会决定最终渲染层文本，例如到底显示为 “Figure 3” 还是 “Fig. 3”。
        """
        return DocumentNumbering.from_document(self, config=config)

    def validate(self):
        """
        Validate the whole document and return a structured report.
        校验整份文档并返回结构化报告。
        """
        from .validator import validate_document
        return validate_document(self)

    def assert_valid(self) -> "Document":
        """
        Validate the document and raise if invalid.
        校验文档；若无效则抛错。
        """
        from .validator import assert_valid_document
        return assert_valid_document(self)

    @classmethod
    def from_meta(
        cls,
        *,
        theme: ThemeConfig | dict[str, Any] | None = None,
        strict_ids: bool = False,
        **meta_fields: Any,
    ) -> "Document":
        """
        Alternate constructor that builds a document from metadata fields directly.
        一个备用构造器：直接从 metadata 字段创建 document。
        """
        theme_value = theme if isinstance(theme, ThemeConfig) else ThemeConfig(**(theme or {}))
        return cls(meta=DocumentMeta(**meta_fields), theme=theme_value, strict_ids=strict_ids)
