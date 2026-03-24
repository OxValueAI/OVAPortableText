from __future__ import annotations

"""
Registry-entry models for OVAPortableText.
OVAPortableText 的 registry 条目模型。

This module contains typed implementations of the top-level registries.
本模块提供顶层 registry 的强类型实现。

Current implementation focus / 当前实现重点：
- assets.images / 图片资源
- assets.logos / 品牌 logo 资源
- assets.backgrounds / 背景资源
- assets.icons / 图标资源
- assets.attachments / 附件资源
- datasets.tables / 表格数据
- datasets.charts (pie only for now) / 图表数据（当前仅正式支持 pie）
- datasets.metrics / 指标数据占位
- bibliography / footnotes / glossary

Important note / 重要说明：
The protocol intentionally leaves some registries less detailed in v1.
协议在 v1 中有意没有把部分 registry 细字段彻底写死。
So we provide small typed cores with extension-friendly behaviour.
因此这里采用“最小强类型核心 + 允许扩展”的方式。
"""

from typing import Annotated, Any, Literal

from pydantic import ConfigDict, Field, field_validator, model_validator

from .base import OvaBaseModel
from .text import TextBlock


class RegistryEntryBase(OvaBaseModel):
    """
    Common base for registry entries.
    registry 条目的公共基类。

    The protocol repeatedly uses a common entry pattern:
    协议中多次复用了一类公共条目模式：
    - `id`: stable unique identifier / 稳定唯一标识
    - `anchor`: render-time anchor / 渲染时锚点
    - `label`: human-friendly label / 人类可读标签
    - `meta`: extension bag / 扩展元数据
    """

    id: str
    anchor: str | None = None
    label: str | None = None
    meta: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def set_default_anchor(self) -> "RegistryEntryBase":
        """
        Use `id` as fallback anchor.
        当未提供 anchor 时，使用 `id` 作为默认锚点。
        """
        if self.anchor is None:
            self.anchor = self.id
        return self


class StaticAssetBase(RegistryEntryBase):
    """
    Common base for lightweight static assets.
    轻量静态资源条目的公共基类。

    Why introduce this layer now?
    为什么现在引入这一层？
    Because the protocol has already fixed the top-level buckets:
    因为协议已经冻结了顶层桶结构：
    - images
    - logos
    - backgrounds
    - icons
    - attachments

    Even though their detailed fields are not all frozen yet,
    it is still useful to keep a shared strongly typed minimum shape.
    即便它们的详细字段还没有全部冻结，
    共享一个最小强类型形态仍然很有价值。
    """

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    src: str
    mimeType: str | None = None
    checksum: str | None = None
    source: str | None = None
    copyright: str | None = None
    language: str | None = None


class ImageSourceUrl(OvaBaseModel):
    """
    URL/path-backed image source descriptor.
    基于 URL / 路径的图片来源描述对象。

    Use this for referenced image assets such as:
    适用于引用型图片资源，例如：
    - https://... / 远程地址
    - file://... / 文件 URI
    - relative/local paths handed to the renderer / 交给渲染器解析的相对或本地路径
    """

    kind: Literal["url"] = "url"
    url: str


class ImageSourceEmbedded(OvaBaseModel):
    """
    Embedded image source descriptor.
    内嵌图片来源描述对象。

    Current protocol decision / 当前协议决策：
    only `encoding="base64"` is formally supported.
    当前仅正式支持 `encoding="base64"`。
    """

    kind: Literal["embedded"] = "embedded"
    encoding: Literal["base64"] = "base64"
    data: str


ImageSource = Annotated[ImageSourceUrl | ImageSourceEmbedded, Field(discriminator="kind")]


class ImageAsset(RegistryEntryBase):
    """
    Entry in `assets.images`.
    `assets.images` 中的图片资源条目。

    New protocol rule / 新协议规则：
    - `src` is no longer the formal image field
      `src` 不再是正式图片字段
    - `imageSource` is the single source of truth
      `imageSource` 是唯一正式真源

    Notes / 说明：
    - `alt` is not the caption.
      `alt` 不是图片题注。
    - caption should still prefer adjacent `figure_caption` text blocks.
      图片题注仍然优先由相邻 `figure_caption` 文本块承载。
    """

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    imageSource: ImageSource
    alt: str | None = None
    mimeType: str | None = None
    checksum: str | None = None
    source: str | None = None
    copyright: str | None = None
    language: str | None = None
    width: int | None = None
    height: int | None = None

    @model_validator(mode="after")
    def validate_image_source_requirements(self) -> "ImageAsset":
        """
        Enforce the pure-`imageSource` protocol contract.
        强制执行纯 `imageSource` 协议约束。
        """
        if self.model_extra and "src" in self.model_extra:
            raise ValueError("Legacy `src` is not allowed on ImageAsset; use `imageSource` instead.")
        if self.imageSource.kind == "embedded" and not self.mimeType:
            raise ValueError("Embedded image assets require `mimeType`.")
        return self


