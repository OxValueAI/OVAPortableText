# OVA Portable Text v1.0 正式协议

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
4. 最后看第 15～18 章，理解统一引用模型、回退策略、校验要求与非目标。

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

# 4. Portable Text 的原生能力

## 4.1 本节目的

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

## 4.2 Portable Text 是什么

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

## 4.3 Portable Text 原生的最基本形态

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

## 4.4 Portable Text 原生文本块：`block`

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

### 在本协议中的使用方式

本协议继续使用 `block` 作为正文富文本的基本单位。

## 4.5 `style`：文本块的语义样式角色

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

### 在本协议中的使用方式

特别需要注意的是：

- Portable Text 原生可用 `h1 / h2 / h3` 表达标题语义
- **本协议不使用 `h1 / h2 / h3` 表达章节层级**，本协议中的正式章节结构由顶层 `sections[]` 和 `subsection.section` 表达
- 本协议中，`style` 仍然表示正文的“文本块的语义角色”，但具体支持哪些语义、如何渲染，以本协议后文定义为准。

渲染器应理解：

- `style` 表示语义，不直接等于最终视觉
- 字号、上下间距多少、是否换页等等，最终均由渲染器实现决定
- 对于本协议**未列入正式支持范围的** `style`，应按回退规则处理，而不是自行推断为正式章节层级

## 4.6 `span`：行内文本单位

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

### 在本协议中的使用方式

本协议沿用 `span` 作为标准行内文本单位类型。
所有加粗、斜体、下划线、链接、引用、术语标记等，均附着于 `span` 或 `span` 所引用的标记定义上。

## 4.7 `marks`：行内简单样式标记

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

### 在本协议中的使用方式

本协议继续使用 `marks` 表达简单行内样式，但仅按本协议允许的 decorator 集合实现。

对于 `marks` 中出现的本协议未正式支持的行内样式：

- 先进入 `markDefs` 机制执行相关逻辑，详情见4.8小节
- 若无法解析，可忽略并不展现其视觉效果

## 4.8 `markDefs`：带数据的行内标记定义

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

### 在本协议中的使用方式

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

## 4.9 列表：`listItem` 与 `level`

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

### 在本协议中的使用方式

本协议允许在正文文本块中使用 Portable Text 原生列表能力。但渲染器开发者应明确：

- 列表本质上仍是一组顺序排列的 `block`
- Portable Text 原生不提供严格块嵌套树
- 因此，本协议中的正式章节层级不能依赖 `listItem + level` 表达

## 4.10 行内对象（Inline Object）

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

### 在本协议中的使用方式

本协议保留使用行内自定义对象的能力，但是否正式支持某种行内对象类型，以本协议正文行内对象定义为准。

## 4.11 块级对象（Block Object）

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

### 在本协议中的使用方式

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

## 4.12 Portable Text 原生负责什么、不负责什么

### 4.12.1 Portable Text 原生适合负责的内容

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

### 4.12.2 Portable Text 原生不负责的内容

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

## 4.13 本协议为何要在 Portable Text 之上再定义 Report Profile

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
  "schemaVersion": "report.v1.0",
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

当前版本固定值：

### 6.3 渲染器要求

- 必须识别 `report.v1.0`
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

