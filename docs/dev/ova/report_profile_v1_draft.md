# Report Profile v1.0 正式协议Draft

## 1. 文档定位

本协议定义一套面向“Python 生成报告内容 JSON，Java 渲染生成 PDF”的中间协议底层结构。

本协议当前包含以下内容：

1. 顶层结构
2. 章节树合同
3. 全局 ID / Anchor / Registry / 引用目标体系
4. 类型清单 taxonomy
5. Portable Text 在本协议中的使用边界
6. 学术装置与高级能力的预留位
7. 文本层规则
8. 对象层规则
9. registry 条目结构
10. 学术与辅助 registry 条目结构

本协议当前不展开以下内容的细字段设计：

- 除 pie chart 基础结构外的其他 `datasets.charts` 详细结构
- Java 渲染样式字段
- PDF 页面级排版字段
- 页面样式与分页策略
- Java 渲染器实现细节

---

## 2. 设计原则

### 2.1 内容与渲染分离

- Python 负责产出结构化内容
- Java 负责读取结构化内容并渲染 PDF
- 内容层不直接写死具体视觉表现

### 2.2 Portable Text 作为富文本底座，而不是整份报告的完整结构

- Portable Text 负责表达 section 内的富文本内容流
- 章节树、全局资源、引用目标、编号体系等放在 Portable Text 外层

### 2.3 章节树优先于扁平内容流

整份报告以树形 `sections` 为主结构，不采用单一扁平 content 流再二次解析 section 范围。

### 2.4 标题文本与结构编号分离

- `title` 存纯标题文本
- 展示编号由系统根据 numbering 规则推导
- 不建议把 `1.2.3` 直接写入标题文本

### 2.5 尽量采用“内容块引用 registry，少量简单内容才内嵌”的策略

- 大型资源、可复用资源、可被引用对象优先进入 registry
- 正文块内优先放 `*Ref`
- 简单且一次性的小对象可内嵌

### 2.6 所有可被引用对象都应可解析

任何将来可能被以下能力引用的对象：

- `xref`
- `citation_ref`
- `footnote_ref`
- 目录
- 图表目录
- PDF 书签
- 页内跳转

都应具备统一可解析目标模型。

### 2.7 先定义结构合同，再细化业务块字段

v1.0 先明确骨架与基础能力，不一次性写死全部块字段细节。

---

## 3. 顶层结构

### 3.1 顶层字段清单

```json
{
  "schemaVersion": "report.v1",
  "meta": {},
  "theme": {},
  "assets": {},
  "datasets": {},
  "bibliography": [],
  "footnotes": [],
  "glossary": [],
  "sections": []
}
```

### 3.2 顶层字段职责

#### `schemaVersion`

协议版本号。

用途：

- 向后兼容
- Java 渲染器按版本分发解析
- Python 模块按版本输出
- 校验器按版本校验

建议初始值：

```json
"schemaVersion": "report.v1"
```

---

#### `meta`

文档级元信息。

建议承载但暂不细化字段的内容包括：

- 文档标题
- 副标题
- 语言
- 作者
- 日期
- 报告编号
- 文档类型
- 保密等级
- 生成来源
- 生成时间
- 客户/项目标识

说明：

- `meta` 属于文档元信息层
- 不参与正文内容流
- 不直接承担页面样式控制

---

#### `theme`

主题占位。

当前版本只保留位置，不细化视觉字段。后续 Java 渲染器开发前再细化，例如：

- 主题名称
- 风格模板
- 页面模板族
- 品牌资源引用
- 封面模板引用

---

#### `assets`

静态资源注册表。

建议先按资源类别拆分子 registry，例如：

```json
{
  "images": [],
  "logos": [],
  "backgrounds": [],
  "icons": [],
  "attachments": []
}
```

说明：

- 存放图片、品牌图、背景图、图标、附件等静态资源
- 正文内容块优先引用这里的资源，而不是直接内嵌大量二进制或重复路径信息

---

#### `datasets`

数据型资源注册表。

建议先按资源类别拆分子 registry，例如：

```json
{
  "charts": [],
  "tables": [],
  "metrics": []
}
```

说明：

- 图表数据、表格数据、指标集等优先放这里
- 正文 `chart` / `table` 等块优先通过 `*Ref` 引用

---

#### `bibliography`

参考文献总表。

说明：

- 正文中的引文标记通过 `citation_ref` 等类型引用这里
- 文献详情不散落在正文块内

---

#### `footnotes`

脚注总表。

说明：

- 正文中的 `footnote_ref` 引用这里
- 脚注正文不直接嵌入原文段落主结构

---

#### `glossary`

术语表 / 缩写表 / 名词解释表。

说明：

- 预留学术与专业术语体系扩展空间
- `glossary_term` 可引用这里

---

#### `sections`

章节树根节点数组。

说明：

- `sections` 是整份报告正文的主结构
- 每个 section 节点拥有自己的 `body`
- `body` 是 section 内部的有序 body item 列表
- body item 同时表达：
  - 本节正文内容块组的顺序
  - 子章节插入位置的顺序
- Portable Text 风格块流挂在 `body` 中的 `content` 类型 item 里

---

## 4. 章节树合同

### 4.1 section 基础结构

推荐基础结构为：

```json
{
  "id": "sec-1",
  "level": 1,
  "title": "Executive Summary",
  "numbering": "auto",
  "anchor": "sec-1",
  "body": []
}
```

---

### 4.2 section 字段说明

#### `id`

section 的全局唯一稳定标识。

要求：

- 全文唯一
- 稳定
- 不因展示编号变化而变化

用途：

- 交叉引用
- 目录
- PDF 书签
- 锚点跳转
- 结构化编辑定位
- 局部更新

建议命名风格：

- `sec-1`
- `sec-market-overview`
- `appendix-a`

---

#### `level`

section 层级。

建议约定：

- 1 = 一级章节
- 2 = 二级章节
- 3 = 三级章节
- 4 = 四级章节

说明：

- `level` 描述逻辑层级
- 不直接决定字号或视觉样式
- Java 端后续可按 `level` + theme 决定标题视觉

---

#### `title`

章节标题纯文本。

要求：

- 存标题文本本身
- 不建议直接写入结构编号前缀
- 当前版本按纯文本处理

后续若确需支持标题内富文本，可考虑升级为：

- `titleText`
- `titleRichText`

---

#### `numbering`

编号策略。

当前版本采用以下基础语义值：

- `auto`
- `none`
- `manual`

含义：

- `auto`：由系统按章节结构自动编号
- `none`：不显示结构编号
- `manual`：后续允许手工指定展示编号

当前版本仅定义语义，不展开 `manual` 的字段结构。

---

#### `anchor`

章节锚点。

当前版本建议：

- 默认可与 `id` 相同
- 但保留独立字段

原因：

- 后续可能需要让系统内部 ID 与外部显示 anchor 分离
- 对外链接、网页锚点、PDF 书签命名可能需要不同策略

---

#### `body`

当前 section 内部的有序 body item 列表。

说明：

- `body` 是 section 内部的唯一正文组织入口
- `body` 负责表达本节内部各种内容与子章节的真实顺序
- `body` 中既可以出现连续正文块组，也可以出现子章节节点
- 引入 `body` 是为了避免原先 `content + children/subsections` 结构无法表达“正文与子章节交错顺序”的问题

