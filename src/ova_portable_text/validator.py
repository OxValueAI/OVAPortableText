from __future__ import annotations

from .block_objects import CalloutBlock, ChartBlock, ImageBlock, MathBlock, TableBlock
from .content import ALLOWED_TEXT_STYLES, ContentItem, Span, TextBlock
from .document import Document
from .exceptions import ValidationReport
from .inline import CitationRef, FootnoteRef, GlossaryTerm, InlineMath, XRef
from .registry import (
    BibliographyEntry,
    FootnoteEntry,
    GlossaryEntry,
    DoughnutChartDataset,
    GridTableDataset,
    ImageLikeAssetBase,
    PieChartDataset,
    RecordTableDataset,
)
from .resolver import DocumentResolver, ResolvedTarget
from .section import Section, SubsectionItem

ALLOWED_DECORATOR_MARKS = {"strong", "em", "underline", "code"}


def validate_document(document: Document) -> ValidationReport:
    report = ValidationReport()

    if not document.schemaVersion:
        report.add_issue(
            code="missing_schema_version",
            message="`schemaVersion` is required.",
            path="schemaVersion",
            contextType="document",
            suggestion="Set `schemaVersion` to `report.v1.2` unless you intentionally target another protocol version.",
        )

    if not isinstance(document.sections, list):
        report.add_issue(
            code="invalid_sections",
            message="`sections` must be a list.",
            path="sections",
            contextType="document",
            suggestion="Top-level `sections` should always be present, even when empty.",
        )
        return report

    _validate_theme(document, report=report)
    _validate_assets(document, report=report)
    _validate_tables(document, report=report)
    _validate_charts(document, report=report)

    for index, section in enumerate(document.sections):
        _validate_section(section, path=f"sections[{index}]", parent_level=None, report=report)

    _validate_bibliography(document.bibliography, report=report)
    _validate_footnotes(document.footnotes, report=report)
    _validate_glossary(document.glossary, report=report)

    resolver = document.build_resolver()

    for duplicate_id, targets in resolver.duplicates.items():
        locations = ", ".join(target.location for target in targets)
        first = targets[0]
        report.add_issue(
            code="duplicate_id",
            message=f"Duplicate global id detected: {duplicate_id!r}. Locations: {locations}",
            contextType="global_id",
            contextId=duplicate_id,
            sectionId=first.sectionId,
            sectionTitle=first.sectionTitle,
            suggestion="Keep each globally resolvable object's `id` unique across the whole document.",
        )

    for anchor, targets in resolver.duplicateAnchors.items():
        locations = ", ".join(target.location for target in targets)
        first = targets[0]
        report.add_issue(
            code="duplicate_anchor",
            message=f"Duplicate anchor detected: {anchor!r}. Locations: {locations}",
            severity="warning",
            contextType="anchor",
            contextAnchor=anchor,
            sectionId=first.sectionId,
            sectionTitle=first.sectionTitle,
            suggestion="Prefer globally unique anchors if the renderer will support page jumps or bookmarks.",
        )

    for index, section in enumerate(document.sections):
        _validate_section_references(section, path=f"sections[{index}]", resolver=resolver, report=report)

    _validate_grid_table_dataset_references(document, resolver=resolver, report=report)

    return report


def assert_valid_document(document: Document) -> Document:
    validate_document(document).raise_for_errors()
    return document


def _ctx(
    *,
    section: Section | None = None,
    context_type: str | None = None,
    context_id: str | None = None,
    context_anchor: str | None = None,
    suggestion: str | None = None,
    location: str | None = None,
) -> dict[str, str | None]:
    return {
        "location": location,
        "contextType": context_type,
        "contextId": context_id,
        "contextAnchor": context_anchor,
        "sectionId": section.id if section else None,
        "sectionTitle": section.title if section else None,
        "suggestion": suggestion,
    }


def _ctx_from_target(target: ResolvedTarget, *, suggestion: str | None = None) -> dict[str, str | None]:
    return {
        "location": target.location,
        "contextType": target.targetType,
        "contextId": target.id,
        "contextAnchor": target.anchor,
        "sectionId": target.sectionId,
        "sectionTitle": target.sectionTitle,
        "suggestion": suggestion,
    }