| 字段名              | 类型   | 是否必须 | 含义                                 | 值格式 / 枚举                                                                                     |
| ------------------- | ------ | -------: | ------------------------------------ | ------------------------------------------------------------------------------------------------- |
| `title`           | string |       否 | 文档主标题                           | 普通字符串                                                                                        |
| `subtitle`        | string |       否 | 文档副标题                           | 普通字符串                                                                                        |
| `language`        | string |       否 | 文档正文语言                         | 枚举值：`zh` 中文，`en` 英文                                                                |
| `author`          | string |       否 | 文档作者或生成责任方                 | 普通字符串                                                                                        |
| `date`            | string |       否 | 文档日期                             | `YYYY-MM-DD`                                                                                    |
| `reportNumber`    | string |       否 | 报告编号、文档编号或业务编号         | 普通字符串                                                                                        |
| `documentType`    | string |       否 | 文档类型                             | 枚举值：`valuationReport` 估值报告                                                              |
| `confidentiality` | string |       否 | 保密级别                             | 枚举值：`public` 公开， `user` 所属用户， `internal` 公司内部、`confidential` 机密        |
| `generatedBy`     | string |       否 | 生成系统、生成模块或生成器名称       | 普通字符串                                                                                        |
| `generatedAt`     | string |       否 | 文档生成时间                         | RFC 3339 / ISO 8601 时间格式字符串，如 `2026-03-24T12:34:56Z`                                   |
| `clientId`        | string |       否 | 客户内部 ID 或业务客户标识           | 普通字符串                                                                                        |
| `projectId`       | string |       否 | 项目标识、任务标识或报告关联对象 ID  | 普通字符串                                                                                        |
| `reportType`      | string |       否 | 业务层报告类型                       | 枚举值：`startupCompany` 初创公司，`innovationTeam` 创新团队，`patent` 专利，`loan` 债权 |
| `clientName`      | string |       否 | 客户名称、委托方名称或展示对象名称   | 普通字符串                                                                                        |
| `locale`          | string |       否 | 渲染区域设置                         | 枚举值：`zh` 中文，`en` 英文                                                                |
| `source`          | string |       否 | 文档来源、数据来源说明或上游系统标识 | 普通字符串                                                                                        |

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

### 7.5 与 py 包当前实现的对齐关系

当前 `OVAPortableText` 已对本节列出的字段提供正式模型字段支持。但当前 py 包尚未对以下内容做强校验：

- `language` / `locale` 的标准格式校验
- `date` 的日期格式校验
- `generatedAt` 的时间格式校验
- `documentType` / `confidentiality` / `reportType` 的枚举值校验

因此，当前版本的协议应将这些字段视为：

- 字段名已正式冻结
- 值类型已正式定义
- 具体枚举暂未冻结

---

## 8. `theme`

### 8.1 字段定义

- 类型：对象
- 是否必须：必须

### 8.2 作用

`theme` 是主题占位对象，用于承载未来可能的主题配置。

### 8.3 当前版本状态

当前版本仅保留 `theme` 位置，不定义稳定字段合同。渲染器可以：

- 忽略其未知字段
- 或按内部实现自行消费已知字段

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

| 字段名          | 类型  | 是否必须 | 含义                |
| --------------- | ----- | -------- | ------------------- |
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

| 字段名     | 类型   | 是否必须 | 含义             | 说明                                   |
| ---------- | ------ | -------- | ---------------- | -------------------------------------- |
| `id`     | string | 是       | 全局唯一稳定标识 | 同一文档内不得重复                     |
| `anchor` | string | 否       | 资源锚点标识     | 若此字段被省略，可直接采用 `id` 的值 |
| `label`  | string | 否       | 人类可读标签     | 仅供展示、调试或辅助识别               |
| `meta`   | object | 否       | 附加元信息       | 当前版本不冻结内部字段                 |

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

##### `assets.images[]`

描述的是：

* 这张图片资源的身份
* 这张图片的来源
* 这张图片的 MIME 类型
* 这张图片的尺寸、校验值、替代文本等

##### 正文中的 `_type = "image"` 块

描述的是：

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

| 字段名          | 类型    | 是否必须 | 含义             | 值格式 / 枚举                                       |
| --------------- | ------- | -------- | ---------------- | --------------------------------------------------- |
| `id`          | string  | 是       | 图片资源唯一标识 | 文档内全局唯一                                      |
| `anchor`      | string  | 否       | 图片资源锚点     | 省略时可回退为 `id`                               |
| `label`       | string  | 否       | 人类可读标签     | 普通字符串                                          |
| `meta`        | object  | 否       | 附加元信息       | 当前不冻结内部字段                                  |
| `alt`         | string  | 应该     | 图片替代文本     | 用于无障碍与图片渲染失败时的降级替换展示            |
| `mimeType`    | string  | 应该     | 图片 MIME 类型   | 如 `image/png`、`image/jpeg`、`image/svg+xml` |
| `checksum`    | string  | 否       | 图片内容校验值   | 建议格式：`sha256:<hex>`                          |
| `width`       | integer | 否       | 原始像素宽度     | 正整数                                              |
| `height`      | integer | 否       | 原始像素高度     | 正整数                                              |
| `imageSource` | object  | 是       | 图片来源描述对象 | 见 9.5.5                                            |

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