class LogoAsset(StaticAssetBase):
    """
    Entry in `assets.logos`.
    `assets.logos` 中的品牌 logo 条目。

    The protocol only fixes the existence of the bucket in v1.
    协议在 v1 中主要冻结了这个 bucket 的存在，而不是全部细字段。
    So we keep the model deliberately small.
    因此这里刻意保持字段较少。
    """

    alt: str | None = None
    width: int | None = None
    height: int | None = None
    variant: str | None = None


class BackgroundAsset(StaticAssetBase):
    """
    Entry in `assets.backgrounds`.
    `assets.backgrounds` 中的背景资源条目。
    """

    width: int | None = None
    height: int | None = None
    usage: str | None = None


class IconAsset(StaticAssetBase):
    """
    Entry in `assets.icons`.
    `assets.icons` 中的图标资源条目。
    """

    alt: str | None = None
    family: str | None = None
    size: int | None = None


class AttachmentAsset(StaticAssetBase):
    """
    Entry in `assets.attachments`.
    `assets.attachments` 中的附件资源条目。

    Attachments are not part of the main body flow,
    but they may still need stable IDs and anchors for future linking.
    附件不属于正文主内容流，
    但未来仍可能需要稳定 ID 与 anchor 来承接链接或下载入口。
    """

    fileName: str | None = None
    description: str | None = None
    sizeBytes: int | None = None


class TableColumn(OvaBaseModel):
    """
    Column definition for `datasets.tables[].columns[]`.
    `datasets.tables[].columns[]` 的列定义对象。
    """

    key: str
    header: str


class TableDataset(RegistryEntryBase):
    """
    Entry in `datasets.tables`.
    `datasets.tables` 中的表格数据条目。

    Structure / 结构：
    - `columns[]` defines order and headers
      `columns[]` 定义列顺序和列标题
    - `rows[]` is an object-array, each row keyed by `columns[].key`
      `rows[]` 是对象数组，每行使用 `columns[].key` 作为键
    """

    columns: list[TableColumn] = Field(default_factory=list)
    rows: list[dict[str, str | int | float | bool | None]] = Field(default_factory=list)
    columnGroups: list[dict[str, Any]] | None = None
    footerRows: list[dict[str, Any]] | None = None
    notes: list[str] | None = None
    defaultAlign: str | None = None
    cellFormatRules: list[dict[str, Any]] | None = None
    rowOrder: list[str] | None = None
    source: str | None = None

    @field_validator("columns")
    @classmethod
    def validate_columns(cls, value: list[TableColumn]) -> list[TableColumn]:
        """
        Require unique `columns[].key` values.
        要求 `columns[].key` 在同一张表内唯一。
        """
        seen: set[str] = set()
        for col in value:
            if col.key in seen:
                raise ValueError(f"Duplicate table column key: {col.key}")
            seen.add(col.key)
        return value

    @model_validator(mode="after")
    def validate_rows_against_columns(self) -> "TableDataset":
        """
        Ensure all row keys can be found in `columns[].key`.
        确保每一行中出现的键都能在 `columns[].key` 中找到。
        """
        allowed_keys = {col.key for col in self.columns}
        for row_index, row in enumerate(self.rows):
            extra_keys = [key for key in row.keys() if key not in allowed_keys]
            if extra_keys:
                raise ValueError(
                    f"Row {row_index} contains keys not declared in columns: {extra_keys}"
                )
        return self


class PieSlice(OvaBaseModel):
    """
    One slice in a pie chart dataset.
    pie chart 数据条目中的一个扇区对象。

    The protocol recommends object-array slices rather than parallel arrays.
    协议推荐使用对象数组 slices，而不是并行数组。
    """

    key: str
    label: dict[str, str] = Field(default_factory=dict)
    value: int | float
    description: dict[str, str] = Field(default_factory=dict)


