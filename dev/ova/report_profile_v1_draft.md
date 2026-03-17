# Report Profile v1 底层结构草案

## 1. 文档定位

本草案用于定义一套面向“Python 生成报告内容 JSON，Java 渲染生成 PDF”的中间协议底层结构。

本草案只冻结以下内容：

1. 顶层结构
2. 章节树合同
3. 全局 ID / Anchor / Registry / 引用目标体系
4. 类型清单 taxonomy
5. Portable Text 在本协议中的使用边界
6. 学术装置与高级能力的预留位

本草案**不**展开以下内容的细字段设计：

- 公式块字段
- 引文与参考文献字段
- 脚注字段
- 图表块字段
- 表格块字段
- Java 渲染样式字段
- PDF 页面级排版字段

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

都应该具备统一可解析目标模型。

### 2.7 先冻结结构合同，再细化业务块字段

v1 当前阶段先冻结骨架，不一次性写死全部块字段细节。

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

建议承载但暂不冻结细字段的内容包括：

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

当前阶段只保留位置，不冻结视觉字段。后续 Java 渲染器开发前再细化，例如：

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

- 正文中的引文标记后续通过 `citation_ref` 等类型引用这里
- 文献详情不散落在正文块内
- 当前阶段只冻结 registry 位置，不冻结条目字段

---

#### `footnotes`

脚注总表。

说明：

- 正文中的 `footnote_ref` 后续引用这里
- 脚注正文不直接嵌入原文段落主结构

---

#### `glossary`

术语表 / 缩写表 / 名词解释表。

说明：

- 预留学术与专业术语体系扩展空间
- 后续 `glossary_term` 可引用这里

---

#### `sections`

章节树根节点数组。

说明：

- `sections` 是整份报告正文的主结构
- 每个 section 节点拥有自己的 `body`
- `body` 是 section 内部的**有序 body item 列表**
- body item 用于同时表达：
  - 本节正文内容块组的顺序
  - 子章节插入位置的顺序
- Portable Text 风格块流挂在 `body` 中的 `content` 类型 item 里

---

## 4. 章节树合同

## 4.1 section 基础结构

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

## 4.2 section 字段说明

### `id`

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

### `level`

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

### `title`

章节标题纯文本。

要求：

- 存标题文本本身
- 不建议直接写入结构编号前缀
- 当前阶段先按纯文本冻结

后续若确需支持标题内富文本，可考虑升级为：

- `titleText`
- `titleRichText`

但 v1 当前阶段先不做复杂化。

---

### `numbering`

编号策略。

当前阶段先冻结为基础语义值：

- `auto`
- `none`
- `manual`

含义：

- `auto`：由系统按章节结构自动编号
- `none`：不显示结构编号
- `manual`：后续允许手工指定展示编号

当前阶段只冻结语义，不展开 `manual` 的字段结构。

---

### `anchor`

章节锚点。

当前阶段建议：

- 默认可与 `id` 相同
- 但保留独立字段

原因：

- 后续可能需要让系统内部 ID 与外部显示 anchor 分离
- 对外链接、网页锚点、PDF 书签命名可能需要不同策略

---

### `body`

当前 section 内部的有序 body item 列表。

说明：

- `body` 是 section 内部的唯一正文组织入口
- `body` 负责表达本节内部各种内容与子章节的**真实顺序**
- `body` 中既可以出现连续正文块组，也可以出现子章节节点
- `body` 的引入，是为了避免原先 `content + children/subsections` 结构无法表达“正文与子章节交错顺序”的问题

---

## 4.3 body item 联合类型

`body` 中的每一个元素都称为一个 **body item**。

当前阶段冻结两类 body item：

### 4.3.1 `content`

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
- 不应用一个超大的 `content` item 把分散在子章节前后的多段本章节正文（非子章节正文）混在一起

---

### 4.3.2 `subsection`

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
- 但它不是普通正文块，不应被降格为普通 content item
- 它承载的是一个真正的 section 结构节点
- 这样既保留顺序，也保留章节作为高阶结构对象的语义

---

## 4.4 section 结构约束

### 约束 1：章节树通过内嵌 section 节点表达

不要用 `block.children.children...` 模拟章节树。

### 约束 2：section 内部顺序由 `body` 表达

不要再使用 `content + children/subsections` 的分离模型来表达 section 内部顺序。

### 约束 3：标题文本与编号分离

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

### 约束 4：父子 section 的 `level` 应自洽

例如：