| 字段名       | 类型   | 是否必须 | 含义             | 值格式 / 枚举                                             |
| ------------ | ------ | -------- | ---------------- | --------------------------------------------------------- |
| `kind`     | string | 是       | 图片来源类型     | 枚举值：`url`，`embedded`                             |
| `url`      | string | 条件必须 | 图片地址         | 当 `kind = "url"`时必须存在                             |
| `encoding` | string | 条件必须 | 内嵌数据编码方式 | 当 `kind = "embedded"`时必须存在；当前仅允许 `base64` |
| `data`     | string | 条件必须 | 内嵌图片数据     | 当 `kind = "embedded"`时必须存在                        |

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

当前版本尚未冻结单个附件条目的正式字段合同。

因此：

* 生成器可以暂不输出附件条目
* 渲染器可以忽略 `attachments`
* 校验器只需检查其顶层值类型为数组

### 9.10 与 py 包当前实现的对齐关系

当前 `OVAPortableText` 已正式支持：

* `assets.images`
* `imageSource.kind = "url"`
* `imageSource.kind = "embedded"`
* 通过 helper 创建 URL 型与 embedded 型图片资源

当前 `OVAPortableText` 尚未对以下内容做进一步强约束：

* `mimeType` 的完整 MIME 合法性校验
* `checksum` 格式的强校验
* `width / height` 是否为正整数的更严格约束
* `logos / backgrounds / icons / attachments` 的独立专用 helper 体系

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

| 字段名      | 类型  | 是否必须 | 含义              |
| ----------- | ----- | -------- | ----------------- |
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

| 字段名        | 类型   | 是否必须 | 含义             | 值格式 / 说明         |
| ------------- | ------ | -------- | ---------------- | --------------------- |
| `id`        | string | 是       | 图表数据唯一标识 | 文档内全局唯一        |
| `anchor`    | string | 否       | 图表数据锚点     | 省略时可回退为 `id` |
| `label`     | string | 否       | 人类可读标签     | 普通字符串            |
| `meta`      | object | 否       | 附加元信息       | 当前不冻结内部字段    |
| `chartType` | string | 是       | 图表类型         | 枚举值：`pie` 饼图  |
| `valueUnit` | string | 否       | 数值单位         | 普通字符串            |

`valueUnit` 当前版本不强制固定枚举，通常可以用它决定：

* 数值展示方式
* tooltip / 图例单位
* 百分比、计数、金额等文案后缀

#### 10.4.5 `pie` 图

##### 10.4.5.1 `pie` 图正式字段表

| 字段名        | 类型   | 是否必须 | 含义             | 值格式 / 说明         |
| ------------- | ------ | -------- | ---------------- | --------------------- |
| `id`        | string | 是       | 图表数据唯一标识 | 文档内全局唯一        |
| `anchor`    | string | 否       | 图表数据锚点     | 省略时可回退为 `id` |
| `label`     | string | 否       | 人类可读标签     | 普通字符串            |
| `meta`      | object | 否       | 附加元信息       | 当前不冻结内部字段    |
| `chartType` | string | 是       | 图表类型         | `pie`               |
| `valueUnit` | string | 否       | 数值单位         | 普通字符串            |
| `slices`    | array  | 是       | 饼图扇区数组     | 饼图扇区内容          |

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

| 字段名          | 类型   | 是否必须 | 含义         | 值格式 / 说明                      |
| --------------- | ------ | -------- | ------------ | ---------------------------------- |
| `key`         | string | 应该     | 扇区稳定标识 | 用于程序内部映射、排序、日志定位   |
| `label`       | object | 是       | 扇区名称     | 推荐语言对象，见 10.4.8            |
| `value`       | number | 是       | 扇区数值     | 当前版本建议为 number              |
| `description` | object | 否       | 扇区说明     | 推荐语言对象，见 10.4.9            |
| `colorHint`   | string | 否       | 颜色提示     | 当前版本不冻结格式，渲染器可以忽略 |