---

### 4.3 body item 联合类型

`body` 中的每一个元素都称为一个 **body item**。

当前版本定义两类 body item：

#### 4.3.1 `content`

表示一组**连续的** Portable Text 风格正文块。

推荐结构：

```json
{
  "itemType": "content",
  "blocks": []
}
```

字段说明：

- `itemType = "content"`：表示这是正文块组
- `blocks`：Portable Text 风格块数组

约束：

- `blocks` 必须理解为**连续正文块组**
- 一个 `content` body item 内的块在阅读顺序上必须连续
- 不应用一个超大的 `content` item 把分散在子章节前后的多段本章节正文混在一起

#### 4.3.2 `subsection`

表示一个真正的子章节节点。

推荐结构：

```json
{
  "itemType": "subsection",
  "section": {
    "id": "sec-1-1",
    "level": 2,
    "title": "Background",
    "numbering": "auto",
    "anchor": "sec-1-1",
    "body": []
  }
}
```

字段说明：

- `itemType = "subsection"`：表示这是子章节项
- `section`：内嵌的真正 section 节点

说明：

- `subsection` 是一种 body item，用于参与本节内部顺序表达
- 它不是普通正文块，不应被降格为普通 content item
- 它承载的是一个真正的 section 结构节点
- 这样既保留顺序，也保留章节作为高阶结构对象的语义

---

### 4.4 section 结构约束

#### 约束 1：章节树通过内嵌 section 节点表达

不要用 `block.children.children...` 模拟章节树。

#### 约束 2：section 内部顺序由 `body` 表达

不要再使用 `content + children/subsections` 的分离模型来表达 section 内部顺序。

#### 约束 3：标题文本与编号分离

例如应优先存：

```json
{
  "title": "Market Overview",
  "numbering": "auto"
}
```

而不是直接存：

```json
{
  "title": "1.2 Market Overview"
}
```

#### 约束 4：父子 section 的 `level` 应自洽

例如：

- 父节点 `level = 1`
- 子节点通常 `level = 2`

校验器应校验层级一致性。

#### 约束 5：`body` 中的正文块和子章节顺序必须可直接由数组顺序读出

也就是说：

- 一段父章节正文在前还是子章节在前
- 两个子章节之间是否插入父章节正文
- 子章节之后是否还有父章节总结性正文

都必须能直接通过 `body[]` 的顺序判断，不应依赖额外推断。

#### 约束 6：`content.blocks` 中不允许再出现正式章节标题样式 `h1/h2/h3/h4`

正式章节的标题级别只能通过：

- 顶层 `sections[]`
- 或 body item 中的 `subsection.section`

的 `level` 字段来表达。

说明：

- `h1/h2/h3/h4` 不再作为正式章节结构的来源
- 若需“正文中的非正式小标题”，应使用 `subheading`

#### 约束 7：`body` 中的 `subsection` 应只承载比当前 section 更深一层的 section 节点

例如当前 section 的 `level = 1`，则其直接 `subsection.section.level` 应为 `2`。

---

## 5. Portable Text 在本协议中的使用边界

### 5.1 使用位置

Portable Text 风格内容数组只用于：

- `section.body[]` 中 `itemType = "content"` 的 `blocks`
- `footnotes[].blocks`
- `callout.blocks`

当前版本不要求以下位置也必须是 Portable Text：

- `meta`
- `bibliography`
- `glossary`
- `datasets`
- `assets`

### 5.2 使用原则

Portable Text 在本协议中负责：

- 文本块流
- 行内文本片段
- 文本 marks / markDefs
- 列表项
- `content` 类型 body item 中的正文块承载
- `footnotes.blocks` 与 `callout.blocks` 的受限子集承载

Portable Text 不负责：

- 顶层文档结构
- section 章节树本体
- section 内部子章节节点结构
- registry 体系
- 编号策略本体
- 引用目标解析体系本体
- PDF 页面排版

### 5.3 当前阶段沿用的 Portable Text 原生能力

#### 直接沿用

- `block`
- `span`
- `marks`
- `markDefs`
- `listItem`
- `level`

#### 保留原生思路但允许扩展

- `block.style`
- 行内对象
- 块级对象

#### 当前新增限制

- `content.blocks` 内不允许使用 `h1/h2/h3/h4` 表示正式章节标题
- 正式章节结构只能由 section 节点表达
- `footnotes.blocks` 与 `callout.blocks` 默认复用正文文本层规则的受限子集，不允许出现正式章节结构

---

## 6. 全局 Registry 体系

### 6.1 registry 的基本目的

registry 的作用是承载：

- 可复用资源
- 大型资源
- 可能被多处引用的对象
- 需要统一管理的对象
- 未来需要单独校验或缓存的对象

### 6.2 当前版本的顶层 registry

#### 静态资源 registry

- `assets.images`
- `assets.logos`
- `assets.backgrounds`
- `assets.icons`
- `assets.attachments`

#### 数据型资源 registry

- `datasets.charts`
- `datasets.tables`
- `datasets.metrics`

#### 学术与辅助 registry

- `bibliography`
- `footnotes`
- `glossary`

### 6.3 内容块与 registry 的关系

采用以下原则：

#### 原则 1：优先引用 registry

例如：

- 图片块优先 `imageRef`
- 图表块优先 `chartRef`
- 表格块优先 `tableRef`
- 引文优先 `citation_ref -> bibliography`
- 脚注优先 `footnote_ref -> footnotes`

#### 原则 2：少量简单内容允许内嵌

例如：

- 很短的一次性 callout 文本
- 简单分隔块
- 简短页内提示

#### 原则 3：复杂对象不要在多个正文块里重复拷贝

特别是：

- 大图片信息
- 大图表数据
- 复杂参考文献条目
- 长脚注正文

---

## 7. 全局 ID / Anchor / Numbering 体系

### 7.1 三层概念分离

推荐统一分离三层概念：

#### 1）系统 ID

系统内部稳定标识，例如：

- `sec-market-overview`
- `fig-valuation-trend`
- `eq-dcf-core`

#### 2）anchor

解析/跳转/书签使用的锚点标识。

#### 3）display number

面向读者展示的编号，例如：

- `1`
- `1.2`
- `Figure 3`
- `Table 2-1`
- `(4.2)`

当前版本明确“概念分离”，但不细化 display number 的视觉文本拼接格式。

### 7.2 推荐的 ID 类型前缀

#### 文档结构类

- `sec-*`
- `appendix-*`

#### 图形图表类

- `fig-*`
- `chart-*`
- `tbl-*`

#### 学术装置类

- `eq-*`
- `cite-*`
- `fn-*`
- `term-*`

#### 资源类

- `img-*`
- `asset-*`
- `data-*`

说明：

- 前缀不是唯一合法方案
- 但建议从 v1 开始形成统一命名惯例

### 7.3 编号策略的当前约定

#### section 编号

- 支持自动生成
- 编号按章节树推导
- 与 `title` 分离

#### figure / table / equation 编号

- 必须预留自动编号空间
- 当前版本不将“全文连续”或“按章节重置”限定为唯一规则
- 后续具体块字段设计时再定默认策略

