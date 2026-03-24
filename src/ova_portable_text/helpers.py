from __future__ import annotations

import base64
import mimetypes
from pathlib import Path
from typing import Any, Iterable

from .block_objects import CalloutBlock, ChartBlock, ImageBlock, MathBlock, TableBlock
from .document import Document, DocumentMeta
from .inline import CitationRef, FootnoteRef, GlossaryTerm, HardBreak, InlineMath, XRef
from .registry import (
    AttachmentAsset,
    BackgroundAsset,
    BibliographyEntry,
    FootnoteEntry,
    GlossaryEntry,
    GridTableCell,
    GridTableDataset,
    GridTableRow,
    IconAsset,
    ImageAsset,
    ImageSourceEmbedded,
    ImageSourceUrl,
    LogoAsset,
    MetricDataset,
    MetricValue,
    PieChartDataset,
    PieSlice,
    RecordTableDataset,
    TableColumn,
)
from .section import NumberingMode, Section
from .theme import ThemeConfig
from .text import (
    AnnotationMarkDef,
    CitationRefMarkDef,
    FootnoteRefMarkDef,
    GlossaryTermMarkDef,
    InlineMathMarkDef,
    LinkMarkDef,
    ListItemStyle,
    MarkDef,
    Span,
    TextBlock,
    TextChild,
    TextStyle,
    XRefMarkDef,
)


def create_document(
    *,
    title: str | None = None,
    language: str | None = None,
    theme: ThemeConfig | dict[str, Any] | None = None,
    strict_ids: bool = False,
    **meta_fields,
) -> Document:
    meta = DocumentMeta(title=title, language=language, **meta_fields)
    theme_value = theme if isinstance(theme, ThemeConfig) else ThemeConfig(**(theme or {}))
    return Document(meta=meta, theme=theme_value, strict_ids=strict_ids)


document = create_document


def section(*, id: str, level: int, title: str, numbering: NumberingMode = "auto", anchor: str | None = None) -> Section:
    return Section(id=id, level=level, title=title, numbering=numbering, anchor=anchor)


def span(text: str, *, marks: list[str] | None = None) -> Span:
    return Span(text=text, marks=marks or [])


def marked(text: str, *marks: str) -> Span:
    return Span(text=text, marks=list(marks))


def strong(text: str) -> Span:
    return Span(text=text, marks=["strong"])


def em(text: str) -> Span:
    return Span(text=text, marks=["em"])


def underline(text: str) -> Span:
    return Span(text=text, marks=["underline"])


def code_span(text: str) -> Span:
    return Span(text=text, marks=["code"])


def link_def(*, key: str, href: str, title: str | None = None, open_in_new_tab: bool | None = None, rel: str | None = None) -> LinkMarkDef:
    return LinkMarkDef(_key=key, href=href, title=title, openInNewTab=open_in_new_tab, rel=rel)


def xref_def(*, key: str, target_id: str, target_type: str | None = None) -> XRefMarkDef:
    return XRefMarkDef(_key=key, targetId=target_id, targetType=target_type)


def citation_ref_def(*, key: str, target_id: str) -> CitationRefMarkDef:
    return CitationRefMarkDef(_key=key, targetId=target_id)


def footnote_ref_def(*, key: str, target_id: str) -> FootnoteRefMarkDef:
    return FootnoteRefMarkDef(_key=key, targetId=target_id)


def glossary_term_def(*, key: str, target_id: str) -> GlossaryTermMarkDef:
    return GlossaryTermMarkDef(_key=key, targetId=target_id)


def inline_math_def(*, key: str, latex: str) -> InlineMathMarkDef:
    return InlineMathMarkDef(_key=key, latex=latex)


def annotation_def(*, key: str, type: str, data: dict[str, Any] | None = None) -> AnnotationMarkDef:
    return AnnotationMarkDef(_key=key, _type=type, data=data or {})


