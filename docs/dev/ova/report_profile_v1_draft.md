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


---

## 16. 正文块规则

## 16.1 适用范围

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

---

## 16.2 `content` body item 的职责

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

---

## 16.3 `blocks` 中允许出现的内容类别

当前阶段，`content.blocks[]` 允许出现以下三类内容：

### 16.3.1 文本块

基于 Portable Text 的 `block`，用于承载文本型内容，例如：

- 普通正文
- 引用块
- 非正式小标题
- caption 类文本
- smallprint
- lead
- quote_source

---

### 16.3.2 列表块

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

---

### 16.3.3 块级对象

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

---

## 16.4 段落与 `block` 的关系

当前阶段冻结如下基本规则：

### 规则 1

默认情况下，一个 `block` = 一个段落级文本块。

这意味着：

- 一个普通正文段落对应一个 `block`
- 一个 blockquote 对应一个 `block`
- 一个 caption 对应一个 `block`
- 一个非正式小标题对应一个 `block`

### 规则 2

新的段落边界通过以下方式体现：

- 新建一个新的 `block`
- 或插入一个块级对象

### 规则 3

不要使用段内硬换行去模拟新段落。

---

## 16.5 同一段内的行内内容关系

当前阶段冻结如下规则：

### 规则 1

同一个 `block.children[]` 中的所有 `span` 与 inline object，属于同一个段落级文本块。

### 规则 2

同一 `block` 内允许混合出现：

- `span`
- `hard_break`
- `xref`
- `citation_ref`
- `footnote_ref`
- `glossary_term`
- 未来其他 inline object

### 规则 3

`marks / markDefs` 仍按 Portable Text 原生机制工作，用于表达：

- 加粗
- 斜体
- 下划线
- 链接
- 批注等 annotation

---

## 16.6 段落换行与段内硬换行

### 16.6.1 段间换行

段间换行统一通过新建 `block` 表达。

示例：

```json
[
  {
    "_type": "block",
    "style": "normal",
    "children": [
      { "_type": "span", "text": "第一段。", "marks": [] }
    ],
    "markDefs": []
  },
  {
    "_type": "block",
    "style": "normal",
    "children": [
      { "_type": "span", "text": "第二段。", "marks": [] }
    ],
    "markDefs": []
  }
]
```

---

### 16.6.2 段内硬换行

段内硬换行引入专用行内对象：

```json
{
  "_type": "hard_break"
}
```

示例：

```json
{
  "_type": "block",
  "style": "normal",
  "children": [
    { "_type": "span", "text": "第一行", "marks": [] },
    { "_type": "hard_break" },
    { "_type": "span", "text": "第二行", "marks": [] }
  ],
  "markDefs": []
}
```

冻结规则：

- `hard_break` 只表示同一段内部的强制换行
- `hard_break` 不等价于新段落
- 不建议在普通 `span.text` 中直接用 `\n` 表达正式硬换行语义

---

## 16.7 缩进与 tab 规则

### 规则 1

普通正文的首行缩进不属于内容语义层，不建议用 tab 字符表达。

### 规则 2

普通正文缩进、段前段后距、对齐方式等属于 Java 渲染样式层控制。

### 规则 3

只有在特殊内容需要保留原始排版时，才考虑保留“制表/预格式”语义，例如：

- `code_block`
- 未来可能的 `preformatted_block`

当前阶段结论：

- 正文层不设计通用 tab 语义
- 正文层设计 `hard_break`
- 普通缩进交给渲染层处理

---

## 16.8 非正式小标题 `subheading`

### 16.8.1 定义

`subheading` 表示 section 内部的**非正式小标题**。

它用于表达：

- 一个 section 内部的逻辑分段标题
- 提示性标题
- 小节说明标题

### 16.8.2 边界

`subheading` 不是正式章节结构，因此：

- 不形成新的 `section`
- 不进入 `sections` 树
- 不参与 section 编号
- 默认不作为正式目录结构来源
- 默认不作为正式 `xref` 目标

### 16.8.3 推荐示例

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

---

## 16.9 caption 类文本块

当前阶段保留以下文本块 style：

- `caption`
- `figure_caption`
- `table_caption`
- `equation_caption`

说明：

- 当前阶段它们仍然是文本块 style，不升级成独立 block object
- 它们用于承载说明性文本
- 不形成章节结构
- 默认服务于其相邻相关对象

建议语义：

- `caption`：通用说明文字
- `figure_caption`：图题注
- `table_caption`：表题注
- `equation_caption`：公式说明文字

---

## 16.10 当前阶段允许的正文文本 style 清单

在 `content.blocks[]` 中，当前阶段建议允许以下文本块 style：

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

当前阶段明确不允许：

- `h1`
- `h2`
- `h3`
- `h4`

说明：

- 这些样式不再作为正式章节标题使用
- 正式章节统一由 section 节点表达

---

## 16.11 正文块层的补充约束

1. `content.blocks[]` 中允许混排文本块与块级对象
2. `content.blocks[]` 中不允许出现正式章节节点
3. `content.blocks[]` 中不允许使用 `h1/h2/h3/h4` 充当正式章节标题
4. 一个 `content` body item 应只表示一段连续内容流
5. `subheading` 只能表示非正式小标题，不能替代 `subsection`

---

## 17. 第一批行内对象规则（新增）

## 17.1 适用范围

本章规则适用于：

- `block.children[]` 中的自定义 inline object

当前阶段冻结第一批行内对象如下：

- `hard_break`
- `xref`
- `citation_ref`
- `footnote_ref`
- `glossary_term`

---

## 17.2 通用原则

### 原则 1