def _validate_theme(document: Document, *, report: ValidationReport) -> None:
    for style_key in document.theme.blockStyleDefaults.keys():
        if style_key not in ALLOWED_TEXT_STYLES:
            report.add_issue(
                code="invalid_theme_block_style_default",
                message=f"Unsupported `theme.blockStyleDefaults` key: {style_key!r}",
                path=f"theme.blockStyleDefaults.{style_key}",
                contextType="theme",
                suggestion="Use only protocol-approved block styles as keys.",
            )


def _validate_image_like_asset(asset: ImageLikeAssetBase, *, path: str, report: ValidationReport) -> None:
    if not asset.alt:
        report.add_issue(
            code="missing_image_alt",
            message="Image-like asset is missing `alt` text.",
            path=f"{path}.alt",
            severity="warning",
            contextType="asset",
            contextId=asset.id,
            contextAnchor=asset.anchor,
            location=f"{path}.alt",
            suggestion="Provide `alt` for accessibility and graceful fallback rendering.",
        )


def _validate_assets(document: Document, *, report: ValidationReport) -> None:
    for index, asset in enumerate(document.assets.images):
        _validate_image_like_asset(asset, path=f"assets.images[{index}]", report=report)
    for index, asset in enumerate(document.assets.logos):
        _validate_image_like_asset(asset, path=f"assets.logos[{index}]", report=report)
    for index, asset in enumerate(document.assets.backgrounds):
        _validate_image_like_asset(asset, path=f"assets.backgrounds[{index}]", report=report)
    for index, asset in enumerate(document.assets.icons):
        _validate_image_like_asset(asset, path=f"assets.icons[{index}]", report=report)


def _validate_tables(document: Document, *, report: ValidationReport) -> None:
    for index, table in enumerate(document.datasets.tables):
        path = f"datasets.tables[{index}]"
        if isinstance(table, RecordTableDataset):
            if table.layout is not None and table.layout.columnSpecs:
                if len(table.layout.columnSpecs) != len(table.columns):
                    report.add_issue(
                        code="invalid_record_table_layout_column_count",
                        message="`layout.columnSpecs` length must match `columns` length for record tables.",
                        path=f"{path}.layout.columnSpecs",
                        contextType="table_dataset",
                        contextId=table.id,
                        contextAnchor=table.anchor,
                    )
        elif isinstance(table, GridTableDataset):
            if table.layout is not None and table.layout.columnSpecs:
                if table.columnCount is None:
                    report.add_issue(
                        code="missing_grid_column_count_for_layout",
                        message="`columnCount` is required when `layout.columnSpecs` is present.",
                        path=f"{path}.columnCount",
                        contextType="table_dataset",
                        contextId=table.id,
                        contextAnchor=table.anchor,
                    )
                elif len(table.layout.columnSpecs) != table.columnCount:
                    report.add_issue(
                        code="invalid_grid_table_layout_column_count",
                        message="`layout.columnSpecs` length must match `columnCount` for grid tables.",
                        path=f"{path}.layout.columnSpecs",
                        contextType="table_dataset",
                        contextId=table.id,
                        contextAnchor=table.anchor,
                    )
            for row_index, row in enumerate(table.rows):
                for cell_index, cell in enumerate(row.cells):
                    cell_path = f"{path}.rows[{row_index}].cells[{cell_index}]"
                    if cell.blocks is not None and len(cell.blocks) == 0:
                        report.add_issue(
                            code="empty_grid_cell_blocks",
                            message="Grid cell `blocks` must not be empty.",
                            path=f"{cell_path}.blocks",
                            contextType="table_cell",
                            contextId=table.id,
                            contextAnchor=table.anchor,
                        )
                    for block_index, block in enumerate(cell.blocks or []):
                        block_path = f"{cell_path}.blocks[{block_index}]"
                        if isinstance(block, TextBlock):
                            _validate_text_block_structure(block, path=block_path, section=None, report=report)
                        elif isinstance(block, (ImageBlock, ChartBlock)):
                            continue
                        else:
                            report.add_issue(
                                code="unsupported_grid_cell_block_type",
                                message="Grid cell `blocks` only support `_type='block'`, `_type='image'`, and `_type='chart'`.",
                                path=block_path,
                                contextType="table_cell",
                                contextId=table.id,
                                contextAnchor=table.anchor,
                            )


