# Test Matrix / 测试矩阵

This page summarizes what the current test suite is intended to cover.  
本页总结当前测试集主要覆盖哪些层次。

---

## 1. Skeleton / 文档骨架层

Covered / 已覆盖：

- minimal document export
- top-level skeleton presence
- section / subsection structure
- numbering behavior

---

## 2. Text layer / 文本层

Covered / 已覆盖：

- text styles
- spans
- decorator marks
- markDefs
- lists
- inline objects
- inline reference helpers

---

## 3. Block objects / 块级对象层

Covered / 已覆盖：

- `image`
- `chart`
- `table`
- `math_block`
- `callout`

---

## 4. Registry layer / registry 层

Covered / 已覆盖：

- image assets and image-source modes
- logos / backgrounds / icons / attachments
- pie chart datasets
- table datasets (`record` / `grid`)
- metrics registry basics
- bibliography / footnotes / glossary

---

## 5. Validation / 校验层

Covered / 已覆盖：

- success cases
- expected failure cases
- duplicate IDs / duplicate anchors
- bad references
- mark validation
- xref resolution
- issue context output

---

## 6. Resolver / 解析器层

Covered / 已覆盖：

- global ID indexing
- anchor indexing
- xref lookup
- semantic figure alias behavior
- debug summary output

---

## 7. Round-trip / 回转层

Covered / 已覆盖：

- `to_dict()` + `from_dict()`
- `to_json()` + `from_json()`
- `save_json()` + `load_json()`

---

## 8. Example smoke runs / 示例冒烟运行

Selected runnable examples are executed as smoke tests.  
一部分可运行示例会被纳入冒烟测试。

This ensures that public-facing example code does not silently drift away from the package API.  
这能防止面向用户的示例代码悄悄偏离真实 API。
