# OVAPortableText

A Python package for building JSON documents that conform to the **OVAPortableText / Report Profile v1.0** protocol.

OVAPortableText 的目标不是直接渲染 PDF，而是让 Python 端**以强类型、可校验、可维护**的方式，生成符合协议的 JSON；再交给 Java 侧去渲染 PDF。

## Current scope / 当前实现范围

Step 9 currently includes:

- top-level document / section skeleton
- content body items
- Portable Text `block` / `span`
- protocol-approved text styles for v1
- decorator marks + annotation `markDefs`
- list semantics: `listItem` / `level`
- first batch of inline objects:
  - `hard_break`
  - `xref`
  - `citation_ref`
  - `footnote_ref`
  - `glossary_term`
- first batch of block objects:
  - `image`
  - `chart`
  - `table`
  - `math_block`
  - `callout`
- first typed registries:
  - `assets.images / logos / backgrounds / icons / attachments`
  - `datasets.tables / charts(pie) / metrics`
  - `bibliography / footnotes / glossary`
- append-style builder APIs
- section / figure / table / equation numbering helpers
- global resolver / index builder
- structured document validation report with issue context
- detailed bilingual comments / 详细中英文双语注释
- round-trip helpers: `from_dict()` / `from_json()` / `save_json()` / `load_json()`

## Install / 安装

### Local development / 本地开发

```bash
pip install -e .
```

### Release-style build test / 类发布方式构建测试

```bash
python -m pip install --upgrade build
python -m build
python -m venv .venv-test-wheel
source .venv-test-wheel/bin/activate
pip install dist/*.whl
```

## Quick start / 快速开始

```python
from ova_portable_text import create_document, section

report = create_document(
    title="Patent Valuation Report",
    language="en",
    documentType="report",
)

intro = report.new_section(id="sec-1", level=1, title="Executive Summary")
intro.append_paragraph("This is the opening introduction of the chapter.")

background = intro.new_subsection(id="sec-1-1", title="Background")
background.append_paragraph("This is the body text of subsection 1.1.")

intro.append_paragraph("This is a concluding paragraph after subsection 1.1.")

report.assert_valid()
print(report.to_json())
```

## Recommended workflow / 推荐工作流

1. create one `Document`
2. append sections and registries
3. call `validate()` during development
4. call `assert_valid()` before exporting or handing off to Java
5. export with `to_dict()` / `to_json()`

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

### 3) Validate before export / 导出前校验

```python
validation = report.validate()
print(validation.to_text())
report.assert_valid()
```

### 4) Save JSON to disk and read it back / 落盘 JSON 再读回

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

Step 8 adds maintenance-friendly context in each issue, such as:
第 8 步开始，每条 issue 会尽量附带更适合维护的上下文，例如：
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

## Included docs / 附带文档

- `docs/QUICKSTART.md`
- `docs/VALIDATION_AND_RESOLVER.md`
- `docs/TEST_MATRIX.md`
- `docs/REAL_WORLD_RECIPES.md`
- `docs/USER_TESTING_CHECKLIST.md`
- `docs/PROTOCOL_ALIGNMENT.md`

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


## Release readiness / 发布准备

Step 9 adds release-oriented engineering pieces:

- `LICENSE`
- `CHANGELOG.md`
- `py.typed`
- GitHub Actions CI workflow
- `docs/API_REFERENCE.md`
- `docs/PUBLISHING_CHECKLIST.md`

## Version / 版本

```python
import ova_portable_text
print(ova_portable_text.__version__)
```