#### appendix 编号

- 必须预留附录编号扩展空间
- 当前版本不细化

### 7.4 编号类别与对象类型的关系

编号类别（如 `section / figure / table / equation / appendix`）与对象 `_type` 是两个不同层级。

例如：

- `image` 与 `chart` 都可以归入 `figure` 编号类别
- `math_block` 归入 `equation` 编号类别
- `table` 归入 `table` 编号类别

---

## 8. 统一“可解析目标”模型

### 8.1 设计目标

任何可能被引用的对象，都应该可以被统一解析。

例如：

- section
- figure
- chart
- table
- equation
- bibliography item
- footnote
- glossary term
- image asset

### 8.2 当前版本的底层要求

一个可解析目标至少应具备：

- `id`
- `targetType` 或可推出类型
- `anchor`（显式或可推导）
- 可定位来源（所在 registry 或所在 section/body）

说明：

- 当前阶段不要求把所有对象都写成完全一致的 JSON 结构
- 但要求在底层设计上，所有可引用对象都具备统一解析入口
- 对 section 而言，其在结构上既可以位于顶层 `sections[]`，也可以位于某 section 的 `body[] -> subsection.section`

### 8.3 xref / 引文 / 脚注 对统一可解析目标模型的依赖

后续这些能力都会依赖本层：

- `xref`
- `citation_ref`
- `footnote_ref`
- TOC
- 图表目录
- 表格目录
- PDF 书签
- 页内跳转

因此本层属于底层合同，应在本版本中明确。

---

## 9. 类型清单 taxonomy

本节仅定义“清单与分类”，不展开字段细节。

### 9.1 A 类：直接沿用 Portable Text 原生能力

这些不重新发明。

#### 文本块与行内文本

- `block`
- `span`

#### 行内标记与定义

- `marks`
- `markDefs`

#### 列表能力

- `listItem`
- `level`

用途：

- 普通段落
- 正文文本内容
- 行内样式文本内容
- 加粗
- 斜体
- 下划线
- 链接
- 批注
- 列表项

### 9.2 B 类：先作为 `block.style` 扩展，而不是独立块对象

建议预留的 style 清单：

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

说明：

- 这些内容本质上仍然是“文本块”
- 当前版本不急于升级成独立 block object
- 后续如果出现明显结构化需求，再升级为独立对象
- `h1/h2/h3/h4` 不作为 `content.blocks` 中的正式章节样式使用；正式章节结构统一由 section 节点表达

### 9.3 C 类：预留为行内对象 / annotation 的类型清单

这些适合嵌在段落中，未来再补字段。

建议清单：

- `xref`
- `citation_ref`
- `footnote_ref`
- `inline_math`
- `glossary_term`
- `badge`
- `highlight_token`

说明：

- `xref` 用于交叉引用 section / figure / table / equation 等
- `citation_ref` 用于引用 bibliography
- `footnote_ref` 用于引用 footnotes
- `inline_math` 用于行内数学公式
- `glossary_term` 用于术语表链接
- `badge` / `highlight_token` 预留商业报告风格增强空间

### 9.4 D 类：预留为块级对象的类型清单

#### 基础报告块

- `image`
- `table`
- `chart`
- `code_block`
- `math_block`
- `callout`
- `quote_box`
- `page_break`

#### 文档结构辅助块

- `cover`
- `abstract_block`
- `toc_placeholder`
- `references_block`
- `appendix_marker`
- `section_divider`

#### 未来可扩展块

- `timeline`
- `comparison_card`
- `kpi_grid`
- `risk_matrix`
- `author_note`

说明：

- 当前版本只定义名字和分类
- 不细化具体字段
- 后续按优先级逐一细化

---

## 10. 学术装置与高级能力预留

当前版本先保留占位，不展开字段细节。

### 10.1 已预留的顶层 registry

- `bibliography`
- `footnotes`
- `glossary`

### 10.2 已预留的行内类型

- `citation_ref`
- `footnote_ref`
- `xref`
- `inline_math`
- `glossary_term`

### 10.3 已预留的块级类型

- `math_block`
- `references_block`

必要时后续可补：

- `footnotes_block`
- `glossary_block`

### 10.4 预留但暂不细化的高级能力

- 目录自动生成
- 图表目录
- 表格目录
- 公式编号
- 交叉引用解析
- 学术引文风格渲染
- 脚注布局
- 标题内富文本
- 附录体系

---

## 11. 当前版本的非目标

以下内容明确不在本协议当前范围内：

- Java PDF 渲染字号
- 字体
- 颜色
- 页边距
- 页眉页脚
- 背景图铺设方式
- 具体分页算法
- 公式排版实现
- 图表绘制实现
- 参考文献样式实现
- 主题视觉规范

这些将在后续渲染器合同或样式层专题中再设计。

---

## 12. 校验建议

虽然暂不写正式校验器，但 v1.0 建议至少满足以下校验规则：

1. `schemaVersion` 必填
2. `sections` 必须存在
3. section 的 `id` 全文唯一
4. section 的 `body` 必须是数组
5. body item 的 `itemType` 必须合法
6. `itemType = "content"` 时，`blocks` 必须是数组
7. `itemType = "subsection"` 时，`section` 必须存在
8. 父子 section 的 `level` 应自洽
9. 顶层 registry 字段必须存在，即使为空
10. 所有 `*Ref` 应能解析到有效目标
11. 标题文本不应强依赖展示编号
12. `content.blocks` 中不应出现正式章节标题样式 `h1/h2/h3/h4`
13. 同一对象不要在多个位置重复保存冲突定义

---

## 13. 当前版本未纳入详细定义但允许后续专题扩展的内容

以下点不阻塞 v1.0，可放到后续专题设计：

### 13.1 `meta` 的详细字段表

例如：

- `reportType`
- `clientName`
- `projectId`
- `generatedAt`
- `locale`

### 13.2 `manual` numbering 的具体表示方式

例如是字符串还是对象。

### 13.3 标题未来是否支持富文本

v1.0 当前不做。

### 13.4 `datasets.charts` 详细结构

延后到 chart 专题统一设计。

---

## 14. 最小示例

```json
{
  "schemaVersion": "report.v1",
  "meta": {
    "title": "Patent Valuation Report",
    "language": "en"
  },
  "theme": {},
  "assets": {
    "images": [],
    "logos": [],
    "backgrounds": [],
    "icons": [],
    "attachments": []
  },
  "datasets": {
    "charts": [],
    "tables": [],
    "metrics": []
  },
  "bibliography": [],
  "footnotes": [],
  "glossary": [],
  "sections": [
    {
      "id": "sec-1",
      "level": 1,
      "title": "Executive Summary",
      "numbering": "auto",
      "anchor": "sec-1",
      "body": [
        {
          "itemType": "content",
          "blocks": [
            {
              "_type": "block",
              "style": "normal",
              "children": [
                {
                  "_type": "span",
                  "text": "This is the opening introduction of the chapter.",
                  "marks": []
                }
              ],
              "markDefs": []
            }
          ]
        },
        {
          "itemType": "subsection",
          "section": {
            "id": "sec-1-1",
            "level": 2,
            "title": "Background",
            "numbering": "auto",
            "anchor": "sec-1-1",
            "body": [
              {
                "itemType": "content",
                "blocks": [
                  {
                    "_type": "block",
                    "style": "normal",
                    "children": [
                      {
                        "_type": "span",
                        "text": "This is the body text of subsection 1.1.",
                        "marks": []
                      }
                    ],
                    "markDefs": []
                  }
                ]
              }
            ]
          }
        },
        {
          "itemType": "content",
          "blocks": [
            {
              "_type": "block",
              "style": "normal",
              "children": [
                {
                  "_type": "span",
                  "text": "This is a concluding paragraph after subsection 1.1.",
                  "marks": []
                }
              ],
              "markDefs": []
            }
          ]
        }
      ]
    }
  ]
}
```

