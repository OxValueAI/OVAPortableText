# Examples / 示例索引

This page lists the runnable examples shipped with the repository and explains what each one demonstrates.  
本页列出仓库内自带的可运行示例，并说明每个示例主要演示什么能力。

---

## Recommended reading order / 推荐阅读顺序

If you are new to the package, read in this order:  
如果你是第一次使用这个包，建议按以下顺序阅读：

1. `examples/minimal_report.py`
2. `examples/marks_and_lists_report.py`
3. `examples/registry_blocks_report.py`
4. `examples/full_report_workflow_demo.py`
5. The specialized demos that match your use case  
   再看与你业务最相关的专项示例

---

## Example catalog / 示例目录

### 1. Minimal and lifecycle basics / 最小示例与生命周期基础

- `minimal_report.py`  
  The smallest valid report document. / 最小可用报告文档。
- `save_and_load_json_demo.py`  
  Save JSON to disk and read it back. / JSON 落盘与读回。
- `builder_numbering_roundtrip_demo.py`  
  Builder-style authoring, numbering helpers, round-trip restore. / builder 风格 authoring、编号辅助与回转。

### 2. Text layer / 文本层

- `marks_and_lists_report.py`  
  Decorator marks, markDefs, lists, and text styles. / 装饰 marks、markDefs、列表和文本样式。
- `inline_objects_report.py`  
  Inline objects such as `xref`, `citation_ref`, `footnote_ref`, `glossary_term`, `hard_break`. / 行内对象示例。
- `references_and_marks_demo.py`  
  MarkDefs-based references, bibliography / footnotes / glossary integration, inline math. / 基于 markDefs 的引用、参考文献/脚注/术语整合、行内公式。

### 3. Registry-backed body content / registry 引用型正文内容

- `registry_blocks_report.py`  
  Images, charts, and tables referenced from registries. / 从 registry 引用图片、图表和表格。
- `image_sources_demo.py`  
  URL and embedded image-source models. / URL 与内嵌 imageSource 模型。
- `grid_table_demo.py`  
  `record` and `grid` table datasets, including duplicate headers and irregular layouts. / `record` 与 `grid` 表格模式。
- `extended_registries_demo.py`  
  Logos, backgrounds, icons, attachments, and metric datasets. / logo、背景、图标、附件和指标数据集。

### 4. Validation and debugging / 校验与调试

- `validation_context_demo.py`  
  Demonstrates validation output with context. / 演示带上下文的校验输出。
- `validation_report.py`  
  A more complete validation report workflow. / 更完整的校验报告流程。

### 5. Full-report examples / 完整报告示例

- `full_report_workflow_demo.py`  
  End-to-end protocol authoring workflow. / 端到端协议 authoring 流程。
- `patent_valuation_style_report.py`  
  A business-shaped valuation report. / 接近业务报告形态的估值报告示例。

---

## Tips for using the examples / 使用示例时的建议

- Start by running the file directly.  
  先直接运行示例脚本。
- Read the generated JSON before you read the code in detail.  
  先看生成的 JSON，再细看代码。
- Compare a simple example with a full-report example.  
  对比最小示例与完整报告示例。
- Reuse example fragments instead of copying whole files blindly.  
  优先复用示例片段，而不是整份文件机械复制。
