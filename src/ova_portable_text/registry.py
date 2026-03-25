from __future__ import annotations

from typing import Annotated, Any, Literal, TypeAlias

from pydantic import ConfigDict, Field, field_validator, model_validator

from .base import OvaBaseModel
from .text import TextBlock


class RegistryEntryBase(OvaBaseModel):
    """Common base for top-level registry entries."""

    id: str
    anchor: str | None = None
    label: str | None = None
    meta: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def set_default_anchor(self) -> "RegistryEntryBase":
        if self.anchor is None:
            self.anchor = self.id
        return self


class ImageSourceUrl(OvaBaseModel):
    kind: Literal["url"] = "url"
    url: str


class ImageSourceEmbedded(OvaBaseModel):
    kind: Literal["embedded"] = "embedded"
    encoding: Literal["base64"] = "base64"
    data: str


ImageSource = Annotated[ImageSourceUrl | ImageSourceEmbedded, Field(discriminator="kind")]


class ImageAsset(RegistryEntryBase):
    """Pure image-source-based asset model used by images/logos/backgrounds/icons."""

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

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
        if self.imageSource.kind == "embedded" and not self.mimeType:
            raise ValueError("Embedded image assets require `mimeType`.")
        if self.width is not None and self.width <= 0:
            raise ValueError("`width` must be a positive integer when provided.")
        if self.height is not None and self.height <= 0:
            raise ValueError("`height` must be a positive integer when provided.")
        return self


class LogoAsset(ImageAsset):
    variant: str | None = None


class BackgroundAsset(ImageAsset):
    usage: str | None = None


class IconAsset(ImageAsset):
    family: str | None = None
    size: int | None = None


class AttachmentAsset(RegistryEntryBase):
    """Attachments remain extension-oriented in v1.0."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    fileName: str | None = None
    description: str | None = None
    sizeBytes: int | None = None
    mimeType: str | None = None
    source: str | None = None
    url: str | None = None


class TableColumn(OvaBaseModel):
    key: str
    header: str


class RecordTableDataset(RegistryEntryBase):
    tableType: Literal["record"] = "record"
    columns: list[TableColumn] = Field(default_factory=list)
    rows: list[dict[str, str | int | float | bool | None]] = Field(default_factory=list)

    @field_validator("columns")
    @classmethod
    def validate_columns(cls, value: list[TableColumn]) -> list[TableColumn]:
        seen: set[str] = set()
        for col in value:
            if col.key in seen:
                raise ValueError(f"Duplicate table column key: {col.key}")
            seen.add(col.key)
        return value

    @model_validator(mode="after")
    def validate_rows_against_columns(self) -> "RecordTableDataset":
        allowed_keys = {col.key for col in self.columns}
        for row_index, row in enumerate(self.rows):
            extra_keys = [key for key in row.keys() if key not in allowed_keys]
            if extra_keys:
                raise ValueError(
                    f"Row {row_index} contains keys not declared in columns: {extra_keys}"
                )
        return self


class GridTableCell(OvaBaseModel):
    text: str | None = None
    blocks: list[TextBlock] | None = None
    header: bool | None = None
    colSpan: int | None = None
    rowSpan: int | None = None
    align: Literal["left", "center", "right"] | None = None
    verticalAlign: Literal["top", "middle", "bottom"] | None = None
    meta: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_payload(self) -> "GridTableCell":
        if self.text is None and self.blocks is None:
            raise ValueError("Grid table cell requires `text` or `blocks`.")
        if self.colSpan is not None and self.colSpan < 1:
            raise ValueError("`colSpan` must be >= 1 when provided.")
        if self.rowSpan is not None and self.rowSpan < 1:
            raise ValueError("`rowSpan` must be >= 1 when provided.")
        return self


class GridTableRow(OvaBaseModel):
    cells: list[GridTableCell] = Field(default_factory=list)


class GridTableDataset(RegistryEntryBase):
    tableType: Literal["grid"] = "grid"
    columnCount: int
    rows: list[GridTableRow] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_grid_rows(self) -> "GridTableDataset":
        if self.columnCount < 1:
            raise ValueError("`columnCount` must be >= 1.")
        for row_index, row in enumerate(self.rows):
            if len(row.cells) > self.columnCount:
                raise ValueError(
                    f"Row {row_index} has more cells ({len(row.cells)}) than columnCount ({self.columnCount})."
                )
        return self


TableDataset = Annotated[RecordTableDataset | GridTableDataset, Field(discriminator="tableType")]


class PieSlice(OvaBaseModel):
    key: str
    label: dict[str, str] = Field(default_factory=dict)
    value: int | float
    description: dict[str, str] = Field(default_factory=dict)
    colorHint: str | None = None

    @model_validator(mode="after")
    def validate_label_presence(self) -> "PieSlice":
        if not self.label:
            raise ValueError("Pie slice requires a non-empty `label` object.")
        return self


class PieChartDataset(RegistryEntryBase):
    chartType: Literal["pie"] = "pie"
    valueUnit: str | None = None
    slices: list[PieSlice] = Field(default_factory=list)

    @field_validator("slices")
    @classmethod
    def validate_unique_slice_keys(cls, value: list[PieSlice]) -> list[PieSlice]:
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
    key: str
    label: str | None = None
    value: str | int | float | bool | None = None
    unit: str | None = None


class MetricDataset(RegistryEntryBase):
    values: list[MetricValue] = Field(default_factory=list)
    source: str | None = None

    @field_validator("values")
    @classmethod
    def validate_unique_metric_keys(cls, value: list[MetricValue]) -> list[MetricValue]:
        seen: set[str] = set()
        for item in value:
            if item.key in seen:
                raise ValueError(f"Duplicate metric key: {item.key}")
            seen.add(item.key)
        return value


class BibliographyEntry(RegistryEntryBase):
    model_config = ConfigDict(populate_by_name=True, extra="allow")

    displayText: str
    type: Literal["article", "book", "report", "webpage", "dataset", "other"] | None = None
    title: str | None = None
    authors: list[str] = Field(default_factory=list)
    year: int | None = None
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
    blocks: list[TextBlock] = Field(default_factory=list)


class GlossaryEntry(RegistryEntryBase):
    model_config = ConfigDict(populate_by_name=True, extra="allow")

    term: str
    definition: str
    aliases: list[str] | None = None
    short: str | None = None

    @field_validator("aliases")
    @classmethod
    def validate_aliases(cls, value: list[str] | None) -> list[str] | None:
        return value


class AssetsRegistry(OvaBaseModel):
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
