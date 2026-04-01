# OVA Portable Text v1.1 正式协议

## 1. 文档定位与阅读方式

本协议定义一套面向“**上游生成报告内容 JSON，下游读取 JSON 并渲染文档**”的中间协议。

本协议的核心目标不是定义具体视觉样式，而是定义一套**稳定、可校验、可解析、可扩展**的内容结构合同，使不同实现方能够围绕同一份 JSON 完成：

- 内容生成
- 协议校验
- 引用解析
- 渲染实现
- 局部更新
- 图表、表格、图片等资源复用

本协议的主要读者是：

- 上游内容生成开发者
- 下游渲染器开发者
- 协议维护者
- 校验器开发者

### 1.1 本文推荐阅读顺序

为便于开发者理解，本协议按“**JSON 顶层字段顺序 + 每个字段的职责与引用关系”**组织：

1. 先看第 4 章，理解 Portable Text 的原生能力与本协议中的使用边界。
2. 再看第 5 章，理解整份 JSON 的总览与推荐读取顺序。
3. 然后按第 6～14 章，逐个阅读顶层字段：
   - `schemaVersion`
   - `meta`
   - `theme`
   - `assets`
   - `datasets`
   - `bibliography`
   - `footnotes`
   - `glossary`
   - `sections`
4. 最后看第 15～20 章，理解统一引用模型、回退策略、校验要求与非目标。

### 1.2 协议范围

当前版本已经正式定义：

* 顶层 JSON 结构
* 章节树结构
* `body` 联合类型
* section 内部富文本承载方式
* 一组最小可用的文本样式与行内引用类型
* 一组最小可用的块级对象类型
* `assets.images` 的双来源图片资源模式
* `datasets.tables` 的基础结构
* `datasets.charts` 中 `pie` 图的基础结构
* bibliography / footnotes / glossary 的基础条目结构
* 渲染器最低实现要求与回退规则

当前版本不细化：

* 除 `pie` 外的其他图表详细结构
* 视觉主题细节
* 页面级排版与分页算法
* 页眉页脚
* `manual` numbering 的详细对象结构
* 标题富文本

## 2. 规范性术语

为避免“建议”和“必须”混淆，本协议使用以下术语：

* **必须** ：实现方需要严格满足，否则视为不符合协议。
* **应该** ：强烈建议满足；如不满足，应自行承担兼容风险。
* **可以** ：允许实现，但不是最低要求。
* **预留** ：协议为未来扩展保留该概念或位置；当前版本不要求渲染器完整实现其行为。

本协议同时区分两类内容：

1. **正式定义内容** ：字段、枚举与基本行为已经明确，渲染器应按此开发。
2. **预留内容** ：当前版本只保留名字、位置或扩展口，渲染器不得自行臆测其完整语义。

---

## 3. 设计原则

### 3.1 内容与渲染分离

- 上游只负责产生结构化内容。
- 下游只负责读取结构化内容并渲染。
- 内容层不直接写死字号、颜色、页边距、分页算法等视觉实现细节。

### 3.2 Portable Text 是富文本底座，不是整份报告的全部结构

- Portable Text 只负责承载顶层字段 section 的内部富文本内容流。
- 章节树、全局资源、编号体系、引用目标体系都位于 Portable Text 外层。

### 3.3 章节树优先于扁平内容流

整份报告以树形 `sections` 为主结构，不采用单一扁平内容流再二次推断章节范围。

### 3.4 标题文本与展示编号分离

- `title` 只存标题文本。
- 展示编号由系统依据 `numbering` 与章节结构推导。
- 不应把 `1.2.3` 之类的编号直接写入 `title`。

### 3.5 大资源优先进入 registry

- 图片、图表数据、表格数据、参考文献、脚注等资源应优先注册到顶层 registry。
- 正文内容优先通过 `*Ref` 引用 registry。
- 少量简单且一次性的内容才考虑直接内嵌。

### 3.6 所有可被引用对象都必须可解析

任何将来可能被以下能力引用的对象，都应具备统一可解析目标模型：

- `xref`
- `citation_ref`
- `footnote_ref`
- 目录
- 图表目录
- 表格目录
- PDF 书签
- 页内跳转

---

## 4. Portable Text 的原生能力

### 4.1 本节目的

本节用于说明：

1. **Portable Text 原生提供了哪些富文本表达能力**
2. **本协议如何在这些原生能力之上定义报告语义**
3. **开发者应如何理解“Portable Text 原生层”与“本协议扩展层”的关系**

本协议不是直接原样使用 Portable Text 的全部自由度，而是：

* 以 Portable Text 作为**富文本 JSON 底座**
* 在其外层增加报告系统所需的**结构规则、引用规则、资源规则和渲染语义**

因此，渲染器开发时应区分两层：

* **Portable Text 原生层** ：负责表达通用富文本内容
* **本协议扩展层** ：负责表达报告系统中的章节、图表、脚注、参考文献、交叉引用等业务语义

### 4.2 Portable Text 是什么

Portable Text 是一种使用 JSON 表达富文本内容的规范。

它的核心思想是：

* **先把内容结构化存储**
* **再由不同渲染器决定最终显示方式**

同一份内容 JSON，理论上可以被渲染为：

* HTML
* PDF
* Markdown
* Word
* 其他自定义输出格式

对于本项目，Portable Text 的价值主要体现在：

* 上游负责生成统一的内容 JSON
* 下游渲染器负责根据协议将 JSON 渲染为 PDF 等可视化展现
* 内容与展示解耦
* 同一套渲染器可以复用到多份报告

### 4.3 Portable Text 原生的最基本形态

Portable Text 最基本的形态是一个内容块数组**。**

示意如下：

```json
[
  { ...第1个内容块... },
  { ...第2个内容块... },
  { ...第3个内容块... }
]
```

可以将其理解为：

* 一个数组元素 = 一个内容块
* 内容块可以是文本块，也可以是自定义对象块
* 所有内容块按顺序排列，形成最终的阅读流

Portable Text 原生更擅长表达“ **块流** ”，而不是严格的章节树。

### 4.4 Portable Text 原生文本块：`block`

Portable Text 中最常见的内容块类型是 `_type = "block"`。Portable Text 也允许在块数组中放入非 `block` 的块级对象，详情见4.11小节。

`block` 块通常用于表达：

- 普通段落
- 标题
- 引用块
- 列表项

一个典型的 `block` 通常包含以下字段：

- `_type`：通常固定为 `"block"`
- `style`：块的语义样式角色
- `children`：块内的行内内容数组
- `markDefs`：复杂行内标记的数据定义区

最简单段落示例：

```json
[
  {
    "_type": "block",
    "style": "normal",
    "children": [
      {
        "_type": "span",
        "text": "这是一段普通正文第一句话。",
        "marks": []
      },
      {
        "_type": "span",
        "text": "这是一段普通正文第二句话。",
        "marks": []
      }
    ],
    "markDefs": []
  }
]
```

**在本协议中的使用方式**

本协议继续使用 `block` 作为正文富文本的基本单位。

### 4.5 `style`：文本块的语义样式角色

`style` 用于表达该文本块在内容上的语义角色，例如普通段落，标题，引用等等。Portable Text 原生的 `style` 并没有一个规范级固定全集。

Portable Text 原生常见样式包括：

- `normal`
- `h1`
- `h2`
- `h3`
- `blockquote`

例如：

```json
[
  {
    "_type": "block",
    "style": "blockquote",
    "children": [
      {
        "_type": "span",
        "text": "Valuation should be interpreted with market context.",
        "marks": []
      }
    ],
    "markDefs": []
  }
]
```

**在本协议中的使用方式**

特别需要注意的是：

- Portable Text 原生可用 `h1 / h2 / h3` 表达标题语义
- **本协议不使用 `h1 / h2 / h3` 表达章节层级**，本协议中的正式章节结构由顶层 `sections[]` 和 `subsection.section` 表达
- 本协议中，`style` 仍然表示正文的“文本块的语义角色”，但具体支持哪些语义、如何渲染，以本协议后文定义为准。

渲染器应理解：

- `style` 表示语义，不直接等于最终视觉
- 字号、上下间距多少、是否换页等等，最终均由渲染器实现决定
- 对于本协议**未列入正式支持范围的** `style`，应按回退规则处理，而不是自行推断为正式章节层级

### 4.6 `span`：行内文本单位

`span` 是 `block.children[]` 中 `_type` 的最基础类型，语义为行内文本。 `block.children[]` 除了支持 `span`，还支持自定义的 inline type，详情见4.10小节。

一个段落通常会拆成多个 `span`，这样才能只对某一句话，或同一句话中的局部文本施加不同标记。

示例：

```json
[
  {
    "_type": "block",
    "style": "normal",
    "children": [
      { "_type": "span", "text": "这个结论是", "marks": [] },
      { "_type": "span", "text": "重要", "marks": ["strong"] },
      { "_type": "span", "text": "的。", "marks": [] }
    ],
    "markDefs": []
  }
]
```

**在本协议中的使用方式**

本协议沿用 `span` 作为标准行内文本单位类型。
所有加粗、斜体、下划线、链接、引用、术语标记等，均附着于 `span` 或 `span` 所引用的标记定义上。

### 4.7 `marks`：行内简单样式标记

Portable Text 原生允许 `span.marks[]` 挂载简单样式标记，常见包括：

- `strong`
- `em`
- `underline`

也可叠加多个标记。

示例：

```json
{
  "_type": "span",
  "text": "同时加粗斜体",
  "marks": ["strong", "em"]
}
```

**在本协议中的使用方式**

本协议继续使用 `marks` 表达简单行内样式，但仅按本协议允许的 decorator 集合实现。

对于 `marks` 中出现的本协议未正式支持的行内样式：

- 先进入 `markDefs` 机制执行相关逻辑，详情见4.8小节
- 若无法解析，可忽略并不展现其视觉效果

### 4.8 `markDefs`：带数据的行内标记定义

当某个行内标记不仅仅是视觉样式，而是还包含额外数据时，Portable Text 使用 `markDefs` 机制。

其工作方式是：

1. `span.marks[]` 中出现某个 key
2. `markDefs[]` 中用相同 key 定义该标记的详细数据

典型用途包括：

- 链接
- 批注
- 引用
- 术语说明
- 外部跳转
- 自定义 annotation

链接示例：

```json
[
  {
    "_type": "block",
    "style": "normal",
    "children": [
      { "_type": "span", "text": "查看 ", "marks": [] },
      { "_type": "span", "text": "Portable Text 官网", "marks": ["link-1"] }
    ],
    "markDefs": [
      {
        "_key": "link-1",
        "_type": "link",
        "href": "https://www.portabletext.org"
      }
    ]
  }
]
```

**在本协议中的使用方式**

本协议使用 `markDefs` 承载行内复杂语义，例如：

- 超链接
- 参考文献引用
- 脚注引用
- 术语引用
- 交叉引用

渲染器应注意：

- `marks` 只表示“挂了哪个标记”
- `markDefs` 才表示“这个标记的具体含义和数据”
- 未识别的 annotation 类型应按回退规则处理

### 4.9 列表：`listItem` 与 `level`

Portable Text 原生支持列表，但其列表模型不是 HTML 的嵌套 DOM，而是通过以下字段表达：

- `listItem`
- `level`

常见写法：

- `listItem: "bullet"`：无序列表
- `listItem: "number"`：有序列表
- `level: 1 / 2 / 3 ...`：列表层级深度

示例：

```json
[
  {
    "_type": "block",
    "style": "normal",
    "listItem": "bullet",
    "level": 1,
    "children": [
      { "_type": "span", "text": "第一点", "marks": [] }
    ],
    "markDefs": []
  },
  {
    "_type": "block",
    "style": "normal",
    "listItem": "bullet",
    "level": 2,
    "children": [
      { "_type": "span", "text": "第一点的子项", "marks": [] }
    ],
    "markDefs": []
  },
  {
    "_type": "block",
    "style": "normal",
    "listItem": "bullet",
    "level": 1,
    "children": [
      { "_type": "span", "text": "第二点", "marks": [] }
    ],
    "markDefs": []
  }
]
```

**在本协议中的使用方式**

本协议允许在正文文本块中使用 Portable Text 原生列表能力。但渲染器开发者应明确：

- 列表本质上仍是一组顺序排列的 `block`
- Portable Text 原生不提供严格块嵌套树
- 因此，本协议中的正式章节层级不能依赖 `listItem + level` 表达

### 4.10 行内对象（Inline Object）

Portable Text 原生允许在 `block.children[]` 中放入除 `span` 外的行内对象。

这意味着一行文字中可以混入非纯文本内容，例如：