行内对象只能出现在 `block.children[]` 中。

### 原则 2

行内对象属于当前 `block`，不独立形成段落。

### 原则 3

行内对象的阅读顺序由其在 `children[]` 中的位置决定。

### 原则 4

行内对象如果带引用关系，其目标必须可被统一解析。

---

## 17.3 `hard_break`

### 定义

表示同一段内部的强制换行。

### 推荐结构

```json
{
  "_type": "hard_break"
}
```

### 规则

- 不带附加字段
- 不形成独立内容块
- 不等价于新段落

---

## 17.4 `xref`

### 定义

用于交叉引用正式结构目标或可编号对象，例如：

- section
- figure
- table
- equation

### 推荐最小结构

```json
{
  "_type": "xref",
  "targetType": "section",
  "targetId": "sec-1-1"
}
```

### 推荐最小字段

- `_type`
- `targetType`
- `targetId`

### 说明

- `targetType` 用于帮助渲染器选择展示文本，例如“Section”“Figure”“Table”“Equation”
- `targetId` 必须能解析到有效目标
- 当前阶段不冻结更复杂字段，如 prefix / suffix / explicitText

---

## 17.5 `citation_ref`

### 定义

用于引用 `bibliography` 中的一个或多个文献条目。

### 推荐最小结构

```json
{
  "_type": "citation_ref",
  "refIds": ["cite-smith-2024"],
  "mode": "parenthetical"
}
```

### 推荐最小字段

- `_type`
- `refIds`
- `mode`

### 字段说明

- `refIds`：引用的 bibliography 条目 ID 列表
- `mode`：引用模式，当前阶段建议至少预留：
  - `parenthetical`
  - `narrative`

### 说明

- 当前阶段不冻结具体引文样式输出格式
- 具体样式由后续 bibliography 规则和渲染器决定

---

## 17.6 `footnote_ref`

### 定义

用于引用 `footnotes` 中的脚注条目。

### 推荐最小结构

```json
{
  "_type": "footnote_ref",
  "refId": "fn-1"
}
```

### 推荐最小字段

- `_type`
- `refId`

### 说明

- `refId` 必须能解析到顶层 `footnotes` 中的有效目标
- 当前阶段不冻结脚注编号显示方式

---

## 17.7 `glossary_term`

### 定义

用于引用 `glossary` 中的术语或缩写条目。

### 推荐最小结构

```json
{
  "_type": "glossary_term",
  "termId": "term-dcf"
}
```

### 推荐最小字段

- `_type`
- `termId`

### 说明

- `termId` 必须能解析到顶层 `glossary` 中的有效目标
- 当前阶段不冻结渲染行为是“跳转”“悬浮提示”还是“首次解释”

---

## 17.8 行内对象与 span / marks 的关系

### 规则 1

行内对象与 `span` 可以在同一 `children[]` 中混排。

### 规则 2

简单文本样式仍优先使用 `marks / markDefs`，而不是滥用自定义 inline object。

### 规则 3

“引用目标”类语义优先使用行内对象，不建议塞进普通 span 文本里硬编码。

例如应优先写：

```json
[
  { "_type": "span", "text": "See ", "marks": [] },
  { "_type": "xref", "targetType": "figure", "targetId": "fig-1" }
]
```

而不是在普通文本里直接写：

```json
"See Figure 1"
```

---

## 17.9 行内对象校验建议

当前阶段建议至少满足：

1. `hard_break` 不应带多余业务字段
2. `xref.targetId` 必须能解析到有效目标
3. `citation_ref.refIds` 不应为空
4. `citation_ref.refIds[]` 中的每个 ID 都应能解析到 bibliography 条目
5. `footnote_ref.refId` 应能解析到 footnote 条目
6. `glossary_term.termId` 应能解析到 glossary 条目
7. 行内对象不得伪装为正式章节结构

---

## 18. 结论与下一步（新增）

本次新增章节已经完成了“文本层协议”的第一阶段冻结，主要包括：

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

## 18.1 后续建议顺序

下一步建议继续按以下顺序推进：

### 第一步：registry 条目基型

统一资源对象的公共字段，例如：

- `id`
- `anchor`
- `label`
- `meta`

---

### 第二步：核心块级对象

逐个细化：

- `image`
- `chart`
- `table`
- `math_block`
- `callout`

---

### 第三步：学术与辅助 registry 条目

逐个细化：

- bibliography 条目结构
- footnote 条目结构
- glossary 条目结构

---

### 第四步：Java 渲染器合同

明确：

- body item 分发
- block 分发
- inline object 分发
- registry resolve
- 页面样式层接口




## 19. 设计回顾与本阶段前置结论（新增）

**在进入对象层之前，当前协议已经冻结了以下关键前提：**

1. **顶层结构已确定为：**
   * `schemaVersion`
   * `meta`
   * `theme`
   * `assets`
   * `datasets`
   * `bibliography`
   * `footnotes`
   * `glossary`
   * `sections`
2. **章节结构已确定为：**
   * **顶层 **`sections[]`
   * **section 内部使用 **`body[]`
   * `body[]` 当前包含：
     * `content`
     * `subsection`
3. **Portable Text 的边界已明确：**
   * **仅用于 **`content.blocks[]`
   * **不再承载正式章节标题**
   * `content.blocks[]` 可混排文本块与块级对象
4. **文本层规则已明确：**
   * **一个 **`block` 默认表示一个段落级文本块
   * **段间换行用新 **`block`
   * **段内硬换行用 **`hard_break`
   * `subheading` 只表示非正式小标题
   * `caption / figure_caption / table_caption / equation_caption` 作为文本块 style 保留

