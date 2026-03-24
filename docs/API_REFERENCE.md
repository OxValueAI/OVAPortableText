# API Reference

This page is a practical API map instead of a generated full symbol dump.
本文档是实用型 API 地图，而不是自动生成的完整符号清单。

## Scope note / 范围说明

This package intentionally documents the stable, author-facing subset of the protocol that is already implemented.
本文档刻意只覆盖已经稳定、面向作者使用的那部分 API。

That means:

- the protocol may reserve more taxonomy items than this package currently exposes as helpers
- internal classes may exist without being recommended as public authoring entry points

## Main entry points / 主要入口

- `create_document(...)`
- `document(...)`
- `Document.from_meta(...)`
- `Document.from_dict(...)`
- `Document.from_json(...)`

Commonly used constructor options:

- `title`
- `language`
- `documentType`
- `strict_ids=False`

## Core authoring objects / 核心写作对象

- `Document`
- `Section`
- `TextBlock`
- `Span`
- `ImageBlock`
- `ChartBlock`
- `TableBlock`
- `MathBlock`
- `CalloutBlock`

## Registries / 注册表对象

- `ImageAsset`
- `LogoAsset`
- `BackgroundAsset`
- `IconAsset`
- `AttachmentAsset`
- `TableDataset`
- `PieChartDataset`
- `MetricDataset`
- `BibliographyEntry`
- `FootnoteEntry`
- `GlossaryEntry`

## Validation / 校验

- `Document.validate()`
- `Document.assert_valid()`
- `ValidationReport`
- `DocumentValidationError`

## Resolver / 解析器

- `Document.build_resolver()`
- `DocumentResolver.resolve_xref(...)`
- `DocumentResolver.get_by_id(...)`
- `DocumentResolver.get_by_anchor(...)`
- `DocumentResolver.debug_summary()`

## Numbering / 编号辅助

- `Document.build_numbering()`
- `NumberingConfig`
- `DocumentNumbering`
- `Section.numbering`
- `NumberingMode = Literal["auto", "none", "manual"]`

## Export / 导出

- `to_dict(exclude_none=True)`
- `to_json(indent=2, exclude_none=True)`
- `save_json(path, indent=2, exclude_none=True)`
- `load_json(path)`

## Recommended import style / 推荐导入方式

```python
from ova_portable_text import (
    create_document,
    section,
    paragraph,
    xref,
    citation_ref,
)
```

## Authoring helpers / 常用 authoring helper

### Document-level helpers

- `Document.new_section(...)`
- `Document.append_section(...)`
- `Document.add_image_asset(...)`
- `Document.add_chart_dataset(...)`
- `Document.add_table_dataset(...)`
- `Document.add_bibliography_entry(...)`
- `Document.add_footnote(...)`
- `Document.add_glossary_entry(...)`

### Section-level helpers

- `Section.append_paragraph(...)`
- `Section.append_paragraphs(*paragraphs)`
- `Section.append_lead(...)`
- `Section.append_bullet_item(...)`
- `Section.append_bullet_items(*items, level=1)`
- `Section.append_number_item(...)`
- `Section.append_number_items(*items, level=1)`
- `Section.new_subsection(...)`

### Continuous-content helpers

- `Section.append_to_last_content(block)`
- `Section.append_blocks_to_last_content(*blocks)`
- `Section.append_text_block_to_last_content(block)`
- `Section.append_paragraph_to_last_content(...)`

Use these when you want multiple blocks to remain in the same protocol `content` item until a subsection boundary naturally starts a new one.
当你希望多个 block 仍然属于同一个协议 `content` item 时，优先使用这些 helper；遇到 `subsection` 边界后，再自然开始新的 `content`。

## Strict ID mode / 严格 ID 模式

`create_document(..., strict_ids=True)` enables fail-early duplicate-ID checks for the most common authoring paths.
`create_document(..., strict_ids=True)` 会在最常见的 authoring 路径上，把重复 ID 尽量前置到添加当下报错。

Important notes:

- this mode is authoring-time only
- it does **not** serialize into final JSON
- full validation is still available through `validate()` / `assert_valid()`

## Image helpers / 图片 helper

- `image_asset(...)`
- `image_asset_url(...)`
- `image_asset_embedded(...)`
- `image_asset_from_file(...)`

Image assets now use the protocol-native `imageSource` field.
图片资源现在使用协议原生的 `imageSource` 字段。

## Compatibility helpers / 兼容性 helper

- `pie_chart_from_parallel_arrays(...)`

This helper converts older parallel-array pie inputs into the protocol-native pie `slices[]` dataset structure.
这个 helper 会把旧的并行数组饼图输入，转换成协议原生的 pie `slices[]` 数据结构。