---

## 15. 协议状态总结

基于当前已确认的方向，本协议已完成从“Portable Text 富文本底座”到“报告中间协议底层骨架”的第一版定义。

### 15.1 已定义的内容

1. **顶层结构**

   - `schemaVersion`
   - `meta`
   - `theme`
   - `assets`
   - `datasets`
   - `bibliography`
   - `footnotes`
   - `glossary`
   - `sections`
2. **章节结构模型**

   - 采用树形 `sections`
   - section 标题使用 `section.title`
   - section 内部顺序使用 `body[]` 表达
   - `body[]` 当前包含：
     - `content`
     - `subsection`
3. **正文与章节的边界**

   - Portable Text 只用于 `body` 中的 `content.blocks`
   - 正式章节结构不再通过 `content.blocks` 中的标题块表达
   - `content.blocks` 表示连续正文块组
4. **全局资源与 registry 体系**

   - 静态资源放入 `assets`
   - 数据型资源放入 `datasets`
   - 学术与辅助对象放在 `bibliography / footnotes / glossary`
5. **统一引用目标基础**

   - 所有可被引用对象都应具备统一可解析入口
   - 已明确 `id / anchor / display number` 的概念分离
   - 已明确基础 ID 命名前缀建议
   - 已区分“编号类别”与“对象类型”
6. **类型清单 taxonomy**

   - 直接沿用的 Portable Text 原生能力
   - `block.style` 扩展层
   - 行内对象 / annotation 预留层
   - 块级对象预留层
7. **学术装置扩展空间**

   - 已为 `xref`
   - `citation_ref`
   - `footnote_ref`
   - `inline_math`
   - `math_block`
   - `references_block`
     等能力预留位置

### 15.2 已能稳定表达的能力

本协议已经能够正确表达：

- 章节与子章节的树形结构
- section 内部正文与子章节交错出现的真实顺序
- 子章节之间插入正文、图表、总结块等内容的可能性
- 子章节之后继续出现正文的情况
- 标题文本与结构编号分离
- 章节结构语义与 Portable Text 正文块流语义的清晰边界
- 面向后续交叉引用、目录、图表编号、公式编号的底层扩展空间

### 15.3 本版本未纳入详细定义但已预留空间的内容

以下内容尚未定义具体字段，但底层已预留扩展空间：

- `datasets.charts`
- Java 渲染器合同
- Java PDF 样式与页面级排版规则
- chart 专题中的自定义图表协议

---

## 16. 正文块规则

### 16.1 适用范围

本章规则适用于：

- `section.body[]` 中 `itemType = "content"` 的 body item
- 该 body item 内部的 `blocks[]`
- `blocks[]` 中的文本块、列表块、块级对象与行内对象

本章不适用于：

- 顶层 `sections[]`
- `subsection.section`
- `meta`
- `assets`
- `datasets`
- `bibliography`
- `footnotes`
- `glossary`

### 16.2 `content` body item 的职责

`content` body item 表示一组**连续的正文块**。

推荐结构保持为：

```json
{
  "itemType": "content",
  "blocks": []
}
```

说明：

- `blocks` 的数组顺序就是阅读顺序
- 一个 `content` body item 内的内容必须在阅读上连续
- 若正文被一个 `subsection` 打断，则应拆分为两个 `content` body item
- `content` body item 不表达章节结构
- `content` body item 仅表达当前 section 内的一段连续内容流

### 16.3 `blocks` 中允许出现的内容类别

当前版本，`content.blocks[]` 允许出现以下三类内容：

#### 16.3.1 文本块

基于 Portable Text 的 `block`，用于承载文本型内容，例如：

- 普通正文
- 引用块
- 非正式小标题
- caption 类文本
- smallprint
- lead
- quote_source

#### 16.3.2 列表块

仍然是 `block`，但带：

- `listItem`
- `level`

用于承载：

- 无序列表
- 有序列表
- 分层列表

说明：

- 列表块在模型层仍属于正文块
- 不构成章节结构

#### 16.3.3 块级对象

块级对象也允许出现在 `content.blocks[]` 中，例如：

- `image`
- `chart`
- `table`
- `code_block`
- `math_block`
- `callout`
- `quote_box`
- `page_break`

说明：

- `content.blocks[]` 不是“纯文字段落数组”
- 它表示当前 section 内一段连续内容流
- 文本块与块级对象可以混排，只要顺序连续即可

### 16.4 段落与 `block` 的关系

当前版本采用如下基本规则：

#### 规则 1

默认情况下，一个 `block` = 一个段落级文本块。

这意味着：

- 一个普通正文段落对应一个 `block`
- 一个 blockquote 对应一个 `block`
- 一个 caption 对应一个 `block`
- 一个非正式小标题对应一个 `block`

#### 规则 2

新的段落边界通过以下方式体现：

- 新建一个新的 `block`
- 或插入一个块级对象

#### 规则 3

不要使用段内硬换行去模拟新段落。

### 16.5 同一段内的行内内容关系

当前版本采用如下规则：

#### 规则 1

同一个 `block.children[]` 中的所有 `span` 与 inline object，属于同一个段落级文本块。

#### 规则 2

同一 `block` 内允许混合出现：

- `span`
- `hard_break`
- `xref`
- `citation_ref`
- `footnote_ref`
- `glossary_term`
- 未来其他 inline object

#### 规则 3

`marks / markDefs` 按 Portable Text 原生机制工作，用于表达：

- 加粗
- 斜体
- 下划线
- 链接
- 批注等 annotation

### 16.6 段落换行与段内硬换行

#### 16.6.1 段间换行

段间换行统一通过新建 `block` 表达。

#### 16.6.2 段内硬换行

段内硬换行引入专用行内对象：

```json
{
  "_type": "hard_break"
}
```

规则如下：

- `hard_break` 只表示同一段内部的强制换行
- `hard_break` 不等价于新段落
- 不建议在普通 `span.text` 中直接用 `\n` 表达正式硬换行语义

### 16.7 缩进与 tab 规则

#### 规则 1

普通正文的首行缩进不属于内容语义层，不建议用 tab 字符表达。

#### 规则 2

普通正文缩进、段前段后距、对齐方式等属于 Java 渲染样式层控制。

#### 规则 3

只有在特殊内容需要保留原始排版时，才考虑保留“制表/预格式”语义，例如：

- `code_block`
- 未来可能的 `preformatted_block`

当前结论：

- 正文层不设计通用 tab 语义
- 正文层设计 `hard_break`
- 普通缩进交给渲染层处理