**基于以上前提，本阶段进入对象层设计时，可以直接采用以下原则。**

---

## 19.1 本阶段额外冻结的两个关键原则

### 原则 A：caption 优先保持为相邻文本块，而不是内嵌到对象字段中

**当前阶段建议：**

* `image`
* `chart`
* `table`
* `math_block`

**这些对象本身不强制内嵌 caption 文本字段。**  ** **caption 继续优先使用相邻的文本块 style，例如：

* `figure_caption`
* `table_caption`
* `equation_caption`

**这样做的好处：**

* **与已经冻结的文本层规则保持一致**
* **文本说明仍可使用 Portable Text 机制处理**
* **避免对象层与文本层重复承载 caption**
* **Java 端可以通过相邻块关系决定最终版式**

---

### 原则 B：块对象自己的 `id` 与底层 `*Ref` 分离

**当前阶段建议：**

* **渲染到正文中的对象块，允许拥有自己的 **`id / anchor`
* **同时它们再通过：**
  * `imageRef`
  * `chartRef`
  * `tableRef`
  * **未来其他 **`*Ref`

**引用 registry 中的底层资源**

**例如：**

```
{
  "_type": "chart",
  "id": "fig-market-share",
  "anchor": "fig-market-share",
  "chartRef": "chart-market-share"
}
```

**这意味着：**

* `chartRef` 指向底层数据资源
* `id / anchor` 指向正文中的这个可引用对象实例

**这样做的好处：**

* **同一底层数据资源可在不同正文位置复用**
* **同一资源可有不同局部上下文、编号、相邻 caption**
* `xref` 可以指向正文对象实例，而不是生硬指向底层数据条目

---

## 19.2 当前阶段无须再额外确认的点

**本阶段可以直接继续设计，无需再次卡住讨论的点包括：**

1. **是否继续采用 registry 优先**  ** **→ 已确认：优先引用 registry，少量简单内容才内嵌
2. **是否继续保留 body 有序模型**  ** **→ 已确认：保留
3. **是否继续区分正式章节与正文小标题**  ** **→ 已确认：区分
4. **caption 是否已经有承载方式**  ** **→ 已确认：由相邻 caption 类文本块承载

**当前未发现新的结构性遗漏会阻塞对象层设计。**

---

## 20. registry 条目基型（新增）

## 20.1 设计目标

**registry 条目基型用于统一：**

* `assets.*`
* `datasets.*`
* **未来其他可复用资源集合**

**其目标是让不同 registry 条目至少具备一组稳定公共字段，便于：**

* **Python 生成**
* **Java 解析**
* **校验器校验**
* **日后扩展更多资源类型**

---

## 20.2 推荐公共字段基型

**当前阶段建议所有 registry 条目优先具备以下公共字段：**

```
{
  "id": "resource-id",
  "anchor": "resource-id",
  "label": "Optional human-readable label",
  "meta": {}
}
```

### 字段说明

#### `id`

**条目全局唯一稳定标识。**

**用途：**

* **被 **`*Ref` 引用
* **程序内部解析**
* **去重与校验**

---

#### `anchor`

**锚点标识。**

**说明：**

* **默认可与 **`id` 相同
* **预留独立字段，方便未来对外展示锚点与内部 ID 分离**

---

#### `label`

**可选的人类可读标签。**

**说明：**

* **用于调试、后台编辑、日志、检索**
* **不等价于最终渲染标题或 caption**
* **不强制要求唯一**

---

#### `meta`

**附加元信息对象。**

**说明：**

* **用于承载该 registry 条目的附加属性**
* **当前阶段不冻结 **`meta` 内部字段
* **例如来源、创建时间、语言、版权、说明等**

---

## 20.3 registry 条目基型的补充约束

1. **同一 registry 中 **`id` 必须唯一
2. **跨 registry 的 **`id` 最好也保持全局唯一
3. `anchor` 默认可省略并回退为 `id`
4. `label` 可省略
5. `meta` 可为空对象

---

## 20.4 现阶段建议的 registry 分类与条目基型适配

### 静态资源类

**适用于：**

* `assets.images`
* `assets.logos`
* `assets.backgrounds`
* `assets.icons`
* `assets.attachments`

### 数据资源类

**适用于：**

* `datasets.charts`
* `datasets.tables`
* `datasets.metrics`

### 学术辅助类

**后续可参考相同思路：**

* `bibliography`
* `footnotes`
* `glossary`

**说明：**

* **bibliography / footnotes / glossary 在语义上更特殊**
* **后续会有自己的专题字段**
* **但仍建议尽量复用 **`id / anchor / label / meta` 的公共思想

---

## 20.5 资源条目与正文对象实例的关系

**当前阶段正式冻结如下区分：**

### 资源条目（registry entry）

**表示底层可复用资源，例如：**

* **一张原始图片**
* **一组图表数据**
* **一张表格数据集**

### 正文对象实例（content block object）

**表示正文中的一次使用，例如：**

* **文中的某张图**
* **文中的某个图表**
* **文中的某个表格**

**这两个层级不应混为一谈。**

**例如：**

* **registry 条目：**`chart-market-share`
* **正文实例：**`fig-market-share`

**正文实例通过 **`chartRef` 指向底层 registry 条目。

---

## 21. 核心块级对象第一版规则（新增）

## 21.1 适用范围

**本章定义以下对象的第一版规则：**

* `image`
* `chart`
* `table`
* `math_block`
* `callout`

**当前阶段只冻结：**

* **对象职责**
* **最小字段集合**
* **与 registry 的关系**
* **与 caption 的关系**
* **与可引用目标模型的关系**

**不冻结：**

