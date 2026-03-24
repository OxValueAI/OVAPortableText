# API Reference / API 参考

This page is a practical API map for the public surface of OVAPortableText.  
本文档是 OVAPortableText 公开接口的实用型 API 地图。

It is intentionally not a generated full symbol dump.  
它刻意不是自动生成的“全量符号索引”。

---

## 1. Main entry points / 主要入口

### Document creation / 文档创建

- `create_document(...)`
- `document(...)`  
  Alias of `create_document`. / `create_document` 的别名。
- `Document.from_dict(...)`
- `Document.from_json(...)`
- `Document.load_json(...)`

Typical arguments / 常用参数：

- `title`
- `language` → current package validation: `"zh"` or `"en"`  
  当前包校验：`"zh"` 或 `"en"`
- `documentType` → current package validation: `"valuationReport"`  
  当前包校验：`"valuationReport"`
- `strict_ids=False`

---

## 2. Core authoring objects / 核心 authoring 对象

- `Document`
- `DocumentMeta`
- `Section`
- `ContentItem`
- `TextBlock`
- `Span`

Body block objects / 正文块对象：

- `ImageBlock`
- `ChartBlock`
- `TableBlock`
- `MathBlock`
- `CalloutBlock`

---

## 3. Text helpers / 文本层 helper

### Inline text constructors / 行内文本构造

- `span(text, marks=None)`
- `marked(text, *marks)`
- `strong(text)`
- `em(text)`
- `underline(text)`
- `code_span(text)`

### Mark-definition helpers / markDef helper

- `link_def(key=..., href=...)`
- `xref_def(key=..., target_id=..., target_type=...)`
- `citation_ref_def(key=..., target_id=...)`
- `footnote_ref_def(key=..., target_id=...)`
- `glossary_term_def(key=..., target_id=...)`
- `inline_math_def(key=..., latex=...)`
- `annotation_def(key=..., type=..., data=...)`

### Block constructors / 文本块构造

- `paragraph(*parts, style="normal", mark_defs=None, list_item=None, level=None)`
- `bullet_item(*parts, level=1, mark_defs=None)`
- `number_item(*parts, level=1, mark_defs=None)`
- `blocks_from_items(...)`

### Inline object helpers / 行内对象 helper

- `hard_break()`
- `xref(target_id=..., target_type=None)`
- `citation_ref(target_id)`
- `footnote_ref(target_id)`
- `glossary_term(target_id)`
- `inline_math(latex)`

---

## 4. Section helpers / Section 级 helper

### Create sections / 创建章节

- `Document.new_section(...)`
- `Document.append_section(section)`
- `section(...)`
- `Section.new_subsection(...)`
- `Section.append_subsection(section)`

### Append text / 追加文本

- `Section.append_paragraph(...)`
- `Section.append_paragraphs(...)`
- `Section.append_lead(...)`
- `Section.append_blockquote(...)`
- `Section.append_subheading(...)`
- `Section.append_smallprint(...)`
- `Section.append_quote_source(...)`

### Append lists / 追加列表

- `Section.append_bullet_item(...)`
- `Section.append_bullet_items(...)`
- `Section.append_number_item(...)`
- `Section.append_number_items(...)`

### Continuous-content helpers / 连续 content helper

- `Section.append_to_last_content(block)`
- `Section.append_blocks_to_last_content(*blocks)`
- `Section.append_text_block_to_last_content(block)`
- `Section.append_paragraph_to_last_content(...)`

Use these when multiple blocks should remain in the same protocol `content` item.  
当多段内容应继续停留在同一个协议 `content` item 中时，使用这组 helper。

### Append block objects / 追加块对象

- `Section.append_block(...)`
- `Section.append_blocks(...)`
- `Section.append_callout(...)`
- `Section.append_image_with_caption(...)`
- `Section.append_chart_with_caption(...)`
- `Section.append_table_with_caption(...)`
- `Section.append_math_with_caption(...)`

---

## 5. Registry helpers / registry helper

### Assets / 资源

