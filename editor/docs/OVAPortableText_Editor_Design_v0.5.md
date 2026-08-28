# OVAPortableText 前端编辑器设计方案 v0.5

**状态：** MVP 开发实施基线（精简实用版）  
**日期：** 2026-08-27  
**目标协议：** OVA Portable Text / `report.v1.3`  
**目标形态：** 可独立运行、可嵌入其他前端项目的结构化报告编辑器

---

## 1. 目标与定位

本编辑器用于读取、展示和编辑符合 OVAPortableText 的报告 JSON。产品本质是一个**带 Visual Render/Edit Mode 的 JSON Editor**：JSON 是唯一输出格式，Visual Mode 只是让用户更容易理解和安全修改这份 JSON。它不是 CMS、在线 Word，也不负责重新实现最终 PDF Renderer。

核心定位：

> **Visual Mode 用于安全地编辑报告内容和常用结构；JSON Mode 用于完整编辑底层协议。两种模式最终操作同一份 OVAPortableText 文档。**

第一版重点解决五件事：

1. **看得懂**：把 18k 行 JSON 转成用户能理解的章节、正文、表格和图表。
3. **改得动**：常见内容无需进入 JSON 即可编辑。
4. **改不坏**：新增、删除、移动、重命名时自动维护 ID 和引用关系。
5. **存得住**：用户可以在浏览器中手动保存多个 JSON 版本，并随时切换或恢复。
6. **容易接入**：宿主前端可以简单传入 JSON、取回 JSON，不绑定后端和业务框架。

### 1.1 明确边界

第一版只围绕“JSON 编辑 + Visual 编辑 + 本地版本”展开：

- 不追求与 70 页 PDF 像素级一致；
- 不负责 PDF 生成；
- 不做多人协作、评论、审批工作流；
- 不做云同步、账号系统、权限系统；
- 不做完整 Excel 级表格编辑；
- 不要求 Visual Mode 覆盖协议中的每一个高级字段，高级字段可以回到 JSON Mode；
- 不为尚未提出的未来需求预留复杂通用框架；
- 不要求 JSON 文本级 byte-perfect round-trip（空格、缩进、`1.0` 与 `1` 等格式可能变化），但必须保证**语义字段、未知字段和未编辑内容不被丢失或自动改写**；
- 浏览器本地版本只用于轻量暂存和恢复，不作为长期备份或服务器存储的替代。

---

## 2. OVAPortableText 对编辑器最重要的特点

编辑器设计只需要围绕以下几个协议特点展开。

### 2.1 章节树是正式结构

报告结构由 `sections`、`body`、`content`、`subsection` 组成，而不是一条扁平 block 列表。

因此 Visual Mode 必须提供章节树，并正确维护：

- `id`；
- `level`；
- `title`；
- `numbering`；
- `sectionRole`；
- `navigation`；
- `pagination`；
- `body` 顺序。

### 2.2 正文实例与数据本体经常分离

典型结构：

```text
Section
  -> ContentItem
      -> ChartBlock(chartRef)
          -> datasets.charts[id]

Section
  -> ContentItem
      -> TableBlock(tableRef)
          -> datasets.tables[id]
```

表格 Cell 中还可以继续包含 `block`、`chart`、`image` 等受限 block。

因此编辑器必须有一个简单可靠的 **Reference Manager**，能够回答：

- 这个 block 引用了什么？
- 这个 dataset 被哪里使用？
- 删除或重命名后是否会产生断链？

### 2.3 Registry 是一等内容

需要识别并管理：

- `assets.images`；
- `datasets.charts`；
- `datasets.tables`；
- `bibliography`；
- `footnotes`；
- `glossary`。

用户通常不需要直接理解 Registry，但编辑器不能忽略它。

### 2.4 协议存在默认值和扩展字段

例如 `anchor` 缺省时可以回退到 `id`，`meta` 还可能带有业务扩展数据。

因此：

- Load 时不要自动把所有默认值写回 JSON；
- 不认识的字段必须保留；
- Visual Mode 只修改目标字段和必要关联字段。

### 2.5 当前真实报告就是第一版基准

当前测试样例约包含：

- 18,000 行 JSON；
- 70 页 PDF；
- 约 49 个递归 section；
- 13 个 chart dataset；
- 10 个 table dataset；
- `pie`、`doughnut`、`bar`、`line`、`matrix_bubble`；
- `grid` 表、`rowSpan`、复杂列宽、Cell 内嵌 chart。

