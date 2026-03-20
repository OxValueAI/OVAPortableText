# API Reference

This page is a practical API map instead of a generated full symbol dump.
本文档是实用型 API 地图，而不是自动生成的完整符号清单。

## Main entry points / 主要入口

- `create_document(...)`
- `document(...)`
- `Document.from_meta(...)`
- `Document.from_dict(...)`
- `Document.from_json(...)`

## Core authoring objects / 核心写作对象

- `Document`
- `Section`
- `TextBlock`
- `Span`
- `ImageBlock`
- `ChartBlock`
- `TableBlock`

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

## Export / 导出

- `to_dict(exclude_none=True)`
- `to_json(indent=2, exclude_none=True)`
- `save_json(path, indent=2, exclude_none=True)`
- `load_json(path)`

## Recommended import style / 推荐导入方式

```python
from ova_portable_text import create_document, section, paragraph, xref
```


## Small ergonomics helpers / 小型易用性 helper

- `Section.append_paragraphs(*paragraphs)`
- `Section.append_bullet_items(*items, level=1)`
- `Section.append_number_items(*items, level=1)`