###### `pie.slices[].label`

推荐结构：

```json
{
  "zh": "技术",
  "en": "Technology"
}
```

规则：

* `label` 当前版本建议采用语言对象，而不是单一字符串
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

* `description` 当前版本建议采用语言对象
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

| 字段名        | 类型   | 是否必须 | 含义             | 值格式 / 说明                     |
| ------------- | ------ | -------- | ---------------- | --------------------------------- |
| `id`        | string | 是       | 表格数据唯一标识 | 文档内全局唯一                    |
| `anchor`    | string | 否       | 表格数据锚点     | 省略时可回退为 `id`             |
| `label`     | string | 否       | 人类可读标签     | 普通字符串                        |
| `meta`      | object | 否       | 附加元信息       | 当前不冻结内部字段                |
| `tableType` | string | 是       | 表格模式         | 枚举值：`"record"` ，`"grid"` |
| `rows`      | array  | 是       | 行数据数组       | 具体结构取决于 `tableType`      |

##### 10.5.4.2 caption 与 table 的关系

当前版本延续统一原则：

* 表题注优先使用相邻正文文本块，例如 `table_caption`
* 不强制在 `datasets.tables[]` 条目中存 caption
* 不强制在正文 `_type = "table"` 实例中存 caption

推荐相邻模式：

<pre class="overflow-visible! px-0!" data-start="2292" data-end="2323"><div class="relative w-full mt-4 mb-1"><div class=""><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-token-bg-elevated-secondary corner-superellipse/1.1 overflow-clip rounded-3xl lxnfua_clipPathFallback"><div class="pointer-events-none absolute end-1.5 top-1 z-2 md:end-2 md:top-1"></div><div class="pe-11 pt-3"><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼk ͼy"><div class="cm-scroller"><div class="cm-content q9tKkq_readonly"><span>table</span><br/><span>table_caption</span></div></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></pre>

#### 10.5.5 `record` 模式

##### 10.5.5.1 定义

当 `tableType = "record"` 时，表格采用规则结构化模式。

此时表格条目除通用字段外，还应包含：

* `columns`

##### 10.5.5.2 正式字段表

| 字段名        | 类型   | 是否必须 | 含义             | 值格式 / 说明         |
| ------------- | ------ | -------- | ---------------- | --------------------- |
| `id`        | string | 是       | 表格数据唯一标识 | 文档内全局唯一        |
| `anchor`    | string | 否       | 表格数据锚点     | 省略时可回退为 `id` |
| `label`     | string | 否       | 人类可读标签     | 普通字符串            |
| `meta`      | object | 否       | 附加元信息       | 当前不冻结内部字段    |
| `tableType` | string | 是       | 表格模式         | `record`            |
| `columns`   | array  | 是       | 列定义数组       | 见 10.5.5.4           |
| `rows`      | array  | 是       | 行数据数组       | 见 10.5.5.5           |

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

| 字段名     | 类型   | 是否必须 | 含义       | 说明                                     |
| ---------- | ------ | -------- | ---------- | ---------------------------------------- |
| `key`    | string | 是       | 列稳定键名 | 在同一张表内唯一                         |
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

| 字段名          | 类型    | 是否必须 | 含义                               | 值格式 / 说明         |
| --------------- | ------- | -------- | ---------------------------------- | --------------------- |
| `id`          | string  | 是       | 表格数据唯一标识                   | 文档内全局唯一        |
| `anchor`      | string  | 否       | 表格数据锚点                       | 省略时可回退为 `id` |
| `label`       | string  | 否       | 人类可读标签                       | 普通字符串            |
| `meta`        | object  | 否       | 附加元信息                         | 当前不冻结内部字段    |
| `tableType`   | string  | 是       | 表格模式                           | `grid`              |
| `columnCount` | integer | 是       | 表格逻辑列数（所有行中最大的列数） | 便于渲染器计算布局    |
| `rows`        | array   | 是       | 行数据数组                         | 见 10.5.6.4           |

##### 10.5.6.3 正式结构