### 16.8 非正式小标题 `subheading`

#### 16.8.1 定义

`subheading` 表示 section 内部的**非正式小标题**。

#### 16.8.2 边界

`subheading` 不是正式章节结构，因此：

- 不形成新的 `section`
- 不进入 `sections` 树
- 不参与 section 编号
- 默认不作为正式目录结构来源
- 默认不作为正式 `xref` 目标

#### 16.8.3 推荐示例

```json
{
  "_type": "block",
  "style": "subheading",
  "children": [
    { "_type": "span", "text": "Key Assumptions", "marks": [] }
  ],
  "markDefs": []
}
```

### 16.9 caption 类文本块

当前版本保留以下文本块 style：

- `caption`
- `figure_caption`
- `table_caption`
- `equation_caption`

说明：

- 当前版本它们仍然是文本块 style，不升级成独立 block object
- 它们用于承载说明性文本
- 不形成章节结构
- 默认服务于其相邻相关对象

建议语义：

- `caption`：通用说明文字
- `figure_caption`：图题注
- `table_caption`：表题注
- `equation_caption`：公式说明文字

### 16.10 当前版本允许的正文文本 style 清单

在 `content.blocks[]` 中，当前版本建议允许以下文本块 style：

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

当前版本明确不允许：

- `h1`
- `h2`
- `h3`
- `h4`

说明：

- 这些样式不再作为正式章节标题使用
- 正式章节统一由 section 节点表达

### 16.11 正文块层的补充约束

1. `content.blocks[]` 中允许混排文本块与块级对象
2. `content.blocks[]` 中不允许出现正式章节节点
3. `content.blocks[]` 中不允许使用 `h1/h2/h3/h4` 充当正式章节标题
4. 一个 `content` body item 应只表示一段连续内容流
5. `subheading` 只能表示非正式小标题，不能替代 `subsection`

---

## 17. 第一批行内对象规则

### 17.1 适用范围

本章规则适用于：

- `block.children[]` 中的自定义 inline object

当前版本定义第一批行内对象如下：

- `hard_break`
- `xref`
- `citation_ref`
- `footnote_ref`
- `glossary_term`

### 17.2 通用原则

#### 原则 1

行内对象只能出现在 `block.children[]` 中。

#### 原则 2

行内对象属于当前 `block`，不独立形成段落。

#### 原则 3

行内对象的阅读顺序由其在 `children[]` 中的位置决定。

#### 原则 4

行内对象如果带引用关系，其目标必须可被统一解析。

### 17.3 `hard_break`

#### 定义

表示同一段内部的强制换行。

#### 推荐结构

```json
{
  "_type": "hard_break"
}
```

#### 规则

- 不带附加字段
- 不形成独立内容块
- 不等价于新段落

### 17.4 `xref`

#### 定义

用于交叉引用正式结构目标或可编号对象，例如：

- section
- figure
- table
- equation

#### 推荐最小结构

```json
{
  "_type": "xref",
  "targetType": "section",
  "targetId": "sec-1-1"
}
```

#### 推荐最小字段

- `_type`
- `targetType`
- `targetId`

#### 说明

- `targetType` 表示**语义引用类别**，不是对象 `_type`
- `figure` 可对应正文中的 `image` 或 `chart` 实例
- `equation` 可对应正文中的 `math_block` 实例
- `targetId` 必须能解析到有效目标
- 当前版本不细化更复杂字段，如 `prefix / suffix / explicitText`

### 17.5 `citation_ref`

#### 定义

用于引用 `bibliography` 中的一个或多个文献条目。

#### 推荐最小结构

```json
{
  "_type": "citation_ref",
  "refIds": ["cite-smith-2024"],
  "mode": "parenthetical"
}
```

#### 推荐最小字段

- `_type`
- `refIds`
- `mode`

#### 字段说明

- `refIds`：引用的 bibliography 条目 ID 列表
- `mode`：引用模式，当前版本至少预留：
  - `parenthetical`
  - `narrative`

### 17.6 `footnote_ref`

#### 定义

用于引用 `footnotes` 中的脚注条目。

#### 推荐最小结构

```json
{
  "_type": "footnote_ref",
  "refId": "fn-1"
}
```

#### 推荐最小字段

- `_type`
- `refId`

### 17.7 `glossary_term`

#### 定义

用于引用 `glossary` 中的术语或缩写条目。

#### 推荐最小结构

```json
{
  "_type": "glossary_term",
  "termId": "term-dcf"
}
```

#### 推荐最小字段

- `_type`
- `termId`

### 17.8 行内对象与 span / marks 的关系

#### 规则 1

行内对象与 `span` 可以在同一 `children[]` 中混排。

#### 规则 2

简单文本样式仍优先使用 `marks / markDefs`，而不是滥用自定义 inline object。

#### 规则 3

“引用目标”类语义优先使用行内对象，不建议塞进普通 span 文本里硬编码。

### 17.9 行内对象校验建议

当前版本建议至少满足：

1. `hard_break` 不应带多余业务字段
2. `xref.targetId` 必须能解析到有效目标
3. `citation_ref.refIds` 不应为空
4. `citation_ref.refIds[]` 中的每个 ID 都应能解析到 bibliography 条目
5. `footnote_ref.refId` 应能解析到 footnote 条目
6. `glossary_term.termId` 应能解析到 glossary 条目
7. 行内对象不得伪装为正式章节结构

---

## 18. 文本层状态总结

本协议已经完成了“文本层协议”的第一阶段定义，主要包括：

1. `content` body item 的职责
2. `content.blocks[]` 中允许出现的内容类别
3. 段落与 `block` 的关系
4. 段内硬换行 `hard_break`
5. 正文缩进与 tab 的边界
6. 非正式小标题 `subheading`
7. caption 类文本块规则
8. 正文层实际可用 style 清单
9. 第一批行内对象：
   - `xref`
   - `citation_ref`
   - `footnote_ref`
   - `glossary_term`

这使得当前协议已经能够更完整地表达：

- section 内连续正文流
- 段落边界
- 段内强制换行
- 非正式小标题
- caption 类说明文字
- 正文中的引用、脚注、术语、交叉引用

---

## 19. 对象层前置结论

在进入对象层之前，当前协议已经明确了以下关键前提：

1. 顶层结构已确定
2. 章节结构已确定为 `sections[] -> section.body[]`
3. Portable Text 的边界已明确
4. 文本层规则已明确

基于以上前提，对象层采用以下原则。

### 19.1 原则 A：caption 优先保持为相邻文本块

当前版本建议：

- `image`
- `chart`
- `table`
- `math_block`

这些对象本身不强制内嵌 caption 文本字段。caption 继续优先使用相邻的文本块 style，例如：

- `figure_caption`
- `table_caption`
- `equation_caption`

### 19.2 原则 B：块对象自己的 `id` 与底层 `*Ref` 分离

当前版本建议：

- 渲染到正文中的对象块，允许拥有自己的 `id / anchor`
- 同时它们通过：
  - `imageRef`
  - `chartRef`
  - `tableRef`
  - 未来其他 `*Ref`

引用 registry 中的底层资源

例如：