def _validate_charts(document: Document, *, report: ValidationReport) -> None:
    for index, chart in enumerate(document.datasets.charts):
        path = f"datasets.charts[{index}]"
        if isinstance(chart, PieChartDataset):
            seen: set[str] = set()
            for slice_index, item in enumerate(chart.slices):
                if item.key in seen:
                    report.add_issue(
                        code="duplicate_pie_slice_key",
                        message=f"Duplicate pie slice key: {item.key!r}",
                        path=f"{path}.slices[{slice_index}].key",
                        contextType="chart_dataset",
                        contextId=chart.id,
                        contextAnchor=chart.anchor,
                    )
                seen.add(item.key)
        elif isinstance(chart, DoughnutChartDataset):
            seen: set[str] = set()
            total_value = 0
            if chart.total <= 0:
                report.add_issue(
                    code="invalid_doughnut_total",
                    message="`doughnut.total` must be > 0.",
                    path=f"{path}.total",
                    contextType="chart_dataset",
                    contextId=chart.id,
                    contextAnchor=chart.anchor,
                )
            for slice_index, item in enumerate(chart.slices):
                if item.key in seen:
                    report.add_issue(
                        code="duplicate_doughnut_slice_key",
                        message=f"Duplicate doughnut slice key: {item.key!r}",
                        path=f"{path}.slices[{slice_index}].key",
                        contextType="chart_dataset",
                        contextId=chart.id,
                        contextAnchor=chart.anchor,
                    )
                seen.add(item.key)
                if item.value < 0:
                    report.add_issue(
                        code="invalid_doughnut_slice_value",
                        message="`doughnut.slices[].value` must be >= 0.",
                        path=f"{path}.slices[{slice_index}].value",
                        contextType="chart_dataset",
                        contextId=chart.id,
                        contextAnchor=chart.anchor,
                    )
                total_value += item.value
            if total_value > chart.total:
                report.add_issue(
                    code="invalid_doughnut_sum",
                    message="`sum(doughnut.slices[].value)` must be <= `total`.",
                    path=f"{path}.slices",
                    contextType="chart_dataset",
                    contextId=chart.id,
                    contextAnchor=chart.anchor,
                )


def _validate_section(section: Section, *, path: str, parent_level: int | None, report: ValidationReport) -> None:
    if not isinstance(section.body, list):
        report.add_issue(
            code="invalid_section_body",
            message="Section `body` must be a list.",
            path=f"{path}.body",
            **_ctx(section=section, context_type="section", context_id=section.id, context_anchor=section.anchor, location=f"{path}.body", suggestion="Set `body` to an array of `content` / `subsection` items."),
        )
        return

    if parent_level is None:
        if section.level < 1:
            report.add_issue(
                code="invalid_top_section_level",
                message=f"Top-level section level should be >= 1. Got {section.level}.",
                path=f"{path}.level",
                **_ctx(section=section, context_type="section", context_id=section.id, context_anchor=section.anchor, location=f"{path}.level", suggestion="Top-level sections are normally level 1."),
            )
    elif section.level != parent_level + 1:
        report.add_issue(
            code="invalid_section_level",
            message=f"Child section level should be parent level + 1. Got parent={parent_level}, child={section.level}.",
            path=f"{path}.level",
            **_ctx(section=section, context_type="section", context_id=section.id, context_anchor=section.anchor, location=f"{path}.level", suggestion="Keep formal subsections strictly aligned with the section tree, instead of using heading-like text styles."),
        )

    if section.presentation is not None and section.presentation.titleBlockStyle is not None:
        if section.presentation.titleBlockStyle not in ALLOWED_TEXT_STYLES:
            report.add_issue(
                code="invalid_section_title_block_style",
                message=f"Unsupported `presentation.titleBlockStyle`: {section.presentation.titleBlockStyle!r}",
                path=f"{path}.presentation.titleBlockStyle",
                **_ctx(section=section, context_type="section", context_id=section.id, context_anchor=section.anchor, location=f"{path}.presentation.titleBlockStyle", suggestion="Use one of the protocol-approved text styles for titleBlockStyle, or omit it."),
            )

    for body_index, item in enumerate(section.body):
        item_path = f"{path}.body[{body_index}]"
        if item.itemType not in {"content", "subsection"}:
            report.add_issue(
                code="invalid_body_item_type",
                message=f"Unsupported body itemType: {item.itemType!r}",
                path=f"{item_path}.itemType",
                **_ctx(section=section, context_type="body_item", location=f"{item_path}.itemType", suggestion="Use `itemType = \"content\"` or `itemType = \"subsection\"`."),
            )

        if isinstance(item, ContentItem):
            if not isinstance(item.blocks, list):
                report.add_issue(
                    code="invalid_content_blocks",
                    message="`content.blocks` must be a list.",
                    path=f"{item_path}.blocks",
                    **_ctx(section=section, context_type="content", location=f"{item_path}.blocks", suggestion="Wrap consecutive content blocks in an array."),
                )
                continue
            for block_index, block in enumerate(item.blocks):
                block_path = f"{item_path}.blocks[{block_index}]"
                if isinstance(block, TextBlock):
                    _validate_text_block_structure(block, path=block_path, section=section, report=report)
                elif isinstance(block, CalloutBlock):
                    for sub_index, sub_block in enumerate(block.blocks):
                        _validate_text_block_structure(sub_block, path=f"{block_path}.blocks[{sub_index}]", section=section, report=report)
                elif isinstance(block, MathBlock) and not block.latex.strip():
                    report.add_issue(
                        code="empty_math_block",
                        message="`math_block.latex` must not be empty.",
                        path=f"{block_path}.latex",
                        **_ctx(section=section, context_type="math_block", context_id=block.id, context_anchor=block.anchor, location=f"{block_path}.latex", suggestion="Provide a non-empty LaTeX string."),
                    )
        elif isinstance(item, SubsectionItem):
            _validate_section(item.section, path=f"{item_path}.section", parent_level=section.level, report=report)


