# OVAPortableText

**OVAPortableText** is a Python authoring package for building JSON documents that conform to the **OVA Report Profile v1.0** protocol.  
**OVAPortableText** 是一个 Python 端的协议生成包，用于创建符合 **OVA Report Profile v1.0** 协议的 JSON 文档。

It is **not** a PDF renderer. Its job is to help Python code produce a typed, validated, protocol-aligned document payload that can be handed off to a downstream renderer.  
它**不是** PDF 渲染器。它的职责是帮助 Python 代码以强类型、可校验、可维护的方式生成协议 JSON，再交给下游渲染器处理。

---

## 1. What this package is for / 这个包解决什么问题

Use OVAPortableText when you need to:  
适合在以下场景使用 OVAPortableText：

- build report JSON in Python instead of hand-writing nested dictionaries  
  在 Python 中构建报告 JSON，而不是手工拼接多层嵌套 dict
- keep document structure aligned with the protocol  
  让文档结构始终与协议保持一致
- validate registry references, IDs, anchors, sections, and text-layer semantics before handoff  
  在交给下游之前先校验 registry 引用、ID、anchor、章节树和文本层语义
- generate reusable assets / datasets / bibliography / footnotes / glossary registries  
  生成可复用的 assets / datasets / bibliography / footnotes / glossary 顶层 registry
- hand a stable JSON contract to a Java or other downstream renderer  
  给 Java 或其他下游渲染器提供稳定 JSON 合同

OVAPortableText is especially useful when the rendering stack and the authoring stack are separated.  
当“内容生成端”和“渲染端”分离时，OVAPortableText 尤其有价值。

---

## 2. What this package is not / 这个包不做什么

OVAPortableText does **not** try to:  
OVAPortableText **不**负责：

- lay out final PDF pages  
  最终 PDF 页面排版
- decide exact typography, spacing, page breaking, or printer behavior  
  精确的字体、间距、分页、打印行为
- replace your Java / web / document renderer  
  替代你的 Java / Web / 文档渲染器

The package ends at **structured JSON generation + validation + debugging support**.  
本包的职责边界到 **结构化 JSON 生成 + 校验 + 调试辅助** 为止。

---

## 3. Current protocol scope implemented by the package / 当前包已实现的协议范围

This package intentionally implements the **stable, author-facing subset** of Report Profile v1.0.  
当前包刻意只实现了 Report Profile v1.0 中**已经稳定、适合作者侧使用的那部分能力**。

Currently implemented / 当前已实现：

- top-level document skeleton  
  顶层文档骨架
  - `schemaVersion / meta / theme / assets / datasets / bibliography / footnotes / glossary / sections`
- section-tree-first authoring  
  以章节树为核心的 authoring 方式
- Portable Text style text blocks  
  Portable Text 风格文本块
  - `_type="block"`
  - `_type="span"`
  - `marks / markDefs`
  - `listItem / level`
- protocol text styles  
  协议定义的文本样式
  - `normal`
  - `blockquote`
  - `caption`
  - `figure_caption`
  - `table_caption`
  - `equation_caption`
  - `smallprint`
  - `lead`
  - `quote_source`
  - `subheading`
- decorator marks  
  装饰 marks
  - `strong`
  - `em`
  - `underline`
  - `code`
- inline references / annotations  
  行内引用 / 注解
  - `link`
  - `xref`
  - `citation_ref`
  - `footnote_ref`
  - `glossary_term`
  - `inline_math`
  - `hard_break`
- block objects  
  块级对象
  - `image`
  - `chart`
  - `table`
  - `math_block`
  - `callout`
- registries  
  顶层 registry
  - `assets.images / logos / backgrounds / icons / attachments`
  - `datasets.charts (pie)`
  - `datasets.tables (record / grid)`
  - `datasets.metrics`
  - `bibliography`
  - `footnotes`
  - `glossary`
- validation, resolver, numbering, round-trip IO  
  校验、解析器、编号、读写回转

Not yet first-class authoring helpers / 暂未形成一等 authoring helper 的能力：

- reserved taxonomy items that exist in the protocol but are not yet stabilized in the package  
  协议里已预留、但还未在包里稳定暴露 helper 的 taxonomy 项
- renderer-side visual contracts  
  渲染器侧视觉合同