- 父节点 `level = 1`
- 子节点通常 `level = 2`

校验器后续应校验层级一致性。

### 约束 5：`body` 中的正文块和子章节顺序必须可直接由数组顺序读出

也就是说：

- 一段父章节正文在前还是子章节在前
- 两个子章节之间是否插入父章节正文
- 子章节之后是否还有父章节总结性正文

都必须能直接通过 `body[]` 的顺序判断，不应依赖额外推断。

### 约束 6：`content.blocks` 中不允许再出现正式章节标题样式 `h1/h2/h3`

正式章节的标题级别只能通过：

- 顶层 `sections[]`
- 或 body item 中的 `subsection.section`

的 `level` 字段来表达。

说明：

- `h1/h2/h3` 不再作为正式章节结构的来源
- 后续如需“正文中的非正式小标题”，可单独设计其他 style，例如 `subheading`

### 约束 7：`body` 中的 `subsection` 应只承载比当前 section 更深一层的 section 节点

`body` 中的 `subsection` 应只承载比当前 section 更深一层的 section 节点。

例如当前 section 的 `level = 1`，则其直接 `subsection.section.level` 应为 `2`。

---

## 5. Portable Text 在本协议中的使用边界

## 5.1 使用位置

Portable Text 风格内容数组(不直接挂在 `section.content`)只用于：

- `section.body[]` 中 `itemType = "content"` 的 `blocks`

当前阶段不要求以下位置也必须是 Portable Text：

- `meta`
- `bibliography`
- `footnotes`
- `glossary`
- `datasets`
- `assets`

---

## 5.2 使用原则

Portable Text 在本协议中负责：

- 文本块流
- 行内文本片段
- 文本 marks / markDefs
- 列表项
- `content` 类型 body item 中的正文块承载

Portable Text 不负责：

- 顶层文档结构
- section 章节树本体
- section 内部子章节节点结构
- registry 体系
- 编号策略本体
- 引用目标解析体系本体
- PDF 页面排版

---

## 5.3 当前阶段沿用的 Portable Text 原生能力

### 直接沿用

- `block`
- `span`
- `marks`
- `markDefs`
- `listItem`
- `level`

### 保留原生思路但允许扩展

- `block.style`
- 行内对象
- 块级对象

### 当前新增限制

- `content.blocks` 内不允许使用 `h1/h2/h3` 表示正式章节标题
- 正式章节结构只能由 section 节点表达

---

## 6. 全局 Registry 体系

## 6.1 registry 的基本目的

registry 的作用是承载：

- 可复用资源
- 大型资源
- 可能被多处引用的对象
- 需要统一管理的对象
- 未来需要单独校验或缓存的对象

---

## 6.2 当前冻结的顶层 registry

### 静态资源 registry

- `assets.images`
- `assets.logos`
- `assets.backgrounds`
- `assets.icons`
- `assets.attachments`

### 数据型资源 registry

- `datasets.charts`
- `datasets.tables`
- `datasets.metrics`

### 学术与辅助 registry

- `bibliography`
- `footnotes`
- `glossary`

---

## 6.3 内容块与 registry 的关系

冻结如下原则：

### 原则 1：优先引用 registry

例如：

- 图片块优先 `imageRef`
- 图表块优先 `chartRef`
- 表格块优先 `tableRef`
- 引文优先 `citation_ref -> bibliography`
- 脚注优先 `footnote_ref -> footnotes`

### 原则 2：少量简单内容允许内嵌

例如：

- 很短的一次性 callout 文本
- 简单分隔块
- 简短页内提示

### 原则 3：复杂对象不要在多个正文块里重复拷贝

特别是：

- 大图片信息
- 大图表数据
- 复杂参考文献条目
- 长脚注正文

---

## 7. 全局 ID / Anchor / Numbering 体系

## 7.1 三层概念分离

推荐统一分离三层概念：

### 1）系统 ID

系统内部稳定标识，例如：

- `sec-market-overview`
- `fig-valuation-trend`
- `eq-dcf-core`

### 2）anchor

解析/跳转/书签使用的锚点标识。

### 3）display number

面向读者展示的编号，例如：

- `1`
- `1.2`
- `Figure 3`
- `Table 2-1`
- `(4.2)`

当前阶段只冻结“概念分离”，不冻结 display number 的视觉文本拼接格式。

---

## 7.2 推荐的 ID 类型前缀

### 文档结构类

- `sec-*`
- `appendix-*`

