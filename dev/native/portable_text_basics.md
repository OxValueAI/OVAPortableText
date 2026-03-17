# Portable Text 原生能力与报告扩展对照

## 1. 理解 Portable Text

**Portable Text 是一种用 JSON 表达富文本内容的规范。**

它的目标不是直接决定“最终长什么样”，而是先把内容结构化存下来。
同一份内容数据，后续可以被不同渲染器转成 HTML、PDF、Markdown 等不同输出格式。

对你的场景来说，它最重要的意义是：

- Python 负责生成内容 JSON
- Java 负责按统一规则渲染 PDF
- 内容和展示解耦
- 同一套 Java 渲染器可复用在多份报告上

---

## 2. 用 Portable Text 作为底座，再定义 report profile

可以把它理解成：

- **Portable Text** = 通用富文本 JSON 骨架
- **Report Profile** = 你们项目自己的报告协议规则

也就是：

Portable Text 先解决这些通用问题：

- 段落怎么存
- 标题怎么存
- 加粗、斜体、链接怎么存
- 图片、表格、自定义块怎么混排

然后自定义的 report profile 再补充：

- 什么叫一级章节、二级章节
- 公式块怎么存
- 引文、脚注、参考文献怎么存
- 图表块怎么存
- 封面、摘要卡片、背景图怎么存
- Java 渲染器看到每种块后该怎么画到 PDF 上

所以它不是“直接拿 Portable Text 原样用到底”，而是：

**在 Portable Text 的基础富文本模型上，增加你们自己的业务规则。**

---

## 3. Portable Text 的最核心整体结构

## 3.1 最外层是数组

Portable Text 最基本的形态是一个数组：

```json
[
  { ...第1个内容块... },
  { ...第2个内容块... },
  { ...第3个内容块... }
]
```

你可以先这样理解：

- 一个数组元素 = 一个内容块
- 内容块可以是正文段落、标题、引用块
- 也可以是图片、代码块、表格、自定义对象块

---

## 3.2 最常见的块类型是 `block`

`block` 是最标准的文本块，常用来表示：

- 段落
- 标题
- 引用块
- 列表项

一个典型 `block` 一般会有这些字段：

- `_type`: 通常是 `"block"`
- `style`: 块的样式角色，例如 `normal`、`h1`
- `children`: 块内的行内内容
- `markDefs`: 行内复杂标记的数据定义区

最简单段落示例：

```json
[
  {
    "_type": "block",
    "style": "normal",
    "children": [
      {
        "_type": "span",
        "text": "这是一段普通正文。",
        "marks": []
      }
    ],
    "markDefs": []
  }
]
```

---

## 4. Portable Text 原生能力详解

## 4.1 块级样式：`style`

`style` 用来表达这个文本块的“角色”，常见有：

- `normal`：普通正文
- `h1`：一级标题
- `h2`：二级标题
- `h3`：三级标题
- `blockquote`：引用块

注意：

`style` 更像语义角色，不直接等于最终视觉样式。例如 `h1` 只表示“这是一级标题”，至于：

- 字号多大
- 是否加粗
- 上下间距多少
- 是否另起一页

这些都由渲染器决定，不是 Portable Text 本身决定。

### 示例：一级标题

```json
[
  {
    "_type": "block",
    "style": "h1",
    "children": [
      {
        "_type": "span",
        "text": "1. Executive Summary",
        "marks": []
      }
    ],
    "markDefs": []
  }
]
```

### 示例：引用块

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

---

## 4.2 行内文本：`span`

`span` 是块里的标准行内文本单位。

一个段落通常不是一整串 text，而是被拆成多个 `span`，这样你才能只给其中某几个词加粗、加链接、加注释。

### 示例：一段带局部强调的正文

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

这里“重要”单独拆成一个 `span`，以便挂上 `strong` 标记。

---

## 4.3 行内简单格式：`marks`（Decorator）