def paragraph(*parts: str | TextChild, style: TextStyle = "normal", mark_defs: list[MarkDef] | None = None, list_item: ListItemStyle | None = None, level: int | None = None) -> TextBlock:
    return TextBlock.from_parts(*parts, style=style, mark_defs=mark_defs, list_item=list_item, level=level)


def bullet_item(*parts: str | TextChild, level: int = 1, mark_defs: list[MarkDef] | None = None) -> TextBlock:
    return TextBlock.list_block(*parts, list_item="bullet", level=level, mark_defs=mark_defs)


def number_item(*parts: str | TextChild, level: int = 1, mark_defs: list[MarkDef] | None = None) -> TextBlock:
    return TextBlock.list_block(*parts, list_item="number", level=level, mark_defs=mark_defs)


def blocks_from_items(items: Iterable[str | tuple[str | TextChild, ...] | list[str | TextChild]], *, list_item: ListItemStyle, level: int = 1, mark_defs: list[MarkDef] | None = None) -> list[TextBlock]:
    output: list[TextBlock] = []
    for item in items:
        parts = (item,) if isinstance(item, str) else tuple(item)
        output.append(TextBlock.list_block(*parts, list_item=list_item, level=level, mark_defs=mark_defs))
    return output


def hard_break() -> HardBreak:
    return HardBreak()


def xref(*, target_type: str | None = None, target_id: str) -> XRef:
    return XRef(targetType=target_type, targetId=target_id)


def citation_ref(target_id: str) -> CitationRef:
    return CitationRef(targetId=target_id)


def footnote_ref(target_id: str) -> FootnoteRef:
    return FootnoteRef(targetId=target_id)


def glossary_term(target_id: str) -> GlossaryTerm:
    return GlossaryTerm(targetId=target_id)


def inline_math(latex: str) -> InlineMath:
    return InlineMath(latex=latex)


def image_block(*, id: str, image_ref: str, anchor: str | None = None) -> ImageBlock:
    return ImageBlock(id=id, anchor=anchor, imageRef=image_ref)


def chart_block(*, id: str, chart_ref: str, anchor: str | None = None) -> ChartBlock:
    return ChartBlock(id=id, anchor=anchor, chartRef=chart_ref)


def table_block(*, id: str, table_ref: str, anchor: str | None = None) -> TableBlock:
    return TableBlock(id=id, anchor=anchor, tableRef=table_ref)


def math_block(*, id: str, latex: str, anchor: str | None = None) -> MathBlock:
    return MathBlock(id=id, anchor=anchor, latex=latex)


def callout(*, id: str, blocks: list[TextBlock] | None = None, anchor: str | None = None) -> CalloutBlock:
    return CalloutBlock(id=id, anchor=anchor, blocks=blocks or [])


def image_asset(
    *,
    id: str,
    image_source: ImageSourceUrl | ImageSourceEmbedded | dict[str, Any],
    alt: str | None = None,
    label: str | None = None,
    anchor: str | None = None,
    meta: dict[str, Any] | None = None,
    **extra,
) -> ImageAsset:
    if isinstance(image_source, dict):
        kind = image_source.get("kind")
        if kind == "url":
            image_source = ImageSourceUrl(**image_source)
        elif kind == "embedded":
            image_source = ImageSourceEmbedded(**image_source)
        else:
            raise ValueError("`image_source.kind` must be 'url' or 'embedded'.")
    return ImageAsset(id=id, imageSource=image_source, alt=alt, label=label, anchor=anchor, meta=meta or {}, **extra)


def image_asset_url(*, id: str, url: str, alt: str | None = None, label: str | None = None, anchor: str | None = None, meta: dict[str, Any] | None = None, **extra) -> ImageAsset:
    return image_asset(id=id, image_source=ImageSourceUrl(kind="url", url=url), alt=alt, label=label, anchor=anchor, meta=meta, **extra)


def image_asset_embedded(*, id: str, data_base64: str, mime_type: str, alt: str | None = None, label: str | None = None, anchor: str | None = None, meta: dict[str, Any] | None = None, **extra) -> ImageAsset:
    return image_asset(id=id, image_source=ImageSourceEmbedded(kind="embedded", encoding="base64", data=data_base64), alt=alt, label=label, anchor=anchor, meta=meta, mimeType=mime_type, **extra)