- 行内徽章
- 行内状态标签
- 行内公式 token
- 行内引用 token
- 其他小型嵌入对象

示例：

```json
[
  {
    "_type": "block",
    "style": "normal",
    "children": [
      { "_type": "span", "text": "本专利评级为 ", "marks": [] },
      { "_type": "badge", "label": "A+", "tone": "green" },
      { "_type": "span", "text": "，表现突出。", "marks": [] }
    ],
    "markDefs": []
  }
]
```

**在本协议中的使用方式**

本协议保留使用行内自定义对象的能力，但是否正式支持某种行内对象类型，以本协议正文行内对象定义为准。

### 4.11 块级对象（Block Object）

Portable Text 原生还允许在块数组中直接放入非 `block` 的块级对象。
这些对象与普通文本块处于同一层级，可与文本块顺序混排。

这使其能够表达：

- 图片
- 表格
- 图表
- 代码块
- 数学公式块
- 自定义业务块

示例：

```json
[
  {
    "_type": "image",
    "src": "https://example.com/cover.png",
    "alt": "封面图"
  },
  {
    "_type": "code",
    "language": "python",
    "code": "print('hello world')"
  }
]
```

**在本协议中的使用方式**

本协议中的 `image`、`chart`、`table`、`math_block`、`callout` 等正文对象，都属于在 Portable Text 原生块级对象能力上的业务扩展。

但需要特别区分：

- **正文块级对象**：出现在正文内容流中
- **资源数据本体**：通常位于 `assets` 或 `datasets` 顶层字段中，被正文块引用

例如：

- 正文中的 `_type = "image"` 只是一个**图片实例节点**
- 真正的图片资源数据位于 `assets.images[]`
- 正文实例通过 `imageRef` 指向图片资源

同理：

- 正文中的 `_type = "chart"` 是**图表实例节点**
- 真正的图表数据位于 `datasets.charts[]`
- 正文实例通过 `chartRef` 指向图表数据
- 正文中的 `_type = "table"` 是**表格实例节点**
- 真正的表格数据位于 `datasets.tables[]`
- 正文实例通过 `tableRef` 指向表格数据

渲染器开发时必须清楚区分“**实例层**”与“**资源层 / 数据层**”。

### 4.12 Portable Text 原生负责什么、不负责什么

#### 4.12.1 Portable Text 原生适合负责的内容

Portable Text 原生适合承担以下能力：

1. 文本块流表达

   - 段落
   - 标题样式角色
   - 引用块
   - 列表项
   - 顺序排列的内容块
2. 行内富文本表达

   - 加粗
   - 斜体
   - 下划线
   - 行内链接
   - 行内注解
3. 混合对象表达

   - 行内对象
   - 块级对象
   - 文本与对象的顺序混排

#### 4.12.2 Portable Text 原生不负责的内容

Portable Text 原生不直接负责：

- 最终视觉排版
- PDF 分页
- 页眉页脚
- 字号、字重、颜色、边距
- 正式章节树
- 图表编号规则
- 脚注体系
- 参考文献体系
- 目录生成
- 交叉引用解析
- 报告模板语义
- 页面级布局策略

这些都应由本协议扩展层 + 渲染器实现共同完成。

### 4.13 本协议为何要在 Portable Text 之上再定义 Report Profile

本协议采用 Portable Text 作为富文本底座，但报告系统本身还需要一套更强的结构化规则。

原因在于：

1. Portable Text 更擅长“块流”，不擅长“严格章节树”
2. Portable Text 不原生内置学术报告或商业报告语义
3. Portable Text 不负责资源注册、图表数据、脚注库、参考文献库等顶层数据组织

因此，本协议在 Portable Text 之上补充了以下规则：

- 顶层数据组织方式
- 正式章节树结构
- 正文实例层与资源层的分离
- 图表 / 表格 / 图片的引用规则
- bibliography / footnotes / glossary 的独立存储
- 目录、交叉引用、脚注、术语等报告语义
- 渲染器最低实现要求与回退规则

Portable Text 负责提供通用富文本骨架。
本协议负责规定报告系统中的正式结构、正式类型、正式引用关系和正式渲染语义。

---

## 5. 协议顶层 JSON 总览

### 5.1 顶层结构

```json
{
  "schemaVersion": "report.v1.1",
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

### 5.2 渲染器推荐读取顺序

建议渲染器按以下顺序处理整份文档：

1. 读取 `schemaVersion`，分发解析逻辑
2. 读取 `meta`
3. 读取 `theme`
4. 建立 registry 索引：

   * `assets`
   * `datasets`
   * `bibliography`
   * `footnotes`
   * `glossary`
5. 遍历 `sections`，递归渲染章节树
6. 在渲染过程中，按 `*Ref` 回查 registry 条目

---

## 6. `schemaVersion`

### 6.1 字段定义

- 类型：字符串
- 是否必须：必须

### 6.2 作用

`schemaVersion` 表示当前文档所遵循的协议版本。渲染器必须按该值分发解析逻辑。

当前版本固定值： `report.v1.1`

### 6.3 渲染器要求

- 必须识别 `report.v1.1`
- 遇到未知版本时，应返回清晰错误，而不是静默按旧版本解析

---

## 7. `meta`

### 7.1 定义

- 类型：对象
- 是否必须：必须

### 7.2 作用

`meta` 承载文档级元信息，用于描述文档身份、生成信息、业务归属与渲染上下文。

`meta` 不属于正文内容流，不直接出现在 `sections[].body[]` 中。
渲染器可以根据 `meta` 决定是否在封面、页眉、页脚、标题区、文档属性区展示其中部分字段。

### 7.3 正式字段表

当前版本中，`meta` 的正式字段如下。


| 字段名            | 类型   | 是否必须 | 含义                                 | 值格式 / 枚举                                                                             |
| ----------------- | ------ | -------: | ------------------------------------ | ----------------------------------------------------------------------------------------- |
| `title`           | string |       否 | 文档主标题                           | 普通字符串                                                                                |
| `subtitle`        | string |       否 | 文档副标题                           | 普通字符串                                                                                |
| `language`        | string |       否 | 文档正文语言                         | 枚举值：`zh` 中文，`en` 英文                                                            |
| `author`          | string |       否 | 文档作者或生成责任方                 | 普通字符串                                                                                |
| `date`            | string |       否 | 文档日期                             | `YYYY-MM-DD`                                                                              |
| `reportNumber`    | string |       否 | 报告编号、文档编号或业务编号         | 普通字符串                                                                                |
| `documentType`    | string |       否 | 文档类型                             | 枚举值：`valuationReport` 估值报告                                                        |
| `confidentiality` | string |       否 | 保密级别                             | 枚举值：`public` 公开， `user` 所属用户， `internal` 公司内部、`confidential` 机密        |
| `generatedBy`     | string |       否 | 生成系统、生成模块或生成器名称       | 普通字符串                                                                                |
| `generatedAt`     | string |       否 | 文档生成时间                         | RFC 3339 / ISO 8601 时间格式字符串，如`2026-03-24T12:34:56Z`                              |
| `clientId`        | string |       否 | 客户内部 ID 或业务客户标识           | 普通字符串                                                                                |
| `projectId`       | string |       否 | 项目标识、任务标识或报告关联对象 ID  | 普通字符串                                                                                |
| `reportType`      | string |       否 | 业务层报告类型                       | 枚举值：`startupCompany` 初创公司，`innovationTeam` 创新团队，`patent` 专利，`loan` 债权 |
| `clientName`      | string |       否 | 客户名称、委托方名称或展示对象名称   | 普通字符串                                                                                |
| `locale`          | string |       否 | 渲染区域设置                         | 枚举值：`zh` 中文，`en` 英文                                                            |
| `source`          | string |       否 | 文档来源、数据来源说明或上游系统标识 | 普通字符串                                                                                |

### 7.4 字段使用说明

#### 7.4.1 必须性说明

- `meta` 对象本身必须存在
- `meta` 内部字段在当前版本中均不是强制必填
- 若某字段无值，可以省略，也可以显式设为 `null`

#### 7.4.2 渲染说明

- 渲染器不得将 `meta` 自动视为正文段落
- 渲染器可以按自身模板决定是否展示以下信息：
  - `title`
  - `subtitle`
  - `author`
  - `date`
  - `reportNumber`
  - `clientName`
  - `confidentiality`
- 若渲染器不使用某个 `meta` 字段，应忽略，而不应报致命错误

#### 7.4.3 值约束说明

- 当前版本中，除了明确指定的格式与枚举值需要校验，其余字符串字段不做格式约束

---

## 8. `theme`

### 8.1 字段定义

- 类型：对象
- 是否必须：必须

### 8.2 作用

`theme` 用于承载渲染层可消费的主题与默认布局提示。

本协议仍坚持“内容与渲染分离”原则，因此 `theme` 不直接等同于最终视觉实现；
它表达的是**渲染器可参考的默认规则**，而不是强制像素级排版结果。

### 8.3 v1.1 正式支持的最小稳定字段

当前版本正式定义以下稳定字段：

```json
{
  "blockStyleDefaults": {}
}
```

字段表：


| 字段名               | 类型   | 是否必须 | 含义                               |
| -------------------- | ------ | -------- | ---------------------------------- |
| `blockStyleDefaults` | object | 否       | 各类`block.style` 的默认布局提示表 |

### 8.4 `blockStyleDefaults`

`blockStyleDefaults` 的 key 应为正式支持的 `block.style` 值，例如：

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

value 为：

```json
{
  "layout": { ... }
}
```

示例：

```json
{
  "blockStyleDefaults": {
    "normal": {
      "layout": {
        "textAlign": "justify",
        "firstLineIndent": { "unit": "em", "value": 2 }
      }
    },
    "figure_caption": {
      "layout": {
        "textAlign": "center"
      }
    },
    "table_caption": {
      "layout": {
        "textAlign": "center"
      }
    }
  }
}
```

### 8.5 `layout` 段落布局

`layout` 用于表达块级文本在版式上的提示信息，例如：

- 是否居中
- 是否两端对齐
- 是否首行缩进
- 段前距 / 段后距

需要特别注意：

- `style` 继续表示**语义角色**
- `layout` 表示**布局提示**
- 二者职责不同，不应混用

当前版本中，`layout` 只正式用于 `_type = "block"` 的文本块；
不用于 `span`，也不用于 `marks`。

##### 最小结构示例

```json
{
  "_type": "block",
  "style": "normal",
  "layout": {
    "textAlign": "justify",
    "firstLineIndent": { "unit": "em", "value": 2 }
  },
  "children": [
    { "_type": "span", "text": "这是正文。", "marks": [] }
  ],
  "markDefs": []
}
```

#### 8.5.1 当前版本正式支持的字段


| 字段名            | 类型   | 是否必须 | 含义             |
| ----------------- | ------ | -------- | ---------------- |
| `textAlign`       | string | 否       | 段落文本对齐方式 |
| `firstLineIndent` | object | 否       | 段首缩进提示     |
| `spaceBefore`     | object | 否       | 段前距提示       |
| `spaceAfter`      | object | 否       | 段后距提示       |

#### 8.5.2 `textAlign` 对齐方式

当前正式枚举：

- `left`
- `center`
- `right`
- `justify`

#### 8.5.3 长度对象

`firstLineIndent 段首缩进 / spaceBefore 段前距 / spaceAfter 段后距` 采用统一长度对象：

```json
{
  "unit": "em",
  "value": 2
}
```

字段表：


| 字段名  | 类型   | 是否必须 | 含义     |
| ------- | ------ | -------- | -------- |
| `unit`  | string | 是       | 长度单位 |
| `value` | number | 是       | 长度值   |

当前版本正式支持的 `unit`：

- `em`
- `pt`

约定：

- `firstLineIndent` 推荐优先使用 `em`
- `spaceBefore / spaceAfter` 推荐优先使用 `pt`

#### 8.5.4 规则

- `layout` 只表达布局提示，不保证不同渲染器的最终视觉完全一致
- 未识别的 `layout` 字段，渲染器可以忽略并记录兼容日志
- 不得把 `layout` 误解释为章节层级信号

### 8.6 继承与覆盖规则

同一个文本块的布局提示，按以下优先级生效：

1. 当前 `block.layout`
2. `theme.blockStyleDefaults[block.style].layout`
3. 渲染器自身模板默认值

也就是说：

- `theme` 负责给某类段落提供默认布局
- 某个具体段落若需要例外，可在该段自己的 `layout` 中覆盖

### 8.7 当前版本不正式定义的内容

当前版本仍不正式定义以下字段合同：

- 颜色系统
- 字体族
- 具体字号
- 页面尺寸
- 页边距
- 页眉页脚
- 分页算法

渲染器可以内部实现这些能力，但不得将其误认为当前协议的正式稳定字段。

---

## 9. `assets`

### 9.1 定义

- 类型：对象
- 是否必须：必须

`assets` 是静态资源 registry，用于存放可被正文或模板引用的资源数据本体。
`assets` 本身不参与正文内容流，不直接出现在 `sections[].body[]` 中。

当前版本的顶层结构为：

```json
{
  "images": [],
  "logos": [],
  "backgrounds": [],
  "icons": [],
  "attachments": []
}
```

### 9.2 作用

`assets` 用于承载“资源本体”，例如：

* 图片资源
* Logo 资源
* 背景图资源
* 图标资源
* 附件资源

正文中的块对象只负责引用“ 在这里插入哪个资源 ”，不直接承载资源本体数据。

例如：

* `assets.images[]` 描述“这张图片资源本身是什么”
* 正文中的 `_type = "image"` 块描述“这里插入哪张图片资源”

### 9.3 顶层字段表


| 字段名        | 类型  | 是否必须 | 含义                |
| ------------- | ----- | -------- | ------------------- |
| `images`      | array | 是       | 图片资源 registry   |
| `logos`       | array | 是       | Logo 资源 registry  |
| `backgrounds` | array | 是       | 背景图资源 registry |
| `icons`       | array | 是       | 图标资源 registry   |
| `attachments` | array | 是       | 附件资源 registry   |

#### 9.3.1 必须性说明

* `assets` 对象本身必须存在
* `images / logos / backgrounds / icons / attachments` 五个字段在当前版本中都应存在
* 若某一类资源未使用，其值应为 `[]`

### 9.4 通用 registry 条目基型

`assets` 中的资源条目，当前版本推荐优先具备以下公共字段：

```json
{
  "id": "resource-id",
  "anchor": "resource-id",
  "label": "Optional human-readable label",
  "meta": {}
}
```

#### 9.4.1 通用字段表


| 字段名   | 类型   | 是否必须 | 含义             | 说明                                |
| -------- | ------ | -------- | ---------------- | ----------------------------------- |
| `id`     | string | 是       | 全局唯一稳定标识 | 同一文档内不得重复                  |
| `anchor` | string | 否       | 资源锚点标识     | 若此字段被省略，可直接采用`id` 的值 |
| `label`  | string | 否       | 人类可读标签     | 仅供展示、调试或辅助识别            |
| `meta`   | object | 否       | 附加元信息       | 当前版本不商定内部字段              |

#### 9.4.2 通用规则

* `id` 必须在整个文档范围内稳定且唯一
* `anchor` 若存在，应为字符串；若缺失，渲染器可回退使用 `id`
* `meta` 若未使用，可以省略，也可以写为 `{}`
* 未经当前版本正式定义的附加字段，渲染器可以忽略，但不应报致命错误

### 9.5 `assets.images`

#### 9.5.1 定义

* 类型：array
* 元素类型：对象
* 是否必须：必须

`assets.images` 存储的是 图片资源本体 ，不是正文中的图片实例。

#### 9.5.2 与正文 `_type = "image"` 的关系

两者职责不同：

`assets.images[]` 描述的是：

* 这张图片资源的身份
* 这张图片的来源
* 这张图片的 MIME 类型
* 这张图片的尺寸、校验值、替代文本等

正文中的 `_type = "image"` 块描述的是：

* 当前正文位置要插入哪张图片
* 图注、布局、对齐等展示信息

因此：

* `assets.images[]` 是资源层
* `_type = "image"` 是正文实例层
* 正文图片块通过 `imageRef` 引用 `assets.images[].id`

#### 9.5.3 正式结构

```json
{
  "id": "img-system-overview",
  "anchor": "img-system-overview",
  "label": "System overview",
  "meta": {},
  "alt": "System overview diagram",
  "mimeType": "image/png",
  "checksum": "sha256:abc123",
  "width": 1200,
  "height": 800,
  "imageSource": {
    "kind": "url",
    "url": "https://example.com/system-overview.png"
  }
}
```

或：

```json
{
  "id": "img-qrcode",
  "anchor": "img-qrcode",
  "label": "QR code",
  "meta": {},
  "alt": "Company QR code",
  "mimeType": "image/png",
  "checksum": "sha256:def456",
  "width": 512,
  "height": 512,
  "imageSource": {
    "kind": "embedded",
    "encoding": "base64",
    "data": "iVBORw0KGgoAAAANSUhEUgAA..."
  }
}
```

#### 9.5.4 字段表


| 字段名        | 类型    | 是否必须 | 含义             | 值格式 / 枚举                                |
| ------------- | ------- | -------- | ---------------- | -------------------------------------------- |
| `id`          | string  | 是       | 图片资源唯一标识 | 文档内全局唯一                               |
| `anchor`      | string  | 否       | 图片资源锚点     | 省略时可回退为`id`                           |
| `label`       | string  | 否       | 人类可读标签     | 普通字符串                                   |
| `meta`        | object  | 否       | 附加元信息       | 当前不商定内部字段                           |
| `alt`         | string  | 应该     | 图片替代文本     | 用于无障碍与图片渲染失败时的降级替换展示     |
| `mimeType`    | string  | 应该     | 图片 MIME 类型   | 如`image/png`、`image/jpeg`、`image/svg+xml` |
| `checksum`    | string  | 否       | 图片内容校验值   | 建议格式：`sha256:<hex>`                     |
| `width`       | integer | 否       | 原始像素宽度     | 正整数                                       |
| `height`      | integer | 否       | 原始像素高度     | 正整数                                       |
| `imageSource` | object  | 是       | 图片来源描述对象 | 见 9.5.5                                     |

##### 9.5.4.1 字段说明

* `alt` 在当前版本中应尽量提供；渲染器可以将其用于：
  * 无障碍输出
  * 图片加载失败时的替代文本
* `mimeType` 在当前版本中应尽量提供，便于渲染器识别图片格式
* `width / height` 若提供，应表示资源原始像素尺寸，而非版式显示尺寸
* `imageSource` 是当前版本图片资源的正式来源字段，必须存在

#### 9.5.5 `imageSource`

##### 9.5.5.1 定义

* 类型：对象
* 是否必须：必须

`imageSource` 用于描述图片资源的真实来源。

当前版本正式支持两种来源模式：

* `kind = "url"`
* `kind = "embedded"`

##### 9.5.5.2 字段表


| 字段名     | 类型   | 是否必须 | 含义             | 值格式 / 枚举                                        |
| ---------- | ------ | -------- | ---------------- | ---------------------------------------------------- |
| `kind`     | string | 是       | 图片来源类型     | 枚举值：`url`，`embedded`                            |
| `url`      | string | 条件必须 | 图片地址         | 当`kind = "url"`时必须存在                           |
| `encoding` | string | 条件必须 | 内嵌数据编码方式 | 当`kind = "embedded"`时必须存在；当前仅允许 `base64` |
| `data`     | string | 条件必须 | 内嵌图片数据     | 当`kind = "embedded"`时必须存在                      |

##### 9.5.5.3 `kind = "url"`

```json
{
  "kind": "url",
  "url": "https://example.com/image.png"
}
```

规则

* `url` 必须存在，且值类型为字符串
* `encoding` 不应出现
* `data` 不应出现

`url` 当前版本允许表示：

* `http://...`
* `https://...`
* 相对路径，例如 `assets/images/cover.png`
* 本地路径字符串（是否允许由具体交付环境决定）

