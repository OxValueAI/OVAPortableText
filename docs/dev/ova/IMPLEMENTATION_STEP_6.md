# OVAPortableText - Implementation Step 6

## 本步目标
本步把几个代码量不大的方向合并推进：

1. **builder API 再顺手化**
2. **编号辅助层（numbering helper）**
3. **round-trip 能力（from_dict / from_json）**
4. **meta / theme 协议对齐增强**
5. **resolver 的语义类型对齐修正**

这一步继续遵循协议里的几个关键原则：
- 顶层结构保持 `schemaVersion / meta / theme / assets / datasets / bibliography / footnotes / glossary / sections` 这组骨架。
- 标题文本与结构编号分离，显示编号由系统推导，不直接写进标题文本。
- `figure / table / equation` 应预留自动编号空间，但协议本身不写死最终渲染文案。
- 所有可被引用对象都应具备统一可解析入口。

## 本步新增内容

### 1. round-trip 基础能力
`OvaBaseModel` 新增：
- `from_dict()`
- `from_json()`

这让包现在具备：
- 生成对象
- 导出 JSON
- 再读回对象

的完整 round-trip 工作流。

### 2. `DocumentMeta` 改为“强类型 + 可扩展”
因为协议明确说明 `meta` 详细字段表在 v1.0 还没有完全冻结，所以本步把 `DocumentMeta` 改成：
- 常见字段强类型化
- 允许附加扩展字段

新增 / 明确保留的字段包括：
- `title`
- `subtitle`
- `language`
- `author`
- `date`
- `reportNumber`
- `documentType`
- `confidentiality`
- `generatedBy`
- `generatedAt`
- `clientId`
- `projectId`
- `reportType`
- `clientName`
- `locale`
- `source`

### 3. `theme` 改为轻量 typed model
新增 `ThemeConfig`：
- `name`
- `styleTemplate`
- `pageTemplateFamily`
- `brandAssetRefs`
- `coverTemplateRef`

同时允许自定义扩展字段，避免过早把 theme 写死。

### 4. builder API 再顺手一层
新增或增强：

#### `Document`
- `append_sections(*sections)`
- `new_section(...)`
- `build_numbering(...)`
- `from_meta(...)`

#### `Section`
- `append_blocks(*blocks)`
- `new_subsection(...)`
- `append_image_with_caption(...)`
- `append_chart_with_caption(...)`
- `append_table_with_caption(...)`
- `append_math_with_caption(...)`

这样你现在可以更自然地写：

```python
report = create_document(title="Demo", language="en")
sec = report.new_section(id="sec-1", level=1, title="Executive Summary")
sec.append_paragraph("Hello")
sec.append_image_with_caption(id="fig-1", image_ref="img-1", caption="Overview")
sub = sec.new_subsection(id="sec-1-1", title="Background")
sub.append_paragraph("More details")
```

### 5. 编号辅助层
新增：
- `NumberingConfig`
- `NumberedTarget`
- `DocumentNumbering`

当前支持：
- `section` 层级编号，例如 `1 / 1.1 / 1.2.3`
- `figure / table / equation` 的逻辑 display number 辅助
- 对象编号模式：
  - `global`
  - `section`

注意：
**这一层只负责计算 display number 辅助值，不会把编号写回协议 JSON。**

### 6. resolver 语义对齐修正
协议里明确区分了：
- 具体对象 `_type`
- 语义引用类别 `targetType`

例如：
- `figure` 是语义类别
- 实际正文对象可能是 `image` 或 `chart`

本步修复了一个重要对齐点：
- 正文里的 `chart` 实例现在也可以被 `xref(targetType="figure", ...)` 解析到

这更贴近协议里“`figure` 可能对应 `image` 或 `chart` 实例”的语义。

### 7. registry 条目结构进一步贴近协议
#### `BibliographyEntry`
现在更接近协议推荐最小结构：
- `type`
- `title`
- `authors`
- `year`

同时为了兼容前面步骤的用法，仍保留 `text` 作为兼容字段；helper 允许：
- 新写法：`title=...`
- 旧写法：`text=...`

#### `GlossaryEntry`
现在更接近协议推荐结构：
- `term`
- `definition`
- `aliases`

同时保留 `short` 作为兼容字段。

## 新增测试
本步新增了 4 个重点方向测试：

1. **round-trip + meta/theme 扩展测试**
2. **编号辅助测试**
3. **section 模式编号重置测试**
4. **chart 实例可被 `figure` 语义 xref 解析测试**

## 当前测试结果
本地执行结果：

```bash
18 passed
```

## 本步新增示例
新增示例文件：
- `examples/builder_numbering_roundtrip_demo.py`

演示内容：
- `report.new_section(...)`
- `section.new_subsection(...)`
- `append_*_with_caption(...)`
- `build_numbering(...)`
- `from_json(...)`

## 对协议的自查结论
本步实现与协议当前版本保持一致的点：

1. **没有把显示编号写回标题文本**
2. **没有把 caption 强行塞回 image/chart/table/math_block 内部字段**
3. **仍保持顶层 registry 存在，即使为空**
4. **theme 仍是占位层，而不是提前做成渲染合同**
5. **继续把 `figure / table / equation` 视为语义编号类别，而不是简单等同 `_type`**
6. **round-trip 只影响 Python 端使用体验，不改变协议 JSON 结构本身**

## 下一步建议
下一步更适合进入：

1. **validator / resolver 再增强一轮**
   - 更清晰的错误路径
   - 更细粒度 issue code
   - anchor 冲突检查
   - bibliography / glossary / footnotes 条目形状校验

2. **meta / assets / datasets 其余占位字段再补一点 typed model**
   - logos / backgrounds / attachments
   - metrics

3. **集中开始准备后续大文档和样例体系**
   - README
   - Quick Start
   - API 使用样例
   - 错误示例