* **具体视觉样式**
* **最终编号格式**
* **Java 渲染细节**
* **高级可选字段**

---

## 21.2 块级对象的共同规则

**以下规则适用于本章所有对象：**

### 规则 1

**块级对象可以出现在 **`content.blocks[]` 中。

### 规则 2

**块级对象在阅读顺序上是正文流的一部分。**

### 规则 3

**块级对象如果可能被 **`xref` 引用，则应具备：

* `id`
* `anchor`

### 规则 4

**块级对象优先通过 **`*Ref` 指向 registry 条目，而不是重复内嵌大资源。

### 规则 5

**caption 优先由相邻 caption 类文本块承载，不强制内嵌在对象字段中。**

### 规则 6

**块级对象的 **`id` 不等于底层 `*Ref`，两者在语义上分离。

---

## 21.3 `image`

### 21.3.1 定义

**表示正文中的图片对象实例。**

### 21.3.2 推荐最小结构

```
{
  "_type": "image",
  "id": "fig-pipeline-overview",
  "anchor": "fig-pipeline-overview",
  "imageRef": "img-pipeline-overview"
}
```

### 21.3.3 推荐最小字段

* `_type`
* `id`
* `anchor`
* `imageRef`

### 21.3.4 说明

* `imageRef` 指向 `assets.images` 中的图片资源条目
* `id / anchor` 表示正文中的该图片实例
* **若该图片需要题注，优先在其相邻位置使用 **`figure_caption` 文本块

---

## 21.4 `chart`

### 21.4.1 定义

**表示正文中的图表对象实例。**

### 21.4.2 推荐最小结构

```
{
  "_type": "chart",
  "id": "fig-market-share",
  "anchor": "fig-market-share",
  "chartRef": "chart-market-share"
}
```

### 21.4.3 推荐最小字段

* `_type`
* `id`
* `anchor`
* `chartRef`

### 21.4.4 说明

* `chartRef` 指向 `datasets.charts` 中的图表数据条目
* `id / anchor` 表示正文中的图表实例
* **图表标题与说明优先使用相邻 **`figure_caption`

---

## 21.5 `table`

### 21.5.1 定义

**表示正文中的表格对象实例。**

### 21.5.2 推荐最小结构

```
{
  "_type": "table",
  "id": "tbl-financial-summary",
  "anchor": "tbl-financial-summary",
  "tableRef": "table-financial-summary"
}
```

### 21.5.3 推荐最小字段

* `_type`
* `id`
* `anchor`
* `tableRef`

### 21.5.4 说明

* `tableRef` 指向 `datasets.tables` 中的表格数据条目
* `id / anchor` 表示正文中的表格实例
* **表题注优先使用相邻 **`table_caption`

---

## 21.6 `math_block`

### 21.6.1 定义

**表示独立占块显示的数学公式对象。**

### 21.6.2 推荐最小结构

```
{
  "_type": "math_block",
  "id": "eq-dcf-core",
  "anchor": "eq-dcf-core",
  "latex": "V = \\sum_{t=1}^{n} \\frac{CF_t}{(1+r)^t}"
}
```

### 21.6.3 推荐最小字段

* `_type`
* `id`
* `anchor`
* `latex`

### 21.6.4 说明

* `math_block` 当前阶段允许直接内嵌 `latex`
* **这是因为数学公式通常体量不大，且正文上下文强**
* **后续若出现大量复用或复杂公式资源管理需求，再考虑抽出 **`mathRef`
* **若需要额外说明文字，优先使用相邻 **`equation_caption`

---

## 21.7 `callout`

### 21.7.1 定义

**表示正文中的提示框 / 强调框 / 结论框。**

### 21.7.2 推荐最小结构

```
{
  "_type": "callout",
  "id": "callout-key-finding-1",
  "anchor": "callout-key-finding-1",
  "blocks": []
}
```

### 21.7.3 推荐最小字段

* `_type`
* `id`
* `anchor`
* `blocks`

### 21.7.4 说明

* `callout` 当前阶段允许直接内嵌 `blocks`
* **其内部内容仍然建议使用 Portable Text 风格块数组**
* **这是因为 callout 更像局部正文容器，而非独立底层资源**
* **当前阶段不必为 callout 单独建 registry**

---

## 21.8 对象与 caption 的相邻使用建议

**当前阶段推荐如下相邻模式：**

### 图片

```
image
figure_caption
```

### 图表

```
chart
figure_caption
```

### 表格

```
table
table_caption
```

### 公式

```
math_block
equation_caption
```

### callout

**通常无需 caption，除非后续有特殊需要。**

**说明：**

* **当前阶段 caption 与对象之间不通过强绑定字段耦合**
* **默认通过正文顺序和相邻关系表达关联**
* **后续若 Java 渲染器需要更强约束，可再引入可选关联字段**

---

## 21.9 核心块级对象校验建议

**当前阶段建议至少满足：**

1. `image.imageRef` 必须能解析到 `assets.images`
2. `chart.chartRef` 必须能解析到 `datasets.charts`
3. `table.tableRef` 必须能解析到 `datasets.tables`
4. `math_block.latex` 不应为空
5. `callout.blocks` 必须是数组
6. **可被引用的块级对象应具备 **`id`
7. `anchor` 默认可回退为 `id`
8. **块对象的 **`id` 与底层 `*Ref` 不应混淆使用

---

## 21.10 本阶段的边界

**本章当前仍未冻结以下内容：**

* **图片资源条目的详细字段**
* **图表数据条目的详细字段**
* **表格数据条目的详细字段**
* **公式编号策略**
* **callout 的风格类型枚举**
* **caption 与对象的强绑定机制**
* **Java 侧具体绘制规则**

