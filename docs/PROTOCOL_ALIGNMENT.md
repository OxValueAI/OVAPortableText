# Protocol Alignment / 协议对齐说明

This page explains how OVAPortableText 0.1.3 aligns with the current Report Profile v1.0 protocol draft used in this repository.  
本文档说明 OVAPortableText 0.1.3 与当前仓库内维护的 Report Profile v1.0 协议草案之间的对齐关系。

---

## 1. Aligned top-level structure / 已对齐的顶层结构

The package aligns to this top-level shape:  
当前包对齐如下顶层结构：

- `schemaVersion`
- `meta`
- `theme`
- `assets`
- `datasets`
- `bibliography`
- `footnotes`
- `glossary`
- `sections`

`schemaVersion` defaults to `report.v1.0`.  
`schemaVersion` 默认值为 `report.v1.0`。

---

## 2. Aligned structure-first authoring model / 已对齐的“结构优先” authoring 模型

The package aligns to the protocol’s structure-first approach:  
当前包对齐协议里的“结构优先”思路：

- formal document structure is represented by `sections`
- section children are represented by `subsection`
- content flow is represented by `content.blocks[]`
- registry data is separated from body instances

---

## 3. Aligned text layer / 已对齐的文本层

### Implemented / 已实现

- Portable Text style `block`
- Portable Text style `span`
- `marks / markDefs`
- list semantics via `listItem / level`
- protocol-approved text styles
- decorator marks
- inline reference annotations

### Current package scope / 当前包实现范围

Supported block styles / 支持的 block.style：

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

Supported decorator marks / 支持的装饰 mark：

- `strong`
- `em`
- `underline`
- `code`

Supported inline annotations / 支持的行内注解：

- `link`
- `xref`
- `citation_ref`
- `footnote_ref`
- `glossary_term`
- `inline_math`
- `hard_break`

---

## 4. Aligned block objects / 已对齐的块级对象

Implemented as first-class models / 已作为一等模型实现：

- `image`
- `chart`
- `table`
- `math_block`
- `callout`

These appear inside `content.blocks[]` as body instances.  
这些对象作为正文实例出现在 `content.blocks[]` 中。

---

## 5. Aligned registries / 已对齐的 registry

### Assets / 资源 registry

Implemented / 已实现：

- `assets.images`
- `assets.logos`
- `assets.backgrounds`
- `assets.icons`
- `assets.attachments`

Image-like assets use the protocol’s `imageSource` model.  
图片类资源采用协议中的 `imageSource` 模型。

### Datasets / 数据集 registry

Implemented / 已实现：

- `datasets.charts` → currently formalized as pie chart datasets  
  当前正式细化为 pie chart dataset
- `datasets.tables` → supports both `record` and `grid`  
  同时支持 `record` 与 `grid`
- `datasets.metrics`

### Reference registries / 引用型 registry

Implemented / 已实现：

- `bibliography`
- `footnotes`
- `glossary`

---

## 6. Validation and resolver alignment / 校验与解析器对齐

The package currently aligns to the protocol by validating:  
当前包通过以下校验与协议对齐：

- duplicate IDs
- duplicate anchors
- registry reference existence
- text-style validity
- markDef integrity
- xref target resolution
- image-source shape
- table dataset shape
- pie chart dataset shape
- bibliography / footnote / glossary reference integrity

It also builds a resolver for globally addressable targets.  
同时会构建一个 resolver，用于全局可解析目标的索引与定位。

---

## 7. Current intentional boundary / 当前刻意保留的边界

The package does **not** yet claim to fully implement every reserved taxonomy item named by the protocol.  
当前包**并不**声称已经完整实现协议里所有预留 taxonomy 项。

Examples of intentionally partial areas / 当前刻意保持部分实现的区域：

- non-pie chart detailed schemas  
  非 pie 图表的细化数据合同
- metrics detailed schema  
  metrics 的完整细字段合同
- renderer-specific visual behavior  
  渲染器侧视觉行为
- final PDF pagination / layout  
  最终 PDF 分页 / 布局

---

## 8. Practical interpretation / 实际理解方式

The package should be understood as:  
可以把当前包理解为：

- a **protocol authoring package**  
  一个**协议 authoring 包**
- a **validation and debugging layer**  
  一个**校验与调试层**
- a **handoff boundary** between Python and the renderer  
  一个 Python 与渲染器之间的**交接边界层**
