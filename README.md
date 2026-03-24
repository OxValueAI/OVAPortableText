# OVAPortableText

A Python package for building JSON documents that conform to the **OVAPortableText / Report Profile v1.0** protocol.

OVAPortableText 的目标不是直接渲染 PDF，而是让 Python 端**以强类型、可校验、可维护**的方式，生成符合协议的 JSON；再交给渲染器去渲染 PDF。

## Current scope / 当前实现范围

The package currently implements an intentionally selected, production-usable subset of the v1.0 protocol rather than every reserved taxonomy item.
当前实现是 v1.0 协议里一个**可生产使用的已落地子集**，并不是把规范里所有预留 taxonomy 一次性全部实现。

Implemented today:

- top-level document / section skeleton
- content body items
- Portable Text `block` / `span`
- protocol-approved text styles for v1
- decorator marks + annotation `markDefs`
- list semantics: `listItem` / `level`
- inline objects:
  - `hard_break`
  - `xref`
  - `citation_ref`
  - `footnote_ref`
  - `glossary_term`
- block objects:
  - `image`
  - `chart`
  - `table`
  - `math_block`
  - `callout`
- typed registries:
  - `assets.images / logos / backgrounds / icons / attachments`
  - `datasets.tables / charts(pie) / metrics`
  - `bibliography / footnotes / glossary`
- append-style builder APIs
- section / figure / table / equation numbering helpers
- global resolver / index builder
- structured document validation report with issue context
- round-trip helpers: `from_dict()` / `from_json()` / `save_json()` / `load_json()`

Not yet implemented as first-class authoring helpers:

- reserved or future taxonomy items that are present in the protocol but not yet exposed as stable Python helpers
- a full generated symbol reference for every internal class or helper

This boundary is intentional: the package focuses on the pieces that are already stable enough for Python authoring and downstream renderer handoff.
这个边界是有意为之：当前包优先把已经稳定、适合 Python 生产 JSON 和交给下游渲染器的部分做好。

## Install / 安装

### PIP

```bash
pip install OVAPortableText
```

## Quick start / 快速开始

```python
from ova_portable_text import create_document

report = create_document(
    title="Patent Valuation Report",
    language="en",
    documentType="report",
    strict_ids=True,
)

intro = report.new_section(id="sec-1", level=1, title="Executive Summary")
intro.append_paragraph("This is the opening introduction of the chapter.")

background = intro.new_subsection(id="sec-1-1", title="Background")
background.append_paragraph("This is the body text of subsection 1.1.")

intro.append_paragraph_to_last_content("This is a concluding paragraph after subsection 1.1.")

report.assert_valid()
print(report.to_json())
```

## Recommended workflow / 推荐工作流

1. create one `Document`
2. append sections and registries
3. enable `strict_ids=True` during authoring when you want duplicate IDs to fail early
4. call `validate()` during development
5. call `assert_valid()` before exporting or handing off to Java
6. export with `to_dict()` / `to_json()`

## Common authoring patterns / 常见写法

### 1) Append sections naturally / 顺手追加章节

```python
from ova_portable_text import create_document

report = create_document(title="Demo", language="en")
sec = report.new_section(id="sec-intro", level=1, title="Introduction")
sec.append_lead("This report summarises the project scope.")
sec.append_bullet_item("Point A")
sec.append_bullet_item("Point B")
```

### 2) Add registry resources, then reference them / 先放 registry，再在正文引用

```python
from ova_portable_text import (
    create_document,
    image_asset,
    pie_chart_from_parallel_arrays,
    table_column,
    table_dataset,
)

report = create_document(title="Data Demo", language="en")

report.add_image_asset(
    image_asset(
        id="img-cover",
        src="https://example.com/cover.png",
        alt="Cover image",
    )
)

report.add_table_dataset(
    table_dataset(
        id="table-summary",
        columns=[
            table_column(key="year", header="Year"),
            table_column(key="revenue", header="Revenue"),
        ],
        rows=[
            {"year": "2024", "revenue": "12.3M"},
            {"year": "2025", "revenue": "13.8M"},
        ],
    )
)

report.add_chart_dataset(
    pie_chart_from_parallel_arrays(
        id="chart-area-share",
        area_en=["Technology", "Finance"],
        area_zh=["技术", "金融"],
        value=[60, 40],
    )
)
```

