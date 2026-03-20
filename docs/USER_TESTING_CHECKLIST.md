# User Testing Checklist

This checklist is intended for the next manual testing round.
这份清单用于下一轮你的人工回测。

## 1. Authoring feel / 使用手感

请重点留意：

- `Document` / `Section` 的创建过程是否顺手
- append 风格 API 是否自然
- 你是否经常需要“退回去手拼 dict”
- 命名是否容易理解

## 2. JSON shape / JSON 结构

请检查导出的 JSON 是否符合你的预期：

- 顶层字段是否齐全
- section / subsection 是否正确嵌套
- caption 是否出现在期望位置
- registry 与正文引用是否一致

## 3. Validation / 校验体验

请检查：

- 报错是否容易定位
- issue 的 `sectionId / contextType / contextId` 是否有帮助
- warning 和 error 的区分是否合理

## 4. Real business samples / 真实业务样例

建议至少手工构造三类报告：

1. 最小报告
2. 带图表/表格/引文的标准报告
3. 你真实业务中的一份复杂报告

## 5. Save failing JSON / 保存失败样例

遇到 bug 时，建议同时保留：

- 触发 bug 的 Python 构造代码
- 导出的 JSON 文件
- `validate().to_text()` 输出