**这些内容将放到后续专题中继续细化。**

---

## 21.11 本次新增的结论与下一步

**本次新增章节已经完成了“对象层协议”的第一阶段冻结，主要包括：**

1. **registry 条目公共基型：**
   * `id`
   * `anchor`
   * `label`
   * `meta`
2. **资源条目与正文对象实例分离**
3. **核心块级对象第一版最小规则：**
   * `image`
   * `chart`
   * `table`
   * `math_block`
   * `callout`
4. **caption 与对象之间当前优先采用“相邻文本块”模式**

**这使得当前协议已经能够进一步稳定表达：**

* **registry 条目的基础公共结构**
* **正文对象与底层资源的引用关系**
* **图、表、图表、公式、提示框在正文中的第一版对象模型**
* **面向后续 **`xref` 与渲染器分发的对象层基础

---

## 21.12 后续建议顺序

**下一步建议继续按以下顺序推进：**

### 第一步：具体 registry 条目结构

**逐个细化：**

* `assets.images`
* `datasets.charts`
* `datasets.tables`

### 第二步：学术与辅助 registry 条目

**逐个细化：**

* **bibliography 条目结构**
* **footnote 条目结构**
* **glossary 条目结构**

### 第三步：Java 渲染器合同

**明确：**

* **body item 分发**
* **block 分发**
* **inline object 分发**
* **object block 分发**
* **registry resolve**
* **页面样式层接口**



## 22. 本阶段范围与设计回顾（新增）

**在进入具体 registry 条目结构之前，当前协议已经冻结了以下前提：**

1. **registry 条目已具备统一公共基型：**
   * `id`
   * `anchor`
   * `label`
   * `meta`
2. **正文对象实例与底层资源条目已明确分离：**
   * **正文中的 **`image` 使用 `imageRef`
   * **正文中的 **`table` 使用 `tableRef`
   * **正文中的 **`chart` 使用 `chartRef`
3. **caption 当前优先采用“相邻文本块”模式，而不是内嵌在对象或资源条目中**
4. **当前阶段已经有对象层最小结构：**
   * `image`
   * `table`
   * `chart`
   * `math_block`
   * `callout`

**基于以上前提，本阶段进一步细化最基础、最常用的两类 registry 条目：**

* `assets.images`
* `datasets.tables`

**同时明确：**

* `datasets.charts` 暂缓详细设计，等基础能力稳定后再单独专题展开

---

## 22.1 当前阶段冻结范围

**本阶段冻结：**

1. `assets.images` 条目字段
2. `datasets.tables` 条目字段
3. **table 数据的推荐组织方式**
4. **image/table 与正文对象实例之间的关系**
5. **chart 暂缓设计的边界说明**

**本阶段不冻结：**

* `datasets.charts` 详细结构
* **图片裁切/缩放等渲染策略**
* **表格跨页与续表规则**
* **表格复杂合并单元格**
* **图表系列、坐标轴、样式细节**
* **Java 侧具体绘制逻辑**

---

## 23. `assets.images` 条目结构（新增）

## 23.1 设计目标

`assets.images` 用于承载底层图片资源条目。**  ** **正文中的图片对象实例通过 **`imageRef` 指向这里。

**其目标是：**

* **避免在正文对象中重复存放大图片资源信息**
* **支持同一图片资源被多处复用**
* **为后续背景图、封面图、普通插图等统一提供基础资源模型**

---

## 23.2 推荐最小结构

```
{
  "id": "img-pipeline-overview",
  "anchor": "img-pipeline-overview",
  "label": "Pipeline overview image",
  "meta": {},
  "src": "https://example.com/pipeline-overview.png",
  "alt": "Pipeline overview"
}
```

---

## 23.3 推荐字段说明

### 通用基型字段

* `id`
* `anchor`
* `label`
* `meta`

### 图片专属字段

#### `src`

**图片资源位置。**

**说明：**

* **当前阶段建议存储可解析的资源路径或 URL**
* **后续也可扩展为内部文件键、对象存储 key、相对路径等**
* **Java 渲染器最终通过 **`src` 或其映射值取得实际图片资源

---

#### `alt`

**图片的替代文本。**

**说明：**

* **用于语义说明、无障碍、日志、调试**
* **不等价于图片题注**
* **图片题注仍优先由相邻 **`figure_caption` 文本块承载

---

## 23.4 可选扩展字段（当前不强制）

**当前阶段允许未来扩展但暂不强制的字段包括：**

* `width`
* `height`
* `mimeType`
* `checksum`
* `source`
* `copyright`
* `language`

**这些字段如有需要，可优先放入：**

* **显式专属字段**
* **或 **`meta`

**当前阶段不冻结其标准化写法。**

---

## 23.5 与正文对象实例的关系

**正文中的图片实例推荐结构如下：**

```
{
  "_type": "image",
  "id": "fig-pipeline-overview",
  "anchor": "fig-pipeline-overview",
  "imageRef": "img-pipeline-overview"
}
```

**语义分离如下：**

### registry 条目

```
img-pipeline-overview
```

**表示底层图片资源。**

### 正文实例

```
fig-pipeline-overview
```

**表示该图片在正文中的一次使用。**

**说明：**

* **一个 **`assets.images` 条目可被多个正文 `image` 实例复用
* **不同正文实例可以有不同的局部上下文、编号、相邻 caption**

---

## 23.6 `assets.images` 校验建议

**当前阶段建议至少满足：**

1. `id` 必填
2. `src` 必填
3. `alt` 建议提供
4. **同一 registry 中 **`id` 唯一
5. `anchor` 缺省时可回退为 `id`
6. **被 **`imageRef` 引用的条目必须存在