def image_asset_from_file(*, id: str, path: str | Path, alt: str | None = None, label: str | None = None, anchor: str | None = None, meta: dict[str, Any] | None = None, mime_type: str | None = None, embed: bool = True, url: str | None = None, **extra) -> ImageAsset:
    file_path = Path(path)
    final_mime = mime_type or mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
    if embed:
        data_base64 = base64.b64encode(file_path.read_bytes()).decode("ascii")
        return image_asset_embedded(id=id, data_base64=data_base64, mime_type=final_mime, alt=alt, label=label, anchor=anchor, meta=meta, **extra)
    final_url = url or str(file_path)
    return image_asset_url(id=id, url=final_url, alt=alt, label=label, anchor=anchor, meta=meta, mimeType=final_mime, **extra)


def _coerce_image_source(*, url: str | None = None, data_base64: str | None = None, image_source: ImageSourceUrl | ImageSourceEmbedded | dict[str, Any] | None = None) -> ImageSourceUrl | ImageSourceEmbedded:
    if image_source is not None:
        if isinstance(image_source, dict):
            kind = image_source.get("kind")
            if kind == "url":
                return ImageSourceUrl(**image_source)
            if kind == "embedded":
                return ImageSourceEmbedded(**image_source)
            raise ValueError("`image_source.kind` must be 'url' or 'embedded'.")
        return image_source
    if url is not None:
        return ImageSourceUrl(url=url)
    if data_base64 is not None:
        return ImageSourceEmbedded(data=data_base64)
    raise ValueError("Provide `image_source`, `url`, or `data_base64`.")


def logo_asset(*, id: str, url: str | None = None, data_base64: str | None = None, image_source: ImageSourceUrl | ImageSourceEmbedded | dict[str, Any] | None = None, alt: str | None = None, label: str | None = None, anchor: str | None = None, meta: dict[str, Any] | None = None, **extra) -> LogoAsset:
    return LogoAsset(id=id, imageSource=_coerce_image_source(url=url, data_base64=data_base64, image_source=image_source), alt=alt, label=label, anchor=anchor, meta=meta or {}, **extra)


def background_asset(*, id: str, url: str | None = None, data_base64: str | None = None, image_source: ImageSourceUrl | ImageSourceEmbedded | dict[str, Any] | None = None, label: str | None = None, anchor: str | None = None, meta: dict[str, Any] | None = None, **extra) -> BackgroundAsset:
    return BackgroundAsset(id=id, imageSource=_coerce_image_source(url=url, data_base64=data_base64, image_source=image_source), label=label, anchor=anchor, meta=meta or {}, **extra)


def icon_asset(*, id: str, url: str | None = None, data_base64: str | None = None, image_source: ImageSourceUrl | ImageSourceEmbedded | dict[str, Any] | None = None, alt: str | None = None, label: str | None = None, anchor: str | None = None, meta: dict[str, Any] | None = None, **extra) -> IconAsset:
    return IconAsset(id=id, imageSource=_coerce_image_source(url=url, data_base64=data_base64, image_source=image_source), alt=alt, label=label, anchor=anchor, meta=meta or {}, **extra)


def attachment_asset(*, id: str, url: str | None = None, file_name: str | None = None, description: str | None = None, label: str | None = None, anchor: str | None = None, meta: dict[str, Any] | None = None, **extra) -> AttachmentAsset:
    return AttachmentAsset(id=id, url=url, fileName=file_name, description=description, label=label, anchor=anchor, meta=meta or {}, **extra)


def table_column(*, key: str, header: str) -> TableColumn:
    return TableColumn(key=key, header=header)


def table_dataset(*, id: str, columns: list[TableColumn], rows: list[dict], label: str | None = None, anchor: str | None = None, meta: dict[str, Any] | None = None, **extra) -> RecordTableDataset:
    return RecordTableDataset(id=id, columns=columns, rows=rows, label=label, anchor=anchor, meta=meta or {}, **extra)