渲染器应将其理解为“可读取的图片资源地址”，而不是正文文字内容。

##### 9.5.5.4 `kind = "embedded"`

```json
{
  "kind": "embedded",
  "encoding": "base64",
  "data": "iVBORw0KGgoAAAANSUhEUgAA..."
}
```

规则

* `data` 必须存在，且值类型为字符串
* `encoding` 必须存在，且当前正式支持值只有 `"base64"`
* `url` 不应出现

`embedded` 的解释

* `data` 存储图片内嵌数据本体
* 渲染器应根据 `encoding` 对 `data` 解码后再进行图片渲染
* 当前版本不支持除 `base64` 之外的其他编码方式

#### 9.5.6 渲染器处理要求

##### 9.5.6.1 解析优先级

由于当前版本将 `imageSource` 定义为正式来源字段，渲染器应直接按 `imageSource` 解析图片资源。

##### 9.5.6.2 最低实现要求

渲染器至少应支持：

* `imageSource.kind = "url"`
* `imageSource.kind = "embedded"`
* `encoding = "base64"`

##### 9.5.6.3 错误处理

若出现以下情况，渲染器应将其视为图片资源无效：

* `imageSource` 缺失
* `kind` 不在正式枚举中
* `kind = "url"` 但缺少 `url`
* `kind = "embedded"` 但缺少 `data`
* `kind = "embedded"` 但 `encoding` 不是 `"base64"`

渲染器可以选择：

* 显示 `alt` 作为降级文本
* 显示固定错误提示文本

但不应导致整份文档直接崩溃。

### 9.6 `assets.logos`

#### 9.6.1 定义

* 类型：array
* 是否必须：必须

`assets.logos` 用于存放 Logo 资源本体。

#### 9.6.2 当前版本结构规则

当前版本中，`assets.logos[]` 与 `assets.images[]` 共享相同的资源结构与 `imageSource` 规则。

也就是说，`assets.logos[]` 的单个条目字段合同应与 9.5 节一致。

### 9.7 `assets.backgrounds`

#### 9.7.1 定义

* 类型：array
* 是否必须：必须

`assets.backgrounds` 用于存放背景图资源本体。

#### 9.7.2 当前版本结构规则

当前版本中，`assets.backgrounds[]` 与 `assets.images[]` 共享相同的资源结构与 `imageSource` 规则。

也就是说，`assets.backgrounds[]` 的单个条目字段合同应与 9.5 节一致。

### 9.8 `assets.icons`

#### 9.8.1 定义

* 类型：array
* 是否必须：必须

`assets.icons` 用于存放图标资源本体。

#### 9.8.2 当前版本结构规则

当前版本中，`assets.icons[]` 与 `assets.images[]` 共享相同的资源结构与 `imageSource` 规则。

也就是说，`assets.icons[]` 的单个条目字段合同应与 9.5 节一致。

### 9.9 `assets.attachments`

#### 9.9.1 定义

* 类型：array
* 是否必须：必须

`assets.attachments` 用于存放附件资源 registry。

#### 9.9.2 当前版本说明

当前版本只定义：

* `assets.attachments` 这个 registry 位置存在
* 其值类型为数组

当前版本尚未商定单个附件条目的正式字段合同。

因此：

* 生成器可以暂不输出附件条目
* 渲染器可以忽略 `attachments`
* 校验器只需检查其顶层值类型为数组

---

## 10. `datasets`

### 10.1 定义

- 类型：对象
- 是否必须：必须

当前版本的顶层结构为：

```json
{
  "charts": [],
  "tables": [],
  "metrics": []
}
```

`datasets` 是数据型资源 registry，用于存放可被正文或模板引用的数据资源本体。
`datasets` 本身不参与正文内容流，不直接出现在 `sections[].body[]` 中。

`datasets` 用于承载“数据本体”，例如：

* 图表底层数据
* 表格底层数据
* 指标集数据

正文中的块对象只负责描述“ 在这里插入哪个数据资源 ”，不直接承载完整数据本体。

### 10.3 顶层字段表


| 字段名    | 类型  | 是否必须 | 含义              |
| --------- | ----- | -------- | ----------------- |
| `charts`  | array | 是       | 图表数据 registry |
| `tables`  | array | 是       | 表格数据 registry |
| `metrics` | array | 是       | 指标集 registry   |

#### 10.3.1 必须性说明

* `datasets` 对象本身必须存在
* `charts / tables / metrics` 三个字段在当前版本中都应存在
* 若某一类数据未使用，其值应为 `[]`

### 10.4 `datasets.charts`

#### 10.4.1 定义

* 类型：array
* 元素类型：对象
* 是否必须：必须

`datasets.charts` 存储的是 **图表数据本体** ，不是正文中的图表实例。

#### 10.4.2 与正文 `_type = "chart"` 的关系

两者职责不同：

`datasets.charts[]` 描述的是：

* 这份图表数据的身份
* 图表属于哪一类数据结构
* 图表数据本身的数值、标签、说明等

正文中的图表块 `_type = "chart"` 块描述的是：

* 当前正文位置要插入哪份图表数据
* 当前这个图表实例的局部展示上下文

```json
{
  "_type": "chart",
  "id": "fig-area-share",
  "anchor": "fig-area-share",
  "chartRef": "chart-area-share"
}
```