MVP 必须直接以这份真实报告作为兼容和性能测试，而不是只用简化 demo。该报告固定为 Golden Fixture，路径建议为 `fixtures/report-v1.3-company.json`，开发过程中不得为了让测试通过而修改该文件。

---

## 3. 用户工作流

### 3.1 嵌入业务项目

```text
宿主项目取得 OVAPortableText JSON
        ↓
调用编辑器 setValue / initialValue
        ↓
用户 Visual / JSON 编辑
        ↓
Validate
        ↓
宿主通过 getValue / onSave 获取 JSON
        ↓
宿主保存或提交给现有 Renderer
```

### 3.2 独立使用

```text
Paste JSON / Open .json
        ↓
编辑
        ↓
Validate
        ↓
Copy JSON / Download .json
```

### 3.3 最终报告预览

编辑器本身只做 Semantic Preview。

如果宿主项目已经有 PDF/HTML Renderer，可选提供：

```ts
onRequestFinalPreview(document)
```

编辑器显示一个 **Final Preview** 按钮，把当前合法 JSON 交给宿主现有 Renderer。这样不需要在编辑器中重复实现 PDF 排版。

### 3.4 浏览器本地版本

用户可以在编辑过程中主动保存检查点：

```text
编辑当前 JSON
      ↓
点击 Save
      ↓
浏览器保存一个完整 JSON Snapshot
      ↓
继续编辑
      ↓
Versions 中随时切换 / 恢复旧版本
```

第一版采用**完整快照**，不做 diff/patch 版本链。报告 JSON 的当前规模下，这种方式实现最简单、恢复最可靠。

本地版本应支持：

- 默认以保存时间命名，可选填写版本备注；
- 查看保存时间、协议版本、校验状态和大致大小；
- Load / Rename / Download / Delete；
- 当前文档有未保存修改时，切换版本前提醒用户；
- 不同报告通过稳定的 `documentKey` 隔离版本记录。

浏览器存储只属于当前站点（origin），用户清理浏览器数据、使用隐私模式或浏览器配额不足时可能丢失，因此界面应明确提示“Local only”，重要版本仍应 Download 或由宿主保存到服务端。

---

## 4. 界面设计

第一版保持简单，采用三个主要区域。

```text
+------------------------------------------------------------------------+
| Visual | JSON   Find   Undo Redo   Validate   Final Preview   Save   Versions |
+----------------+--------------------------------------+----------------+
| Outline        |                                      | Properties     |
| Resources      |          Document Editor             |                |
| Issues         |                                      | General        |
|                |  3. Technological Novelty            | Layout         |
|                |                                      | Data           |
|                |  [editable paragraph]                | Advanced       |
|                |                                      |                |
|                |  [chart preview] [Edit Data]         |                |
+----------------+--------------------------------------+----------------+
| Modified · 0 Errors · 2 Warnings                                       |
+------------------------------------------------------------------------+
```

### 4.1 Visual Mode

普通用户的默认模式：

- 看章节和报告内容；
- 直接改文字；
- 修改表格 Cell；
- 修改图表数据；
- 新增/删除/移动常用对象；
- 不需要理解 `chartRef`、`tableRef` 等底层字段。

### 4.2 JSON Mode

高级模式：

- 完整 JSON 源码；
- 搜索；
- 格式化；
- Syntax / Protocol diagnostics；
- Apply / Discard。

JSON Mode 允许自由修改协议，但不能在 JSON 尚未 Apply 时同时继续 Visual 编辑，避免产生两份冲突状态。

### 4.3 Split Mode

Split 有价值，但不是 MVP 必需。放到 P1。

---

## 5. 左侧导航

### 5.1 Outline

展示 Section Tree。

P0 支持：

- 展开/折叠；
- 点击定位；
- 修改标题；
- Add Section / Add Subsection；
- Delete；
- Duplicate；
- Drag & Drop；
- 显示错误和 Modified 状态。

拖动 subsection 时，编辑器负责同步必要的 `level`。

### 5.2 Resources

只展示最常用 Registry，不把用户淹没在协议细节中。

```text
Charts (13)
Tables (10)
Images (0)
References
```

资源项至少显示：

- 名称 / ID；
- Used / Unused；
- Preview；
- Edit；
- Show Usage。

### 5.3 Issues

集中展示：

