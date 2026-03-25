from __future__ import annotations

"""
Document validation for OVAPortableText.
OVAPortableText 的文档校验器。

This validator intentionally stays close to the protocol's v1 guidance:
本校验器刻意贴近协议 v1 的建议：
- schemaVersion must exist / `schemaVersion` 必填
- sections/body structure must be valid / `sections` 与 `body` 结构必须合法
- top-level registries should exist / 顶层 registry 应存在
- section nesting levels should be self-consistent / section 层级应自洽
- all references should resolve / 所有引用应能解析
- formal heading styles should not appear inside content.blocks
  `content.blocks` 中不应出现正式标题样式

Step 8 improves the *quality* of validation output:
第 8 步重点提升的是校验输出质量：
- richer issue context / 更丰富的 issue 上下文
- better maintenance hints / 更明确的维护提示
- readable report summaries / 更易读的报告摘要
"""

from .block_objects import CalloutBlock, ChartBlock, ImageBlock, TableBlock
from .content import ALLOWED_TEXT_STYLES, ContentItem, Span, TextBlock
from .document import Document
from .exceptions import ValidationReport
from .inline import CitationRef, FootnoteRef, GlossaryTerm, InlineMath, XRef
from .registry import BibliographyEntry, FootnoteEntry, GlossaryEntry
from .resolver import DocumentResolver, ResolvedTarget
from .section import Section, SubsectionItem

ALLOWED_DECORATOR_MARKS = {"strong", "em", "underline", "code"}


def validate_document(document: Document) -> ValidationReport:
    """
    Validate the whole document and return a structured report.
    校验整份文档，并返回结构化报告。
    """
    report = ValidationReport()

    if not document.schemaVersion:
        report.add_issue(
            code="missing_schema_version",
            message="`schemaVersion` is required.",
            path="schemaVersion",
            contextType="document",
            suggestion="Set `schemaVersion` to `report.v1.0` unless you intentionally target another protocol version.",
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

    return report


def assert_valid_document(document: Document) -> Document:
    """
    Validate and raise on errors.
    校验文档；若存在 error 则抛错。
    """
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
    """
    Build common context kwargs for `ValidationReport.add_issue()`.
    为 `ValidationReport.add_issue()` 构建通用上下文参数。

    This helper keeps the validator code readable while still attaching
    rich issue context.
    这个 helper 的意义是：
    既让校验器代码保持可读，又能给 issue 挂上较丰富的上下文信息。
    """
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
    """
    Build context kwargs from a resolved target.
    根据 resolver target 构建上下文参数。
    """
    return {
        "location": target.location,
        "contextType": target.targetType,
        "contextId": target.id,
        "contextAnchor": target.anchor,
        "sectionId": target.sectionId,
        "sectionTitle": target.sectionTitle,
        "suggestion": suggestion,
    }


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


def _validate_text_block_inline_references(block: TextBlock, *, path: str, section: Section, resolver: DocumentResolver, report: ValidationReport) -> None:
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