因此：

* `datasets.charts[]` 是**数据层**
* 正文中的 `_type = "chart"` 是**实例层**
* 正文图表块通过 `chartRef` 引用 `datasets.charts[].id`
* 同一图表数据可在多个正文位置复用
* 不同正文实例可拥有不同上下文、不同相邻 caption 或不同编号语境

#### 10.4.3 当前版本正式支持范围

当前版本中，`datasets.charts`  **只正式定义一种图表类型** ：

* `chartType = "pie"`

除 `pie` 外：

* 其他图表类型可以保留在 `datasets.charts` registry 中
* 但当前版本**不构成稳定字段合同**，若未实现可忽略并记录兼容日志

#### 10.4.4 图表通用字段表

当前版本中，`datasets.charts[]` 条目具备以下通用字段：


| 字段名      | 类型   | 是否必须 | 含义             | 值格式 / 说明      |
| ----------- | ------ | -------- | ---------------- | ------------------ |
| `id`        | string | 是       | 图表数据唯一标识 | 文档内全局唯一     |
| `anchor`    | string | 否       | 图表数据锚点     | 省略时可回退为`id` |
| `label`     | string | 否       | 人类可读标签     | 普通字符串         |
| `meta`      | object | 否       | 附加元信息       | 当前不商定内部字段 |
| `chartType` | string | 是       | 图表类型         | 枚举值：`pie` 饼图 |
| `valueUnit` | string | 否       | 数值单位         | 普通字符串         |

`valueUnit` 当前版本不强制固定枚举，通常可以用它决定：

* 数值展示方式
* tooltip / 图例单位
* 百分比、计数、金额等文案后缀

#### 10.4.5 `pie` 图

##### 10.4.5.1 `pie` 图正式字段表


| 字段名      | 类型   | 是否必须 | 含义             | 值格式 / 说明      |
| ----------- | ------ | -------- | ---------------- | ------------------ |
| `id`        | string | 是       | 图表数据唯一标识 | 文档内全局唯一     |
| `anchor`    | string | 否       | 图表数据锚点     | 省略时可回退为`id` |
| `label`     | string | 否       | 人类可读标签     | 普通字符串         |
| `meta`      | object | 否       | 附加元信息       | 当前不商定内部字段 |
| `chartType` | string | 是       | 图表类型         | `pie`              |
| `valueUnit` | string | 否       | 数值单位         | 普通字符串         |
| `slices`    | array  | 是       | 饼图扇区数组     | 饼图扇区内容       |

* 当 `chartType = "pie"` 时，`slices` 必须存在

##### 10.4.5.2 `pie` 图正式结构

```json
{
  "id": "chart-area-share",
  "anchor": "chart-area-share",
  "label": "Area share",
  "meta": {},
  "chartType": "pie",
  "valueUnit": "percent",
  "slices": [
    {
      "key": "technology",
      "label": {
        "zh": "技术",
        "en": "Technology"
      },
      "value": 60,
      "description": {
        "zh": "占比最高",
        "en": "Largest share"
      }
    },
    {
      "key": "finance",
      "label": {
        "zh": "金融",
        "en": "Finance"
      },
      "value": 40,
      "description": {
        "zh": "占比第二",
        "en": "Second largest"
      }
    }
  ]
}
```

##### 10.4.5.3 `slices[]`

**定义**

* 类型：array
* 元素类型：对象
* 是否必须：必须

`slices[]` 中每个对象表示一个饼图扇区。

**扇区字段表**


| 字段名        | 类型   | 是否必须 | 含义         | 值格式 / 说明                      |
| ------------- | ------ | -------- | ------------ | ---------------------------------- |
| `key`         | string | 应该     | 扇区稳定标识 | 用于程序内部映射、排序、日志定位   |
| `label`       | object | 是       | 扇区名称     | 推荐语言对象，见 10.4.8            |
| `value`       | number | 是       | 扇区数值     | 当前版本建议为 number              |
| `description` | object | 否       | 扇区说明     | 推荐语言对象，见 10.4.9            |
| `colorHint`   | string | 否       | 颜色提示     | 当前版本不商定格式，渲染器可以忽略 |

###### `pie.slices[].label`

推荐结构：

```json
{
  "zh": "技术",
  "en": "Technology"
}
```

规则：

* `label` 当前版本采用多语言对象，而不是简单字符串，若仅提供单语言，也应至少保证存在一个可展示值
* 渲染器可按以下顺序选择显示值：

1. `meta.language`
2. `meta.locale`
3. 渲染器自身语言策略

* 若目标语言缺失，可回退到任一存在值

###### `pie.slices[].description`

结构：

```json
{
  "zh": "占比最高",
  "en": "Largest share"
}
```

规则：

* `description` 当前版本采用多语言对象，而不是简单字符串，若仅提供单语言，也应至少保证存在一个可展示值
* 若未提供，渲染器不应报错
* 若提供，渲染器可以用于：
* 图下注释
* tooltip
* 图例扩展说明
* 无障碍辅助文本

### 10.5 `datasets.tables`

#### 10.5.1 定义

* 类型：array
* 元素类型：对象
* 是否必须：必须

`datasets.tables` 存储的是 **表格数据本体** ，不是正文中的表格实例。

#### 10.5.2 与正文 `_type = "table"` 的关系

两者职责不同：

`datasets.tables[]` 描述的是：

* 这张表的数据本体
* 这张表采用哪一种表格结构模式
* 这张表的列定义、行数据、单元格布局等

正文中的 `_type = "table"` 块描述的是：

* 当前正文位置要插入哪张表
* 当前这个表格实例的局部展示上下文

```json
{
  "_type": "table",
  "id": "tbl-financial-summary",
  "anchor": "tbl-financial-summary",
  "tableRef": "table-financial-summary"
}
```

因此：

* `datasets.tables[]` 是**数据层**
* 正文中的 `_type = "table"` 是**实例层**
* 正文表格块通过 `tableRef` 引用 `datasets.tables[].id`

#### 10.5.3 当前版本正式支持范围

当前版本中，`datasets.tables[]` 正式支持两种表格模式：

* `tableType = "record"`
* `tableType = "grid"`

两种模式的设计目标不同：

* `record`：用于**规则结构化表格**
* `grid`：用于**不规则表格 / 复杂排版表格 / 存在跨行跨列的表格**

渲染器必须先读取 `tableType`，再按对应模式解析表格数据。

##### 10.5.3.1 `record`

`record` 类型表格适用于：

* 普通数据表
* 每一列有稳定键名
* 每一行可表示为一个对象
* 适合程序生成、排序、导出、统计

##### 10.5.3.2 `grid`

`grid` 类型表格适用于：

* 不规则表格
* 复杂表头
* 存在 `rowSpan` / `colSpan` 的表格
* 某些行单元格数量不同的表格
* 更偏“版式表达”的表格

#### 10.5.4 表格通用字段表

当前版本中，`datasets.tables[]` 条目具备以下通用字段：


| 字段名      | 类型   | 是否必须 | 含义             | 值格式 / 说明                 |
| ----------- | ------ | -------- | ---------------- | ----------------------------- |
| `id`        | string | 是       | 表格数据唯一标识 | 文档内全局唯一                |
| `anchor`    | string | 否       | 表格数据锚点     | 省略时可回退为`id`            |
| `label`     | string | 否       | 人类可读标签     | 普通字符串                    |
| `meta`      | object | 否       | 附加元信息       | 当前不商定内部字段            |
| `tableType` | string | 是       | 表格模式         | 枚举值：`"record"` ，`"grid"` |
| `rows`      | array  | 是       | 行数据数组       | 具体结构取决于`tableType`     |
| `layout`    | object | 否       | 表格布局提示     | 当前版本主要用于列宽分配      |

##### 10.5.4.1 caption 与 table 的关系

当前版本延续统一原则：

* 表题注优先使用相邻正文文本块，例如 `table_caption`
* 不强制在 `datasets.tables[]` 条目中存 caption
* 不强制在正文 `_type = "table"` 实例中存 caption

推荐相邻模式：

table

table_caption

##### 10.5.4.2 `layout`

`datasets.tables[]` 可选包含 `layout` 对象（勿与段落 `layout` 字段混淆），用于表达表格级布局提示。

当前版本正式支持的 `layout` 结构：

```json
{
  "columnSpecs": []
}
```

字段表：


| 字段名        | 类型  | 是否必须 | 含义           |
| ------------- | ----- | -------- | -------------- |
| `columnSpecs` | array | 否       | 列布局规格数组 |

`columnSpecs[]` 的顺序就是逻辑列顺序。

- 对 `record` 表：其长度应与 `columns[]` 长度一致
- 对 `grid` 表：其长度应与 `columnCount` 一致

当前版本不引入：

- 单元格级宽度百分比
- 行高百分比
- 单元格固定高度

行高应默认由内容和渲染器共同决定。

##### 10.5.4.3 `columnSpecs[]`

每个 `columnSpecs[]` 元素描述一列的宽度分配提示。

最小结构：

```json
{
  "width": {
    "mode": "weight",
    "value": 3
  }
}
```

或：

```json
{
  "width": {
    "mode": "auto"
  }
}
```

字段表：


| 字段名  | 类型   | 是否必须 | 含义               |
| ------- | ------ | -------- | ------------------ |
| `width` | object | 是       | 当前列宽度提示对象 |

`width` 字段表：


| 字段名  | 类型   | 是否必须 | 含义                           |
| ------- | ------ | -------- | ------------------------------ |
| `mode`  | string | 是       | 宽度分配模式                   |
| `value` | number | 条件必须 | 当`mode = "weight"` 时的权重值 |

当前版本正式支持的 `mode`：

- `auto`
- `weight`

规则：

- `mode = "auto"` 时，不应出现 `value`
- `mode = "weight"` 时，`value` 必须为正数
- `weight` 不是百分比，而是相对权重，不要求总和为 100
- 渲染器应在可用表格宽度内，按各列 `weight` 比例分配剩余空间
- 若混用 `auto` 与 `weight`，渲染器应先满足 `auto` 列的最小内容宽度，再把剩余宽度按 `weight` 分配

#### 10.5.5 `record` 模式

##### 10.5.5.1 定义

当 `tableType = "record"` 时，表格采用规则结构化模式。

此时表格条目除通用字段外，还应包含：

* `columns`

##### 10.5.5.2 正式字段表


| 字段名      | 类型   | 是否必须 | 含义             | 值格式 / 说明      |
| ----------- | ------ | -------- | ---------------- | ------------------ |
| `id`        | string | 是       | 表格数据唯一标识 | 文档内全局唯一     |
| `anchor`    | string | 否       | 表格数据锚点     | 省略时可回退为`id` |
| `label`     | string | 否       | 人类可读标签     | 普通字符串         |
| `meta`      | object | 否       | 附加元信息       | 当前不商定内部字段 |
| `tableType` | string | 是       | 表格模式         | `record`           |
| `columns`   | array  | 是       | 列定义数组       | 见 10.5.5.4        |
| `rows`      | array  | 是       | 行数据数组       | 见 10.5.5.5        |

##### 10.5.5.3 正式结构

```json
{
  "id": "table-financial-summary",
  "anchor": "table-financial-summary",
  "label": "Financial summary",
  "meta": {},
  "tableType": "record",
  "columns": [
    { "key": "year", "header": "Year" },
    { "key": "revenue", "header": "Revenue" }
  ],
  "rows": [
    { "year": "2024", "revenue": "12.3M" },
    { "year": "2025", "revenue": "13.8M" }
  ]
}
```

##### 10.5.5.4 `columns[]`

**定义**

* 类型：array
* 元素类型：对象
* 是否必须：必须

每个 `columns[]` 元素表示一列的定义。

**列字段表**


| 字段名   | 类型   | 是否必须 | 含义       | 说明                               |
| -------- | ------ | -------- | ---------- | ---------------------------------- |
| `key`    | string | 是       | 列稳定键名 | 在同一张表内唯一                   |
| `header` | string | 是       | 列标题文本 | 当前版本按纯文本处理，**允许重名** |

**规则**

* `columns[]` 的数组顺序就是表格列顺序
* `columns[].key` 在同一张表内必须唯一
* `columns[].header`  **允许重复** ，不要求唯一
* 渲染器应以 `columns[].key` 识别列，以 `columns[].header` 展示列标题
* 当前版本不细化：
* 列对齐方式
* 列宽
* 列类型
* 排序规则
* 合并单元格能力

##### 10.5.5.5 `rows[]`

**定义**

* 类型：array
* 元素类型：对象
* 是否必须：必须