- JSON Syntax Error；
- Protocol Error；
- Reference Error；
- Unsupported / Unknown Warning；
- Unused Resource；
- TOC stale warning。

点击问题应尽量直接定位到 Visual 对象或 JSON Path。

### 5.4 全局 Find

70 页级报告只靠 Outline 不够。P0 提供轻量全文查找，至少覆盖：

- Section title；
- Paragraph / Span 文本；
- Table cell 文本；
- 常用资源 label。

结果按章节分组，点击直接定位。支持 `Ctrl/Cmd + F`；批量 Replace 放到 P1。

---

## 6. Visual Editing Capability Matrix

这是第一版最重要的功能边界。

| 对象 | P0 主要能力 | P1 / 后续 |
|---|---|---|
| Document Meta | 查看/编辑 title、language 等常用字段 | 更完整 theme 管理 |
| Section | Add / Delete / Duplicate / Move / Rename | Promote/Demote、高级 presentation |
| Paragraph / Span | 文本、bold、italic、underline、列表、link | xref/citation/footnote/glossary 完整编辑器 |
| ContentItem | 自动保持结构，不要求用户理解 | 高级拆分/合并 |
| Chart Block | Preview、Delete、Move、Duplicate | 更复杂 caption/布局 |
| Chart Dataset | 编辑当前 5 类图表常用数据、label、axis、orientation | 高级 chart options |
| Table Block | Preview、Delete、Move、Duplicate | 高级 caption/布局 |
| Grid Table | 编辑 Cell 内容、header、列宽；保持 span | Insert/Delete/Merge/Unmerge 复杂操作 |
| Record Table | 编辑 rows / values；简单增删行 | 高级列定义 |
| Image | Preview、修改 URL；保留 embedded image | 本地图片转 embedded、图片管理 |
| Math / Callout | 能展示、保留、删除、移动；必要时 Go to JSON | 完整 Visual Editor |
| Bibliography / Footnote / Glossary | 保留、校验引用 | 可视化管理界面 |
| Unknown Type | 只读占位、保留原 JSON、Go to Source | 按实际协议需要再增加专用编辑器 |

### 6.1 新增对象

P0 工具栏建议只提供常用对象：

```text
+ Paragraph
+ Section
+ Table
+ Chart
+ Image
```

创建时由编辑器生成合法默认结构和唯一 ID。

高级对象暂时通过 JSON Mode 创建即可，不需要第一版把所有协议能力都做成表单。

---

## 7. 几个关键编辑规则

### 7.1 删除正文实例时，不自动删除 Registry 数据

例如删除一个 Chart Block：

```text
删除正文 chart instance
→ dataset 先保留
→ Resources 中标记为 Unused
```

用户可以之后执行：

```text
Clean Unused Resources
```

这样比自动猜测“这个 dataset 是否也要删除”更安全、更简单。

### 7.2 Duplicate 默认创建独立数据

用户 Duplicate 一个 Chart/Table 时，通常希望之后可以独立修改。

因此默认行为：

```text
Duplicate Chart Block
→ Clone Chart Dataset
→ Generate New Dataset ID
→ Generate New Block ID
→ Update chartRef
```

如果用户确实想共享同一个 dataset，应通过 **Insert Existing Resource** 明确操作。

### 7.3 Rename ID 必须维护引用

Visual Mode 修改可引用对象 ID 时：

1. 检查唯一性；
2. 找到所有已知引用；
3. 一次 Transaction 更新；
4. 重新 Validate。

JSON Mode 手工改 ID 时不自动猜测用户意图，只显示断链问题和 Quick Fix。

### 7.4 Figure/Table 与 Caption 作为视觉关联组

如果 `chart/table` 后紧跟对应 caption block，Visual Mode 默认一起选择、一起拖动。

Raw JSON 不需要引入新的 group 类型。

### 7.5 特殊 Section 需要更谨慎

对于：

- `cover`；
- `toc`；
- `backCover`；

删除或移动时给出二次确认。宿主还可以通过 `readOnly` 或 Feature Flags 直接锁定。

---

## 8. Table 与 Chart 的实用设计

### 8.1 Table

第一版不要做“网页版 Excel”。

#### Grid Table P0

重点是**安全编辑内容**：

- Cell text / blocks；
- header；
- column width；
- 保留 `rowSpan / colSpan`；
- Cell 内 chart/image 可正常展示和定位。

对于已有 span 的复杂表格，P0 不开放任意 Merge/Insert Column，避免把结构改坏。

