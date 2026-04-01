# API Reference / API 参考

This page is a practical map of the public API in OVAPortableText `v0.2.0`, aligned to `report.v1.1`.
本文档是 OVAPortableText `v0.2.0` 的实用 API 地图，对齐 `report.v1.1`。

---

## 1. Main entry points / 主要入口

### Document creation / 文档创建

- `create_document(...)`
- `document(...)` — alias of `create_document`
- `Document.from_dict(...)`
- `Document.from_json(...)`
- `Document.load_json(...)`

Default schema version:

- `Document.schemaVersion == "report.v1.1"`

Common arguments / 常用参数：

- `title`
- `language`
- `documentType`
- `theme`
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

Important v1.1 note / v1.1 重点：

- `ImageBlock(imageRef="...")` is valid
- `ImageBlock.id` and `ImageBlock.anchor` are optional
- `imageRef` is required

---

## 3. Theme and block layout / theme 与块级 layout

### Theme models / theme 模型

- `ThemeConfig`
- `BlockStyleDefault`
- `BlockLayout`
- `LengthValue`

### Theme helpers / theme helper

- `block_layout(...)`
- `length_em(value)`
- `length_pt(value)`

### v1.1 formal fields / v1.1 正式字段

- `theme.blockStyleDefaults`
- `TextBlock.layout`

Supported `BlockLayout` fields:

- `textAlign`
- `firstLineIndent`
- `spaceBefore`
- `spaceAfter`

Supported `textAlign` values:

- `left`
- `center`
- `right`
- `justify`

Supported length units:

- `em`
- `pt`

---

## 4. Text helpers / 文本层 helper

### Inline text constructors / 行内文本构造

- `span(text, marks=None)`
- `marked(text, *marks)`
- `strong(text)`
- `em(text)`
- `underline(text)`
- `code_span(text)`

### Mark-definition helpers / markDef helper

- `link_def(key=..., href=...)`
- `annotation_def(key=..., type=..., data=...)`

### Block constructors / 文本块构造

- `paragraph(*parts, style="normal", mark_defs=None, list_item=None, level=None, layout=None)`
- `bullet_item(*parts, level=1, mark_defs=None)`
- `number_item(*parts, level=1, mark_defs=None)`
- `blocks_from_items(...)`

### Inline object helpers / 行内对象 helper

- `hard_break()`
- `xref(target_type=..., target_id=...)`
- `citation_ref(target_id)`
- `footnote_ref(target_id)`
- `glossary_term(target_id)`
- `inline_math(latex)`

---

## 5. Section helpers / Section 级 helper

### Create sections / 创建章节

- `Document.new_section(...)`
- `Document.append_section(section)`
- `section(...)`
- `Section.new_subsection(...)`
- `Section.append_subsection(section)`

### Append text / 追加文本

- `Section.append_paragraph(..., layout=None)`
- `Section.append_paragraphs(...)`
- `Section.append_lead(...)`
- `Section.append_blockquote(...)`
- `Section.append_subheading(...)`
- `Section.append_smallprint(...)`
- `Section.append_caption(...)`
- `Section.append_figure_caption(...)`
- `Section.append_table_caption(...)`
- `Section.append_equation_caption(...)`

### Append lists / 追加列表

- `Section.append_bullet_item(...)`
- `Section.append_bullet_items(...)`
- `Section.append_number_item(...)`
- `Section.append_number_items(...)`

### Continuous-content helpers / 连续 content helper

- `Section.append_to_last_content(block)`
- `Section.append_blocks_to_last_content(*blocks)`
- `Section.append_text_block_to_last_content(block)`
- `Section.append_paragraph_to_last_content(..., layout=None)`

### Append block objects / 追加块对象

- `Section.append_block(...)`
- `Section.append_blocks(...)`
- `Section.append_callout(...)`
- `Section.append_image(image_ref=..., id=None, anchor=None)`
- `Section.append_chart(...)`
- `Section.append_table(...)`
- `Section.append_math(...)`
- `Section.append_image_with_caption(image_ref=..., id=None, caption=...)`
- `Section.append_chart_with_caption(...)`
- `Section.append_table_with_caption(...)`
- `Section.append_math_with_caption(...)`

---

## 6. Registry helpers / registry helper

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
- `record_table_dataset(...)`
- `grid_table_cell(...)`
- `grid_table_row(...)`
- `grid_table_dataset(...)` → returns `GridTableDataset`
- `table_column_spec_auto()`
- `table_column_spec_weight(value)`
- `table_layout(*column_specs)`
- `pie_slice(...)`
- `pie_chart_dataset(...)`
- `pie_chart_from_parallel_arrays(...)`
- `metric_value(...)`
- `metric_dataset(...)`

### Registry-backed block instances / 正文引用实例

- `image_block(image_ref=..., id=None, anchor=None)`
- `chart_block(id=..., chart_ref=..., anchor=None)`
- `table_block(id=..., table_ref=..., anchor=None)`
- `math_block(id=..., latex=..., anchor=None)`
- `callout(id=..., blocks=None, anchor=None)`

### Bibliography / footnotes / glossary

- `bibliography_entry(...)`
- `footnote_entry(...)`
- `glossary_entry(...)`

---

## 7. Main registry models / 主要 registry 模型

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
- `TableColumn`
- `TableLayout`
- `TableColumnSpec`
- `TableColumnWidth`
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

## 8. v1.1 table notes / v1.1 表格说明

### Table-level layout / 表级 layout

Both record and grid tables now support:

- `layout.columnSpecs[]`

Width modes:

- `auto`
- `weight`

Rules:

- `mode="auto"` → no `value`
- `mode="weight"` → `value > 0`
- `weight` is relative weight, not percent

### Grid cell blocks / grid 单元格 blocks

`GridTableCell.blocks` is now a restricted block array.

Currently supported block types:

- `_type="block"`
- `_type="image"`

Not supported in cell blocks:

- `chart`
- `table`
- `math_block`
- `callout`

---

## 9. Validation / 校验

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

Validator additions relevant to v1.1:

- checks `theme.blockStyleDefaults` keys
- checks `TextBlock.layout`
- checks table `layout.columnSpecs`
- checks grid cell image refs
- warns when image-like assets omit `alt`

---

## 10. Resolver / 解析器

- `Document.build_resolver()`
- `DocumentResolver.get(...)`
- `DocumentResolver.get_by_anchor(...)`
- `DocumentResolver.resolve_xref(...)`
- `DocumentResolver.debug_summary()`

Use the resolver when you need to inspect what is globally addressable in the document.
当你需要检查文档中哪些对象在全局可解析时，使用 resolver。

---

## 11. Numbering / 编号

- `Document.build_numbering()`
- `NumberingConfig`
- `DocumentNumbering`
- `NumberedTarget`