- PDF pagination / page layout decisions  
  PDF 分页 / 页面布局决策

---

## 4. Repository layout / 仓库结构

```text
OVAPortableText/
├── src/ova_portable_text/   # package source / 包源码
├── examples/                # runnable examples / 可直接运行的示例脚本
├── docs/                    # user-facing docs / 面向使用者的文档
├── tests/                   # test suite / 测试集
├── README.md                # project overview / 项目总览
├── PROTOCOL.md   			 # OVAPortableText PROTOCOL / 协议文档
├── CHANGELOG.md             # release history / 版本变更历史
└── pyproject.toml           # packaging config / 打包配置
```

Recommended reading order for new users:  
新用户建议阅读顺序：

1. `README.md`
1. `PROTOCOL.md`
2. `docs/QUICKSTART.md`
3. `docs/API_REFERENCE.md`
4. `examples/`

---

## 5. Installation / 安装

### 5.1 Install from PyPI / 从 PyPI 安装

```bash
pip install OVAPortableText
```

### 5.2 Local editable install / 本地可编辑安装

```bash
pip install -e .
```

### 5.3 Python import name / Python 导入名

```python
import ova_portable_text
```

Package name on PyPI: `OVAPortableText`  
PyPI 包名：`OVAPortableText`

Import name in Python: `ova_portable_text`  
Python 导入名：`ova_portable_text`

---

## 6. Quick start / 快速开始

```python
from ova_portable_text import create_document

report = create_document(
    title="Patent Valuation Report",
    language="en",
    documentType="valuationReport",
    strict_ids=True,
)

intro = report.new_section(id="sec-intro", level=1, title="Executive Summary")
intro.append_lead("This report is generated as protocol-aligned JSON.")
intro.append_paragraph("The renderer will consume the exported JSON payload.")

method = intro.new_subsection(id="sec-intro-method", title="Methodology")
method.append_paragraph("The protocol separates registries from body instances.")

report.assert_valid()
print(report.to_json(indent=2))
```

Why this is the recommended style / 为什么推荐这种写法：

- start from one `Document`  
  从一个 `Document` 开始
- append sections and registries incrementally  
  逐步追加 section 和 registry
- validate before handoff  
  在交接下游前先校验

---

## 7. Core authoring workflow / 核心 authoring 工作流

### 7.1 Build the registries first / 先准备 registry

For reusable resources and datasets, prefer:  
对于会被正文引用的资源和数据，优先使用 registry：

- `assets.images / logos / backgrounds / icons / attachments`
- `datasets.charts / tables / metrics`
- `bibliography / footnotes / glossary`

### 7.2 Build the section tree second / 再构建章节树

Sections are the formal document structure.  
章节树是正式文档结构。

Use:  
推荐用法：

- `Document.new_section(...)`
- `Section.new_subsection(...)`
- `Section.append_paragraph(...)`
- `Section.append_*_with_caption(...)`

### 7.3 Validate early / 尽早校验

```python
validation = report.validate()
print(validation.to_text())
```

### 7.4 Fail fast before handoff / 交接下游前强制校验

```python
report.assert_valid()
```

### 7.5 Export JSON / 导出 JSON

```python
report.save_json("build/report.json")
```

---

## 8. Capability map / 能力地图

### 8.1 Top-level metadata and registries / 顶层元信息与 registry

You can author:  
可构造：

- `meta`
- `theme`
- `assets`
- `datasets`
- `bibliography`
- `footnotes`
- `glossary`
- `sections`

### 8.2 Text layer / 文本层

You can author:  
可构造：

- paragraphs
- lists
- blockquotes
- captions
- lead paragraphs
- subheadings
- decorator marks
- annotation `markDefs`
- inline references

### 8.3 Registry-backed block objects / registry 引用型块对象

You can author body instances that reference top-level registries:  
可以在正文中构造引用顶层 registry 的实例对象：

- `image` → `assets.images[]`
- `chart` → `datasets.charts[]`
- `table` → `datasets.tables[]`
- `math_block`
- `callout`

### 8.4 Table modes / 表格模式

The package supports both protocol table modes:  
当前包支持协议中的两种表格模式：

- `record` for regular structured tables  
  `record`：规则结构化表格