#### Record Table P0

可以更自由：

- 编辑 values；
- 简单 Add/Delete Row；
- 列定义通过 Properties 修改。

### 8.2 Chart

针对真实报告，P0 直接支持：

- `pie`；
- `doughnut`；
- `bar`；
- `line`；
- `matrix_bubble`。

每类图表只做自己的结构化 Data Editor，不强行统一成一个万能表单。

例如 Bar：

```text
Category | Series A | Series B
2024     | 12       | 8
2025     | 15       | 9
```

同时提供常用：

- label；
- value / point；
- axis label；
- unit；
- orientation；
- series/category 增删。

图表复杂的 `meta` 或 renderer hint 放到 Advanced JSON Inspector。

### 8.3 多语言字段

如果原字段是：

```json
{
  "en": "Market",
  "zh": "市场"
}
```

P0 必须至少做到**不会因为编辑英文而丢失中文**。

如果视觉界面暂时只编辑当前 `meta.language`，其他语言值仍原样保留。

完整 EN/ZH 切换编辑器可放到 P1。

---

## 9. 数据与状态模型

不需要把内部架构设计得过度复杂，第一版保留三个核心状态即可。

```text
Source Draft Text
       │ Apply
       ▼
Raw Document  --------------------> Visual Transactions
       │                                  │
       ├─ Reference Index                 ├─ Undo / Redo
       ├─ Numbering                       └─ Dirty State
       ├─ Validation / Preview Model
       │
       └──────── Save Snapshot ────────> Browser Version Store
                                           │
                                           └─ Versions
```

### 9.1 Raw Document

唯一业务真值。

要求：

- 保留未知字段；
- 不主动注入缺省字段；
- Visual 只改目标字段和必要引用；
- 输出仍是标准 OVAPortableText JSON。

### 9.2 Derived Data

以下都可以随时从 Raw 重新计算，不写回 Raw：

- effective anchor；
- Section 显示编号；
- Resource usage；
- validation issues；
- Figure/Table 视觉关联；
- TOC stale 状态。

### 9.3 Source Draft

JSON Mode 正在输入的文本单独保存。

状态只需要：

```text
SYNCED
DRAFT
INVALID
```

`DRAFT / INVALID` 时：

- Visual 可以看最后一次已 Apply 的文档；
- Visual 暂时只读；
- 用户必须 Apply 或 Discard 后才能继续 Visual 编辑。

### 9.4 Unsaved Change Protection（未保存修改保护）

以下操作都不能静默丢弃当前修改：

- 切换本地版本；
- 宿主调用 `setValue()` 载入另一份报告；
- 重新 Open / Paste 新 JSON；
- 页面关闭或刷新。

统一使用 Dirty Guard：有未保存修改时提示 **Save / Discard / Cancel**。页面关闭使用浏览器 `beforeunload` 做最后一道保护。

宿主在 Dirty 状态调用 `setValue()` 时，默认拒绝直接覆盖并返回“存在未保存修改”的结果；宿主只有在用户确认后才应显式 force replace。这里属于未保存修改保护，不设计任何并发或版本合并机制。

---

## 10. 浏览器版本保存与恢复

### 10.1 存储选择

使用浏览器原生 **IndexedDB**，不使用 `localStorage` 或 Cache Storage。原因：

- JSON 可能较大，`localStorage` 容量小且同步阻塞；
- IndexedDB 可保存较大的字符串/对象，异步且无需后端；
- 版本数据是应用状态，不适合使用 HTTP Cache Storage。

实现上保持轻量，可以直接封装 IndexedDB，也可以使用很薄的 `idb-keyval` 类工具。

### 10.2 保存模型

P0 直接保存完整 JSON 字符串：

```ts
interface SavedVersion {
  id: string;
  documentKey: string;
  createdAt: number;
  label?: string;
  schemaVersion?: string;
  editorVersion: string;
  validationStatus: 'valid' | 'warning' | 'error';
  sizeBytes: number;
  json: string;
}
```

不做增量 diff，也不做 Asset 去重。这样代码少、版本之间相互独立，任何一个版本都能单独恢复。

### 10.3 Save 行为

统一保留一个 Save 按钮：

1. 如果 Source 有未 Apply 的修改，先要求 Apply 或 Discard；
2. 将当前 Raw Document 序列化为完整 JSON；
3. 如果启用 browser versioning，则写入 IndexedDB；
4. 如果宿主提供 `onSave`，再把同一份 document 和 validation 状态通知宿主。