Portable Text 原生支持给 `span` 加简单样式标记，例如：

- `strong`：加粗
- `em`：斜体
- `underline`：下划线

也可以多个标记叠加。

### 示例：加粗与斜体

```json
[
  {
    "_type": "block",
    "style": "normal",
    "children": [
      { "_type": "span", "text": "这是", "marks": [] },
      { "_type": "span", "text": "加粗", "marks": ["strong"] },
      { "_type": "span", "text": "和", "marks": [] },
      { "_type": "span", "text": "斜体", "marks": ["em"] },
      { "_type": "span", "text": "文本。", "marks": [] }
    ],
    "markDefs": []
  }
]
```

### 示例：多重叠加

```json
{
  "_type": "span",
  "text": "同时加粗斜体",
  "marks": ["strong", "em"]
}
```

---

## 4.4 行内复杂标记：`markDefs`（Annotation）

如果只是加粗斜体，`marks` 里放字符串就够了。但如果要表达的是“带额外数据的标记”，例如：

- 链接
- 批注
- 外部引用
- 术语解释
- 引用锚点

就需要用 `markDefs`。

Portable Text 的机制是：

- `span.marks` 里放一个 key
- 这个 key 指向 `markDefs` 中对应的对象
- 对象里再存具体数据

### 示例：链接

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

### 示例：批注

```json
[
  {
    "_type": "block",
    "style": "normal",
    "children": [
      { "_type": "span", "text": "该结论需要复核", "marks": ["comment-1"] }
    ],
    "markDefs": [
      {
        "_key": "comment-1",
        "_type": "comment",
        "text": "建议补充数据来源说明",
        "author": "reviewer_a"
      }
    ]
  }
]
```

你可以这样理解：

- `marks` 负责“这段文字挂了什么标记”
- `markDefs` 负责“这个标记的详细数据是什么”

---

## 4.5 列表：`listItem` + `level`

Portable Text 原生支持列表，但它不是 HTML 那种真正的嵌套 DOM。它的做法是给每个列表项 block 加上：

- `listItem`
- `level`

常见写法：

- `listItem: "bullet"`：无序列表
- `listItem: "number"`：有序列表
- `level: 1 / 2 / 3`：层级深度

