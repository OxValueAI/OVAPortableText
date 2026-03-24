# Real-world Authoring Recipes / 真实业务写法建议

This page collects practical writing patterns that work well in real report-generation code.  
本页整理在真实报告生成代码里更好用的一些写法模式。

---

## 1. Start from typed objects, not raw dicts / 从强类型对象开始，而不是手拼 dict

Prefer this:  
推荐这样写：

```python
report = create_document(...)
sec = report.new_section(...)
sec.append_paragraph(...)
```

Avoid starting from raw nested dicts unless you are writing a migration layer.  
除非你在写迁移层，否则不建议一开始就手拼嵌套 dict。

---

## 2. Registry first, body later / 先 registry，后正文

For resources or datasets that may be referenced multiple times, add the registry entry first.  
对于可能被多处引用的资源或数据，先建 registry 条目。

Typical order / 典型顺序：

1. add `assets.*` or `datasets.*`
2. add bibliography / footnotes / glossary if needed
3. create sections
4. append body blocks using `*Ref`

---

## 3. Keep captions adjacent / caption 优先相邻放置

The protocol prefers:  
协议更推荐：

- object block
- adjacent caption block

Instead of embedding caption inside the object payload.  
而不是把 caption 硬塞进对象字段里。

Use these helpers when possible / 推荐优先使用：

- `append_image_with_caption(...)`
- `append_chart_with_caption(...)`
- `append_table_with_caption(...)`
- `append_math_with_caption(...)`

---

## 4. Use `record` tables for data, `grid` tables for layout / 数据表用 `record`，版式表用 `grid`

Choose `record` when:  
以下情况优先用 `record`：

- each row is naturally an object
- columns have stable keys
- you may want export / analytics / sorting later

Choose `grid` when:  
以下情况优先用 `grid`：

- the table is irregular
- headers span rows or columns
- row lengths differ
- the table is more presentation-oriented than data-oriented

---

## 5. Use markDefs when the inline target carries payload / 行内目标有载荷时优先用 markDefs

If the inline target needs structured payload such as:  
如果行内目标需要结构化载荷，例如：

- external links
- xref targets
- citation targets
- inline math payload

prefer `markDefs` + span marks.  
更推荐使用 `markDefs + span.marks`。

Direct inline objects are still useful for simple authoring, but markDefs are closer to the protocol’s portable-text style.  
直接行内对象仍然适合简单 authoring，但 markDefs 更贴近协议的 Portable Text 风格。

---

## 6. Enable `strict_ids=True` during authoring / 编写阶段打开 `strict_ids=True`

This catches common duplicate-ID mistakes earlier.  
这能更早发现常见的重复 ID 问题。

```python
report = create_document(..., strict_ids=True)
```

Still treat `validate()` / `assert_valid()` as the final gate.  
但仍应把 `validate()` / `assert_valid()` 作为最后一道闸门。

---

## 7. Save JSON snapshots while iterating / 迭代时保存 JSON 快照

When building a new renderer or a new report family, save intermediate JSON outputs.  
在开发新渲染器或新的报告模板时，建议保存中间 JSON 快照。

This helps with:  
这样有助于：

- regression comparison / 回归比对
- renderer debugging / 渲染器调试
- protocol-shape review / 协议结构审查

---

## 8. Keep one business sample as a long-lived regression fixture / 保留一份长期回归业务样例

In addition to unit tests, keep one representative business report JSON and regenerate it when package behavior changes.  
除了单元测试外，建议保留一份代表性的业务报告 JSON，并在包行为变化时重新生成它。

That sample is often the fastest way to spot protocol drift.  
这通常是发现协议漂移最快的方法。