---

## 24. `datasets.tables` 条目结构（新增）

## 24.1 设计目标

`datasets.tables` 用于承载底层表格数据资源。**  ** **正文中的 **`table` 对象实例通过 `tableRef` 指向这里。

**其目标是：**

* **把表格数据与正文使用场景分离**
* **支持同一张表在多个正文位置复用**
* **让 Java 渲染器以统一方式读取和绘制表格**
* **为未来扩展排序、格式化、列类型、复杂表格能力预留空间**

---

## 24.2 当前阶段推荐的数据组织方式

**当前阶段推荐采用：**

* `columns[]` 定义列
* `rows[]` 定义行
* **每一行用对象表达，键名与列 **`key` 对应

**推荐最小结构如下：**

```
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

---

## 24.3 为什么当前推荐“列定义 + 行对象”而不是纯二维数组

**当前阶段推荐这种结构，原因如下：**

### 原因 1

**列顺序由 **`columns[]` 明确控制。

### 原因 2

**每个单元格值通过列 **`key` 关联，语义更清晰。

### 原因 3

**对 Python 生成与 Java 解析都更友好。**

### 原因 4

**后续更容易扩展列类型、对齐方式、格式化规则等。**

**因此当前阶段不推荐把表格主结构直接冻结为纯二维数组。**

---

## 24.4 `columns[]` 字段建议

### 推荐最小结构

```
{
  "key": "revenue",
  "header": "Revenue"
}
```

### 推荐最小字段

#### `key`

**列的稳定键名。**

**要求：**

* **在同一张表内唯一**
* **用于与 **`rows[]` 中的字段映射

#### `header`

**列标题文本。**

**说明：**

* **当前阶段先冻结为纯文本**
* **后续若需要多级表头、富文本表头，再单独扩展**

---

## 24.5 `rows[]` 字段建议

### 推荐结构

`rows[]` 是对象数组，每个对象表示一行。

**例如：**

```
[
  { "year": "2022", "revenue": "12.3M", "margin": "18%" },
  { "year": "2023", "revenue": "15.8M", "margin": "21%" }
]
```

### 当前阶段规则

1. `rows[]` 中每个对象的键应来自 `columns[].key`
2. **缺失键允许存在，但渲染器应按空值处理**
3. **当前阶段单元格值先允许：**
   * **string**
   * **number**
   * **boolean**
   * **null**
4. **当前阶段不冻结复杂单元格对象结构**
5. **当前阶段不冻结合并单元格能力**

---

## 24.6 与正文对象实例的关系

**正文中的表格实例推荐结构如下：**

```
{
  "_type": "table",
  "id": "tbl-financial-summary",
  "anchor": "tbl-financial-summary",
  "tableRef": "table-financial-summary"
}
```

**语义分离如下：**

### registry 条目

```
table-financial-summary
```

**表示底层表格数据资源。**

### 正文实例

```
tbl-financial-summary
```

**表示该表格在正文中的一次使用。**

**说明：**

* **同一表格数据可在多个正文位置被引用**
* **不同正文实例可配不同上下文或相邻 **`table_caption`

---

## 24.7 caption 与 table 的关系

**当前阶段继续沿用已冻结原则：**

* **表题注优先使用相邻 **`table_caption`
* **不强制在 **`datasets.tables` 条目中存 caption
* **不强制在正文 **`table` 对象实例中存 caption

**推荐相邻模式：**

```
table
table_caption
```

---

## 24.8 `datasets.tables` 的可选扩展字段（当前不强制）

**当前阶段允许未来扩展但暂不强制的字段包括：**

* `columnGroups`
* `footerRows`
* `notes`
* `defaultAlign`
* `cellFormatRules`
* `rowOrder`
* `source`

**这些字段后续如果需要，可放在：**

* **显式专属字段**
* **或 **`meta`

**当前阶段不冻结其标准结构。**

---

## 24.9 `datasets.tables` 校验建议

**当前阶段建议至少满足：**

1. `id` 必填
2. `columns` 必须是数组
3. `rows` 必须是数组
4. `columns[].key` 在同一表内唯一
5. `columns[].header` 必填
6. `rows[]` 中出现的键应能在 `columns[].key` 中找到
7. **被 **`tableRef` 引用的条目必须存在
8. `anchor` 缺省时可回退为 `id`

---

## 24.10 `datasets.charts` 的当前阶段策略

**考虑到你后续会有较多自定义图表能力，例如：**

* **饼图**
* **柱状图**
* **雷达图**
* **其他业务自定义图表**

**当前阶段不建议现在仓促冻结 **`datasets.charts` 的详细结构。

### 当前结论

* **保留 **`datasets.charts` registry 位置
* **保留正文 **`chart` 对象实例最小结构：
  * `_type`
  * `id`
  * `anchor`
  * `chartRef`
* `datasets.charts` 条目详细字段延后到 chart 专题统一设计

### 当前好处

* **不会因为过早冻结 chart 结构而限制后续图表能力**
* **不影响当前协议继续推进 image/table/bibliography/footnotes/glossary 等基础能力**
* **Java 端之后可以在 chart 专题里一次性定好图表数据协议**

---

## 24.11 本次新增的结论与下一步

**本次新增章节已经完成了“具体 registry 条目结构”的第一阶段冻结，主要包括：**

1. `assets.images` 的最小条目结构
2. `datasets.tables` 的最小条目结构
3. **registry 条目与正文对象实例的语义分离**
4. **表格数据当前推荐采用：**
   * `columns[]`
   * `rows[]`
5. `datasets.charts` 当前阶段明确暂缓详细设计

**这使得当前协议已经能够进一步稳定表达：**

* **图片资源条目**
* **表格数据条目**
* **正文中的图片实例与表格实例**
* **caption 与对象的相邻协作模式**
* **chart 的延后专题化设计边界**

---

## 24.12 后续建议顺序

**下一步建议继续按以下顺序推进：**

### 第一步：学术与辅助 registry 条目

**逐个细化：**

* **bibliography 条目结构**
* **footnote 条目结构**
* **glossary 条目结构**

### 第二步：Java 渲染器合同

**明确：**

* **body item 分发**
* **block 分发**
* **inline object 分发**
* **object block 分发**
* **registry resolve**
* **页面样式层接口**

### 第三步：chart 专题

**在其他基础都稳定后，再单独设计：**

* `datasets.charts`
* **自定义图表数据协议**
* **图表类型枚举**
* **图表样式与数据结构约定**



## 25. 本阶段范围与设计回顾（新增）

**在进入学术与辅助 registry 条目之前，当前协议已经冻结了以下关键前提：**

1. **顶层已预留：**
   * `bibliography`
   * `footnotes`
   * `glossary`
2. **文本层已经冻结第一批行内对象：**
   * `citation_ref`
   * `footnote_ref`
   * `glossary_term`
3. **统一可解析目标模型已冻结：**
   * **可引用对象至少应具备 **`id`
   * **可具备 **`anchor`
   * **必须可被统一解析**
4. **registry 条目公共基型已经冻结：**
   * `id`
   * `anchor`
   * `label`
   * `meta`

**基于这些前提，本阶段的目标不是设计最终显示样式，而是先冻结这些条目的****最小语义结构**，让：

* **Python 可以稳定生成**
* **Java 可以稳定 resolve**
* `citation_ref / footnote_ref / glossary_term` 真正闭环

---

## 25.1 当前阶段冻结范围

**本阶段冻结：**

1. `bibliography` 条目的最小结构
2. `footnotes` 条目的最小结构
3. `glossary` 条目的最小结构
4. **它们与行内对象的引用关系**
5. **它们与公共基型的结合方式**

**本阶段不冻结：**

* **bibliography 的最终输出引文样式**
* **footnote 的版面排布方式**
* **glossary 的展示交互方式**
* **复杂文献类型的全量字段体系**
* **术语的多语言显示策略**
* **Java 端最终格式化细节**

---

## 26. `bibliography` 条目结构（新增）

## 26.1 设计目标

`bibliography` 用于承载可被 `citation_ref` 引用的参考文献条目。

**其目标是：**

* **把正文中的引文标记与文献详情分离**
* **允许同一文献条目被多次引用**
* **为后续不同引文风格渲染预留空间**
* **保持最小但可扩展的文献数据结构**

---

## 26.2 当前阶段推荐最小结构

```
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