class PieChartDataset(RegistryEntryBase):
    """
    Pie chart dataset entry in `datasets.charts`.
    `datasets.charts` 中的 pie chart 数据条目。

    Current boundary / 当前边界：
    only `chartType="pie"` is formally implemented right now.
    当前仅正式实现 `chartType="pie"`。
    """

    chartType: Literal["pie"] = "pie"
    valueUnit: str | None = None
    slices: list[PieSlice] = Field(default_factory=list)

    @field_validator("slices")
    @classmethod
    def validate_unique_slice_keys(cls, value: list[PieSlice]) -> list[PieSlice]:
        """
        Require unique slice keys within the chart.
        要求同一张饼图内的扇区 key 唯一。
        """
        seen: set[str] = set()
        for item in value:
            if item.key in seen:
                raise ValueError(f"Duplicate pie slice key: {item.key}")
            seen.add(item.key)
        return value

    @classmethod
    def from_parallel_arrays(
        cls,
        *,
        id: str,
        area_en: list[str],
        area_zh: list[str] | None,
        value: list[int | float],
        description_en: list[str] | None = None,
        description_zh: list[str] | None = None,
        label: str | None = None,
        anchor: str | None = None,
        meta: dict[str, Any] | None = None,
        valueUnit: str | None = None,
        sort_desc: bool = True,
    ) -> "PieChartDataset":
        """
        Compatibility helper for older parallel-array pie-chart input.
        兼容旧的并行数组饼图输入风格。

        The formal protocol prefers normalized `slices[]` objects.
        正式协议更推荐归一化后的 `slices[]` 对象数组。
        This helper accepts an ergonomic legacy input shape and converts it.
        这个 helper 接收更顺手的旧输入形态，并自动转换。
        """
        area_zh = area_zh or [""] * len(area_en)
        description_en = description_en or [""] * len(area_en)
        description_zh = description_zh or [""] * len(area_en)

        lengths = {len(area_en), len(area_zh), len(value), len(description_en), len(description_zh)}
        if len(lengths) != 1:
            raise ValueError("All pie-chart parallel arrays must have the same length")

        rows = []
        for idx, (en, zh, val, den, dzh) in enumerate(
            zip(area_en, area_zh, value, description_en, description_zh, strict=True)
        ):
            key = cls._slugify_key(en or zh or f"slice-{idx + 1}")
            item = PieSlice(
                key=key,
                label={k: v for k, v in {"en": en, "zh": zh}.items() if v},
                value=val,
                description={k: v for k, v in {"en": den, "zh": dzh}.items() if v},
            )
            rows.append(item)

        if sort_desc:
            rows.sort(key=lambda item: item.value, reverse=True)

        return cls(
            id=id,
            anchor=anchor,
            label=label,
            meta=meta or {},
            chartType="pie",
            valueUnit=valueUnit,
            slices=rows,
        )

    @staticmethod
    def _slugify_key(text: str) -> str:
        """
        Create a stable-ish key from human text.
        根据可读文本生成相对稳定的 key。
        """
        text = text.strip().lower()
        output = []
        prev_dash = False
        for ch in text:
            if ch.isalnum():
                output.append(ch)
                prev_dash = False
            else:
                if not prev_dash:
                    output.append("-")
                    prev_dash = True
        result = "".join(output).strip("-")
        return result or "slice"


class MetricValue(OvaBaseModel):
    """
    One metric item in a metric dataset.
    metric dataset 中的单个指标对象。

    The protocol currently only fixes the existence of `datasets.metrics`.
    协议当前主要冻结了 `datasets.metrics` 的存在，而不是完整细字段。
    So this model intentionally stays small but typed.
    因此这个模型刻意保持小而强类型。
    """

    key: str
    label: str | None = None
    value: str | int | float | bool | None = None
    unit: str | None = None


class MetricDataset(RegistryEntryBase):
    """
    Entry in `datasets.metrics`.
    `datasets.metrics` 中的指标数据条目。
    """

    values: list[MetricValue] = Field(default_factory=list)
    source: str | None = None

    @field_validator("values")
    @classmethod
    def validate_unique_metric_keys(cls, value: list[MetricValue]) -> list[MetricValue]:
        """
        Require unique metric keys within one metric dataset.
        要求同一个 metric dataset 内部 key 唯一。
        """
        seen: set[str] = set()
        for item in value:
            if item.key in seen:
                raise ValueError(f"Duplicate metric key: {item.key}")
            seen.add(item.key)
        return value