### 图形图表类

- `fig-*`
- `chart-*`
- `tbl-*`

### 学术装置类

- `eq-*`
- `cite-*`
- `fn-*`
- `term-*`

### 资源类

- `img-*`
- `asset-*`
- `data-*`

说明：

- 前缀不是唯一合法方案
- 但建议从 v1 开始形成统一命名惯例

---

## 7.3 编号策略的冻结范围

当前阶段冻结如下原则：

### section 编号

- 支持自动生成
- 编号按章节树推导
- 与 `title` 分离

### figure / table / equation 编号

- 必须预留自动编号空间
- 当前阶段不冻结“全文连续”还是“按章节重置”为唯一规则
- 后续具体块字段设计时再定默认策略

### appendix 编号

- 必须预留附录编号扩展空间
- 当前阶段不细化

---

## 8. 统一“可解析目标”模型

## 8.1 设计目标

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

---

## 8.2 当前阶段冻结的底层要求

一个可解析目标至少应具备：

- `id`
- `targetType` 或可推出类型
- `anchor`（显式或可推导）
- 可定位来源（所在 registry 或所在 section/body）

说明：

- 当前阶段不要求把所有对象都写成完全一致的 JSON 结构
- 但要求在底层设计上，所有可引用对象都具备统一解析入口
- 对 section 而言，其在结构上既可以位于顶层 `sections[]`，也可以位于某 section 的 `body[] -> subsection.section`

---

## 8.3 xref / 引文 / 脚注 对统一可解析目标模型的依赖

后续这些能力都会依赖本层：

- `xref`
- `citation_ref`
- `footnote_ref`
- TOC
- 图表目录
- 表格目录
- PDF 书签
- 页内跳转

因此本层属于底层合同，必须先冻结。

---

## 9. 类型清单 taxonomy

本节只冻结“清单与分类”，不展开字段细节。

---

## 9.1 A 类：直接沿用 Portable Text 原生能力

这些不重新发明。

### 文本块与行内文本

- `block`
- `span`

### 行内标记与定义

- `marks`
- `markDefs`

### 列表能力

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

---

## 9.2 B 类：先作为 `block.style` 扩展，而不是独立块对象

建议预留的 style 清单：

* `normal`
* `blockquote`
* `caption`
* `figure_caption`
* `table_caption`
* `equation_caption`
* `smallprint`
* `lead`
* `quote_source`
* `subheading（作为非正式小标题预留）`

说明：

- 这些内容本质上仍然是“文本块”
- 当前阶段不急于升级成独立 block object
- 后续如果出现明显结构化需求，再升级为独立对象
- `h1/h2/h3/h4` 不作为 `content.blocks` 中的正式章节样式使用；正式章节结构统一由 section 节点表达。

---

## 9.3 C 类：预留为行内对象 / annotation 的类型清单

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

---

## 9.4 D 类：预留为块级对象的类型清单

### 基础报告块

- `image`
- `table`
- `chart`
- `code_block`
- `math_block`
- `callout`
- `quote_box`
- `page_break`

### 文档结构辅助块

- `cover`
- `abstract_block`
- `toc_placeholder`
- `references_block`
- `appendix_marker`
- `section_divider`

### 未来可扩展块

- `timeline`
- `comparison_card`
- `kpi_grid`
- `risk_matrix`
- `author_note`

说明：

- 当前阶段只冻结名字和分类
- 不冻结具体字段
- 后续按优先级逐一细化

---

## 10. 学术装置与高级能力预留

当前阶段先冻结占位，不展开字段细节。

---

## 10.1 已预留的顶层 registry

- `bibliography`
- `footnotes`
- `glossary`

---

## 10.2 已预留的行内类型

- `citation_ref`
- `footnote_ref`
- `xref`
- `inline_math`
- `glossary_term`

---

## 10.3 已预留的块级类型

- `math_block`
- `references_block`

必要时后续可补：

- `footnotes_block`
- `glossary_block`

---

## 10.4 预留但暂不细化的高级能力

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

## 11. 当前阶段的非目标

以下内容明确不在本草案冻结范围内：

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

这些将在后续“Java 渲染器合同 / 样式层”阶段再设计。

---

## 12. 校验建议（当前阶段可先形成规则意识）

虽然暂不写正式校验器，但 v1 底层结构建议至少满足以下校验规则：

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
12. `content.blocks` 中不应出现正式章节标题样式 `h1/h2/h3`
13. 同一对象不要在多个位置重复保存冲突定义

