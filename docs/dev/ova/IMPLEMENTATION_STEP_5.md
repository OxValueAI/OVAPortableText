# OVAPortableText - Implementation Step 5

## 本步目标 / Goal of this step

第 5 步的目标是把包进一步做成“更像成熟文档类库”的使用体验，重点补齐：

1. `marks / markDefs`
2. `link` annotation
3. `listItem / level`
4. 更顺手的 builder-style text API
5. 对上述文本能力的基础校验

也就是把前面已经完成的：
- document / section / body 结构
- inline object
- block objects
- registry
- resolver / validator

进一步往 Portable Text 的文本原生能力上补齐一层。

---

## 本步新增内容 / What was added in Step 5

### 1. 文本 marks 能力 / Native text marks

新增支持：

- decorator marks
  - `strong`
  - `em`
  - `underline`
  - `code`
- annotation-style `markDefs`
  - `link`
  - generic custom annotation

对应模型：

- `MarkDefBase`
- `LinkMarkDef`
- `AnnotationMarkDef`
- `MarkDef`

文件：

- `src/ova_portable_text/text.py`

---

### 2. 列表能力 / List semantics

`TextBlock` 现在支持：

- `listItem`
- `level`

因此可以表达：

- 无序列表项
- 有序列表项
- 多级嵌套列表项

当前规则：

- 有 `listItem` 但没写 `level` 时，默认补 `level = 1`
- `level` 必须 `>= 1`
- 不能只写 `level` 不写 `listItem`

文件：

- `src/ova_portable_text/text.py`

---

### 3. 更顺手的 helper API / More ergonomic helper API

新增 helper：

- `marked(text, *marks)`
- `strong(text)`
- `em(text)`
- `underline(text)`
- `code_span(text)`
- `link_def(...)`
- `annotation_def(...)`
- `bullet_item(...)`
- `number_item(...)`
- `blocks_from_items(...)`

并增强：

- `paragraph(..., mark_defs=..., list_item=..., level=...)`

文件：

- `src/ova_portable_text/helpers.py`

---

### 4. Section 层 append API 增强 / More convenient Section append API

`Section` 新增或增强：

- `append_text_block(...)`
- `append_paragraph(..., mark_defs=...)`
- `append_list_item(...)`
- `append_bullet_item(...)`
- `append_number_item(...)`
- `append_blockquote(...)`
- `append_lead(...)`
- `append_smallprint(...)`
- `append_caption(...)`

这使得你可以更自然地写：

```python
sec.append_paragraph("Hello ", strong("world"), "!")
sec.append_bullet_item("Point A")
sec.append_number_item("Step 1", level=1)
sec.append_number_item("Step 1.1", level=2)
```

文件：

- `src/ova_portable_text/section.py`

---

### 5. 文本层校验增强 / Validation improvements for text layer

validator 新增检查：

- `markDefs[]` 内 `_key` 是否重复
- `Span.marks[]` 中的每个 mark 是否可解析：
  - 要么是已知 decorator mark
  - 要么是当前 block 的 `markDefs[]` 中存在的 `_key`
- `level` 是否错误使用

新增错误码：

- `duplicate_mark_def_key`
- `unresolved_mark_reference`
- `invalid_list_level_without_list_item`
- `invalid_list_level`

文件：

- `src/ova_portable_text/validator.py`

---

### 6. 新示例 / New example

新增示例文件：

- `examples/marks_and_lists_report.py`

该示例演示：

- decorator marks
- `link` markDefs
- bullet / numbered list

---

### 7. 新测试 / New tests

新增测试：

- `tests/test_marks_and_lists.py`
- `tests/test_mark_validation.py`

当前测试结果：

- `14 passed`

---

## 使用示例 / Example usage

```python
from ova_portable_text import (
    create_document,
    em,
    link_def,
    section,
    span,
    strong,
)

report = create_document(title="Text Demo", language="en")
sec = section(id="sec-text", level=1, title="Text Features")

sec.append_paragraph(
    "This paragraph contains ",
    strong("bold"),
    ", ",
    em("italic"),
    " text.",
)

sec.append_paragraph(
    "Visit ",
    span("OpenAI", marks=["m-link-openai"]),
    ".",
    mark_defs=[
        link_def(
            key="m-link-openai",
            href="https://openai.com",
            title="OpenAI",
            open_in_new_tab=True,
        )
    ],
)

sec.append_bullet_item("Point A")
sec.append_number_item("Step 1")
sec.append_number_item("Step 1.1", level=2)

report.append_section(sec)
report.assert_valid()
print(report.to_json())
```

---

## 这一步的价值 / Why this step matters

这一步之后，这个包已经不只是：

- 能拼 document / section / registry JSON
- 能做基础引用校验

而是进一步具备了比较接近实际写报告所需的文本层表达能力：

- 行内加粗/斜体/下划线
- 链接 annotation
- 列表项与层级
- 更自然的 append 风格 API

对你后面手写 Python 生成 JSON 会更顺手，也更接近 Portable Text 本来的使用心智。

---

## 建议的下一步 / Recommended next step

建议进入 **Step 6**：

1. theme / meta 的更强类型化
2. numbering / label 的辅助生成
3. 更细的 document builder API
4. import / export utilities（从普通 Python dict 转模型）
5. 更丰富的 resolver 查询接口

如果继续沿当前路线推进，下一步最值得做的是：

**“更强的 builder API + 编号/标签辅助层”**

这样你写完整报告时会更省手。