def grid_table_cell(*, text: str | None = None, blocks: list[TextBlock] | None = None, header: bool | None = None, col_span: int | None = None, row_span: int | None = None, align: str | None = None, vertical_align: str | None = None, meta: dict[str, Any] | None = None) -> GridTableCell:
    return GridTableCell(text=text, blocks=blocks, header=header, colSpan=col_span, rowSpan=row_span, align=align, verticalAlign=vertical_align, meta=meta or {})


def grid_table_row(*cells: GridTableCell) -> GridTableRow:
    return GridTableRow(cells=list(cells))


def grid_table_dataset(*, id: str, column_count: int, rows: list[GridTableRow], label: str | None = None, anchor: str | None = None, meta: dict[str, Any] | None = None, **extra) -> GridTableDataset:
    return GridTableDataset(id=id, columnCount=column_count, rows=rows, label=label, anchor=anchor, meta=meta or {}, **extra)


def metric_value(*, key: str, value: str | int | float | bool | None, label: str | None = None, unit: str | None = None) -> MetricValue:
    return MetricValue(key=key, value=value, label=label, unit=unit)


def metric_dataset(*, id: str, values: list[MetricValue], label: str | None = None, anchor: str | None = None, meta: dict[str, Any] | None = None, **extra) -> MetricDataset:
    return MetricDataset(id=id, values=values, label=label, anchor=anchor, meta=meta or {}, **extra)


def pie_slice(*, key: str, value: int | float, en: str | None = None, zh: str | None = None, description_en: str | None = None, description_zh: str | None = None, color_hint: str | None = None) -> PieSlice:
    return PieSlice(key=key, label={k: v for k, v in {"en": en, "zh": zh}.items() if v}, value=value, description={k: v for k, v in {"en": description_en, "zh": description_zh}.items() if v}, colorHint=color_hint)


def pie_chart_dataset(*, id: str, slices: list[PieSlice], label: str | None = None, anchor: str | None = None, meta: dict[str, Any] | None = None, value_unit: str | None = None) -> PieChartDataset:
    return PieChartDataset(id=id, slices=slices, label=label, anchor=anchor, meta=meta or {}, valueUnit=value_unit)


def pie_chart_from_parallel_arrays(*, id: str, area_en: list[str], area_zh: list[str] | None, value: list[int | float], description_en: list[str] | None = None, description_zh: list[str] | None = None, label: str | None = None, anchor: str | None = None, meta: dict[str, Any] | None = None, value_unit: str | None = None, sort_desc: bool = True) -> PieChartDataset:
    return PieChartDataset.from_parallel_arrays(id=id, area_en=area_en, area_zh=area_zh, value=value, description_en=description_en, description_zh=description_zh, label=label, anchor=anchor, meta=meta, valueUnit=value_unit, sort_desc=sort_desc)


def bibliography_entry(*, id: str, display_text: str, type: str | None = None, title: str | None = None, authors: list[str] | None = None, year: int | None = None, label: str | None = None, anchor: str | None = None, meta: dict[str, Any] | None = None, **extra) -> BibliographyEntry:
    return BibliographyEntry(id=id, displayText=display_text, type=type, title=title, authors=authors or [], year=year, label=label, anchor=anchor, meta=meta or {}, **extra)


def footnote_entry(*, id: str, blocks: list[TextBlock], label: str | None = None, anchor: str | None = None, meta: dict[str, Any] | None = None) -> FootnoteEntry:
    return FootnoteEntry(id=id, blocks=blocks, label=label, anchor=anchor, meta=meta or {})


def glossary_entry(*, id: str, term: str, definition: str, aliases: list[str] | None = None, short: str | None = None, label: str | None = None, anchor: str | None = None, meta: dict[str, Any] | None = None, **extra) -> GlossaryEntry:
    return GlossaryEntry(id=id, term=term, definition=definition, aliases=aliases, short=short, label=label, anchor=anchor, meta=meta or {}, **extra)