---

## 26.3 推荐字段说明

### 通用基型字段

* `id`
* `anchor`
* `label`
* `meta`

### bibliography 专属最小字段

#### `type`

**文献类型。**

**当前阶段建议至少允许以下值：**

* `article`
* `book`
* `report`
* `webpage`
* `paper`
* `other`

**说明：**

* **当前阶段不冻结更细的类型体系**
* **该字段主要用于后续 Java 渲染器选择不同文献格式模板**

---

#### `title`

**文献标题。**

**说明：**

* **当前阶段冻结为纯文本**
* **后续如需 subtitle、translated title，可再扩展**

---

#### `authors`

**作者列表。**

**说明：**

* **当前阶段采用字符串数组**
* **每个元素表示一个作者的显示名**
* **当前阶段不冻结更细的姓/名拆分结构**

---

#### `year`

**文献年份。**

**说明：**

* **当前阶段为 number**
* **主要用于引用展示和文献表展示**
* **不冻结更复杂日期结构**

---

## 26.4 可选扩展字段（当前不强制）

**当前阶段允许未来扩展但暂不强制的字段包括：**

* `journal`
* `publisher`
* `volume`
* `issue`
* `pages`
* `doi`
* `url`
* `accessedAt`
* `edition`
* `institution`
* `language`

**这些字段后续如果需要，可放在：**

* **显式专属字段**
* **或 **`meta`

**当前阶段不冻结其标准化写法。**

---

## 26.5 与 `citation_ref` 的关系

**正文中的 **`citation_ref` 推荐最小结构已冻结为：

```
{
  "_type": "citation_ref",
  "refIds": ["cite-smith-2024"],
  "mode": "parenthetical"
}
```

**两者关系如下：**

### bibliography 条目

```
cite-smith-2024
```

**表示底层文献条目。**

### 正文引用

```
citation_ref(refIds=["cite-smith-2024"])
```

**表示正文中的一次引用动作。**

**说明：**

* **一个 bibliography 条目可被多次引用**
* **一个 **`citation_ref` 可引用一个或多个 bibliography 条目
* **当前阶段不在正文中重复写文献详情**

---

## 26.6 `bibliography` 校验建议

**当前阶段建议至少满足：**

1. `id` 必填
2. `type` 必填
3. `title` 必填
4. `authors` 必须是数组，且不应为空
5. `year` 建议提供
6. **同一 **`bibliography` 中 `id` 唯一
7. **被 **`citation_ref.refIds[]` 引用的条目必须存在
8. `anchor` 缺省时可回退为 `id`

---

## 27. `footnotes` 条目结构（新增）

## 27.1 设计目标

`footnotes` 用于承载可被 `footnote_ref` 引用的脚注条目。

**其目标是：**

