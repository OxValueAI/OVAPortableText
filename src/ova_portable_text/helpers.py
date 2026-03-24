from __future__ import annotations

from typing import Any, Iterable

from .block_objects import CalloutBlock, ChartBlock, ImageBlock, MathBlock, TableBlock
from .document import Document, DocumentMeta
from .inline import CitationRef, FootnoteRef, GlossaryTerm, HardBreak, XRef
from .registry import (
    AttachmentAsset,
    BackgroundAsset,
    BibliographyEntry,
    FootnoteEntry,
    GlossaryEntry,
    IconAsset,
    ImageAsset,
    LogoAsset,
    MetricDataset,
    MetricValue,
    PieChartDataset,
    PieSlice,
    TableColumn,
    TableDataset,
)
from .section import NumberingMode, Section
from .theme import ThemeConfig
from .text import (
    AnnotationMarkDef,
    LinkMarkDef,
    ListItemStyle,
    MarkDef,
    Span,
    TextBlock,
    TextChild,
    TextStyle,
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


def xref(*, target_type: str, target_id: str) -> XRef:
    return XRef(targetType=target_type, targetId=target_id)


def citation_ref(*ref_ids: str, mode: str = "parenthetical") -> CitationRef:
    return CitationRef(refIds=list(ref_ids), mode=mode)


def footnote_ref(ref_id: str) -> FootnoteRef:
    return FootnoteRef(refId=ref_id)


def glossary_term(term_id: str) -> GlossaryTerm:
    return GlossaryTerm(termId=term_id)


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


def image_asset(*, id: str, src: str, alt: str | None = None, label: str | None = None, anchor: str | None = None, meta: dict[str, Any] | None = None, **extra) -> ImageAsset:
    return ImageAsset(id=id, src=src, alt=alt, label=label, anchor=anchor, meta=meta or {}, **extra)


def logo_asset(*, id: str, src: str, alt: str | None = None, label: str | None = None, anchor: str | None = None, meta: dict[str, Any] | None = None, **extra) -> LogoAsset:
    return LogoAsset(id=id, src=src, alt=alt, label=label, anchor=anchor, meta=meta or {}, **extra)


def background_asset(*, id: str, src: str, label: str | None = None, anchor: str | None = None, meta: dict[str, Any] | None = None, **extra) -> BackgroundAsset:
    return BackgroundAsset(id=id, src=src, label=label, anchor=anchor, meta=meta or {}, **extra)


def icon_asset(*, id: str, src: str, alt: str | None = None, label: str | None = None, anchor: str | None = None, meta: dict[str, Any] | None = None, **extra) -> IconAsset:
    return IconAsset(id=id, src=src, alt=alt, label=label, anchor=anchor, meta=meta or {}, **extra)


def attachment_asset(*, id: str, src: str, file_name: str | None = None, description: str | None = None, label: str | None = None, anchor: str | None = None, meta: dict[str, Any] | None = None, **extra) -> AttachmentAsset:
    return AttachmentAsset(id=id, src=src, fileName=file_name, description=description, label=label, anchor=anchor, meta=meta or {}, **extra)


def table_column(*, key: str, header: str) -> TableColumn:
    return TableColumn(key=key, header=header)


def table_dataset(*, id: str, columns: list[TableColumn], rows: list[dict], label: str | None = None, anchor: str | None = None, meta: dict[str, Any] | None = None, **extra) -> TableDataset:
    return TableDataset(id=id, columns=columns, rows=rows, label=label, anchor=anchor, meta=meta or {}, **extra)


def metric_value(*, key: str, value: str | int | float | bool | None, label: str | None = None, unit: str | None = None) -> MetricValue:
    return MetricValue(key=key, value=value, label=label, unit=unit)


def metric_dataset(*, id: str, values: list[MetricValue], label: str | None = None, anchor: str | None = None, meta: dict[str, Any] | None = None, **extra) -> MetricDataset:
    return MetricDataset(id=id, values=values, label=label, anchor=anchor, meta=meta or {}, **extra)


def pie_slice(*, key: str, value: int | float, en: str | None = None, zh: str | None = None, description_en: str | None = None, description_zh: str | None = None) -> PieSlice:
    return PieSlice(key=key, label={k: v for k, v in {"en": en, "zh": zh}.items() if v}, value=value, description={k: v for k, v in {"en": description_en, "zh": description_zh}.items() if v})


def pie_chart_dataset(*, id: str, slices: list[PieSlice], label: str | None = None, anchor: str | None = None, meta: dict[str, Any] | None = None, value_unit: str | None = None) -> PieChartDataset:
    return PieChartDataset(id=id, slices=slices, label=label, anchor=anchor, meta=meta or {}, valueUnit=value_unit)


def pie_chart_from_parallel_arrays(*, id: str, area_en: list[str], area_zh: list[str] | None, value: list[int | float], description_en: list[str] | None = None, description_zh: list[str] | None = None, label: str | None = None, anchor: str | None = None, meta: dict[str, Any] | None = None, value_unit: str | None = None, sort_desc: bool = True) -> PieChartDataset:
    return PieChartDataset.from_parallel_arrays(id=id, area_en=area_en, area_zh=area_zh, value=value, description_en=description_en, description_zh=description_zh, label=label, anchor=anchor, meta=meta, valueUnit=value_unit, sort_desc=sort_desc)


def bibliography_entry(*, id: str, title: str | None = None, authors: list[str] | None = None, year: int | None = None, type: str = "misc", text: str | None = None, label: str | None = None, anchor: str | None = None, meta: dict[str, Any] | None = None, **extra) -> BibliographyEntry:
    final_title = title or text
    if not final_title:
        raise ValueError("`bibliography_entry` requires either `title` or legacy `text`.")
    return BibliographyEntry(id=id, title=final_title, authors=authors or [], year=year, type=type, text=text, label=label, anchor=anchor, meta=meta or {}, **extra)


def footnote_entry(*, id: str, blocks: list[TextBlock], label: str | None = None, anchor: str | None = None, meta: dict[str, Any] | None = None) -> FootnoteEntry:
    return FootnoteEntry(id=id, blocks=blocks, label=label, anchor=anchor, meta=meta or {})


def glossary_entry(*, id: str, term: str, definition: str, aliases: list[str] | None = None, short: str | None = None, label: str | None = None, anchor: str | None = None, meta: dict[str, Any] | None = None, **extra) -> GlossaryEntry:
    return GlossaryEntry(id=id, term=term, definition=definition, aliases=aliases, short=short, label=label, anchor=anchor, meta=meta or {}, **extra)