- `image_asset(...)`
- `image_asset_url(...)`
- `image_asset_embedded(...)`
- `image_asset_from_file(...)`
- `logo_asset(...)`
- `background_asset(...)`
- `icon_asset(...)`
- `attachment_asset(...)`

### Datasets / 数据集

- `table_column(...)`
- `table_dataset(...)` → returns `RecordTableDataset`  
  返回 `RecordTableDataset`
- `grid_table_cell(...)`
- `grid_table_row(...)`
- `grid_table_dataset(...)` → returns `GridTableDataset`  
  返回 `GridTableDataset`
- `pie_slice(...)`
- `pie_chart_dataset(...)`
- `pie_chart_from_parallel_arrays(...)`
- `metric_value(...)`
- `metric_dataset(...)`

### Registry content / 引用型内容

- `image_block(...)`
- `chart_block(...)`
- `table_block(...)`
- `math_block(...)`
- `callout(...)`

### Bibliography / footnotes / glossary

- `bibliography_entry(...)`
- `footnote_entry(...)`
- `glossary_entry(...)`

---

## 6. Main registry models / 主要 registry 模型

### Assets / 资源模型

- `ImageAsset`
- `LogoAsset`
- `BackgroundAsset`
- `IconAsset`
- `AttachmentAsset`
- `ImageSourceUrl`
- `ImageSourceEmbedded`
- `ImageSource`
- `AssetsRegistry`

### Datasets / 数据集模型

- `RecordTableDataset`
- `GridTableDataset`
- `GridTableRow`
- `GridTableCell`
- `TableDataset`  
  Discriminated union of `record | grid`. / `record | grid` 判别联合类型。
- `TableColumn`
- `PieChartDataset`
- `PieSlice`
- `MetricDataset`
- `MetricValue`
- `DatasetsRegistry`

### Reference registries / 引用型 registry 模型

- `BibliographyEntry`
- `FootnoteEntry`
- `GlossaryEntry`

---

## 7. Validation / 校验

- `Document.validate()`
- `Document.assert_valid()`
- `validate_document(document)`
- `assert_valid_document(document)`
- `ValidationReport`
- `ValidationIssue`
- `DocumentValidationError`

Typical usage / 典型用法：

```python
validation = report.validate()
print(validation.to_text())
report.assert_valid()
```

---

## 8. Resolver / 解析器

- `Document.build_resolver()`
- `DocumentResolver.get(...)`
- `DocumentResolver.get_by_id(...)`
- `DocumentResolver.get_by_anchor(...)`
- `DocumentResolver.resolve_xref(...)`
- `DocumentResolver.debug_summary()`

Use the resolver when you need to inspect what is globally addressable in the document.  
当你需要检查文档中哪些对象在全局可解析时，使用 resolver。

---

## 9. Numbering / 编号

- `Document.build_numbering()`
- `NumberingConfig`
- `DocumentNumbering`
- `NumberedTarget`
- `Section.numbering`
- `NumberingMode = Literal["auto", "none", "manual"]`

---

## 10. Export and round-trip / 导出与回转

- `Document.to_dict(exclude_none=True)`
- `Document.to_json(indent=2, exclude_none=True)`
- `Document.save_json(path, indent=2, exclude_none=True)`
- `Document.from_dict(data)`
- `Document.from_json(text)`
- `Document.load_json(path)`

---

## 11. Package-level enums and constrained values / 包内枚举与约束值

### Text styles / 文本样式

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

### Decorator marks / 装饰 mark

- `strong`
- `em`
- `underline`
- `code`

### List styles / 列表类型

- `bullet`
- `number`

### Image source kinds / 图片来源类型

- `url`
- `embedded`

### Current package metadata validation / 当前包对 meta 的校验

- `language` / `locale`: `"zh"` or `"en"`
- `documentType`: `"valuationReport"`
- `confidentiality`: `"public" | "user" | "internal" | "confidential"`
- `reportType`: `"startupCompany" | "innovationTeam" | "patent" | "loan"`
- `date`: `YYYY-MM-DD`
- `generatedAt`: RFC 3339 / ISO 8601 datetime string