class BibliographyEntry(RegistryEntryBase):
    """
    Bibliography entry.
    参考文献条目。

    Protocol alignment / 与协议对齐：
    the protocol's minimum semantic shape is roughly:
    协议推荐的最小语义结构大致为：
    - `type`
    - `title`
    - `authors`
    - `year`

    Backward-compatible note / 向后兼容说明：
    older internal examples sometimes used a single `text` field.
    较早的内部示例有时只使用一个 `text` 字段。
    We still accept that optional field as a convenience fallback.
    这里仍保留这个可选字段作为兼容性回退。
    """

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    type: str = "misc"
    title: str
    authors: list[str] = Field(default_factory=list)
    year: int | None = None
    text: str | None = None
    journal: str | None = None
    publisher: str | None = None
    volume: str | None = None
    issue: str | None = None
    pages: str | None = None
    doi: str | None = None
    url: str | None = None
    accessedAt: str | None = None
    edition: str | None = None
    institution: str | None = None
    language: str | None = None


class FootnoteEntry(RegistryEntryBase):
    """
    Footnote entry.
    脚注条目。

    The protocol allows `footnotes[].blocks` to reuse the text-layer rules.
    协议允许 `footnotes[].blocks` 复用文本层规则。
    """

    blocks: list[TextBlock] = Field(default_factory=list)


class GlossaryEntry(RegistryEntryBase):
    """
    Glossary / term entry.
    术语表条目。

    Minimum structure / 最小结构：
    - `term`
    - `definition`
    - optional `aliases`
      可选 `aliases`

    Backward-compatible note / 向后兼容说明：
    since some earlier local examples occasionally use `short`,
    较早的本地示例偶尔会用 `short`，
    we keep it as an optional compatibility field.
    因此这里保留为可选兼容字段。
    """

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    term: str
    definition: str
    aliases: list[str] | None = None
    short: str | None = None

    @field_validator("aliases")
    @classmethod
    def validate_aliases(cls, value: list[str] | None) -> list[str] | None:
        """
        If aliases exist, they must be a list.
        如果 aliases 存在，则必须是一个列表。
        """
        return value


class AssetsRegistry(OvaBaseModel):
    """
    Top-level assets registry.
    顶层 assets registry。

    Protocol alignment / 与协议对齐：
    the v1 protocol already freezes these buckets:
    v1 协议已经冻结了这些 bucket：
    - images
    - logos
    - backgrounds
    - icons
    - attachments

    This implementation now gives all of them lightweight typed models.
    这一版实现已经为它们全部提供了轻量强类型模型。
    """

    images: list[ImageAsset] = Field(default_factory=list)
    logos: list[LogoAsset] = Field(default_factory=list)
    backgrounds: list[BackgroundAsset] = Field(default_factory=list)
    icons: list[IconAsset] = Field(default_factory=list)
    attachments: list[AttachmentAsset] = Field(default_factory=list)

    def append_image(self, asset: ImageAsset) -> "AssetsRegistry":
        self.images.append(asset)
        return self

    def append_logo(self, asset: LogoAsset) -> "AssetsRegistry":
        self.logos.append(asset)
        return self

    def append_background(self, asset: BackgroundAsset) -> "AssetsRegistry":
        self.backgrounds.append(asset)
        return self

    def append_icon(self, asset: IconAsset) -> "AssetsRegistry":
        self.icons.append(asset)
        return self

    def append_attachment(self, asset: AttachmentAsset) -> "AssetsRegistry":
        self.attachments.append(asset)
        return self


class DatasetsRegistry(OvaBaseModel):
    """
    Top-level datasets registry.
    顶层 datasets registry。

    Protocol alignment / 与协议对齐：
    the v1 protocol already freezes these buckets:
    v1 协议已经冻结了这些 bucket：
    - charts
    - tables
    - metrics
    """

    charts: list[PieChartDataset] = Field(default_factory=list)
    tables: list[TableDataset] = Field(default_factory=list)
    metrics: list[MetricDataset] = Field(default_factory=list)

    def append_chart(self, chart: PieChartDataset) -> "DatasetsRegistry":
        self.charts.append(chart)
        return self

    def append_table(self, table: TableDataset) -> "DatasetsRegistry":
        self.tables.append(table)
        return self

    def append_metric(self, metric: MetricDataset) -> "DatasetsRegistry":
        self.metrics.append(metric)
        return self