def _validate_text_block_structure(block: TextBlock, *, path: str, section: Section | None, report: ValidationReport) -> None:
    if block.style not in ALLOWED_TEXT_STYLES:
        report.add_issue(
            code="invalid_text_style",
            message=f"Unsupported text block style: {block.style!r}",
            path=f"{path}.style",
            **_ctx(section=section, context_type="text_block", location=f"{path}.style", suggestion="Use one of the protocol-approved text styles only."),
        )

    if block.style in {"h1", "h2", "h3", "h4"}:
        report.add_issue(
            code="forbidden_heading_style",
            message="Formal heading styles h1/h2/h3/h4 must not appear in `content.blocks`.",
            path=f"{path}.style",
            **_ctx(section=section, context_type="text_block", location=f"{path}.style", suggestion="Use formal `Section` / `subsection` nodes for document structure, and reserve text styles like `subheading` for in-body visual grouping."),
        )

    if block.listItem is None and block.level is not None:
        report.add_issue(
            code="invalid_list_level_without_list_item",
            message="`level` must not appear without `listItem`.",
            path=f"{path}.level",
            **_ctx(section=section, context_type="text_block", location=f"{path}.level", suggestion="Set both `listItem` and `level`, or remove `level`."),
        )

    if block.level is not None and block.level < 1:
        report.add_issue(
            code="invalid_list_level",
            message="Text block list level must be >= 1.",
            path=f"{path}.level",
            **_ctx(section=section, context_type="text_block", location=f"{path}.level", suggestion="List nesting is 1-based in this package."),
        )

    if block.layout is not None:
        for field_name in ("firstLineIndent", "spaceBefore", "spaceAfter"):
            value = getattr(block.layout, field_name)
            if value is not None and value.value < 0:
                report.add_issue(
                    code="invalid_block_layout_length",
                    message=f"`layout.{field_name}` must be >= 0.",
                    path=f"{path}.layout.{field_name}.value",
                    **_ctx(section=section, context_type="text_block", location=f"{path}.layout.{field_name}.value"),
                )

    mark_def_keys: set[str] = set()
    for mark_def_index, mark_def in enumerate(block.markDefs):
        if mark_def.key in mark_def_keys:
            report.add_issue(
                code="duplicate_mark_def_key",
                message=f"Duplicate markDef key in the same block: {mark_def.key!r}",
                path=f"{path}.markDefs[{mark_def_index}]._key",
                **_ctx(section=section, context_type="text_block", location=f"{path}.markDefs[{mark_def_index}]", suggestion="Keep each markDef key unique within one text block."),
            )
        mark_def_keys.add(mark_def.key)

    for child_index, child in enumerate(block.children):
        if not isinstance(child, Span):
            continue
        for mark_index, mark in enumerate(child.marks):
            if mark not in ALLOWED_DECORATOR_MARKS and mark not in mark_def_keys:
                report.add_issue(
                    code="unresolved_mark_reference",
                    message=f"Span mark {mark!r} is neither a known decorator mark nor a key present in `markDefs[]`.",
                    path=f"{path}.children[{child_index}].marks[{mark_index}]",
                    **_ctx(section=section, context_type="span", location=f"{path}.children[{child_index}]", suggestion="Either use a built-in decorator mark or define the key in `markDefs[]` of the same block."),
                )