`rows[]` 中每个对象表示一行数据。

**规则**

1. `rows[]` 中每个对象的键应来自 `columns[].key`
2. 缺失键允许存在，渲染器应按空值处理
3. 当前版本单元格值允许：

* `string`
* `number`
* `boolean`
* `null`

1. 当前版本不细化复杂单元格对象结构
2. 当前版本不细化合并单元格能力

##### 10.5.5.6 渲染器最低要求

渲染器至少应支持：

* 按 `columns[]` 顺序渲染表头
* 按 `columns[]` 顺序渲染每一行单元格
* 对缺失单元格按空值处理

渲染器最低行为要求：

* 应以 `columns[]` 作为列顺序唯一依据
* `rows[]` 中缺失的单元格不得导致整表失败
* 若 `rows[]` 中出现额外未声明列，渲染器可以忽略并记录日志
* 不应自行重排列顺序

#### 10.5.6 `grid` 模式

##### 10.5.6.1 定义

当 `tableType = "grid"` 时，表格采用网格布局模式。

此模式用于表达不规则表格、复杂表头、跨行跨列表格等。

##### 10.5.6.2 正式字段表


| 字段名        | 类型    | 是否必须 | 含义                                               | 值格式 / 说明      |
| ------------- | ------- | -------- | -------------------------------------------------- | ------------------ |
| `id`          | string  | 是       | 表格数据唯一标识                                   | 文档内全局唯一     |
| `anchor`      | string  | 否       | 表格数据锚点                                       | 省略时可回退为`id` |
| `label`       | string  | 否       | 人类可读标签                                       | 普通字符串         |
| `meta`        | object  | 否       | 附加元信息                                         | 当前不商定内部字段 |
| `tableType`   | string  | 是       | 表格模式                                           | `grid`             |
| `columnCount` | integer | 是       | 表格逻辑列数（不存在横跨多列的单元格时应有的列数） | 便于渲染器计算布局 |
| `rows`        | array   | 是       | 行数据数组                                         | 见 10.5.6.4        |
| `layout`      | object  | 否       | 表格布局提示                                       | 见 10.5.4.2        |

##### 10.5.6.3 正式结构

```json
{
  "id": "table-valuation-method",
  "anchor": "table-valuation-method",
  "label": "Valuation method",
  "meta": {},
  "tableType": "grid",
  "layout": {
    "columnSpecs": [
      { "width": { "mode": "weight", "value": 2 } },
      { "width": { "mode": "weight", "value": 3 } },
      { "width": { "mode": "weight", "value": 5 } }
    ]
  },
  "columnCount": 3,
  "rows": [
    {
      "cells": [
        { "text": "评估模块", "header": true, "align": "center", "verticalAlign": "middle" },
        { "text": "一级指标", "header": true, "align": "center", "verticalAlign": "middle" },
        { "text": "说明", "header": true, "align": "center", "verticalAlign": "middle" }
      ]
    },
    {
      "cells": [
        { "text": "技术维度", "rowSpan": 2, "verticalAlign": "middle" },
        { "text": "技术先进性" },
        { "text": "衡量技术是否领先" }
      ]
    },
    {
      "cells": [
        { "text": "技术稳定性" },
        { "text": "衡量技术成熟程度" }
      ]
    }
  ]
}
```

##### 10.5.6.4 `rows[]`

**定义**

* 类型：array
* 元素类型：对象
* 是否必须：必须

`rows[]` 中每个对象表示一行网格数据。

**行字段表**


| 字段名  | 类型  | 是否必须 | 含义             | 说明        |
| ------- | ----- | -------- | ---------------- | ----------- |
| `cells` | array | 是       | 当前行单元格数组 | 见 10.5.6.5 |

##### 10.5.6.5 `cells[]`

**定义**

* 类型：array
* 元素类型：对象
* 是否必须：必须

`cells[]` 中每个对象表示一个单元格。

**单元格字段表**


| 字段名          | 类型    | 是否必须 | 含义                                 | 值格式 / 说明                       |
| --------------- | ------- | -------- | ------------------------------------ | ----------------------------------- |
| `text`          | string  | 否       | 单元格纯文本内容                     | 与`blocks` 二选一                   |
| `blocks`        | array   | 否       | 单元格富内容块数组，当前为受限块数组 | 与`text` 二选一；见 10.5.6.6        |
| `header`        | boolean | 否       | 是否为表头单元格                     | 默认`false`                         |
| `colSpan`       | integer | 否       | 跨列数                               | 默认`1`                             |
| `rowSpan`       | integer | 否       | 跨行数                               | 默认`1`                             |
| `align`         | string  | 否       | 水平对齐方式                         | 当前建议值：`left`/`center`/`right` |
| `verticalAlign` | string  | 否       | 垂直对齐方式                         | 当前建议值：`top`/`middle`/`bottom` |
| `meta`          | object  | 否       | 单元格附加元信息                     | 当前不商定内部字段                  |

**规则**

1. `text` 与 `blocks` 至少应存在一个
2. 若 `text` 与 `blocks` 同时存在，渲染器应优先使用 `blocks`
3. `colSpan` 与 `rowSpan` 若未提供，默认按 `1` 处理
4. 每行单元格数量必须少于或等于 `columnCount`，因为可能存在跨列、跨行或不规则布局
5. 当前版本允许不同的行拥有不同数量的单元格
6. 当前版本不要求所有 grid 表都可无损回转为规则二维矩阵
7. 若 `cells[].blocks` 中出现当前版本未正式支持的块对象类型，渲染器可以忽略该对象并记录兼容日志，但不应导致整张表失败

##### 10.5.6.6 单元格 `blocks` 的受限块模型

当前版本中，`grid` 单元格的 `blocks` 不再限定为纯文本块数组，而是定义为**受限块数组**。

其数组顺序就是单元格内部阅读顺序。

当前版本正式支持的单元格块类型只有两种：

- `_type = "block"`
- `_type = "image"`

也就是说：

- 允许单元格内出现一个或多个段落
- 允许单元格内插入图片
- 允许段落与图片按顺序混排

当前版本中，以下块对象**仍不正式支持**出现在单元格 `blocks` 中：

- `chart`
- `table`
- `math_block`
- `callout`

**最小示例**

```json
{
  "blocks": [
    {
      "_type": "block",
      "style": "normal",
      "children": [
        { "_type": "span", "text": "系统架构图如下：", "marks": [] }
      ],
      "markDefs": []
    },
    {
      "_type": "image",
      "imageRef": "img-system-overview"
    }
  ]
}
```

**规则**

- `text` 与 `blocks` 二选一
- `blocks` 的数组元素顺序必须保留
- 单元格中的 `_type = "image"` 继续复用 14.9.2 的正式结构
- 单元格中的 `_type = "image"` 仍通过 `imageRef` 指向 `assets.images[]`
- 单元格中的 `_type = "block"` 继续复用正文文本块规则，可包含 `layout`
- 渲染器在单元格内渲染图片时，应优先保证图片不超出单元格可用宽度，并保持原始宽高比
- 若图片资源失效，渲染器可按 `alt` 或固定占位方式降级，但不应导致整张表格失败

### 10.6 `datasets.metrics`

#### 10.6.1 定义

* 类型：array
* 是否必须：必须

`datasets.metrics` 用于存放指标集 registry。

#### 10.6.2 当前版本说明

当前版本只定义：

* `datasets.metrics` 这个 registry 位置存在
* 其值类型为数组

当前版本**尚未商定**单个指标条目的正式字段合同。

因此：

* 生成器可以暂不输出指标条目
* 渲染器可以忽略 `metrics`
* 校验器只需检查其顶层值类型为数组

---

## 11. `bibliography`

### 11.1 字段定义

- 类型：数组
- 是否必须：必须

`bibliography[]` 存储的是参考文献条目本体。正文中如需引用参考文献，应通过行内 `citation_ref` 引用其 `id`。

### 11.2 与正文 `citation_ref` 的关系

两者职责不同：

`bibliography[]` 描述的是：

- 参考文献条目的身份
- 参考文献的题名、作者、年份、来源等元数据

正文中的 `citation_ref` 描述的是：

- 当前正文位置引用哪一条参考文献

例如：

```json
{
  "_key": "m1",
  "_type": "citation_ref",
  "targetId": "cite-fu-2026"
}
```

因此：

* `bibliography[]` 是**数据层**
* 正文中的 `citation_ref` 是**引用层**
* `citation_ref.targetId` 应引用 `bibliography[].id`

### 11.3 正式字段表


| 字段名        | 类型    | 是否必须 | 含义             | 值格式 / 说明                                      |
| ------------- | ------- | -------- | ---------------- | -------------------------------------------------- |
| `id`          | string  | 是       | 参考文献唯一标识 | 文档内全局唯一                                     |
| `displayText` | string  | 是       | 完整展示文本     | 拼接好的完整引用文本，渲染器可直接优先将其用于展示 |
| `anchor`      | string  | 否       | 文献锚点         | 省略时可回退为`id`                                 |
| `label`       | string  | 否       | 人类可读标签     | 普通字符串                                         |
| `meta`        | object  | 否       | 附加元信息       | 当前不商定内部字段                                 |
| `type`        | string  | 否       | 文献类型         | 见 11.4                                            |
| `title`       | string  | 否       | 文献标题         | 普通字符串                                         |
| `authors`     | array   | 否       | 作者列表         | 元素类型为 string                                  |
| `year`        | integer | 否       | 出版 / 发布年份  | 四位年份为宜                                       |
| `journal`     | string  | 否       | 期刊名称         | 适用于 article                                     |
| `publisher`   | string  | 否       | 出版社           | 适用于 book / report                               |
| `volume`      | string  | 否       | 卷号             | 普通字符串                                         |
| `issue`       | string  | 否       | 期号             | 普通字符串                                         |
| `pages`       | string  | 否       | 页码范围         | 如`12-18`                                          |
| `doi`         | string  | 否       | DOI              | 普通字符串                                         |
| `url`         | string  | 否       | 访问地址         | URL 字符串                                         |
| `accessedAt`  | string  | 否       | 访问时间         | 建议使用 RFC 3339 / ISO 8601                       |
| `edition`     | string  | 否       | 版本 / 版次      | 普通字符串                                         |
| `institution` | string  | 否       | 机构名称         | 适用于 report / dataset                            |
| `language`    | string  | 否       | 文献语言         | 建议使用 BCP 47 语言标记                           |

### 11.4 `type` 正式枚举

当前版本建议正式使用以下常见枚举：

* `article`
* `book`
* `report`
* `webpage`
* `dataset`
* `other`

说明：

* 渲染器不应强依赖 `type` 去决定是否能显示该条目
* `type` 主要用于：
* 文献列表样式选择
* 不同来源类型的格式化
* 筛选与导出

### 11.5 最小结构

```json
{
  "id": "cite-fu-2026",
  "displayText": "Fu, X., J.Zhang, C.Ai, and X. M.Fu. 2026. “Digitalisation of International Trade in Intellectual Properties: An Approach Based on the Utility Theory of Technology Value.” The World Economy1–15. https://doi.org/10.1111/twec.70072."
}
```

### 11.6 扩展结构示例

```json
{
  "id": "cite-fu-2026",
  "displayText": "Fu, X., J.Zhang, C.Ai, and X. M.Fu. 2026. “Digitalisation of International Trade in Intellectual Properties: An Approach Based on the Utility Theory of Technology Value.” The World Economy1–15. https://doi.org/10.1111/twec.70072.",
  "anchor": "cite-fu-2026",
  "label": "Fu et al., 2026",
  "meta": {},
  "type": "article",
  "title": "Digitalisation of International Trade in Intellectual Properties: An Approach Based on the Utility Theory of Technology Value",
  "authors": ["X Fu", "J Zhang"],
  "year": 2026,
  "journal": "The World Economy",
  "volume": "n/a",
  "issue": "n/a",
  "pages": "n/a",
  "doi": "10.1111/twec.70072",
  "language": "en"
}
```

### 11.7 正文中的引用方式

正文通过 `citation_ref` 引用 `bibliography[].id`。

例如：

```json
{
  "_type": "citation_ref",
  "targetId": "cite-fu-2026"
}
```

若具体实现仍采用 `markDefs` 风格承载，渲染时应将其解释为“行内参考文献引用”。

---

## 12. `footnotes`

### 12.1 字段定义

* 类型：数组
* 是否必须：必须

`footnotes[]` 存储的是脚注条目本体。正文中如需引用脚注，应通过 `footnote_ref` 引用其 `id`。

### 12.2 与正文 `footnote_ref` 的关系

两者职责不同：

`footnotes[]` 描述的是：