```json
{
  "_type": "chart",
  "id": "fig-market-share",
  "anchor": "fig-market-share",
  "chartRef": "chart-market-share"
}
```

这意味着：

- `chartRef` 指向底层数据资源
- `id / anchor` 指向正文中的这个可引用对象实例

---

## 20. registry 条目基型

### 20.1 设计目标

registry 条目基型用于统一：

- `assets.*`
- `datasets.*`
- 未来其他可复用资源集合

其目标是让不同 registry 条目至少具备一组稳定公共字段，便于：

- Python 生成
- Java 解析
- 校验器校验
- 日后扩展更多资源类型

### 20.2 推荐公共字段基型

当前版本建议所有 registry 条目优先具备以下公共字段：

```json
{
  "id": "resource-id",
  "anchor": "resource-id",
  "label": "Optional human-readable label",
  "meta": {}
}
```

字段说明：

#### `id`

条目全局唯一稳定标识。

#### `anchor`

锚点标识。默认可与 `id` 相同。

#### `label`

可选的人类可读标签。

#### `meta`

附加元信息对象。

### 20.3 registry 条目基型的补充约束

1. 同一 registry 中 `id` 必须唯一
2. 跨 registry 的 `id` 最好也保持全局唯一
3. `anchor` 默认可省略并回退为 `id`
4. `label` 可省略
5. `meta` 可为空对象

### 20.4 资源条目与正文对象实例的关系

当前版本明确如下区分：

#### 资源条目（registry entry）

表示底层可复用资源，例如：

- 一张原始图片
- 一组图表数据
- 一张表格数据集

#### 正文对象实例（content block object）

表示正文中的一次使用，例如：

- 文中的某张图
- 文中的某个图表
- 文中的某个表格

这两个层级不应混为一谈。

---

## 21. 核心块级对象第一版规则

本章定义以下对象的第一版规则：

- `image`
- `chart`
- `table`
- `math_block`
- `callout`

### 21.1 块级对象的共同规则

1. 块级对象可以出现在 `content.blocks[]` 中
2. 块级对象在阅读顺序上是正文流的一部分
3. 块级对象如果可能被 `xref` 引用，则应具备：
   - `id`
   - `anchor`
4. 块级对象优先通过 `*Ref` 指向 registry 条目，而不是重复内嵌大资源
5. caption 优先由相邻 caption 类文本块承载，不强制内嵌在对象字段中
6. 块级对象的 `id` 不等于底层 `*Ref`，两者在语义上分离

### 21.2 `image`

推荐最小结构：

```json
{
  "_type": "image",
  "id": "fig-pipeline-overview",
  "anchor": "fig-pipeline-overview",
  "imageRef": "img-pipeline-overview"
}
```

说明：

- `imageRef` 指向 `assets.images` 中的图片资源条目
- `id / anchor` 表示正文中的该图片实例
- 图片题注优先在相邻位置使用 `figure_caption`

### 21.3 `chart`

推荐最小结构：

```json
{
  "_type": "chart",
  "id": "fig-market-share",
  "anchor": "fig-market-share",
  "chartRef": "chart-market-share"
}
```

说明：

- `chartRef` 指向 `datasets.charts` 中的图表数据条目
- `id / anchor` 表示正文中的图表实例
- 图表标题与说明优先使用相邻 `figure_caption`

### 21.4 `table`

推荐最小结构：

```json
{
  "_type": "table",
  "id": "tbl-financial-summary",
  "anchor": "tbl-financial-summary",
  "tableRef": "table-financial-summary"
}
```

说明：

- `tableRef` 指向 `datasets.tables` 中的表格数据条目
- `id / anchor` 表示正文中的表格实例
- 表题注优先使用相邻 `table_caption`

### 21.5 `math_block`

推荐最小结构：

```json
{
  "_type": "math_block",
  "id": "eq-dcf-core",
  "anchor": "eq-dcf-core",
  "latex": "V = \\sum_{t=1}^{n} \\frac{CF_t}{(1+r)^t}"
}
```

说明：

- 当前阶段允许直接内嵌 `latex`
- 若需要额外说明文字，优先使用相邻 `equation_caption`

### 21.6 `callout`

推荐最小结构：

```json
{
  "_type": "callout",
  "id": "callout-key-finding-1",
  "anchor": "callout-key-finding-1",
  "blocks": []
}
```

说明：

- `callout` 当前阶段允许直接内嵌 `blocks`
- 其内部 `blocks` 默认复用 `content.blocks` 的正文块规则子集
- 不允许出现正式章节结构
- 当前阶段不必为 `callout` 单独建 registry

### 21.7 对象与 caption 的相邻使用建议

推荐如下相邻模式：

#### 图片

```text
image
figure_caption
```

#### 图表

```text
chart
figure_caption
```

#### 表格

```text
table
table_caption
```

#### 公式

```text
math_block
equation_caption
```

#### callout

通常无需 caption，除非后续有特殊需要。

### 21.8 核心块级对象校验建议

当前版本建议至少满足：

1. `image.imageRef` 必须能解析到 `assets.images`
2. `chart.chartRef` 必须能解析到 `datasets.charts`
3. `table.tableRef` 必须能解析到 `datasets.tables`
4. `math_block.latex` 不应为空
5. `callout.blocks` 必须是数组
6. 可被引用的块级对象应具备 `id`
7. `anchor` 默认可回退为 `id`
8. 块对象的 `id` 与底层 `*Ref` 不应混淆使用

---

## 22. 具体 registry 条目结构范围说明

在进入具体 registry 条目结构时，当前协议已明确：

1. registry 条目公共基型
2. 正文对象实例与底层资源条目分离
3. caption 当前优先采用“相邻文本块”模式

本版本进一步细化最基础、最常用的两类 registry 条目：

- `assets.images`
- `datasets.tables`

同时明确：

- `datasets.charts` 暂缓详细设计，等基础能力稳定后再单独专题展开

---

## 23. `assets.images` 条目结构

### 23.1 设计目标

`assets.images` 用于承载底层图片资源条目。正文中的图片对象实例通过 `imageRef` 指向这里。

### 23.2 推荐最小结构

```json
{
  "id": "img-pipeline-overview",
  "anchor": "img-pipeline-overview",
  "label": "Pipeline overview image",
  "meta": {},
  "src": "https://example.com/pipeline-overview.png",
  "alt": "Pipeline overview"
}
```

### 23.3 推荐字段说明

#### 通用基型字段

- `id`
- `anchor`
- `label`
- `meta`

#### 图片专属字段

##### `src`

图片资源位置。

##### `alt`

图片的替代文本。

说明：

- 用于语义说明、无障碍、日志、调试
- 不等价于图片题注
- 图片题注仍优先由相邻 `figure_caption` 文本块承载

### 23.4 可选扩展字段（当前不强制）

- `width`
- `height`
- `mimeType`
- `checksum`
- `source`
- `copyright`
- `language`

### 23.5 与正文对象实例的关系

正文中的图片实例推荐结构如下：

```json
{
  "_type": "image",
  "id": "fig-pipeline-overview",
  "anchor": "fig-pipeline-overview",
  "imageRef": "img-pipeline-overview"
}
```

说明：

- 一个 `assets.images` 条目可被多个正文 `image` 实例复用
- 不同正文实例可以有不同的局部上下文、编号、相邻 caption