def _validate_bibliography(entries: list[BibliographyEntry], *, report: ValidationReport) -> None:
    for index, entry in enumerate(entries):
        path = f"bibliography[{index}]"
        if not entry.displayText:
            report.add_issue(
                code="invalid_bibliography_display_text",
                message="`displayText` is required.",
                path=f"{path}.displayText",
                contextType="bibliography_item",
                contextId=entry.id,
                contextAnchor=entry.anchor,
                location=f"{path}.displayText",
                suggestion="Provide the fully formatted bibliography display text.",
            )
        if entry.type is not None and entry.type == "":
            report.add_issue(
                code="invalid_bibliography_type",
                message="`type` must not be an empty string.",
                path=f"{path}.type",
                contextType="bibliography_item",
                contextId=entry.id,
                contextAnchor=entry.anchor,
                location=f"{path}.type",
                suggestion="Use a normalized bibliography type such as `article`, `book`, `report`, `webpage`, `dataset`, or `other`.",
            )
        if not isinstance(entry.authors, list):
            report.add_issue(
                code="invalid_bibliography_authors",
                message="`authors` must be a list.",
                path=f"{path}.authors",
                contextType="bibliography_item",
                contextId=entry.id,
                contextAnchor=entry.anchor,
                location=f"{path}.authors",
                suggestion="Use a string array, even if there is only one author.",
            )


def _validate_footnotes(entries: list[FootnoteEntry], *, report: ValidationReport) -> None:
    for index, entry in enumerate(entries):
        path = f"footnotes[{index}]"
        if not isinstance(entry.blocks, list):
            report.add_issue(
                code="invalid_footnote_blocks",
                message="`blocks` must be a list.",
                path=f"{path}.blocks",
                contextType="footnote",
                contextId=entry.id,
                contextAnchor=entry.anchor,
                location=f"{path}.blocks",
                suggestion="Store footnote content as a Portable Text block array.",
            )
            continue
        if len(entry.blocks) == 0:
            report.add_issue(
                code="empty_footnote_blocks",
                message="`footnotes[].blocks` should not be empty.",
                path=f"{path}.blocks",
                contextType="footnote",
                contextId=entry.id,
                contextAnchor=entry.anchor,
                location=f"{path}.blocks",
                suggestion="Provide at least one text block for each footnote entry.",
            )
            continue
        for block_index, block in enumerate(entry.blocks):
            _validate_text_block_structure(block, path=f"{path}.blocks[{block_index}]", section=None, report=report)


def _validate_glossary(entries: list[GlossaryEntry], *, report: ValidationReport) -> None:
    for index, entry in enumerate(entries):
        path = f"glossary[{index}]"
        if not entry.term:
            report.add_issue(
                code="invalid_glossary_term",
                message="`term` is required.",
                path=f"{path}.term",
                contextType="glossary_term",
                contextId=entry.id,
                contextAnchor=entry.anchor,
                location=f"{path}.term",
                suggestion="Glossary entries should have a stable visible term string.",
            )
        if not entry.definition:
            report.add_issue(
                code="invalid_glossary_definition",
                message="`definition` is required.",
                path=f"{path}.definition",
                contextType="glossary_term",
                contextId=entry.id,
                contextAnchor=entry.anchor,
                location=f"{path}.definition",
                suggestion="Provide a non-empty definition for glossary links to resolve meaningfully.",
            )
        if entry.aliases is not None:
            if not isinstance(entry.aliases, list):
                report.add_issue(
                    code="invalid_glossary_aliases",
                    message="`aliases` must be a list.",
                    path=f"{path}.aliases",
                    contextType="glossary_term",
                    contextId=entry.id,
                    contextAnchor=entry.anchor,
                    location=f"{path}.aliases",
                    suggestion="Use a string array for aliases.",
                )
            elif len(set(entry.aliases)) != len(entry.aliases):
                report.add_issue(
                    code="duplicate_glossary_alias",
                    message="Duplicate alias strings found in one glossary entry.",
                    path=f"{path}.aliases",
                    severity="warning",
                    contextType="glossary_term",
                    contextId=entry.id,
                    contextAnchor=entry.anchor,
                    location=f"{path}.aliases",
                    suggestion="Remove repeated alias strings inside the same glossary entry.",
                )