因此：

- 独立模式可以只保存到浏览器；
- 嵌入模式可以只调用宿主保存；
- 也可以同时“本地版本 + 宿主后端保存”，无需两套编辑器逻辑。

本地 Snapshot 允许保存**可解析但协议存在 Error 的 JSON**，并把状态记录为 `error`，方便用户保留中间检查点；但 JSON Syntax 非法且尚未 Apply 的 Source Draft 不作为正式版本。

### 10.4 Versions 面板

不新增复杂页面，用一个轻量 Popover / Drawer：

```text
Versions
────────────────────────
22:10  Before chart edit   Valid
21:42  Table updated       2 warnings
20:55  First review        Valid
────────────────────────
Load   Rename   Download   Delete
```

切换版本时：

- 当前 Dirty：提示 Save / Discard / Cancel；
- Load 后重新 Validate；
- 当前 Undo / Redo 栈清空；
- 被加载版本成为新的当前基线；
- 原版本仍保留在 Versions 中，不发生覆盖。

### 10.5 版本隔离、数量和配额

宿主启用版本功能时提供稳定 `documentKey`，例如报告 ID。所有记录按：

```text
namespace + documentKey
```

隔离，避免不同报告串在一起。

默认最多保留 20 个手动版本，数量可配置。达到上限时不静默删除，提示用户删除旧版本或显式确认替换最旧版本。

保存前计算大致 JSON 大小，并捕获 `QuotaExceededError`。如果报告未来包含大量 Base64 image，完整快照会明显增大；P0 只提示和限制，不为了这个场景提前实现复杂去重。

### 10.6 可选 Recovery Draft（P1）

手动 Save Version 是核心需求。自动 Recovery Draft 不是 P0 必需；第一版稳定后如果需要，可在已经引入 IndexedDB 的基础上低成本增加**一个**自动恢复草稿，不形成版本列表：

- Raw Document 变更后 debounce 约 2 秒覆盖同一个 recovery record；
- JSON Mode 的未 Apply Source Draft 也可单独保存文本，用于浏览器崩溃恢复；
- 下次打开同一 `documentKey` 时，如果 recovery draft 比最近手动版本更新，提示 Restore / Ignore；
- 用户成功 Save 后更新或清理 recovery 状态。

这不是“自动生成很多版本”，只是防刷新、崩溃和误关页面。

### 10.7 本地数据安全

浏览器版本：

- 仅存当前 origin 的 IndexedDB；
- 默认不上传网络；
- 不额外加密，因此共享电脑或敏感报告场景可由宿主关闭；
- 提供 Clear Local Versions；
- UI 明确标识 Local only，避免用户误认为已经永久备份。

## 11. Reference Manager 与 Validation

### 11.1 Reference Manager

P0 不需要过度抽象成大型图数据库，只要建立文档级索引：

```text
id / anchor -> target
resource id -> usage locations
source object -> outgoing refs
```

覆盖当前协议常用引用：

- `chartRef`；
- `tableRef`；
- `imageRef`；
- `xref`；
- `citation_ref`；
- `footnote_ref`；
- `glossary_term`。

足以支持：

- duplicate ID 检测；
- dangling ref 检测；
- Show Usage；
- Safe Rename；
- Unused Resource。

### 11.2 四类错误

```text
1. JSON Syntax
2. Protocol / Schema
3. Reference / Semantic
4. Compatibility / Warning
```

第一版最重要的是前三类。

### 11.3 TOC

章节结构变化后，只需要先做：

```text
TOC may be out of date
```

不要在 MVP 自己实现复杂目录生成器。后续可以调用宿主/Renderer 的 regenerate 能力。

### 11.4 Numbering

Visual 显示：

```text
3.2 Innovation Overview
```

实际 `title` 仍然是：

```text
Innovation Overview
```

P0 重点支持 `auto` 和 `none`。

`manual` 可以保留原值并提示当前 Visual 不完全支持，不需要第一版扩展一套手工编号结构。

---

## 12. 技术方案

### 12.1 TypeScript Core + React UI

推荐保持：

```text
@ova/portable-text-editor-core
  Pure TypeScript

@ova/portable-text-editor-react
  React
```

Core 不依赖 React，负责：

- Load / Export；
- types；
- validation；
- reference index；
- commands / transactions；
- undo / redo；
- ID generation / remap。