### 3) Fail duplicate IDs earlier when needed / 需要时尽早拦截重复 ID

```python
from ova_portable_text import create_document

report = create_document(title="Strict IDs", language="en", strict_ids=True)
report.new_section(id="sec-1", level=1, title="Intro")

# Raises immediately instead of waiting until validate()
report.new_section(id="sec-1", level=1, title="Duplicate Intro")
```

### 4) Keep a continuous content flow / 保持连续 content 语义

```python
from ova_portable_text import create_document

report = create_document(title="Flow Demo", language="en")
sec = report.new_section(id="sec-1", level=1, title="Intro")

sec.append_paragraph("Opening paragraph.")
sec.append_paragraph_to_last_content("Still part of the same content item.")

sub = sec.new_subsection(id="sec-1-1", title="Background")
sub.append_paragraph("Subsection text.")

sec.append_paragraph_to_last_content("This now starts a new content item after the subsection.")
```

### 5) Validate before export / 导出前校验

```python
validation = report.validate()
print(validation.to_text())
report.assert_valid()
```

### 6) Save JSON to disk and read it back / 落盘 JSON 再读回

```python
from pathlib import Path
from ova_portable_text import create_document, Document

report = create_document(title="Disk Round Trip", language="en")
report.new_section(id="sec-1", level=1, title="Intro").append_paragraph("Saved to disk.")

out_path = report.save_json(Path("build/report.json"))
restored = Document.load_json(out_path)
print(restored.meta.title)
```

## Validation and resolver / 校验与解析器

`validate()` returns a structured `ValidationReport`.
`validate()` 会返回结构化的 `ValidationReport`。

Each issue tries to include maintenance-friendly context, such as:
每条 issue 会尽量附带更适合维护的上下文，例如：

- `sectionId`
- `sectionTitle`
- `contextType`
- `contextId`
- `contextAnchor`
- `suggestion`

```python
validation = report.validate()
for issue in validation.issues:
    print(issue.code, issue.sectionId, issue.contextType, issue.suggestion)
```

Resolver usage:

```python
resolver = report.build_resolver()
print(resolver.debug_summary())
print(resolver.resolve_xref(target_type="section", target_id="sec-1"))
```

## Protocol-aligned authoring notes / 与协议对齐的写作说明

- `Section.numbering` only accepts `"auto"`, `"none"`, or `"manual"`.
- `strict_ids=True` is an authoring-time safety helper and is **not** serialized into the final JSON.
- `append_*_to_last_content(...)` helpers are ergonomic helpers for preserving the protocol meaning of a continuous `content` item.
- The recommended chart dataset structure is the protocol-native pie `slices[]` shape; `pie_chart_from_parallel_arrays(...)` is a compatibility/helper layer for older parallel-array inputs.

## Included docs / 附带文档

- `docs/QUICKSTART.md`
- `docs/API_REFERENCE.md`
- `docs/VALIDATION_AND_RESOLVER.md`
- `docs/TEST_MATRIX.md`
- `docs/REAL_WORLD_RECIPES.md`
- `docs/USER_TESTING_CHECKLIST.md`
- `docs/PROTOCOL_ALIGNMENT.md`
- `docs/PUBLISHING_CHECKLIST.md`

## Included examples / 附带样例

- `examples/minimal_report.py`
- `examples/inline_objects_report.py`
- `examples/registry_blocks_report.py`
- `examples/validation_report.py`
- `examples/marks_and_lists_report.py`
- `examples/builder_numbering_roundtrip_demo.py`
- `examples/extended_registries_demo.py`
- `examples/validation_context_demo.py`
- `examples/full_report_workflow_demo.py`
- `examples/save_and_load_json_demo.py`
- `examples/patent_valuation_style_report.py`

## Version / 版本

```python
import ova_portable_text
print(ova_portable_text.__version__)
```