def _validate_section_references(section: Section, *, path: str, resolver: DocumentResolver, report: ValidationReport) -> None:
    for body_index, item in enumerate(section.body):
        item_path = f"{path}.body[{body_index}]"
        if isinstance(item, ContentItem):
            for block_index, block in enumerate(item.blocks):
                block_path = f"{item_path}.blocks[{block_index}]"
                if isinstance(block, TextBlock):
                    _validate_text_block_inline_references(block, path=block_path, section=section, resolver=resolver, report=report)
                elif isinstance(block, ImageBlock):
                    if resolver.resolve_xref(target_type="image_asset", target_id=block.imageRef) is None:
                        report.add_issue(
                            code="unresolved_image_ref",
                            message=f"`imageRef` cannot be resolved: {block.imageRef!r}",
                            path=f"{block_path}.imageRef",
                            **_ctx(section=section, context_type="image", context_id=block.id, context_anchor=block.anchor, location=f"{block_path}.imageRef", suggestion="Add the corresponding entry to `assets.images`, or fix the referenced id."),
                        )
                elif isinstance(block, ChartBlock):
                    if resolver.resolve_xref(target_type="chart_dataset", target_id=block.chartRef) is None:
                        report.add_issue(
                            code="unresolved_chart_ref",
                            message=f"`chartRef` cannot be resolved: {block.chartRef!r}",
                            path=f"{block_path}.chartRef",
                            **_ctx(section=section, context_type="chart", context_id=block.id, context_anchor=block.anchor, location=f"{block_path}.chartRef", suggestion="Add the corresponding entry to `datasets.charts`, or fix the referenced id."),
                        )
                elif isinstance(block, TableBlock):
                    if resolver.resolve_xref(target_type="table_dataset", target_id=block.tableRef) is None:
                        report.add_issue(
                            code="unresolved_table_ref",
                            message=f"`tableRef` cannot be resolved: {block.tableRef!r}",
                            path=f"{block_path}.tableRef",
                            **_ctx(section=section, context_type="table", context_id=block.id, context_anchor=block.anchor, location=f"{block_path}.tableRef", suggestion="Add the corresponding entry to `datasets.tables`, or fix the referenced id."),
                        )
                elif isinstance(block, CalloutBlock):
                    for sub_index, sub_block in enumerate(block.blocks):
                        _validate_text_block_structure(sub_block, path=f"{block_path}.blocks[{sub_index}]", section=section, report=report)
                        _validate_text_block_inline_references(sub_block, path=f"{block_path}.blocks[{sub_index}]", section=section, resolver=resolver, report=report)
        elif isinstance(item, SubsectionItem):
            _validate_section_references(item.section, path=f"{item_path}.section", resolver=resolver, report=report)