### 23.6 `assets.images` 校验建议

当前版本建议至少满足：

1. `id` 必填
2. `src` 必填
3. `alt` 建议提供
4. 同一 registry 中 `id` 唯一
5. `anchor` 缺省时可回退为 `id`
6. 被 `imageRef` 引用的条目必须存在

---

## 24. `datasets.tables` 条目结构

### 24.1 设计目标

`datasets.tables` 用于承载底层表格数据资源。正文中的 `table` 对象实例通过 `tableRef` 指向这里。

### 24.2 当前阶段推荐的数据组织方式

当前阶段推荐采用：

- `columns[]` 定义列
- `rows[]` 定义行
- 每一行用对象表达，键名与列 `key` 对应

推荐最小结构如下：

```json
{
  "id": "table-financial-summary",
  "anchor": "table-financial-summary",
  "label": "Financial summary table",
  "meta": {},
  "columns": [
    { "key": "year", "header": "Year" },
    { "key": "revenue", "header": "Revenue" },
    { "key": "margin", "header": "Margin" }
  ],
  "rows": [
    { "year": "2022", "revenue": "12.3M", "margin": "18%" },
    { "year": "2023", "revenue": "15.8M", "margin": "21%" }
  ]
}
```

### 24.3 为什么当前推荐“列定义 + 行对象”而不是纯二维数组

原因如下：

1. 列顺序由 `columns[]` 明确控制
2. 每个单元格值通过列 `key` 关联，语义更清晰
3. 对 Python 生成与 Java 解析都更友好
4. 后续更容易扩展列类型、对齐方式、格式化规则等

### 24.4 `columns[]` 字段建议

推荐最小结构：

```json
{
  "key": "revenue",
  "header": "Revenue"
}
```

字段说明：

- `key`：列的稳定键名，在同一张表内唯一
- `header`：列标题文本，当前阶段先按纯文本处理

### 24.5 `rows[]` 字段建议

`rows[]` 是对象数组，每个对象表示一行。

当前阶段规则：

1. `rows[]` 中每个对象的键应来自 `columns[].key`
2. 缺失键允许存在，但渲染器应按空值处理
3. 当前阶段单元格值允许：
   - string
   - number
   - boolean
   - null
4. 当前阶段不细化复杂单元格对象结构
5. 当前阶段不细化合并单元格能力

### 24.6 与正文对象实例的关系

正文中的表格实例推荐结构如下：

```json
{
  "_type": "table",
  "id": "tbl-financial-summary",
  "anchor": "tbl-financial-summary",
  "tableRef": "table-financial-summary"
}
```

说明：

- 同一表格数据可在多个正文位置被引用
- 不同正文实例可配不同上下文或相邻 `table_caption`

### 24.7 caption 与 table 的关系

当前版本继续沿用既有原则：

- 表题注优先使用相邻 `table_caption`
- 不强制在 `datasets.tables` 条目中存 caption
- 不强制在正文 `table` 对象实例中存 caption

推荐相邻模式：

```text
table
table_caption
```

### 24.8 `datasets.tables` 的可选扩展字段（当前不强制）

- `columnGroups`
- `footerRows`
- `notes`
- `defaultAlign`
- `cellFormatRules`
- `rowOrder`
- `source`

### 24.9 `datasets.tables` 校验建议

当前版本建议至少满足：

1. `id` 必填
2. `columns` 必须是数组
3. `rows` 必须是数组
4. `columns[].key` 在同一表内唯一
5. `columns[].header` 必填
6. `rows[]` 中出现的键应能在 `columns[].key` 中找到
7. 被 `tableRef` 引用的条目必须存在
8. `anchor` 缺省时可回退为 `id`

### 24.10 `datasets.charts` 的当前版本范围

考虑到后续会有较多自定义图表能力，例如：

- 饼图
- 柱状图
- 雷达图
- 其他业务自定义图表

当前版本仅将 **pie chart** 作为 `datasets.charts` 的基础样例与正式支持类型；其他图表类型保留到 chart 专题统一设计。

当前结论：

- 保留 `datasets.charts` registry 位置
- 保留正文 `chart` 对象实例最小结构：
  - `_type`
  - `id`
  - `anchor`
  - `chartRef`
- 当前版本正式定义一类 `chartType = "pie"` 的图表条目结构
- 其他图表类型的详细字段延后到 chart 专题统一设计

### 24.11 pie chart 条目结构

当前版本建议 `datasets.charts` 中的 pie chart 条目采用“图表级对象 + `slices[]` 对象数组”的结构，而不是多组并行数组。

推荐最小结构如下：

```json
{
  "id": "chart-area-share",
  "anchor": "chart-area-share",
  "label": "Area share pie chart",
  "meta": {},
  "chartType": "pie",
  "valueUnit": "percent",
  "slices": [
    {
      "key": "tech",
      "label": {
        "en": "Technology",
        "zh": "技术"
      },
      "value": 42.5,
      "description": {
        "en": "Technology contributes the largest share.",
        "zh": "技术板块占比最高。"
      }
    },
    {
      "key": "finance",
      "label": {
        "en": "Finance",
        "zh": "金融"
      },
      "value": 31.2,
      "description": {
        "en": "Finance is the second largest segment.",
        "zh": "金融板块位居第二。"
      }
    }
  ]
}
```

说明：

- `chartType` 用于声明图表类型；当前版本在 `datasets.charts` 中正式支持 `pie`
- `valueUnit` 用于声明数值单位，例如 `percent / amount / count`
- `slices[]` 中的每个对象表示一个扇区
- `label` 与 `description` 采用语言对象形式，便于后续扩展多语言
- 当前版本推荐正式协议使用对象数组结构；如有需要，Python 包可以在输入层兼容并行数组，再转换成正式协议结构

### 24.12 pie chart 的扇区字段建议

`slices[]` 中每个扇区对象建议至少包含以下字段：

- `key`
- `label`
- `value`
- `description`

字段说明：

#### `key`

扇区的稳定标识。

说明：

- 用于程序内部解析、排序、映射、更新与日志定位
- 不要求直接作为最终展示文本

#### `label`

扇区名称。

推荐结构：

```json
{
  "en": "Technology",
  "zh": "技术"
}
```

#### `value`

扇区数值。

说明：

- 当前版本建议为 number
- 其解释方式由图表级字段 `valueUnit` 决定

#### `description`

扇区说明文字。

推荐结构：

```json
{
  "en": "Technology contributes the largest share.",
  "zh": "技术板块占比最高。"
}
```

说明：

- 当前版本建议为语言对象
- 若某些场景不需要说明文字，可允许为空对象或省略

### 24.13 pie chart 与正文 `chart` 对象实例的关系

正文中的图表实例继续采用已定义的最小结构：

```json
{
  "_type": "chart",
  "id": "fig-area-share",
  "anchor": "fig-area-share",
  "chartRef": "chart-area-share"
}
```

语义分离如下：

- `chart-area-share`：表示底层 pie chart 数据条目
- `fig-area-share`：表示该图表在正文中的一次使用

说明：

- 同一 pie chart 数据条目可在多个正文位置复用
- 不同正文实例可拥有不同局部上下文、编号与相邻 `figure_caption`