```json
{
  "id": "table-valuation-method",
  "anchor": "table-valuation-method",
  "label": "Valuation method",
  "meta": {},
  "tableType": "grid",
  "columnCount": 3,
  "rows": [
    {
      "cells": [
        { "text": "评估模块", "header": true },
        { "text": "一级指标", "header": true },
        { "text": "说明", "header": true }
      ]
    },
    {
      "cells": [
        { "text": "技术维度", "rowSpan": 2 },
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

| 字段名    | 类型  | 是否必须 | 含义             | 说明        |
| --------- | ----- | -------- | ---------------- | ----------- |
| `cells` | array | 是       | 当前行单元格数组 | 见 10.5.6.5 |

##### 10.5.6.5 `cells[]`

**定义**

* 类型：array
* 元素类型：对象
* 是否必须：必须

`cells[]` 中每个对象表示一个单元格。

**单元格字段表**

| 字段名            | 类型    | 是否必须 | 含义                                        | 值格式 / 说明                             |
| ----------------- | ------- | -------- | ------------------------------------------- | ----------------------------------------- |
| `text`          | string  | 否       | 单元格纯文本内容                            | 与 `blocks` 二选一                      |
| `blocks`        | array   | 否       | 单元格富文本内容，Portable Text blocks 数组 | 与 `text` 二选一                        |
| `header`        | boolean | 否       | 是否为表头单元格                            | 默认 `false`                            |
| `colSpan`       | integer | 否       | 跨列数                                      | 默认 `1`                                |
| `rowSpan`       | integer | 否       | 跨行数                                      | 默认 `1`                                |
| `align`         | string  | 否       | 水平对齐方式                                | 当前建议值：`left`/`center`/`right` |
| `verticalAlign` | string  | 否       | 垂直对齐方式                                | 当前建议值：`top`/`middle`/`bottom` |
| `meta`          | object  | 否       | 单元格附加元信息                            | 当前不冻结内部字段                        |

**规则**

1. `text` 与 `blocks` 至少应存在一个
2. 若 `text` 与 `blocks` 同时存在，渲染器应优先使用 `blocks`
3. `colSpan` 与 `rowSpan` 若未提供，默认按 `1` 处理
4. 每行单元格数量必须少于或等于 `columnCount`，因为可能存在跨列、跨行或不规则布局
5. 当前版本允许不同的行拥有不同数量的单元格
6. 当前版本不要求所有 grid 表都可无损回转为规则二维矩阵

### 10.6 `datasets.metrics`

#### 10.6.1 定义

* 类型：array
* 是否必须：必须

`datasets.metrics` 用于存放指标集 registry。

#### 10.6.2 当前版本说明

当前版本只定义：

* `datasets.metrics` 这个 registry 位置存在
* 其值类型为数组

当前版本**尚未冻结**单个指标条目的正式字段合同。

因此：

* 生成器可以暂不输出指标条目
* 渲染器可以忽略 `metrics`
* 校验器只需检查其顶层值类型为数组


---


## 11. `bibliography`

### 11.1 字段定义

- 类型：数组
- 是否必须：必须

### 11.2 作用

`bibliography[]` 存储的是参考文献条目本体。正文中如需引用参考文献，应通过行内 `citation_ref` 引用其 `id`。

### 11.3 最小结构

```json
{
  "id": "cite-fu-2026",
  "anchor": "cite-fu-2026",
  "label": "Fu et al., 2026",
  "meta": {},
  "type": "article",
  "title": "Patent valuation under technical utility theory",
  "authors": ["Fu"],
  "year": 2026
}
```

### 11.4 `type` 建议枚举

当前版本建议使用以下常见枚举：

- `article`
- `book`
- `report`
- `webpage`
- `dataset`
- `other`

### 11.5 正文中的引用方式

正文通过 `citation_ref` 引用 `bibliography[].id`。例如：

```json
{
  "_type": "citation_ref",
  "targetId": "cite-fu-2026"
}
```

若具体实现仍采用 `markDefs` 风格承载，渲染器应将其解释为“行内参考文献引用”。

---

## 12. `footnotes`

### 12.1 字段定义

- 类型：数组
- 是否必须：必须

### 12.2 作用

`footnotes[]` 存储的是脚注条目本体。正文中如需引用脚注，应通过 `footnote_ref` 引用其 `id`。

### 12.3 最小结构

```json
{
  "id": "fn-1",
  "anchor": "fn-1",
  "label": "Footnote 1",
  "meta": {},
  "blocks": []
}
```

### 12.4 `blocks` 的解释

`footnotes[].blocks` 复用正文文本层规则的受限子集。它可以包含普通文本块与行内 marks，但不允许出现正式章节结构。

### 12.5 正文中的引用方式

正文通过 `footnote_ref` 引用 `footnotes[].id`。渲染器应能建立正文引用与脚注条目的对应关系。

---

## 13. `glossary`

### 13.1 字段定义

- 类型：数组
- 是否必须：必须

### 13.2 作用

`glossary[]` 存储的是术语表条目本体。正文中如需引用术语，应通过 `glossary_term` 引用其 `id`。

### 13.3 最小结构

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

### 13.4 正文中的引用方式

正文通过 `glossary_term` 引用 `glossary[].id`。渲染器可以将其渲染为：

- 普通术语文字
- 悬浮解释
- 文末术语索引入口

当前版本不强制规定其具体交互形态。

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

### 14.2 section 最小结构

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

### 14.3 section 字段说明

#### `id`（必须，字符串）

section 的全局唯一稳定标识。必须：

- 全文唯一
- 稳定
- 不因展示编号变化而变化

#### `level`（必须，整数）

逻辑层级。当前版本建议值：

- `1`：一级章节
- `2`：二级章节
- `3`：三级章节
- `4`：四级章节

`level` 表示逻辑层级，不直接决定字号。

#### `title`（必须，字符串）

章节标题纯文本。

#### `numbering`（必须，枚举字符串）

当前版本正式枚举只有：

- `"auto"`
- `"none"`
- `"manual"`

含义：

- `auto`：由系统自动编号
- `none`：不显示结构编号
- `manual`：预留给手工编号；当前版本只定义语义，不定义详细字段

渲染器最低要求：

- 必须支持 `auto`
- 必须支持 `none`
- 遇到 `manual` 时，若没有更细实现，至少不得崩溃；可以按无编号处理并记录兼容日志

#### `anchor`（可选，字符串）

章节锚点。省略时可回退为 `id`。

#### `body`（必须，数组）

当前 section 内部的有序 body item 列表。

### 14.4 body item 联合类型

当前版本正式定义两种 `body[]` 项：

#### 14.4.1 `content`

表示一组连续的正文块。

```json
{
  "itemType": "content",
  "blocks": []
}
```

字段：

- `itemType`：必须为 `"content"`
- `blocks`：Portable Text 风格块数组

约束：

- `blocks` 必须表示一组阅读顺序连续的块
- 不应把被子章节打断的多段正文硬塞进同一个 `content`

#### 14.4.2 `subsection`

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

字段：

- `itemType`：必须为 `"subsection"`
- `section`：必须为完整的 section 节点

### 14.5 章节树约束

1. 正式章节结构只能通过 `sections[]` 或 `body[].section` 表达。
2. 不得用普通文本块模拟正式章节层级。
3. 父子 section 的 `level` 必须自洽；直接子章节通常比父章节深一层。
4. `body[]` 的数组顺序就是阅读顺序，渲染器不得另行重排。
5. `content.blocks[]` 中不得用 `h1/h2/h3/h4` 表达正式章节结构。

### 14.6 section 内部的文本层规则

#### 14.6.1 当前版本正式支持的 `block.style` 枚举

渲染器至少应识别以下 `style`：

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

解释建议：

- `normal`：普通段落
- `blockquote`：引用段落
- `caption`：通用说明文字
- `figure_caption`：图题注
- `table_caption`：表题注
- `equation_caption`：公式题注
- `smallprint`：小号说明文本
- `lead`：导语 / 强调性摘要段落
- `quote_source`：引文来源说明
- `subheading`：正文中的非正式小标题

#### 14.6.2 `h1 / h2 / h3 / h4` 的规则

- `h1 / h2 / h3 / h4` 不得用于表达正式章节结构
- 若输入中出现这些值，渲染器应视为兼容性输入
- 推荐回退策略：按 `subheading` 处理并记录兼容日志

#### 14.6.3 当前版本建议支持的文本修饰 marks

当前版本建议渲染器至少支持：

- `strong`
- `em`
- `underline`
- `code`

若某个 mark 未实现，渲染器应尽量保留文本内容，不得丢字。

#### 14.6.4 当前版本正式支持的行内引用 / 注解类型

当前版本要求渲染器至少识别：

- `link`
- `xref`
- `citation_ref`
- `footnote_ref`
- `glossary_term`
- `inline_math`

其中：

- `link`：外部链接
- `xref`：交叉引用 section / figure / table / equation 等
- `citation_ref`：引用 bibliography 条目
- `footnote_ref`：引用 footnotes 条目
- `glossary_term`：引用 glossary 条目
- `inline_math`：行内公式

#### 14.6.5 行内对象未知类型的回退策略

若渲染器遇到未知行内对象类型：

- 应保留其宿主文本内容
- 不应因此中断整段渲染
- 可以忽略其交互能力并记录日志

### 14.7 section 内部的块级对象层

本节描述的是正文实例层，即这些对象如何出现在 `content.blocks[]` 中。

#### 14.7.1 当前版本正式支持的块级对象类型

当前版本正式定义以下块级对象：

- `image`
- `chart`
- `table`
- `math_block`
- `callout`

以下名字当前仅为预留，不构成正式字段合同：

- `code_block`
- `quote_box`
- `page_break`
- `cover`
- `abstract_block`
- `toc_placeholder`
- `references_block`
- `appendix_marker`
- `section_divider`
- `timeline`
- `comparison_card`
- `kpi_grid`
- `risk_matrix`
- `author_note`

#### 14.7.2 `image`：正文中的图片实例层

最小结构：

```json
{
  "_type": "image",
  "id": "fig-system-overview",
  "anchor": "fig-system-overview",
  "imageRef": "img-system-overview"
}
```

解释：

- `id`：正文中的这一次图片实例 ID
- `imageRef`：它所引用的图片资源 ID
- `imageRef` 必须解析到 `assets.images[]`

因此：

- `assets.images[]` 是资源层
- `_type = "image"` 是正文实例层
- 二者不能混用

#### 14.7.3 `chart`：正文中的图表实例层

最小结构：

```json
{
  "_type": "chart",
  "id": "fig-market-share",
  "anchor": "fig-market-share",
  "chartRef": "chart-market-share"
}
```

解释：

- `chartRef` 必须解析到 `datasets.charts[]`
- `datasets.charts[]` 是数据层
- `_type = "chart"` 是正文实例层

#### 14.7.4 `table`：正文中的表格实例层

最小结构：

```json
{
  "_type": "table",
  "id": "tbl-financial-summary",
  "anchor": "tbl-financial-summary",
  "tableRef": "table-financial-summary"
}
```

解释：

- `tableRef` 必须解析到 `datasets.tables[]`
- `datasets.tables[]` 是数据层
- `_type = "table"` 是正文实例层

#### 14.7.5 `math_block`

最小结构：

```json
{
  "_type": "math_block",
  "id": "eq-dcf-core",
  "anchor": "eq-dcf-core",
  "latex": "V = \\sum_{t=1}^{n} \\frac{CF_t}{(1+r)^t}"
}
```

#### 14.7.6 `callout`

最小结构：

```json
{
  "_type": "callout",
  "id": "callout-key-finding-1",
  "anchor": "callout-key-finding-1",
  "blocks": []
}
```

规则：

- `callout.blocks` 复用正文文本层规则的受限子集
- `callout.blocks` 中不允许出现正式章节结构

#### 14.7.7 caption 的推荐实现

当前版本推荐 caption 继续优先作为相邻文本块，而不是硬塞进对象字段：

- `image` 后可紧跟 `figure_caption`
- `chart` 后可紧跟 `figure_caption`
- `table` 后可紧跟 `table_caption`
- `math_block` 后可紧跟 `equation_caption`

渲染器应该按顺序渲染，不应假定 caption 必定内嵌在对象自身字段中。

---

## 15. 统一 ID / Anchor / Display Number / 引用解析模型

### 15.1 三层概念分离

推荐统一分离三层概念：

1. 系统 ID：内部稳定标识，如 `sec-market-overview`
2. anchor：跳转 / 书签使用的锚点标识
3. display number：读者看到的编号，如 `1.2`、`Figure 3`

### 15.2 推荐命名前缀

推荐前缀：

- `sec-*`
- `appendix-*`
- `fig-*`
- `tbl-*`
- `chart-*`
- `eq-*`
- `cite-*`
- `fn-*`
- `term-*`
- `img-*`

### 15.3 编号类别与对象类型分离

- `image` 与 `chart` 可以同属 `figure` 编号类别
- `table` 属于 `table` 编号类别
- `math_block` 属于 `equation` 编号类别

当前版本只要求保留编号空间，不强制规定“按全文连续”还是“按章节重置”。

### 15.4 可解析目标的最低要求

任何可能被引用的对象，至少应具备：

- `id`
- `anchor`（显式或可推导）
- 可推出的目标类型
- 可定位来源（顶层 registry 或章节正文中的位置）

### 15.5 `xref.targetType` 建议枚举

当前版本建议 `xref.targetType` 使用以下枚举：

- `section`
- `figure`
- `table`
- `equation`
- `bibliography`
- `footnote`
- `glossary`
- `asset`

若渲染器遇到未知 `targetType`，应至少尝试按通用锚点解析，而不是直接报废整段。

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
- 未知 `imageSource.kind` → 若存在 `src`，尝试回退解析 `src`

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
10. `assets.images` 至少满足 `imageSource` 或 `src` 其一可用
11. `imageSource.kind` 合法
12. `embedded` 模式下 `encoding = base64`
13. `datasets.tables.columns` / `rows` 结构合法
14. `datasets.charts` 中 `pie.slices` 结构合法
15. bibliography / footnotes / glossary 的 `id` 可解析

---

## 18. 渲染器最低实现要求

为保证 v1.0 能真正落地，渲染器至少应实现以下能力：

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

---

## 19. 非目标

以下内容明确不在当前协议范围内：

- Java PDF 渲染字号
- 字体
- 颜色
- 页边距
- 页眉页脚
- 背景图铺设方式
- 分页算法
- 复杂公式排版实现
- 视觉主题细节

---

## 20. 最小示例

```json
{
  "schemaVersion": "report.v1",
  "meta": {
    "title": "Patent Valuation Report",
    "language": "en"
  },
  "theme": {},
  "assets": {
    "images": [
      {
        "id": "img-cover",
        "anchor": "img-cover",
        "label": "Cover image",
        "meta": {},
        "alt": "Cover image",
        "mimeType": "image/png",
        "src": "https://example.com/cover.png",
        "imageSource": {
          "kind": "url",
          "url": "https://example.com/cover.png"
        }
      }
    ],
    "logos": [],
    "backgrounds": [],
    "icons": [],
    "attachments": []
  },
  "datasets": {
    "charts": [
      {
        "id": "chart-area-share",
        "anchor": "chart-area-share",
        "label": "Area share",
        "meta": {},
        "chartType": "pie",
        "valueUnit": "percent",
        "slices": [
          { "name": "Technology", "value": 60 },
          { "name": "Finance", "value": 40 }
        ]
      }
    ],
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
            },
            {
              "_type": "chart",
              "id": "fig-1",
              "anchor": "fig-1",
              "chartRef": "chart-area-share"
            },
            {
              "_type": "block",
              "style": "figure_caption",
              "children": [
                {
                  "_type": "span",
                  "text": "Figure 1. Area share pie chart.",
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

## 21. 协议状态总结

基于当前已确认方向，本协议已经能够完整表达：

- 正式章节树
- section 内连续正文流
- 正文与子章节交错顺序
- 文本层样式与行内引用
- 图片、表格、饼图、公式、callout 等块级对象
- 图片资源的 URL / 内嵌双来源模式
- bibliography / footnotes / glossary 的基础引用体系

本版本的核心定位是：

> 先把“渲染器可以明确开发”的底层结构合同写清楚，而不是一次性把所有未来扩展字段写满。

**
