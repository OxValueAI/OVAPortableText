# User Testing Checklist / 用户回测清单

This checklist is intended for manual testing rounds after API or protocol alignment changes.  
这份清单用于在 API 或协议对齐更新之后做人工回测。

---

## 1. Authoring feel / 使用手感

Please check / 请重点检查：

- whether `Document` / `Section` creation still feels natural  
  `Document` / `Section` 的创建过程是否自然
- whether append-style APIs are still easy to remember  
  append 风格 API 是否依旧顺手
- whether you often feel forced to go back to raw dicts  
  你是否经常被迫回退去手拼 dict
- whether names and helper boundaries are easy to understand  
  命名和 helper 边界是否容易理解

---

## 2. JSON shape / JSON 结构

Please inspect exported JSON for / 请检查导出的 JSON：

- top-level fields present as expected  
  顶层字段是否齐全
- section / subsection nesting correctness  
  section / subsection 嵌套是否正确
- registry entries and body refs match each other  
  registry 条目与正文引用是否一致
- captions appear in the expected adjacent pattern  
  caption 是否按相邻模式出现
- table datasets use the intended mode (`record` or `grid`)  
  表格数据集是否用了预期模式（`record` 或 `grid`）

---

## 3. Validation experience / 校验体验

Please check / 请检查：

- whether validation errors are easy to locate  
  报错是否容易定位
- whether issue context is useful  
  issue 的上下文是否有帮助
- whether warnings vs errors are classified reasonably  
  warning 与 error 的区分是否合理
- whether resolver output helps when references fail  
  当引用失败时，resolver 输出是否有帮助

---

## 4. Example coverage / 示例覆盖面

Please review whether the current examples are sufficient for your real usage.  
请评估当前 examples 是否已经足以覆盖你的真实使用场景。

Suggested questions / 建议关注：

- Is there at least one example close to your real report type?  
  是否至少有一个示例接近你的真实报告类型？
- Do we have enough examples for text, references, images, charts, tables, and validation?  
  文本、引用、图片、图表、表格、校验这几类是否都已有足够示例？
- Is any feature supported by the package but still missing from examples?  
  是否存在“包已支持、但 examples 没演示”的能力？

---

## 5. Real business samples / 真实业务样例

Recommended manual sample set / 建议至少手工构造三类业务样例：

1. a smallest valid report  
   最小报告
2. a standard report with images / charts / tables / references  
   含图片 / 图表 / 表格 / 引用的标准报告
3. a complex report close to your real production case  
   接近真实生产场景的复杂报告

---

## 6. Save failing artifacts / 保存失败现场

When you hit a bug, try to keep all of the following:  
当你遇到 bug 时，建议同时保留：

- the Python authoring code  
  触发问题的 Python 构造代码
- the exported JSON file  
  导出的 JSON 文件
- `validate().to_text()` output  
  `validate().to_text()` 输出
- the renderer-side error or screenshot if available  
  若有条件，也保留渲染器侧错误信息或截图