---

## 13. 当前仍可商讨、但不阻塞本草案的点

以下点目前不阻塞 v1 底层骨架，可以放到后续专题设计中：

### 13.1 `meta` 的详细字段表

例如：

- `reportType`
- `clientName`
- `projectId`
- `generatedAt`
- `locale`

### 13.2 registry 条目的详细字段

例如图片条目、图表条目、文献条目的字段结构。

### 13.3 figure / equation / table 的默认编号策略

例如：

- 全文连续
- 按章节重置

### 13.4 `manual` numbering 的具体表示方式

例如是字符串还是对象。

### 13.5 标题未来是否支持富文本

v1 当前先不做。

### 13.6 registry 里对象是否需要统一公共字段基类

例如：

- `id`
- `anchor`
- `label`
- `meta`

这个可以后续补一个通用对象基型。

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


## 15. 结论

基于当前已确认的方向，本草案已经完成了从“Portable Text 富文本底座”到“报告中间协议底层骨架”的第一阶段冻结。

### 15.1 当前已经完成的内容

本阶段已经冻结并明确了以下底层合同：

1. **顶层结构**
   * `schemaVersion`
   * `meta`
   * `theme`
   * `assets`
   * `datasets`
   * `bibliography`
   * `footnotes`
   * `glossary`
   * `sections`
2. **章节结构模型**
   * 采用树形 `sections`
   * section 标题使用 `section.title`
   * section 内部顺序使用 `body[]` 表达
   * `body[]` 当前包含两类 body item：
     * `content`
     * `subsection`
3. **正文与章节的边界**
   * Portable Text 只用于 `body` 中 `content.blocks`
   * 正式章节结构不再通过 `content.blocks` 中的标题块表达
   * `content.blocks` 必须表示连续正文块组
4. **全局资源与 registry 体系**
   * 静态资源放入 `assets`
   * 数据型资源放入 `datasets`
   * 学术与辅助对象预留在 `bibliography` / `footnotes` / `glossary`
5. **统一引用目标基础**
   * 所有可被引用对象都应具备统一可解析入口
   * 已冻结 `id / anchor / display number` 的概念分离
   * 已冻结基础 ID 命名前缀建议
6. **类型清单 taxonomy**
   * 直接沿用的 Portable Text 原生能力
   * `block.style` 扩展层
   * 行内对象 / annotation 预留层
   * 块级对象预留层
7. **学术装置扩展空间**
   * 已为 `xref`
   * `citation_ref`
   * `footnote_ref`
   * `inline_math`
   * `math_block`
   * `references_block`

     等能力预留位置

---

### 15.2 当前草案已经能够稳定表达的能力

更新了一版后，草案已经能够正确表达：

* 章节与子章节的树形结构
* section 内部正文与子章节交错出现的真实顺序
* 子章节之间插入正文、图表、总结块等内容的可能性
* 子章节之后继续出现正文的情况
* 标题文本与结构编号分离
* 章节结构语义与 Portable Text 正文块流语义的清晰边界
* 面向后续交叉引用、目录、图表编号、公式编号的底层扩展空间

---

### 15.3 当前仍未展开、但已预留位置的内容

以下内容尚未冻结具体字段，但底层已预留扩展空间：

* registry 条目基型
* `xref / citation_ref / footnote_ref`
* `chart / table / image / math_block`
* bibliography / footnotes / glossary 条目结构
* 正文块细则（段落、硬换行、非正式小标题、caption 细则）
* Java 渲染器块分发接口
* Java PDF 样式与页面级排版规则

---

### 15.4 后续建议的工作顺序

下一阶段建议按以下顺序推进：

1. **正文块规则**
   * `content.blocks` 的使用规则
   * 段落与 block 的关系
   * 硬换行规则
   * 非正式小标题规则
   * caption 类文本块规则
2. **registry 条目基型**
   * 统一资源对象的公共字段
   * `id / anchor / label / meta` 是否形成通用基型
3. **引用类行内对象**
   * `xref`
   * `citation_ref`
   * `footnote_ref`
   * `glossary_term`
4. **核心块级对象**
   * `image`
   * `chart`
   * `table`
   * `math_block`
   * `callout`
5. **学术与辅助 registry 条目**
   * bibliography 条目结构
   * footnote 条目结构
   * glossary 条目结构
6. **Java 渲染器合同**
   * body item 分发
   * block 分发
   * registry resolve
   * 后续页面样式层接口