def _validate_grid_table_dataset_references(document: Document, *, resolver: DocumentResolver, report: ValidationReport) -> None:
    for table_index, table in enumerate(document.datasets.tables):
        if not isinstance(table, GridTableDataset):
            continue
        table_path = f"datasets.tables[{table_index}]"
        for row_index, row in enumerate(table.rows):
            for cell_index, cell in enumerate(row.cells):
                cell_path = f"{table_path}.rows[{row_index}].cells[{cell_index}]"
                for block_index, block in enumerate(cell.blocks or []):
                    block_path = f"{cell_path}.blocks[{block_index}]"
                    if isinstance(block, TextBlock):
                        _validate_text_block_inline_references(block, path=block_path, section=None, resolver=resolver, report=report)
                    elif isinstance(block, ImageBlock):
                        if resolver.resolve_xref(target_type="image_asset", target_id=block.imageRef) is None:
                            report.add_issue(
                                code="unresolved_grid_cell_image_ref",
                                message=f"Grid cell `imageRef` cannot be resolved: {block.imageRef!r}",
                                path=f"{block_path}.imageRef",
                                contextType="image",
                                contextId=block.id,
                                contextAnchor=block.anchor,
                                location=f"{block_path}.imageRef",
                                suggestion="Add the corresponding entry to `assets.images`, or fix the referenced id.",
                            )
                    elif isinstance(block, ChartBlock):
                        if resolver.resolve_xref(target_type="chart_dataset", target_id=block.chartRef) is None:
                            report.add_issue(
                                code="unresolved_grid_cell_chart_ref",
                                message=f"Grid cell `chartRef` cannot be resolved: {block.chartRef!r}",
                                path=f"{block_path}.chartRef",
                                contextType="chart",
                                contextId=block.id,
                                contextAnchor=block.anchor,
                                location=f"{block_path}.chartRef",
                                suggestion="Add the corresponding entry to `datasets.charts`, or fix the referenced id.",
                            )


def _validate_text_block_inline_references(block: TextBlock, *, path: str, section: Section | None, resolver: DocumentResolver, report: ValidationReport) -> None:
    for child_index, child in enumerate(block.children):
        child_path = f"{path}.children[{child_index}]"
        if isinstance(child, XRef):
            if not resolver.is_supported_target_type(child.targetType):
                report.add_issue(
                    code="unsupported_xref_target_type",
                    message=f"Unsupported `xref.targetType`: {child.targetType!r}. Supported values include: {sorted(resolver.supported_target_types())}",
                    path=f"{child_path}.targetType",
                    **_ctx(section=section, context_type="xref", location=f"{child_path}.targetType", suggestion="Use one of the resolver-supported semantic types, such as `section`, `figure`, `table`, `equation`, `footnote`, or `bibliography`."),
                )
                continue
            target = resolver.resolve_xref(target_type=child.targetType, target_id=child.targetId)
            if target is None:
                report.add_issue(
                    code="unresolved_xref",
                    message=f"`xref` target cannot be resolved: targetType={child.targetType!r}, targetId={child.targetId!r}",
                    path=child_path,
                    **_ctx(section=section, context_type="xref", location=child_path, suggestion="Check both `targetType` and `targetId`, and confirm that the target object exists exactly once in the document."),
                )
        elif isinstance(child, CitationRef):
            target = resolver.resolve_xref(target_type="bibliography_item", target_id=child.targetId)
            if target is None:
                report.add_issue(
                    code="unresolved_citation_ref",
                    message=f"`citation_ref` target cannot be resolved: {child.targetId!r}",
                    path=f"{child_path}.targetId",
                    **_ctx(section=section, context_type="citation_ref", location=f"{child_path}.targetId", suggestion="Create a matching bibliography entry under the top-level `bibliography` registry."),
                )
            else:
                _ = _ctx_from_target(target)
        elif isinstance(child, FootnoteRef):
            target = resolver.resolve_xref(target_type="footnote", target_id=child.targetId)
            if target is None:
                report.add_issue(
                    code="unresolved_footnote_ref",
                    message=f"`footnote_ref` target cannot be resolved: {child.targetId!r}",
                    path=f"{child_path}.targetId",
                    **_ctx(section=section, context_type="footnote_ref", location=f"{child_path}.targetId", suggestion="Create a matching top-level footnote entry."),
                )
        elif isinstance(child, GlossaryTerm):
            target = resolver.resolve_xref(target_type="glossary_term", target_id=child.targetId)
            if target is None:
                report.add_issue(
                    code="unresolved_glossary_term",
                    message=f"`glossary_term` target cannot be resolved: {child.targetId!r}",
                    path=f"{child_path}.targetId",
                    **_ctx(section=section, context_type="glossary_term_ref", location=f"{child_path}.targetId", suggestion="Create a matching top-level glossary entry."),
                )
        elif isinstance(child, InlineMath):
            if not child.latex.strip():
                report.add_issue(
                    code="empty_inline_math",
                    message="`inline_math.latex` must not be empty.",
                    path=f"{child_path}.latex",
                    **_ctx(section=section, context_type="inline_math", location=f"{child_path}.latex", suggestion="Provide a non-empty LaTeX string."),
                )