* 脚注条目的身份
* 脚注内容本体

正文中的 `footnote_ref` 描述的是：

* 当前正文位置引用哪一条脚注

例如：

```json
{
  "_key": "m1",
  "_type": "footnote_ref",
  "targetId": "fn-1"
}
```

因此：

* `footnotes[]` 是**数据层**
* 正文中的 `footnote_ref` 是**引用层**
* `footnote_ref.targetId` 应引用 `footnotes[].id`

### 12.3 正式字段表


| 字段名   | 类型   | 是否必须 | 含义           | 值格式 / 说明      |
| -------- | ------ | -------- | -------------- | ------------------ |
| `id`     | string | 是       | 脚注唯一标识   | 文档内全局唯一     |
| `anchor` | string | 否       | 脚注锚点       | 省略时可回退为`id` |
| `label`  | string | 否       | 人类可读标签   | 普通字符串         |
| `meta`   | object | 否       | 附加元信息     | 当前不商定内部字段 |
| `blocks` | array  | 是       | 脚注内容块数组 | 见 12.4            |

### 12.4 `blocks` 的解释

`footnotes[].blocks` 复用正文文本块规则的 **受限子集** 。文本块规则见14.7。

当前版本建议允许：

* 普通文本块
* 行内 marks
* 行内引用对象，例如：
* `citation_ref`
* `glossary_term`
* `xref`

当前版本不允许：

* 正式章节结构
* `subsection`
* 需要独立 registry 展示上下文的大块级正文对象

也就是说：

* `footnotes[].blocks` 可以承载“脚注内容”
* 不能承载“新的章节树”

### 12.5 最小结构

```json
{
  "id": "fn-1",
  "anchor": "fn-1",
  "label": "Footnote 1",
  "meta": {},
  "blocks": []
}
```

### 12.6 正文中的引用方式

正文通过 `footnote_ref` 引用 `footnotes[].id`。渲染器应能建立正文引用与脚注条目的对应关系。

例如：

```json
{
  "_key": "m1",
  "_type": "footnote_ref",
  "targetId": "fn-1"
}
```

### 12.7 渲染器最低要求

渲染器至少应支持：

* 根据 `footnote_ref.targetId` 解析到 `footnotes[].id`
* 建立正文与脚注内容之间的对应关系
* 将 `blocks` 渲染为脚注正文

最低行为要求：

1. 正文中可显示脚注编号、符号或其他约定标记
2. 文末、页脚或悬浮区都可以作为脚注展示区域
3. 若 `blocks` 为空，不应报致命错误
4. 若 `targetId` 无法解析，渲染器可以显示占位脚注并记录日志

---

## 13. `glossary`

### 13.1 字段定义

* 类型：数组
* 是否必须：必须

`glossary[]` 存储的是术语表条目本体。正文中如需引用术语，应通过 `glossary_term` 引用其 `id`。

### 13.2 与正文 `glossary_term` 的关系

两者职责不同：

`glossary[]` 描述的是：

* 术语条目的身份
* 术语名称、定义与别名

正文中的 `glossary_term` 描述的是：

* 当前正文位置引用哪一个术语条目

例如：

```json
{
  "_key": "m1",
  "_type": "glossary_term",
  "targetId": "term-dcf"
}
```

因此：

* `glossary[]` 是**数据层**
* 正文中的 `glossary_term` 是**引用层**
* `glossary_term.targetId` 应引用 `glossary[].id`

### 13.3 正式字段表


| 字段名       | 类型   | 是否必须 | 含义         | 值格式 / 说明                    |
| ------------ | ------ | -------- | ------------ | -------------------------------- |
| `id`         | string | 是       | 术语唯一标识 | 文档内全局唯一                   |
| `anchor`     | string | 否       | 术语锚点     | 省略时可回退为`id`               |
| `label`      | string | 否       | 人类可读标签 | 普通字符串                       |
| `meta`       | object | 否       | 附加元信息   | 当前不商定内部字段               |
| `term`       | string | 是       | 术语名称     | 普通字符串                       |
| `definition` | string | 是       | 术语定义     | 普通字符串                       |
| `aliases`    | array  | 否       | 术语别名列表 | 元素类型为 string                |
| `short`      | string | 否       | 简短展示名   | 兼容字段，不建议作为正式主要结构 |

### 13.4 最小结构

```json
{
  "id": "term-dcf",
  "anchor": "term-dcf",
  "label": "DCF",
  "meta": {},
  "term": "DCF",
  "definition": "Discounted Cash Flow",
  "aliases": []
}
```

### 13.5 正文中的引用方式

正文通过 `glossary_term` 引用 `glossary[].id`。

例如：

```json
{
  "_key": "m1",
  "_type": "glossary_term",
  "targetId": "term-dcf"
}
```

可以将其渲染为：

* 普通术语文字
* 悬浮解释
* 文末术语索引入口
* 跳转到术语表条目

---

## 14. `sections`

`sections` 是整份报告的主结构，也是渲染器最重要的读取对象。

### 14.1 `sections` 的职责

`sections[]` 表达的是正式章节树。它既可以承载：

- 封面、摘要、目录等前置章节
- 正文主章节
- 附录章节
- 封底等结尾章节

因此，封面、目录、附录并不需要额外顶层字段；在当前版本中，统一通过 `sections` 表达即可。

### 14.2 `sections` 顶层定义

- 类型：数组
- 是否必须：必须
- 元素类型：section 对象

规则：

1. `sections[]` 的数组顺序就是整份文档的章节阅读顺序
2. `sections[]` 中每个元素都必须是完整的 section 节点
3. 顶层 `sections[]` 一般承载一级章节，但不强制只能是 `level = 1`

### 14.3 section 最小结构

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

### 14.4 section 正式字段表


| 字段名      | 类型    | 是否必须 | 含义                          | 值格式 / 说明                                              |
| ----------- | ------- | -------- | ----------------------------- | ---------------------------------------------------------- |
| `id`        | string  | 是       | section 的全局唯一稳定标识    | 全文唯一，且应稳定                                         |
| `level`     | integer | 是       | section 的逻辑层级            | 当前建议使用正整数                                         |
| `title`     | string  | 是       | 章节标题                      | 当前版本按纯文本处理                                       |
| `numbering` | string  | 是       | 编号模式                      | 枚举值：`auto` 自动编号，`none` 无编号， `manual` 手动编号 |
| `anchor`    | string  | 否       | 章节锚点                      | 省略时可回退为`id`                                         |
| `body`      | array   | 是       | 当前章节内部的 body item 列表 | 见 14.5                                                    |

#### 14.4.1 `id`

`id` 是 section 的全局唯一稳定标识。必须满足：

* 全文唯一
* 稳定
* 不因展示编号变化而变化

#### 14.4.2 `level`

`level` 表示逻辑层级。当前版本建议值：

* `1`：一级章节
* `2`：二级章节
* `3`：三级章节
* `4`：四级章节

说明：

* `level` 表示逻辑层级，不直接决定字号、字体、缩进或分页方式
* 样式展示由渲染器模板决定

#### 14.4.3 `title`

`title` 为章节标题纯文本。

当前版本不在 `title` 中承载富文本 marks，也不用于表达展示编号。

#### 14.4.4 `numbering`

当前版本正式枚举只有：

* `"auto"`
* `"none"`
* `"manual"`

含义：

* `auto`：由渲染器自动编号
* `none`：不显示结构编号
* `manual`：预留给手工编号；当前版本只定义语义，不定义详细字段

渲染器最低要求：

* 必须支持 `auto`
* 必须支持 `none`
* 遇到 `manual` 时，若没有更细实现，至少不得崩溃；可以按无编号处理并记录兼容日志

#### 14.4.5 `anchor`

章节锚点。

省略时可回退为 `id`。

#### 14.4.6 `body`

`body` 是当前 section 内部的有序 body item 列表。

`body[]` 的数组顺序就是当前章节内部的阅读顺序。

---

### 14.5 body item 联合类型

当前版本正式定义两种 `body[]` 项：

* `content`
* `subsection`

#### 14.5.1 `content`

表示一组连续的正文块。

```json
{
  "itemType": "content",
  "blocks": []
}
```

字段表：


| 字段名     | 类型   | 是否必须 | 含义           | 说明              |
| ---------- | ------ | -------- | -------------- | ----------------- |
| `itemType` | string | 是       | body item 类型 | 固定为`"content"` |
| `blocks`   | array  | 是       | 连续正文块数组 | 见 14.7 与 14.8   |

约束：

* `blocks` 必须表示一组**阅读顺序连续的块**
* 不应把不连续的多段正文（比如两个段落之间间隔一个子章节）硬塞进同一个 `content`
* `blocks` 中的单个`blocks` 文本块代表一个**段落**，段落内不换行
* `blocks` 中两个`blocks` 文本块之间需要换行

#### 14.5.2 `subsection`

表示一个真正的子章节节点。

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

字段表：


| 字段名     | 类型   | 是否必须 | 含义           | 说明                    |
| ---------- | ------ | -------- | -------------- | ----------------------- |
| `itemType` | string | 是       | body item 类型 | 固定为`"subsection"`    |
| `section`  | object | 是       | 完整子章节节点 | 必须是完整 section 对象 |

---

### 14.6 章节树约束

1. 正式章节结构只能通过 `sections[]` 或 `body[].section` 表达。
2. 不得用普通文本块模拟正式章节层级。
3. 父子 section 的 `level` 必须自洽；直接子章节通常比父章节深一层。
4. `body[]` 的数组顺序就是阅读顺序，渲染器不得另行重排。
5. `content.blocks[]` 中不得用 `h1 / h2 / h3 / h4` 表达正式章节结构。

---

### 14.7 section 内部的文本块层

本节描述的是 `content.blocks[]` 中的 **文本块结构** ，基于 Portable Text 的原生能力。

#### 14.7.1 文本块最小结构

```json
{
  "_type": "block",
  "style": "normal",
  "children": [
    {
      "_type": "span",
      "text": "Example paragraph.",
      "marks": []
    }
  ],
  "markDefs": []
}
```

#### 14.7.2 文本块正式字段表


| 字段名     | 类型    | 是否必须 | 含义             | 值格式 / 说明                           |
| ---------- | ------- | -------- | ---------------- | --------------------------------------- |
| `_type`    | string  | 是       | 块类型           | 文本块固定为`"block"`，其他块类型见14.9 |
| `style`    | string  | 是       | 块样式           | 见 14.7.3                               |
| `children` | array   | 是       | 子节点数组       | 元素通常为`_type = "span"`              |
| `markDefs` | array   | 否       | 行内标注定义数组 | 见 14.7.6                               |
| `listItem` | string  | 否       | 列表项类型       | 当前建议值：`bullet`/`number`           |
| `level`    | integer | 否       | 列表层级         | 用于列表嵌套层级                        |
| `layout`   | object  | 否       | 块级布局提示     | 见 14.7.3；仅用于`_type="block"`        |

说明：

* `children[]` 表示该文本块内部的行内内容顺序
* `markDefs[]` 用于定义链接、引用、脚注、术语等可被 `marks` 引用的行内目标
* `listItem / level` 用于表达列表语义，不表达正式章节结构

#### 14.7.3 样式与布局

**渲染器至少应识别以下 `style`**：

* `normal`：普通段落
* `blockquote`：引用段落
* `caption`：通用说明文字
* `figure_caption`：图题注
* `table_caption`：表题注
* `equation_caption`：公式题注
* `smallprint`：小号说明文本
* `lead`：导语 / 强调性摘要段落
* `quote_source`：引文来源说明
* `subheading`：正文中的非正式小标题

**渲染器需要识别  `layout` 块级布局提示**

具体字段请参考 8.5 小节

适用范围：

- 仅适用于 `_type = "block"`

不适用范围：

- 不适用于 `span`
- 不适用于 `marks`
- 不适用于 `markDefs`

继承优先级：

1. 当前 `block.layout`
2. `theme.blockStyleDefaults[block.style].layout`
3. 渲染器默认样式

#### 14.7.4 `h1 / h2 / h3 / h4` 的规则

* `h1 / h2 / h3 / h4` 不得用于表达正式章节结构
* 若输入中出现这些值，渲染器应视为兼容性输入
* 推荐回退策略：按 `subheading` 处理并记录兼容日志

#### 14.7.5 `children[]` 与 `_type = "span"`

当前版本中，普通文本块的 `children[]` 主要由 `_type = "span"` 的子节点组成。

`span` 最小结构：

```json
{
  "_type": "span",
  "text": "Example text",
  "marks": []
}
```

字段表：


