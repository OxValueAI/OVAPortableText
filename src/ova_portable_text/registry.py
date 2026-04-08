from __future__ import annotations

import re
from typing import Annotated, Any, Literal, TypeAlias

from pydantic import ConfigDict, Field, field_validator, model_validator

from .base import OvaBaseModel
from .block_objects import ChartBlock, ImageBlock
from .text import TextBlock


class RegistryEntryBase(OvaBaseModel):
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

    @field_validator("url")
    @classmethod
    def validate_non_empty_url(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("`imageSource.url` must not be empty.")
        return value


class ImageSourceEmbedded(OvaBaseModel):
    kind: Literal["embedded"] = "embedded"
    encoding: Literal["base64"] = "base64"
    data: str

    @field_validator("data")
    @classmethod
    def validate_non_empty_data(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("`imageSource.data` must not be empty.")
        return value


ImageSource = Annotated[ImageSourceUrl | ImageSourceEmbedded, Field(discriminator="kind")]


class ImageLikeAssetBase(RegistryEntryBase):
    model_config = ConfigDict(populate_by_name=True, extra="allow")

    imageSource: ImageSource
    alt: str | None = None
    mimeType: str | None = None
    checksum: str | None = None
    width: int | None = None
    height: int | None = None
    source: str | None = None
    copyright: str | None = None
    language: str | None = None

    @model_validator(mode="after")
    def validate_image_source_requirements(self) -> "ImageLikeAssetBase":
        if self.model_extra and "src" in self.model_extra:
            raise ValueError("Legacy `src` is not allowed; use `imageSource` instead.")
        if self.imageSource.kind == "embedded" and not self.mimeType:
            raise ValueError("Embedded image-like assets require `mimeType`.")
        if self.width is not None and self.width < 1:
            raise ValueError("`width` must be >= 1 when provided.")
        if self.height is not None and self.height < 1:
            raise ValueError("`height` must be >= 1 when provided.")
        if self.mimeType is not None and not re.fullmatch(r"[A-Za-z0-9.+-]+/[A-Za-z0-9.+-]+", self.mimeType):
            raise ValueError("`mimeType` must look like `image/png` or `image/jpeg`.")
        if self.checksum is not None and not re.fullmatch(r"(?:sha256|md5):[A-Fa-f0-9]+", self.checksum):
            raise ValueError("`checksum` must use `sha256:<hex>` or `md5:<hex>` format.")
        return self


class ImageAsset(ImageLikeAssetBase):
    pass


class LogoAsset(ImageLikeAssetBase):
    pass


class BackgroundAsset(ImageLikeAssetBase):
    pass


class IconAsset(ImageLikeAssetBase):
    pass


class AttachmentAsset(RegistryEntryBase):
    model_config = ConfigDict(populate_by_name=True, extra="allow")

    src: str | None = None
    mimeType: str | None = None
    fileName: str | None = None
    description: str | None = None
    sizeBytes: int | None = None


class TableColumnWidth(OvaBaseModel):
    mode: Literal["auto", "weight"]
    value: int | float | None = None

    @model_validator(mode="after")
    def validate_width(self) -> "TableColumnWidth":
        if self.mode == "auto":
            if self.value is not None:
                raise ValueError("`value` must be omitted when width.mode='auto'.")
        else:
            if self.value is None:
                raise ValueError("`value` is required when width.mode='weight'.")
            if self.value <= 0:
                raise ValueError("`value` must be > 0 when width.mode='weight'.")
        return self


class TableColumnSpec(OvaBaseModel):
    width: TableColumnWidth


class TableLayout(OvaBaseModel):
    columnSpecs: list[TableColumnSpec] = Field(default_factory=list)


class TableColumn(OvaBaseModel):
    key: str
    header: str


class RecordTableDataset(RegistryEntryBase):
    tableType: Literal["record"] = "record"
    columns: list[TableColumn] = Field(default_factory=list)
    rows: list[dict[str, str | int | float | bool | None]] = Field(default_factory=list)
    layout: TableLayout | None = None

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
        if self.layout is not None and self.layout.columnSpecs:
            if len(self.layout.columnSpecs) != len(self.columns):
                raise ValueError("`layout.columnSpecs` length must match `columns` length for record tables.")
        return self


CellBlockElement: TypeAlias = TextBlock | ImageBlock | ChartBlock


class GridTableCell(OvaBaseModel):
    text: str | None = None
    blocks: list[CellBlockElement] | None = None
    header: bool = False
    colSpan: int = 1
    rowSpan: int = 1
    align: Literal["left", "center", "right"] | None = None
    verticalAlign: Literal["top", "middle", "bottom"] | None = None
    meta: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_cell(self) -> "GridTableCell":
        has_text = self.text is not None and self.text != ""
        has_blocks = self.blocks is not None and len(self.blocks) > 0
        if not has_text and not has_blocks:
            raise ValueError("Grid table cells require either `text` or non-empty `blocks`.")
        if self.blocks is not None and len(self.blocks) == 0:
            raise ValueError("`blocks` must not be an empty list.")
        if self.colSpan < 1:
            raise ValueError("`colSpan` must be >= 1.")
        if self.rowSpan < 1:
            raise ValueError("`rowSpan` must be >= 1.")
        for item in self.blocks or []:
            if not isinstance(item, (TextBlock, ImageBlock, ChartBlock)):
                raise ValueError("Grid cell `blocks` only support `TextBlock`, `ImageBlock`, and `ChartBlock`.")
        return self


class GridTableRow(OvaBaseModel):
    cells: list[GridTableCell] = Field(default_factory=list)


class GridTableDataset(RegistryEntryBase):
    tableType: Literal["grid"] = "grid"
    columnCount: int | None = None
    rows: list[GridTableRow] = Field(default_factory=list)
    layout: TableLayout | None = None

    @model_validator(mode="after")
    def validate_grid(self) -> "GridTableDataset":
        if self.columnCount is not None and self.columnCount < 1:
            raise ValueError("`columnCount` must be >= 1 when provided.")
        if self.layout is not None and self.layout.columnSpecs:
            if self.columnCount is None:
                raise ValueError("`columnCount` is required when `layout.columnSpecs` is provided for grid tables.")
            if len(self.layout.columnSpecs) != self.columnCount:
                raise ValueError("`layout.columnSpecs` length must match `columnCount` for grid tables.")
        if self.columnCount is None:
            return self

        carry = [0] * self.columnCount
        for row_index, row in enumerate(self.rows):
            next_carry = [max(v - 1, 0) for v in carry]
            occupied = [v > 0 for v in carry]
            col = 0
            for cell_index, cell in enumerate(row.cells):
                while col < self.columnCount and occupied[col]:
                    col += 1
                if col >= self.columnCount:
                    raise ValueError(
                        f"Grid row {row_index} places cell {cell_index} beyond `columnCount`."
                    )
                end = col + cell.colSpan
                if end > self.columnCount:
                    raise ValueError(
                        f"Grid row {row_index} cell {cell_index} exceeds `columnCount` with colSpan={cell.colSpan}."
                    )
                for slot in range(col, end):
                    if occupied[slot]:
                        raise ValueError(
                            f"Grid row {row_index} cell {cell_index} overlaps a carried rowSpan slot."
                        )
                    occupied[slot] = True
                    if cell.rowSpan > 1:
                        next_carry[slot] = max(next_carry[slot], cell.rowSpan - 1)
                col = end
            carry = next_carry
        return self


TableDataset = Annotated[RecordTableDataset | GridTableDataset, Field(discriminator="tableType")]


class PieSlice(OvaBaseModel):
    key: str
    label: dict[str, str] = Field(default_factory=dict)
    value: int | float
    description: dict[str, str] = Field(default_factory=dict)
    colorHint: str | None = None


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


class DoughnutChartDataset(RegistryEntryBase):
    chartType: Literal["doughnut"] = "doughnut"
    valueUnit: str | None = None
    total: int | float = 100
    showRemainderTrack: bool = True
    slices: list[PieSlice] = Field(default_factory=list)

    @field_validator("slices")
    @classmethod
    def validate_unique_slice_keys(cls, value: list[PieSlice]) -> list[PieSlice]:
        seen: set[str] = set()
        for item in value:
            if item.key in seen:
                raise ValueError(f"Duplicate doughnut slice key: {item.key}")
            seen.add(item.key)
        return value

    @field_validator("total")
    @classmethod
    def validate_total(cls, value: int | float) -> int | float:
        if value <= 0:
            raise ValueError("`total` must be > 0 for doughnut charts.")
        return value

    @field_validator("slices")
    @classmethod
    def validate_slice_values_non_negative(cls, value: list[PieSlice]) -> list[PieSlice]:
        for item in value:
            if item.value < 0:
                raise ValueError("`doughnut.slices[].value` must be >= 0.")
        return value

    @model_validator(mode="after")
    def validate_sum_within_total(self) -> "DoughnutChartDataset":
        total_value = sum(item.value for item in self.slices)
        if total_value > self.total:
            raise ValueError("`sum(doughnut.slices[].value)` must be <= `total`.")
        return self


class GenericChartDataset(RegistryEntryBase):
    model_config = ConfigDict(populate_by_name=True, extra="allow")

    chartType: str

    @field_validator("chartType")
    @classmethod
    def validate_chart_type(cls, value: str) -> str:
        if not value:
            raise ValueError("`chartType` is required.")
        return value


ChartDataset = PieChartDataset | DoughnutChartDataset | GenericChartDataset


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
    type: str | None = None
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
    charts: list[ChartDataset] = Field(default_factory=list)
    tables: list[TableDataset] = Field(default_factory=list)
    metrics: list[MetricDataset] = Field(default_factory=list)

    def append_chart(self, chart: ChartDataset) -> "DatasetsRegistry":
        self.charts.append(chart)
        return self

    def append_table(self, table: TableDataset) -> "DatasetsRegistry":
        self.tables.append(table)
        return self

    def append_metric(self, metric: MetricDataset) -> "DatasetsRegistry":
        self.metrics.append(metric)
        return self