React 层负责：

- Visual Editor；
- Source Editor；
- Outline / Resources / Issues；
- Properties；
- dialogs / toolbar。

### 12.2 为什么这样适合以后嵌入

- React 项目直接使用 React Component；
- 其他框架未来包一层 Web Component；
- Core 不需要重写；
- 宿主不用理解内部状态管理。

### 12.3 Source Editor

采用 Adapter，不把 Monaco 写死进 Core。

第一版优先 **CodeMirror 6**：体积更轻、嵌入简单。

如果内部开发工具需要更完整 IDE 体验，可以增加 Monaco Adapter。

Source Editor 只在用户打开 JSON Mode 时 lazy load。

### 12.4 Rich Text / Chart

- Rich Text：Tiptap / ProseMirror 作为 adapter；
- Chart Preview：ECharts 或复用现有 Web Renderer 的图表组件；
- Grid Table：自定义轻量编辑器，不引入完整 spreadsheet 框架。

### 12.5 Schema 同步

前端不要长期手写另一套协议。

推荐由 OVAPortableText/Pydantic 侧发布版本化 JSON Schema：

```text
report.v1.3.schema.json
```

前端用于：

- AJV validation；
- TypeScript type generation；
- Source Editor diagnostics。

同时使用真实 fixtures 做 Python / TypeScript 校验一致性测试。

---

## 13. 对宿主项目的最小 API

API 不要一开始设计得太大。

### 13.1 React 用法

```tsx
const editorRef = useRef<OVAPortableTextEditorHandle>(null);

<OVAPortableTextEditor
  ref={editorRef}
  initialValue={reportJson}
  readOnly={false}
  versioning={{ enabled: true, documentKey: reportId }}
  onSave={(document, context) => saveReport(document, context)}
  onDirtyChange={(dirty) => setDirty(dirty)}
  onRequestFinalPreview={(document) => openRenderer(document)}
/>
```

### 13.2 Handle

```ts
interface OVAPortableTextEditorHandle {
  setValue(value: object | string, options?: SetValueOptions): Promise<LoadResult>;
  getValue(): OVAReportDocument;
  getJSONString(pretty?: boolean): string;
  validate(): ValidationResult;
  setMode(mode: 'visual' | 'json'): void;
  undo(): void;
  redo(): void;
  isDirty(): boolean;
  saveVersion(label?: string): Promise<SavedVersion>;
  listVersions(): Promise<SavedVersionMeta[]>;
  loadVersion(versionId: string): Promise<LoadResult>;
}
```

### 13.3 主要 Props

```ts
interface OVAPortableTextEditorProps {
  initialValue?: object | string;
  readOnly?: boolean;
  features?: EditorFeatures;
  versioning?: BrowserVersioningOptions;
  onSave?: (document: OVAReportDocument, context: SaveContext) => void | Promise<void>;
  onDirtyChange?: (dirty: boolean) => void;
  onValidationChange?: (result: ValidationResult) => void;
  onRequestFinalPreview?: (document: OVAReportDocument) => void;
}
```

浏览器版本配置保持简单：

```ts
interface BrowserVersioningOptions {
  enabled: boolean;
  documentKey: string;
  namespace?: string;
  maxVersions?: number;      // default 20
}
```

嵌入业务项目时建议显式传 `documentKey`。如果不希望敏感报告留在浏览器中，直接关闭 `versioning`。Recovery Draft 属于 P1，真正实现时再扩展该配置，不要求 MVP 预留字段。

### 13.4 Feature Flags

不同产品不需要 fork 编辑器，只控制功能：

```ts
features={{
  jsonMode: true,
  structureEditing: true,
  chartEditing: true,
  tableEditing: true,
  importExport: true
}}
```

P0 不设计更细粒度权限系统；不同嵌入场景只通过 Feature Flags 控制即可。

### 13.5 输入输出

程序化：

- `initialValue`；
- `setValue()`；
- `getValue()`；
- `onSave()`。

用户操作：

- Paste JSON；
- Open `.json`；
- Copy JSON；
- Download `.json`；
- Save Version；
- Versions -> Load / Rename / Download / Delete。

编辑器不默认调用任何业务 API。本地版本功能开启时只访问当前浏览器 IndexedDB。

---

## 14. 性能与嵌入注意点

当前报告已经较大，因此第一版就需要注意：