| 字段名  | 类型   | 是否必须 | 含义                             | 说明                           |
| ------- | ------ | -------- | -------------------------------- | ------------------------------ |
| `_type` | string | 是       | 行内文本节点类型                 | 文本类型固定为`"span"`         |
| `text`  | string | 是       | 文本内容                         | 普通字符串                     |
| `marks` | array  | 否       | 应用于当前 span 的 mark 键名数组 | 用于关联 markDefs 或简单 marks |

说明：

* 当前版本中，普通文本内容应通过 `_type = "span"` 承载
* `marks[]` 仅描述该 span 应用哪些 marks，不直接携带目标详情
* 目标型 mark 的具体内容应定义在 `markDefs[]` 中

#### 14.7.6 `markDefs[]`

`markDefs[]` 是当前文本块内可被 `children[].marks[]` 引用的行内标注定义数组。

示例：

```json
{
  "_type": "block",
  "style": "normal",
  "children": [
    {
      "_type": "span",
      "text": "See reference",
      "marks": ["m1"]
    }
  ],
  "markDefs": [
    {
      "_key": "m1",
      "_type": "citation_ref",
      "targetId": "cite-fu-2026"
    }
  ]
}
```

规则：

* `markDefs[]` 中每个对象应具备 `_key`
* `children[].marks[]` 通过 `_key` 引用对应 `markDefs[]` 项
* 简单 marks 与目标型 mark 可同时出现在 `marks[]` 中

#### 14.7.7 当前版本正式支持的文本修饰 marks

当前版本要求渲染器至少支持：

* `strong`：加粗
* `em`：斜体
* `underline`：下划线
* `code`：行内代码块

说明：

* 这些 marks 可直接出现在 `children[].marks[]` 中
* 若某个 mark 未实现，渲染器应尽量保留文本内容，不得丢字

---

### 14.8 section 内部的行内引用 / 注解层

当前版本要求渲染器至少识别以下行内引用 / 注解类型：

* `link`：超链接
* `xref`：交叉引用
* `citation_ref`：文献引用
* `footnote_ref`：脚注引用
* `glossary_term`：术语引用
* `inline_math`：数学表达式引用

这些类型通常通过 `markDefs[]` 承载，并由 `children[].marks[]` 引用。

#### 14.8.1 `link`

最小结构：

```json
{
  "_key": "m1",
  "_type": "link",
  "href": "https://example.com"
}
```

字段表：


| 字段名  | 类型   | 是否必须 | 含义           |
| ------- | ------ | -------- | -------------- |
| `_key`  | string | 是       | mark 定义键    |
| `_type` | string | 是       | 固定为`"link"` |
| `href`  | string | 是       | 外部链接地址   |

#### 14.8.2 `xref`

最小结构：

```json
{
  "_key": "m2",
  "_type": "xref",
  "targetId": "sec-1-1",
  "targetType": "section"
}
```

字段表：


| 字段名       | 类型   | 是否必须 | 含义           |
| ------------ | ------ | -------- | -------------- |
| `_key`       | string | 是       | mark 定义键    |
| `_type`      | string | 是       | 固定为`"xref"` |
| `targetId`   | string | 是       | 引用目标 ID    |
| `targetType` | string | 否       | 引用目标类型   |

#### 14.8.3 `citation_ref`

最小结构：

```json
{
  "_key": "m3",
  "_type": "citation_ref",
  "targetId": "cite-fu-2026"
}
```

#### 14.8.4 `footnote_ref`

最小结构：

```json
{
  "_key": "m4",
  "_type": "footnote_ref",
  "targetId": "fn-1"
}
```

#### 14.8.5 `glossary_term`

最小结构：

```json
{
  "_key": "m5",
  "_type": "glossary_term",
  "targetId": "term-dcf"
}
```

#### 14.8.6 `inline_math`

最小结构：

```json
{
  "_key": "m6",
  "_type": "inline_math",
  "latex": "E = mc^2"
}
```

#### 14.8.7 行内对象未知类型的回退策略

若遇到未知行内对象类型：

* 应保留其宿主文本内容
* 不应因此中断整段渲染
* 可以忽略其交互能力并记录日志

---

### 14.9 section 内部的块级对象层

本节描述的是正文实例层，即这些对象如何出现在 `content.blocks[]` 中。

#### 14.9.1 当前版本正式支持的块级对象类型

当前版本正式定义以下块级对象：

* `image`
* `chart`
* `table`
* `math_block`
* `callout`

以下名字当前仅为预留，不构成正式字段合同：

* `code_block`
* `quote_box`
* `page_break`
* `cover`
* `abstract_block`
* `toc_placeholder`
* `references_block`
* `appendix_marker`
* `section_divider`
* `timeline`
* `comparison_card`
* `kpi_grid`
* `risk_matrix`
* `author_note`

#### 14.9.2 `image`：正文中的图片实例层

最小结构：

```json
{
  "_type": "image",
  "id": "fig-system-overview",
  "anchor": "fig-system-overview",
  "imageRef": "img-system-overview"
}
```

字段表：


| 字段名     | 类型   | 是否必须 | 含义             |
| ---------- | ------ | -------- | ---------------- |
| `_type`    | string | 是       | 固定为`"image"`  |
| `id`       | string | 否       | 当前图片实例 ID  |
| `anchor`   | string | 否       | 当前图片实例锚点 |
| `imageRef` | string | 是       | 图片资源 ID      |

解释：

* `imageRef` 必须解析到 `assets.images[]`
* `assets.images[]` 是资源层
* `_type = "image"` 是正文实例层
* 二者不能混用
* 当前版本中，`_type = "image"` 除了可出现在正文 `content.blocks[]` 中，也可出现在 `datasets.tables[].grid.rows[].cells[].blocks[]` 中。两种情况下都复用同一正式结构：
  * 都属于图片实例层
  * 都通过 `imageRef` 指向 `assets.images[]`
  * 不新增单独的“table_cell_image”类型

#### 14.9.3 `chart`：正文中的图表实例层

最小结构：

```json
{
  "_type": "chart",
  "id": "fig-market-share",
  "anchor": "fig-market-share",
  "chartRef": "chart-market-share"
}
```

字段表：


| 字段名     | 类型   | 是否必须 | 含义             |
| ---------- | ------ | -------- | ---------------- |
| `_type`    | string | 是       | 固定为`"chart"`  |
| `id`       | string | 否       | 当前图表实例 ID  |
| `anchor`   | string | 否       | 当前图表实例锚点 |
| `chartRef` | string | 是       | 图表数据 ID      |

解释：

* `chartRef` 必须解析到 `datasets.charts[]`
* `datasets.charts[]` 是数据层
* `_type = "chart"` 是正文实例层

#### 14.9.4 `table`：正文中的表格实例层

最小结构：

```json
{
  "_type": "table",
  "id": "tbl-financial-summary",
  "anchor": "tbl-financial-summary",
  "tableRef": "table-financial-summary"
}
```

字段表：


| 字段名     | 类型   | 是否必须 | 含义             |
| ---------- | ------ | -------- | ---------------- |
| `_type`    | string | 是       | 固定为`"table"`  |
| `id`       | string | 否       | 当前表格实例 ID  |
| `anchor`   | string | 否       | 当前表格实例锚点 |
| `tableRef` | string | 是       | 表格数据 ID      |

解释：

* `tableRef` 必须解析到 `datasets.tables[]`
* `datasets.tables[]` 是数据层
* `_type = "table"` 是正文实例层

#### 14.9.5 `math_block`

最小结构：

```json
{
  "_type": "math_block",
  "id": "eq-dcf-core",
  "anchor": "eq-dcf-core",
  "latex": "V = \\sum_{t=1}^{n} \\frac{CF_t}{(1+r)^t}"
}
```

字段表：


| 字段名   | 类型   | 是否必须 | 含义                 |
| -------- | ------ | -------- | -------------------- |
| `_type`  | string | 是       | 固定为`"math_block"` |
| `id`     | string | 否       | 当前公式实例 ID      |
| `anchor` | string | 否       | 当前公式实例锚点     |
| `latex`  | string | 是       | LaTeX 公式字符串     |

#### 14.9.6 `callout`

最小结构：

```json
{
  "_type": "callout",
  "id": "callout-key-finding-1",
  "anchor": "callout-key-finding-1",
  "blocks": []
}
```

字段表：


| 字段名   | 类型   | 是否必须 | 含义                  |
| -------- | ------ | -------- | --------------------- |
| `_type`  | string | 是       | 固定为`"callout"`     |
| `id`     | string | 否       | 当前 callout 实例 ID  |
| `anchor` | string | 否       | 当前 callout 实例锚点 |
| `blocks` | array  | 是       | callout 内容块数组    |

规则：

* `callout.blocks` 复用正文文本层规则的受限子集
* `callout.blocks` 中不允许出现正式章节结构

#### 14.9.7 caption 的推荐实现

当前版本推荐 caption 继续优先作为相邻文本块，而不是硬塞进对象字段：

* `image` 后可紧跟 `figure_caption`
* `chart` 后可紧跟 `figure_caption`
* `table` 后可紧跟 `table_caption`
* `math_block` 后可紧跟 `equation_caption`

渲染器应该按顺序渲染，不应假定 caption 必定内嵌在对象自身字段中。

---

## 15. 统一 ID / Anchor / Display Number / 引用解析模型

### 15.1 三层概念分离

当前版本推荐统一分离三层概念：

1. 系统 ID：内部稳定标识，如 `sec-market-overview`
2. anchor：跳转 / 书签使用的锚点标识
3. display number：读者看到的编号，如 `1.2`、`Figure 3`

说明：

* `id` 用于程序内部识别与引用
* `anchor` 用于跳转、书签、超链接定位
* `display number` 用于展示，不应反向充当系统主键

### 15.2 `id` 的统一要求

任何可能被引用的对象，其 `id` 都应满足：

* 全文唯一
* 稳定
* 与展示编号解耦
* 不因文档模板变更而变化

### 15.3 `anchor` 的统一要求

`anchor` 是跳转 / 书签使用的锚点标识。

规则：

* `anchor` 可以显式提供
* 若未显式提供，渲染器或生成器可按规则回退为 `id`
* `anchor` 应尽量稳定
* `anchor` 不应依赖当前展示编号

### 15.4 `display number`

`display number` 指读者最终看到的展示编号，例如：

* `1`
* `1.2`
* `Figure 3`
* `表 2`
* `式 (4)`

规则：

* `display number` 属于展示层概念
* 当前版本不要求在 JSON 中显式存储
* 渲染器可以根据：
* 对象类型
* 所在章节
* `numbering`
* 模板规则

  动态计算展示编号
* 当前版本不强制规定“按全文连续”还是“按章节重置”

### 15.5 推荐命名前缀

推荐前缀：

* `sec-*`
* `appendix-*`
* `fig-*`
* `tbl-*`
* `chart-*`
* `eq-*`
* `cite-*`
* `fn-*`
* `term-*`
* `img-*`

说明：

* 这是推荐规范，不是强制校验规则
* 其主要作用是增强可读性、可调试性和跨实现一致性

### 15.6 编号类别与对象类型分离

当前版本建议区分“对象类型”和“编号类别”：

* `image` 与 `chart` 可以同属 `figure` 编号类别
* `table` 属于 `table` 编号类别
* `math_block` 属于 `equation` 编号类别

说明：

* 对象类型决定数据结构与解析方式
* 编号类别决定展示编号归属方式
* 二者不应混为一谈

### 15.7 可解析目标的最低要求

任何可能被引用的对象，至少应具备：

* `id`
* `anchor`（显式或可推导）
* 可推出的目标类型
* 可定位来源（顶层 registry 或章节正文中的位置）

当前版本中，常见可解析目标包括：

* `section`
* `image` / `chart` / `table` / `math_block`
* `bibliography`
* `footnote`
* `glossary`
* `asset`

### 15.8 `xref.targetType` 建议枚举

当前版本建议 `xref.targetType` 使用以下枚举：

* `section`
* `figure`
* `table`
* `equation`
* `bibliography`
* `footnote`
* `glossary`
* `asset`

说明：

* `targetType` 用于帮助渲染器决定展示文案、编号类别、跳转策略
* `targetType` 当前为建议字段，不是绝对必填字段
* 若渲染器遇到未知 `targetType`，应至少尝试按通用锚点解析，而不是直接报废整段

### 15.9 引用解析最低要求

渲染器至少应具备以下解析能力：

1. 根据 `targetId` 找到对应对象
2. 若对象有 `anchor`，可建立跳转关系
3. 若对象属于可编号类别，可生成展示编号或展示占位文案
4. 若目标无法解析，应降级显示并记录日志，而不应导致整段或整篇失败