* **把正文中的脚注标记与脚注正文分离**
* **支持同一脚注条目被引用**
* **为后续脚注区排版与编号留出空间**
* **保持脚注内容本身仍可使用富文本表达**

---

## 27.2 当前阶段推荐最小结构

```
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

---

## 27.3 推荐字段说明

### 通用基型字段

* `id`
* `anchor`
* `label`
* `meta`

### footnotes 专属最小字段

#### `blocks`

**脚注正文内容。**

**说明：**

* **当前阶段建议直接使用 Portable Text 风格块数组**
* **这使脚注内容本身也能承载：**
  * **普通文本**
  * **行内 marks**
  * **链接**
  * **未来必要的轻量行内对象**
* **当前阶段不要求脚注内容进入 section/body 结构**

---

## 27.4 为什么脚注条目当前直接用 `blocks`

**原因如下：**

### 原因 1

**脚注本质上仍然是小段正文说明。**

### 原因 2

**其内容可能需要简单富文本能力，而不是只存一条纯字符串。**

### 原因 3

**这与正文主结构中的 Portable Text 使用方式保持一致，Java 端更容易复用已有文本渲染逻辑。**

---

## 27.5 与 `footnote_ref` 的关系

**正文中的 **`footnote_ref` 推荐最小结构已冻结为：

```
{
  "_type": "footnote_ref",
  "refId": "fn-1"
}
```

**两者关系如下：**

### footnote 条目

```
fn-1
```

**表示脚注正文内容。**

### 正文脚注引用

```
footnote_ref(refId="fn-1")
```

**表示正文中的一次脚注引用。**

**说明：**

* **当前阶段 **`footnote_ref` 指向一个脚注条目
* **当前阶段不冻结是否允许多个位置复用同一脚注条目，但结构上允许**

---

## 27.6 `footnotes` 校验建议

**当前阶段建议至少满足：**

1. `id` 必填
2. `blocks` 必须是数组
3. `blocks` 不应为空
4. **同一 **`footnotes` 中 `id` 唯一
5. **被 **`footnote_ref.refId` 引用的条目必须存在
6. `anchor` 缺省时可回退为 `id`

---

## 28. `glossary` 条目结构（新增）

## 28.1 设计目标

`glossary` 用于承载可被 `glossary_term` 引用的术语、缩写或概念条目。

**其目标是：**

* **把正文中的术语引用与术语定义分离**
* **支持术语在正文中多次出现**
* **为后续术语表、首次解释、术语跳转等能力预留空间**

---

## 28.2 当前阶段推荐最小结构

```
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

---

## 28.3 推荐字段说明

### 通用基型字段

* `id`
* `anchor`
* `label`
* `meta`

### glossary 专属最小字段

#### `term`

**术语主显示文本。**

**说明：**

* **当前阶段建议为纯文本**
* **通常对应正文中的术语主写法，例如 **`DCF`

---

#### `definition`

**术语定义文本。**

**说明：**

* **当前阶段先冻结为纯文本**
* **后续若需要富文本定义，可升级为 **`blocks`
* **当前阶段优先保持简单和可用**

---

#### `aliases`

**术语别名数组。**

**说明：**

* **当前阶段可选**
* **用于支持缩写、全称、同义写法等**
* **不强制要求唯一**

---

## 28.4 与 `glossary_term` 的关系

**正文中的 **`glossary_term` 推荐最小结构已冻结为：

```
{
  "_type": "glossary_term",
  "termId": "term-dcf"
}
```

**两者关系如下：**

### glossary 条目

```
term-dcf
```

**表示术语定义条目。**

### 正文术语引用

```
glossary_term(termId="term-dcf")
```

**表示正文中的一次术语引用。**

**说明：**

* **同一个 glossary 条目可被多次引用**
* **当前阶段不冻结正文渲染时是：**
  * **悬浮提示**
  * **跳转**
  * **首次展开解释**
  * **末尾术语表列出**

**这些行为由后续渲染器策略决定**

---

## 28.5 `glossary` 校验建议

**当前阶段建议至少满足：**

1. `id` 必填
2. `term` 必填
3. `definition` 必填
4. `aliases` 如存在则必须是数组
5. **同一 **`glossary` 中 `id` 唯一
6. **被 **`glossary_term.termId` 引用的条目必须存在
7. `anchor` 缺省时可回退为 `id`

---

## 29. 本次新增的结论与下一步（新增）

**本次新增章节已经完成了“学术与辅助 registry 条目”的第一阶段冻结，主要包括：**

1. `bibliography` 的最小条目结构
2. `footnotes` 的最小条目结构
3. `glossary` 的最小条目结构
4. **它们与：**
   * `citation_ref`
   * `footnote_ref`
   * `glossary_term` **的引用闭环关系**

**这使得当前协议已经能够进一步稳定表达：**

* **正文中的文献引用**
* **正文中的脚注引用**
* **正文中的术语引用**
* **文献、脚注、术语条目的基础 registry 结构**
* **面向后续渲染与解析的学术辅助对象基础**

---

## 29.1 后续建议顺序

**下一步建议继续按以下顺序推进：**

### 第一步：Java 渲染器合同

**明确：**

* **body item 分发**
* **text block 分发**
* **inline object 分发**
* **object block 分发**
* **registry resolve**
* **编号与引用 resolve**
* **页面样式层接口边界**

### 第二步：chart 专题

**在其他基础都稳定后，再单独设计：**

* `datasets.charts`
* **自定义图表数据协议**
* **图表类型枚举**
* **图表样式与数据结构约定**

### 第三步：样式层与分页层

**最后再设计：**

* **字号**
* **字体**
* **颜色**
* **页边距**
* **页眉页脚**
* **分页策略**
* **背景图策略**