- 默认 uncontrolled，不在每次键盘输入把完整文档传回宿主；
- Section 级渲染和 memo；
- 长 Outline 使用 virtualization；
- 图表、Source Editor 按需加载；
- validation debounce；
- 不重复复制大型 Base64 asset；
- Embedded image 的 `data` 在 Source Editor 中默认折叠；
- 输入大小限制由宿主配置；
- CSS 使用 `ova-pte-*` 前缀，不污染宿主全局样式；
- Modal 支持指定 portal container；
- Version Store 全部异步，不阻塞编辑输入；
- 版本列表只读 metadata，真正 Load 时再读取 JSON 内容。

### 14.1 安全与容错

编辑器可能接收来自 AI、接口或用户粘贴的 JSON，因此 P0 需要基础安全边界：

- JSON 文本按纯文本渲染，不执行任意 HTML / Script；
- URL 只允许明确的安全 scheme，禁止 `javascript:` 等危险链接；
- 外部链接使用 `noopener/noreferrer`；
- 不执行 `meta`、renderer hint 或未知字段中的代码；
- 单个 Chart/Table/Image 渲染异常时使用 block-level Error Boundary，显示占位和 Go to JSON，不能让整份 70 页报告白屏；
- Unknown Type 永远保留原 JSON，不因无法渲染而丢失。

---

## 15. MVP 功能清单

### P0：第一版必须完成

#### 文档与集成

- Load object / JSON string；
- Paste / Open JSON；
- Copy / Download JSON；
- React Component + Handle API；
- Semantic preservation；
- 全局 Find；
- 浏览器本地多版本 Save / Load / Rename / Delete；
- 真实 18k JSON 可用。

#### Visual

- Outline；
- Paragraph 基础富文本；
- Section Add/Delete/Duplicate/Move；
- Block Add/Delete/Duplicate/Move；
- Chart Preview + 当前 5 类基础数据编辑；
- Grid/Record Table 内容编辑；
- Image Preview + URL 修改；
- Properties 常用字段；
- Unknown object 只读保留 + Go to JSON。

#### JSON

- Source Editor；
- Search / Format；
- Apply / Discard；
- Syntax diagnostics；
- Source Draft 状态保护。

#### 安全

- ID 唯一性；
- Reference Index；
- Safe Rename；
- Unused Resource；
- Protocol + Reference Validation；
- Undo / Redo；
- Dirty 状态；
- 文档/版本切换 Dirty Guard；
- `setValue()` 未保存修改保护；
- 基础 URL 安全处理；
- Block-level Error Boundary。

### P1：第一版稳定后

- Split Mode；
- Multi-language 完整编辑 UI；
- xref/citation/footnote/glossary 可视化编辑；
- Advanced JSON Inspector；
- Visual 批量 Find & Replace；
- Grid Table 复杂 Insert/Delete/Merge；
- TOC regenerate hook；
- 可选 Recovery Draft；
- 如确有非 React 项目接入需求，再增加 Web Component。

### 明确不做

以下能力不属于本编辑器设计范围，也不需要在 MVP 代码中预留架构：

- 多人协作；
- 评论、审批、Review Workflow；
- 云同步；
- 用户/权限系统；
- 版本分支、Merge、Git 式 diff/patch 链；
- CMS/工作流能力；
- PDF 像素级实时排版。

---

## 16. 固定 Golden Fixture

第一版必须把用户提供的真实报告 JSON 作为固定回归样例：

```text
fixtures/report-v1.3-company.json
```

该文件应直接复制原始样例，不做清洗、简化或重写。它用于验证编辑器面对真实 OVAPortableText 数据时仍然可用。

固定基线：

- `schemaVersion`: `report.v1.3`；
- 文件大小：约 1.03 MiB（1,079,542 bytes）；
- 顶层 sections：12；
- 递归 sections：49；
- chart datasets：13；
- table datasets：10；
- chart types：`pie` 1、`doughnut` 4、`bar` 3、`line` 4、`matrix_bubble` 1；
- SHA-256：`9a280b351539ba3717619900a1f679752ee5079f1f94e124875a230aa5d2d9a2`。

Golden Fixture 规则：

1. **测试文件本身只读**：不得为了适配编辑器而修改 fixture；
2. 新发现的边界情况另放 `fixtures/edge-cases/`；
3. 最低回归测试必须覆盖 Load、Visual Render、Source Apply、Visual Edit、Validation、Export；
4. `Load -> Export` 后允许 JSON 格式化差异，但协议语义、未知字段和未编辑数据不得丢失；
5. 编辑后的 JSON 必须仍可交给现有 Renderer。