### 24.14 `datasets.charts` 的当前边界

当前版本仅正式定义：

- `chartType = "pie"` 的基础结构
- `chart` 正文对象实例与 `chartRef` 的引用关系

当前版本不细化：

- 柱状图、折线图、雷达图等其他图表类型
- 图表颜色、图例、排序、标签显示策略
- 饼图扇区的高级渲染配置
- 多系列图表数据协议

这些内容将在 chart 专题中继续设计。

---

## 25. 学术与辅助 registry 条目前置结论

在进入学术与辅助 registry 条目之前，当前协议已经明确了以下关键前提：

1. 顶层已预留：
   - `bibliography`
   - `footnotes`
   - `glossary`
2. 文本层已经定义第一批行内对象：
   - `citation_ref`
   - `footnote_ref`
   - `glossary_term`
3. 统一可解析目标模型已明确
4. registry 条目公共基型已经明确：
   - `id`
   - `anchor`
   - `label`
   - `meta`

本阶段的目标不是设计最终显示样式，而是先定义这些条目的最小语义结构，让：

- Python 可以稳定生成
- Java 将来可以稳定 resolve
- `citation_ref / footnote_ref / glossary_term` 真正闭环

---

## 26. `bibliography` 条目结构

### 26.1 设计目标

`bibliography` 用于承载可被 `citation_ref` 引用的参考文献条目。

### 26.2 当前阶段推荐最小结构

```json
{
  "id": "cite-smith-2024",
  "anchor": "cite-smith-2024",
  "label": "Smith 2024",
  "meta": {},
  "type": "article",
  "title": "Valuation under Market Uncertainty",
  "authors": ["Alice Smith", "Bob Jones"],
  "year": 2024
}
```

### 26.3 推荐字段说明

#### 通用基型字段

- `id`
- `anchor`
- `label`
- `meta`

#### bibliography 专属最小字段

- `type`
- `title`
- `authors`
- `year`

### 26.4 可选扩展字段（当前不强制）

- `journal`
- `publisher`
- `volume`
- `issue`
- `pages`
- `doi`
- `url`
- `accessedAt`
- `edition`
- `institution`
- `language`

### 26.5 与 `citation_ref` 的关系

正文中的 `citation_ref` 推荐最小结构为：

```json
{
  "_type": "citation_ref",
  "refIds": ["cite-smith-2024"],
  "mode": "parenthetical"
}
```

说明：

- 一个 bibliography 条目可被多次引用
- 一个 `citation_ref` 可引用一个或多个 bibliography 条目
- 当前阶段不在正文中重复写文献详情

### 26.6 `bibliography` 校验建议

当前版本建议至少满足：

1. `id` 必填
2. `type` 必填
3. `title` 必填
4. `authors` 必须是数组，且不应为空
5. `year` 建议提供
6. 同一 `bibliography` 中 `id` 唯一
7. 被 `citation_ref.refIds[]` 引用的条目必须存在
8. `anchor` 缺省时可回退为 `id`

---

## 27. `footnotes` 条目结构

### 27.1 设计目标

`footnotes` 用于承载可被 `footnote_ref` 引用的脚注条目。

### 27.2 当前阶段推荐最小结构

```json
{
  "id": "fn-1",
  "anchor": "fn-1",
  "label": "Footnote 1",
  "meta": {},
  "blocks": [
    {
      "_type": "block",
      "style": "normal",
      "children": [
        { "_type": "span", "text": "This is the content of footnote 1.", "marks": [] }
      ],
      "markDefs": []
    }
  ]
}
```

### 27.3 推荐字段说明

#### 通用基型字段

- `id`
- `anchor`
- `label`
- `meta`

#### footnotes 专属最小字段

- `blocks`

说明：

- 当前版本建议直接使用 Portable Text 风格块数组
- 这使脚注内容本身也能承载普通文本、marks、链接及必要的轻量行内对象
- `footnotes.blocks` 默认复用正文文本层规则的受限子集
- 不允许出现正式章节结构

### 27.4 与 `footnote_ref` 的关系

正文中的 `footnote_ref` 推荐最小结构为：

```json
{
  "_type": "footnote_ref",
  "refId": "fn-1"
}
```

说明：

- 当前阶段 `footnote_ref` 指向一个脚注条目
- 当前版本不细化是否允许多个位置复用同一脚注条目，但结构上允许

### 27.5 `footnotes` 校验建议

当前版本建议至少满足：

1. `id` 必填
2. `blocks` 必须是数组
3. `blocks` 不应为空
4. 同一 `footnotes` 中 `id` 唯一
5. 被 `footnote_ref.refId` 引用的条目必须存在
6. `anchor` 缺省时可回退为 `id`

---

## 28. `glossary` 条目结构

### 28.1 设计目标

`glossary` 用于承载可被 `glossary_term` 引用的术语、缩写或概念条目。

### 28.2 当前阶段推荐最小结构

```json
{
  "id": "term-dcf",
  "anchor": "term-dcf",
  "label": "DCF",
  "meta": {},
  "term": "DCF",
  "definition": "Discounted Cash Flow",
  "aliases": ["Discounted Cash Flow"]
}
```

### 28.3 推荐字段说明

#### 通用基型字段

- `id`
- `anchor`
- `label`
- `meta`

#### glossary 专属最小字段

- `term`
- `definition`
- `aliases`

说明：

- `term` 当前阶段建议为纯文本
- `definition` 当前版本先按纯文本处理
- 后续若需要富文本定义，可升级为 `blocks`
- `aliases` 当前阶段可选

### 28.4 与 `glossary_term` 的关系

正文中的 `glossary_term` 推荐最小结构为：

```json
{
  "_type": "glossary_term",
  "termId": "term-dcf"
}
```

说明：

- 同一个 glossary 条目可被多次引用
- 当前阶段不细化正文渲染时是悬浮提示、跳转、首次展开解释还是末尾术语表列出
- 这些行为由后续渲染器策略决定

### 28.5 `glossary` 校验建议

当前版本建议至少满足：

1. `id` 必填
2. `term` 必填
3. `definition` 必填
4. `aliases` 如存在则必须是数组
5. 同一 `glossary` 中 `id` 唯一
6. 被 `glossary_term.termId` 引用的条目必须存在
7. `anchor` 缺省时可回退为 `id`

---

## 29. 当前协议的完成状态与后续专题

### 29.1 当前已经完成的协议部分

本协议当前已完成以下内容：

1. 顶层结构
2. section/body 章节结构
3. Portable Text 使用边界
4. 文本层规则
5. 第一批行内对象
6. 对象层规则
7. registry 公共基型
8. 图片与表格 registry 条目
9. bibliography / footnotes / glossary 条目

### 29.2 当前未纳入本版详细定义但已明确后续方向的专题

1. 除 pie chart 之外的其他 `datasets.charts` 详细协议
2. Java 渲染器合同
3. 页面样式与分页层
4. Python 包 API 设计

### 29.3 后续建议顺序

建议按以下顺序推进：

1. 扩展 chart 专题（在 pie chart 基础上补充其他图表类型）
2. Python 包设计与实现
3. Java 渲染器合同
4. 样式层与分页层