- `grid` for irregular / merged / layout-oriented tables  
  `grid`：不规则 / 跨行跨列 / 偏版式表格

### 8.5 Image-source model / 图片来源模型

The package uses the protocol’s pure `imageSource` model:  
当前包使用协议中的纯 `imageSource` 模型：

- `kind="url"`
- `kind="embedded"`

---

## 9. Example scripts / 样例代码总览

All examples live under `examples/`.  
所有示例脚本都在 `examples/` 目录下。

### Basic authoring / 基础 authoring

- `examples/minimal_report.py`  
  Smallest valid document. / 最小可用文档
- `examples/save_and_load_json_demo.py`  
  Save JSON to disk and load it back. / JSON 落盘与读回
- `examples/builder_numbering_roundtrip_demo.py`  
  Builder API + numbering + round-trip. / builder API + 编号 + 回转

### Text and inline semantics / 文本层与行内语义

- `examples/marks_and_lists_report.py`  
  Decorator marks, lists, and text styles. / 装饰 marks、列表和文本样式
- `examples/inline_objects_report.py`  
  Inline refs such as `xref`, `citation_ref`, `footnote_ref`, `glossary_term`, `hard_break`. / 行内引用对象示例
- `examples/references_and_marks_demo.py`  
  MarkDefs-based inline annotations, bibliography / footnotes / glossary linking, and inline math. / 基于 markDefs 的行内注解、参考文献/脚注/术语引用与行内公式

### Registries, assets, and datasets / registry、资源与数据集

- `examples/registry_blocks_report.py`  
  Registry-first images / charts / tables. / 先 registry 后正文引用
- `examples/extended_registries_demo.py`  
  Logos, backgrounds, icons, attachments, metrics. / logo、背景、图标、附件、指标集
- `examples/image_sources_demo.py`  
  URL and embedded image sources for images / logos / backgrounds / icons. / URL 与内嵌图片来源模式
- `examples/grid_table_demo.py`  
  `record` and `grid` table datasets, including duplicate headers and irregular layouts. / `record` 与 `grid` 表格模式示例

### Validation and debugging / 校验与调试

- `examples/validation_context_demo.py`  
  Validation output with context. / 带上下文的校验输出
- `examples/validation_report.py`  
  End-to-end validation report generation. / 端到端校验报告示例

### Full reports / 更完整的报告示例

- `examples/full_report_workflow_demo.py`  
  End-to-end authoring workflow. / 端到端报告构造流程
- `examples/patent_valuation_style_report.py`  
  Business-shaped valuation report example. / 更接近业务报告的估值示例

---

## 10. Documentation map / 文档导航

- `docs/QUICKSTART.md`  
  Start here for first-time usage. / 新手快速上手
- `docs/API_REFERENCE.md`  
  Practical API map for the public surface. / 面向使用者的 API 地图
- `docs/EXAMPLES.md`  
  Example index and recommended reading order. / 示例索引与阅读顺序
- `docs/REAL_WORLD_RECIPES.md`  
  Practical authoring patterns. / 更贴近真实业务的写法模式
- `docs/PROTOCOL_ALIGNMENT.md`  
  What part of the protocol is already aligned. / 协议对齐范围说明
- `docs/VALIDATION_AND_RESOLVER.md`  
  Validation, resolver, and debugging workflow. / 校验、解析器与调试流程
- `docs/TEST_MATRIX.md`  
  Test coverage map. / 测试覆盖范围
- `docs/USER_TESTING_CHECKLIST.md`  
  Manual user testing checklist. / 人工回测清单
- `docs/PUBLISHING_CHECKLIST.md`  
  Release checklist. / 发布清单

---

## 11. Development notes / 开发说明

### 11.1 Recommended development command / 推荐开发命令

```bash
python -m pytest -q
```

### 11.2 Build sanity check / 打包自检

```bash
python -m build
twine check dist/*
```

### 11.3 Release note / 发布说明

The current package version is **0.1.3**.  
当前包版本为 **0.1.3**。

This branch of the package is aligned to the current Report Profile v1.0 protocol draft used in this repository.  
当前这版包对齐的是本仓库内维护的 Report Profile v1.0 协议版本。

---

## 12. License / 许可

See `LICENSE`.  
详见 `LICENSE`。