建议在 CI/测试中校验上述 SHA-256，防止 Golden Fixture 被无意改动。

---

## 17. MVP 验收标准

第一版可以认为完成，至少需要通过以下真实场景：

1. **Golden Fixture 完整**：`fixtures/report-v1.3-company.json` 的 SHA-256 与固定值一致。
2. **加载真实报告**：固定样例能正常打开，章节、图表、表格可浏览。
3. **不丢数据**：Load -> Export 不丢未知字段和未编辑协议字段，不自动补大量默认字段。
4. **Visual 修改**：改一个 paragraph 后 JSON 中对应内容正确变化。
5. **JSON 修改**：Source Apply 后 Visual 立即反映；非法 JSON 不污染当前文档。
6. **章节操作**：Add/Delete/Move Section 后结构和 level 合法。
7. **图表编辑**：5 种现有 chart dataset 可修改关键数据并重新 Preview。
8. **表格编辑**：复杂 grid 的 Cell 内容可以修改，同时不破坏现有 rowSpan/colSpan。
9. **引用安全**：Rename / Duplicate / Delete 不产生意外 dangling ref。
10. **版本保存**：连续保存至少 3 个版本，刷新页面后仍可看到并分别 Load。
11. **版本隔离**：两个不同 `documentKey` 的版本列表不会混在一起。
12. **切换保护**：Dirty 状态切换版本或 `setValue()` 不会静默丢失修改。
13. **全局查找**：可以从 70 页报告中搜索文字并定位到对应 Section/Block。
14. **局部故障隔离**：一个无效/异常 block 不会导致整份编辑器白屏。
15. **导出与渲染**：编辑完成的 JSON 能继续被现有 Renderer 接收。
16. **嵌入可用**：另一个 React 项目只需要传 JSON 和 `onSave` 即可工作。

---


## 18. 推荐代码结构

保持简单即可：

```text
packages/
  core/
    src/
      model/
      schema/
      validation/
      references/
      commands/
      history/
      versioning/
      search/
      io/

  react/
    src/
      editor/
      visual/
      source/
      outline/
      resources/
      issues/
      versions/
      properties/
      blocks/
      charts/
      tables/
      styles/

apps/
  playground/

fixtures/
  minimal/
  edge-cases/
  report-v1.3-company.json
```

不要在第一版为了未来可能性拆出过多 package。只有真正出现非 React 接入需求时，再增加 Web Component 包装层。

---

## 19. 最终建议

第一版开发应围绕下面这条主线，不要扩散：

```text
可靠 Load
  -> Visual 看懂报告
  -> 常用内容安全编辑
  -> JSON 高级编辑
  -> Ref / Validation 保证不改坏
  -> Save / Versions 随时恢复
  -> 简单 API 返回 JSON
```

### 19.1 AI Coding 实施约束

给 AI Coding 的首要约束应明确写入开发任务：

> **优先实现一个简单、可靠、可运行的 OVAPortableText JSON 编辑器，不为未提出的未来需求设计通用框架。除 JSON 编辑、Visual Render/Edit、本地版本保存和宿主集成外，不实现协作、云同步、用户系统、评论或工作流。**

> **所有核心功能首先使用 `fixtures/report-v1.3-company.json` 验证，不以人为构造的简化 JSON 作为主要验收标准。**

建议按以下顺序开发，每一步都保持可运行：

1. Load / Export / Schema / Reference / Golden Fixture；
2. Visual Render + Outline + 基础正文编辑；
3. Table / Chart 编辑；
4. JSON Mode + Apply/Discard + Undo/Redo；
5. IndexedDB Versions + Unsaved Change Protection；
6. Find、Issues、宿主 API 和最终回归。

### 19.2 实现优先级

最重要的实现优先级依次是：

1. **文档模型和引用正确性**；
2. **Visual 的正文 / Section / Table / Chart 编辑**；
3. **Source Mode 与 Visual 状态同步**；
4. **本地版本保存与 Unsaved Change Protection**；
5. **全局 Find、容错和基础安全**；
6. **宿主输入输出 API**；
7. **真实报告回归测试**。

其他能力，如复杂表格、完整引用编辑、多语言高级 UI、PDF 级 Preview，都不应阻塞 MVP；协作、云同步、评论工作流等能力则不属于本编辑器范围。

