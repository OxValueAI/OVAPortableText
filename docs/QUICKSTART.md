# Quick Start / 快速开始

This page shows the shortest practical path from installation to a validated JSON export.  
本页展示从安装到导出一份通过校验的 JSON 的最短实用路径。

---

## 1. Install / 安装

```bash
pip install OVAPortableText
```

Import name in Python: `ova_portable_text`  
Python 导入名：`ova_portable_text`

---

## 2. Create your first document / 创建第一份文档

```python
from ova_portable_text import create_document

report = create_document(
    title="Quick Start Demo",
    language="en",
    documentType="valuationReport",
    strict_ids=True,
)

sec = report.new_section(id="sec-intro", level=1, title="Introduction")
sec.append_paragraph("Hello OVAPortableText.")

report.assert_valid()
print(report.to_json(indent=2))
```

What happens here / 这里发生了什么：

1. `create_document(...)` creates a typed top-level `Document`  
   `create_document(...)` 创建强类型顶层 `Document`
2. `new_section(...)` adds a formal section node  
   `new_section(...)` 新建正式章节节点
3. `append_paragraph(...)` appends a Portable Text paragraph block  
   `append_paragraph(...)` 追加一个 Portable Text 段落块
4. `assert_valid()` performs final protocol validation  
   `assert_valid()` 做最终协议校验

---

## 3. Add registry-backed content / 添加引用型内容

The protocol separates top-level registries from body instances. In `report.v1.1`, image instances may omit `id`, and text blocks can carry `layout`.  
协议把“顶层 registry”与“正文实例”分开处理。在 `report.v1.1` 中，图片实例可以省略 `id`，文本块还可以携带 `layout`。

### Example / 示例

```python
from ova_portable_text import (
    create_document,
    image_asset_url,
    image_block,
    table_column,
    table_dataset,
    table_block,
)

report = create_document(title="Registry Demo", language="en", documentType="valuationReport")

report.add_image_asset(
    image_asset_url(
        id="img-cover",
        url="https://example.com/cover.png",
        alt="Cover image",
        mimeType="image/png",
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

sec = report.new_section(id="sec-1", level=1, title="Body")
sec.append_block(image_block(image_ref="img-cover", id="fig-cover"))
sec.append_block(table_block(id="tbl-summary", table_ref="table-summary"))

report.assert_valid()
```

---

## 4. Add references / 添加参考文献、脚注、术语表

```python
from ova_portable_text import (
    bibliography_entry,
    create_document,
    footnote_entry,
    glossary_entry,
    footnote_ref,
    glossary_term,
    paragraph,
)

report = create_document(title="References Demo", language="en", documentType="valuationReport")

report.add_bibliography_entry(
    bibliography_entry(
        id="cite-fu-2026",
        display_text="Fu et al. (2026)",
        type="article",
        title="Patent valuation under technical utility theory",
        authors=["Fu"],
        year=2026,
    )
)

report.add_footnote(
    footnote_entry(
        id="fn-1",
        blocks=[paragraph("This is a footnote.")],
    )
)

report.add_glossary_entry(
    glossary_entry(
        id="term-dcf",
        term="DCF",
        definition="Discounted Cash Flow",
    )
)

sec = report.new_section(id="sec-1", level=1, title="Text")
sec.append_paragraph(
    "DCF means ",
    glossary_term("term-dcf"),
    ". See note",
    footnote_ref("fn-1"),
    ".",
)
```

---

## 5. Validate during development / 开发阶段做校验

```python
validation = report.validate()
print(validation.to_text())
```

Recommended usage / 推荐用法：

- use `validate()` repeatedly while authoring  
  写作过程中反复使用 `validate()`
- use `assert_valid()` before exporting or handoff  
  导出或交接下游前使用 `assert_valid()`

---

## 6. Save and reload JSON / 保存并回读 JSON

```python
from ova_portable_text import Document

report.save_json("build/report.json")
restored = Document.load_json("build/report.json")
restored.assert_valid()
```

---

## 7. What to read next / 下一步看什么

- `docs/API_REFERENCE.md`
- `docs/EXAMPLES.md`
- `examples/`