### 示例：无序列表

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
    "level": 1,
    "children": [
      { "_type": "span", "text": "第二点", "marks": [] }
    ],
    "markDefs": []
  }
]
```

### 示例：有序列表

```json
[
  {
    "_type": "block",
    "style": "normal",
    "listItem": "number",
    "level": 1,
    "children": [
      { "_type": "span", "text": "步骤一", "marks": [] }
    ],
    "markDefs": []
  },
  {
    "_type": "block",
    "style": "normal",
    "listItem": "number",
    "level": 1,
    "children": [
      { "_type": "span", "text": "步骤二", "marks": [] }
    ],
    "markDefs": []
  }
]
```

### 示例：二级嵌套列表示意

```json
[
  {
    "_type": "block",
    "style": "normal",
    "listItem": "bullet",
    "level": 1,
    "children": [{ "_type": "span", "text": "一级项", "marks": [] }],
    "markDefs": []
  },
  {
    "_type": "block",
    "style": "normal",
    "listItem": "bullet",
    "level": 2,
    "children": [{ "_type": "span", "text": "二级项", "marks": [] }],
    "markDefs": []
  }
]
```

### 这里有一个很关键的限制

Portable Text **没有真正的 block nesting 机制**。
也就是说，列表更像“很多个带列表属性的 block 依次排列”，而不是天然一棵严格嵌套的树。

这个点对你后面做严格章节树、复杂容器布局时很重要。

---

## 4.6 行内对象：Inline Object

Portable Text 的 `children` 不只能放 `span`，还可以放“行内对象”。

这表示你可以在一行文字中间插入非纯文本对象，例如：

- 行内 emoji
- 行内标签
- 行内公式 token
- 行内引用 token
- 行内状态徽章

### 示例：行内 badge

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

这里 `badge` 不是官方内置固定类型，但它属于 Portable Text 原生允许的“行内对象能力”。

---

## 4.7 块级对象：Block Object

Portable Text 根数组里除了 `block` 这种文本块，还可以直接放任意块级对象。

这使它可以混排：

- 图片
- 代码块
- 表格
- 视频
- 嵌入对象
- 图表块
- 自定义业务块

### 示例：图片块

```json
[
  {
    "_type": "image",
    "src": "https://example.com/cover.png",
    "alt": "封面图",
    "caption": "Figure 1. Overview"
  }
]
```

### 示例：代码块

```json
[
  {
    "_type": "code",
    "language": "python",
    "code": "print('hello world')"
  }
]
```

### 示例：表格块

```json
[
  {
    "_type": "table",
    "columns": ["Year", "Revenue"],
    "rows": [
      ["2023", "12.3M"],
      ["2024", "15.8M"]
    ]
  }
]
```

Portable Text 原生并没有把这些字段结构全部写死，但它原生允许你在根数组里放这种自定义块级对象。

---

## 5. 一个综合示例

下面是一段综合示例，包含：

- 标题
- 正文
- 加粗
- 链接
- 列表
- 图片块

```json
[
  {
    "_type": "block",
    "style": "h1",
    "children": [
      { "_type": "span", "text": "1. Market Overview", "marks": [] }
    ],
    "markDefs": []
  },
  {
    "_type": "block",
    "style": "normal",
    "children": [
      { "_type": "span", "text": "This report provides an ", "marks": [] },
      { "_type": "span", "text": "important", "marks": ["strong"] },
      { "_type": "span", "text": " analysis. See ", "marks": [] },
      { "_type": "span", "text": "source", "marks": ["link-1"] },
      { "_type": "span", "text": " for details.", "marks": [] }
    ],
    "markDefs": [
      {
        "_key": "link-1",
        "_type": "link",
        "href": "https://example.com"
      }
    ]
  },
  {
    "_type": "block",
    "style": "normal",
    "listItem": "bullet",
    "level": 1,
    "children": [
      { "_type": "span", "text": "Revenue increased", "marks": [] }
    ],
    "markDefs": []
  },
  {
    "_type": "block",
    "style": "normal",
    "listItem": "bullet",
    "level": 1,
    "children": [
      { "_type": "span", "text": "Margin improved", "marks": [] }
    ],
    "markDefs": []
  },
  {
    "_type": "image",
    "src": "https://example.com/chart.png",
    "alt": "Trend chart",
    "caption": "Figure 1. Revenue trend"
  }
]
```

---

## 6. Portable Text 原生“能存什么样的富文本”

从能力边界看，它原生支持这几层：

### A. 文本结构层

- 段落
- 标题
- 引用块
- 列表项
- 多块顺序组织

### B. 行内格式层

- 加粗
- 斜体
- 下划线
- 多标记叠加

### C. 行内带数据标记层

- 链接
- 批注
- 注解
- 术语提示
- 其他 annotation

### D. 列表层

- 无序列表
- 有序列表
- 层级列表

### E. 混合内容层

- 行内对象
- 块级对象
- 图片、代码块、表格、自定义 embed

---

## 7. Portable Text 原生不负责什么

这部分很重要，因为后续你们的业务规则主要就是补这些空白。

## 7.1 不负责最终视觉排版

Portable Text 不决定：

- 字号
- 字体
- 颜色
- 页边距
- PDF 分页
- 背景图怎么铺
- 页眉页脚
- 章节前是否强制换页

这些都属于 Java 渲染器责任。

---

## 7.2 不原生内置学术报告语义

Portable Text 不天然知道：

- 正式参考文献条目是什么
- 公式编号怎么做
- 脚注体系怎么做
- 图表题注规范怎么做
- 章节编号规则怎么做
- 目录如何生成
- 交叉引用如何解析

这些需要你们自己补业务规则。

---

## 7.3 不擅长表达严格树形章节结构

Portable Text 更像“按顺序排列的块流”。
虽然可以表达 h1 / h2 / h3，但它不是天然严格章节树。

如果你需要很强的：

- Section / Subsection / Subsubsection 结构
- 容器块
- 章节级元数据
- 章节级分页策略

通常需要额外加 report profile 规则。

---

## 8. 对你这个报告系统的缺口对照

下面这张表是最关键的整合视图。

| 需求项                 | Portable Text 原生是否足够 | 说明                                                       |
| ---------------------- | -------------------------- | ---------------------------------------------------------- |
| 普通段落               | 足够                       | 直接用 `block + style=normal`                            |
| 标题层级               | 基本足够                   | 可用 `h1/h2/h3`，但只是语义角色，不是严格章节树          |
| 加粗/斜体/下划线       | 足够                       | 直接用 `marks`                                           |
| 链接/批注              | 足够                       | 用 `markDefs`                                            |
| 无序/有序列表          | 基本足够                   | 用 `listItem + level`，但不是真正嵌套树                  |
| 图片块                 | 足够                       | 用 block object                                            |
| 代码块                 | 足够                       | 用 block object                                            |
| 表格块                 | 可实现                     | 用自定义 block object                                      |
| 行内小对象             | 可实现                     | 用 inline object                                           |
| 自定义图表             | 可实现，但需自定义         | Portable Text 允许放自定义块，但图表结构要你们自己定       |
| 公式                   | 不够，需补规则             | 可自定义 `math` 块，但原生没有学术数学语义               |
| 脚注                   | 不够，需补规则             | 原生没有标准脚注体系                                       |
| 文献引用               | 不够，需补规则             | 原生可挂 annotation，但没有完整 citation/bibliography 体系 |
| 参考文献列表           | 不够，需补规则             | 需要单独设计结构                                           |
| 图表编号/题注          | 不够，需补规则             | 需要你们规定 caption/label/编号策略                        |
| 交叉引用               | 不够，需补规则             | 如“见图3”“见公式(2)”需单独设计                         |
| 目录生成               | 不够，需补规则             | 需要由章节规则驱动生成                                     |
| 封面、摘要卡片、背景图 | 不够，需补规则             | 原生能放块，但视觉语义要你们定义                           |
| 页面级布局策略         | 不够，需 Java 渲染器实现   | 如分页、页眉页脚、背景、版式模板                           |

---

## 9. 对你这个项目最适合的理解方式

你不要把 Portable Text 理解成：

> 一个现成完整的报告系统，我直接拿来就能覆盖所有需求。

更准确的理解应该是：

> 它是一个已经很不错的富文本 JSON 基础骨架，适合拿来做内容中间协议；
> 但你们仍然需要在它上面定义自己的“报告子规范”。

也就是：

- 基础文本表达，沿用 Portable Text 思路
- 报告专属内容类型，自己定义
- Java 渲染逻辑，自己实现
- Python 输出和 Java 输入，共同遵守同一份 report profile

---

## 10. 一句最容易记住的话

**Portable Text 负责回答：富文本怎么拆成 JSON。**
**Report Profile 负责回答：在我们的报告系统里，这些 JSON 具体该怎么用。**

---

## 11. 下一步最自然的工作

在 Portable Text 原生能力之上，你们最需要新增的业务规则通常会包括：

1. 章节与子章节规则
2. 数学公式规则
3. 引文与参考文献规则
4. 图表块规则
5. 封面/摘要/结论卡片规则
6. Java 渲染器的块分发接口

也就是说，下一步不是再继续泛泛研究“还有没有别的富文本规范”，而是开始产出你们自己的：

**Report Profile v1 草案**