---

## 16. 回退与兼容策略

### 16.1 未知字段

- 应忽略未知字段
- 不应导致整份文档失败

### 16.2 未知枚举值

- 应记录兼容日志
- 尽量采用最接近的安全回退

例如：

- 未知 `block.style` → 回退为 `normal`
- 未知 `numbering` → 回退为 `none`
- 未知 `imageSource.kind` → 视为该图片资源无效，并记录兼容日志

### 16.3 缺失可选字段

- 不应导致致命失败
- 应使用默认值或降级渲染

### 16.4 缺失必须字段

- 校验器应报错
- 渲染器可以终止当前节点渲染，但不应无提示静默吞掉错误

---

## 17. 校验要求

校验器当前版本至少应检查：

1. 顶层必须字段存在
2. `schemaVersion` 合法
3. 所有全局 `id` 唯一
4. `section.level` 合法且父子层级自洽
5. `section.numbering` 属于正式枚举集合
6. `body.itemType` 属于正式枚举集合
7. `image.imageRef` / `chart.chartRef` / `table.tableRef` 可解析
8. `math_block.latex` 非空
9. `callout.blocks` 为数组
10. `assets.images` 必须满足 `imageSource` 存在且合法
11. `imageSource.kind` 合法
12. `embedded` 模式下 `encoding = base64`
13. `record` 模式校验 `columns + rows`
14. `grid` 模式校验 `rows[].cells[]`
15. `columnCount`、`colSpan`、`rowSpan` 的基本合法性
16. `datasets.charts` 中 `pie.slices` 结构合法
17. `citation_ref.targetId` 可解析到 `bibliography[].id`
18. `footnote_ref.targetId` 可解析到 `footnotes[].id`
19. `glossary_term.targetId` 可解析到 `glossary[].id`
20. `theme.blockStyleDefaults` 的结构
21. `block.layout` 的字段与枚举
22. `table.layout.columnSpecs`
23. `width.mode = auto|weight`
24. `weight.value > 0`
25. `grid.cells[].blocks` 仅允许 `_type="block"` / `_type="image"`

---

## 18. 渲染器最低实现要求

为保证 v1.1 能真正落地，渲染器至少应实现以下能力：

1. 识别顶层结构并遍历 `sections`
2. 识别 `content` 与 `subsection` 两类 body item
3. 支持正文块的基本渲染顺序
4. 支持 `block.style` 的正式枚举集合
5. 支持常见文本 marks
6. 支持 `xref / citation_ref / footnote_ref / glossary_term / link / inline_math`
7. 支持 `image / chart / table / math_block / callout`
8. 支持 `assets.images` 的 `url` 与 `embedded` 两种来源模式
9. 支持 `datasets.tables`
10. 支持 `datasets.charts` 中 `pie`
11. 支持 bibliography / footnotes / glossary 的基础解析
12. 遇到未知预留字段时，采用兼容性忽略策略，而不是中断整份文档渲染
13. 支持解析 `theme.blockStyleDefaults`
14. 支持解析 `_type="block"` 的 `layout`
15. 支持 `block.layout > theme default > renderer default`
16. 支持 `table.layout.columnSpecs[]`
17. 支持 `width.mode = auto|weight`
18. 支持单元格内 `_type="image"`
19. 单元格图片默认适配可用宽度并保持宽高比

---

## 19. 非目标

以下内容明确不在当前协议范围内：

- PDF 渲染字号
- 字体
- 颜色
- 页边距
- 页眉页脚
- 背景图铺设方式
- 分页算法
- 复杂公式排版实现
- 视觉主题细节

---

## 20. 示例

```json
{
  "schemaVersion": "report.v1.1",
  "meta": {
    "title": "OVA Portable Text v1.1 Minimal Example",
    "language": "zh",
    "documentType": "valuationReport"
  },
  "theme": {
    "blockStyleDefaults": {
      "normal": {
        "layout": {
          "textAlign": "justify",
          "firstLineIndent": { "unit": "em", "value": 2 },
          "spaceAfter": { "unit": "pt", "value": 6 }
        }
      },
      "table_caption": {
        "layout": {
          "textAlign": "center",
          "spaceBefore": { "unit": "pt", "value": 4 },
          "spaceAfter": { "unit": "pt", "value": 6 }
        }
      }
    }
  },
  "assets": {
    "images": [
      {
        "id": "img-system-overview",
        "anchor": "img-system-overview",
        "label": "System overview",
        "meta": {},
        "alt": "系统示意图",
        "mimeType": "image/png",
        "imageSource": {
          "kind": "url",
          "url": "https://example.com/system-overview.png"
        }
      }
    ],
    "logos": [],
    "backgrounds": [],
    "icons": [],
    "attachments": []
  },
  "datasets": {
    "charts": [],
    "tables": [
      {
        "id": "table-demo-grid",
        "anchor": "table-demo-grid",
        "label": "Grid table demo",
        "meta": {},
        "tableType": "grid",
        "layout": {
          "columnSpecs": [
            { "width": { "mode": "weight", "value": 3 } },
            { "width": { "mode": "weight", "value": 7 } }
          ]
        },
        "columnCount": 2,
        "rows": [
          {
            "cells": [
              {
                "text": "项目",
                "header": true,
                "align": "center",
                "verticalAlign": "middle"
              },
              {
                "text": "说明",
                "header": true,
                "align": "center",
                "verticalAlign": "middle"
              }
            ]
          },
          {
            "cells": [
              {
                "text": "系统图",
                "verticalAlign": "middle"
              },
              {
                "blocks": [
                  {
                    "_type": "block",
                    "style": "normal",
                    "children": [
                      {
                        "_type": "span",
                        "text": "下方展示单元格中的图片实例：",
                        "marks": []
                      }
                    ],
                    "markDefs": []
                  },
                  {
                    "_type": "image",
                    "imageRef": "img-system-overview"
                  }
                ],
                "verticalAlign": "top"
              }
            ]
          }
        ]
      }
    ],
    "metrics": []
  },
  "bibliography": [],
  "footnotes": [],
  "glossary": [],
  "sections": [
    {
      "id": "sec-demo",
      "level": 1,
      "title": "示例章节",
      "numbering": "auto",
      "anchor": "sec-demo",
      "body": [
        {
          "itemType": "content",
          "blocks": [
            {
              "_type": "block",
              "style": "normal",
              "layout": {
                "textAlign": "center"
              },
              "children": [
                {
                  "_type": "span",
                  "text": "这是一个用于展示 v1.1 新能力的最小示例。",
                  "marks": []
                }
              ],
              "markDefs": []
            },
            {
              "_type": "block",
              "style": "normal",
              "children": [
                {
                  "_type": "span",
                  "text": "本段未显式声明 layout，因此应继承 theme.blockStyleDefaults.normal 中的默认布局提示。",
                  "marks": []
                }
              ],
              "markDefs": []
            },
            {
              "_type": "table",
              "id": "tbl-demo-1",
              "anchor": "tbl-demo-1",
              "tableRef": "table-demo-grid"
            },
            {
              "_type": "block",
              "style": "table_caption",
              "children": [
                {
                  "_type": "span",
                  "text": "表 1. v1.1 grid 表格、列宽权重与单元格图片示例。",
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

## v1.1 更新说明（相对于 v1.0）

### 1. 版本号升级

- 顶层 `schemaVersion` 从 `report.v1.0` 升级为 `report.v1.1`。
- 渲染器应按版本号分发解析逻辑，并显式支持 `report.v1.1`。

### 2. `theme` 从占位对象升级为最小稳定合同

在 v1.0 中，`theme` 仅为主题占位对象，不定义稳定字段合同。v1.1 正式新增：

- `theme.blockStyleDefaults`

其作用是：

- 为各类 `block.style` 提供默认布局提示
- 为渲染器提供模板默认规则的协议入口

当前典型用法包括：

- `normal` 默认两端对齐
- `normal` 默认首行缩进
- `figure_caption` / `table_caption` 默认居中

### 3. 新增块级文本 `layout`

v1.1 正式为 `_type = "block"` 的文本块新增 `layout` 字段，用于表达**块级布局提示**，而不是语义样式角色。

当前正式支持的字段包括：

- `textAlign`
- `firstLineIndent`
- `spaceBefore`
- `spaceAfter`

当前正式支持的 `textAlign` 枚举包括：

- `left`
- `center`
- `right`
- `justify`

当前正式支持的长度单位包括：

- `em`
- `pt`

说明：

- `style` 继续表示语义角色
- `layout` 表示布局提示
- `layout` 不适用于 `span`
- `layout` 不适用于 `marks`
- `layout` 不适用于 `markDefs`

### 4. 明确默认布局与局部覆盖的优先级

v1.1 明确了块级文本布局的优先级：

1. 当前 `block.layout`
2. `theme.blockStyleDefaults[block.style].layout`
3. 渲染器自身模板默认值

这意味着：

- `theme` 可定义某类段落的默认布局
- 单个段落可通过自身 `layout` 做局部 override

### 5. 表格新增表级布局能力

v1.1 为 `datasets.tables[]` 正式新增：

- `layout`

当前版本中，`datasets.tables[].layout` 主要用于表达**表格列宽分配提示**。

### 6. 新增 `columnSpecs` 列宽模型

v1.1 正式新增：

- `datasets.tables[].layout.columnSpecs[]`

每列通过：

- `width.mode`
- `width.value`

表达列宽分配提示。

当前正式支持的宽度模式包括：

- `auto`
- `weight`

规则：

- `mode = "auto"` 时，不应出现 `value`
- `mode = "weight"` 时，`value` 必须为正数
- `weight` 是相对权重，不是百分比
- 不要求所有权重之和为 `100`
- 渲染器应在可用表格宽度内按权重分配剩余空间

### 7. 明确当前版本不引入表格百分比高度与单元格固定高度

v1.1 明确当前版本**不正式支持**：

- 单元格级宽度百分比
- 行高百分比
- 单元格固定高度

当前建议：

- 行高由内容与渲染器共同决定
- 表格宽度优先通过列级相对分配实现

### 8. `grid` 单元格 `blocks` 从文本块数组升级为受限块数组

在 v1.0 中，`grid` 单元格的 `blocks` 被定义为文本块数组。v1.1 将其升级为**受限块数组**。

当前正式支持的单元格块类型只有两种：

- `_type = "block"`
- `_type = "image"`

这意味着单元格中现在可以：

- 放一个或多个段落
- 放图片
- 让段落与图片按顺序混排

### 9. 明确单元格图片继续复用正文图片实例模型

v1.1 明确：

- 单元格中的图片继续使用 `_type = "image"`
- 继续通过 `imageRef` 指向 `assets.images[]`
- 不新增平行的“table_cell_image”类型

这保持了：

- 正文图片实例层
- 表格单元格图片实例层
- 资源层 `assets.images[]`

三者之间的一致引用模型

### 10. 明确单元格 `blocks` 的受限范围

v1.1 当前仍不正式支持以下块对象出现在单元格 `blocks` 中：

- `chart`
- `table`
- `math_block`
- `callout`

也就是说，v1.1 对单元格内容扩展采取的是**最小增量策略**，先支持段落和图片，不一次性开放全部块级对象。

### 11. 新增 v1.1 实现约束

v1.1 新增了几条明确的实现边界：

- `layout` 仅对 `_type = "block"` 生效
- `columnSpecs[].width.mode = "weight"` 表示相对权重，而不是百分比
- 当前版本不引入 cell 级百分比宽度
- 当前版本不引入 row / cell 高度百分比
- 单元格图片默认应适配单元格可用宽度并保持宽高比

### 12. 对渲染器升级的影响

从 v1.0 升级到 v1.1，渲染器至少应增加以下能力：

1. 解析 `theme.blockStyleDefaults`
2. 解析 `_type = "block"` 的 `layout`
3. 应用 `block.layout > theme default > renderer default` 的优先级
4. 解析 `datasets.tables[].layout.columnSpecs[]`
5. 支持 `width.mode = auto|weight`
6. 支持 `grid.cells[].blocks[]` 中的 `_type="image"`
7. 在单元格内渲染图片时控制为不超出单元格可用宽度并保持宽高比
8. 对未知或未支持的新字段继续采用兼容性忽略策略，而不是中断整份文档渲染

### 13. 向后兼容性说明

v1.1 继续保持以下原则：

- 未知字段应忽略
- 未知枚举值应记录兼容日志
- 缺失可选字段应采用默认值或降级策略
- 不应因单个节点无法解析而直接导致整份文档崩溃

v1.1 是在 v1.0 基础上的**增量扩展版本**，不是推翻式重构版本。

---
