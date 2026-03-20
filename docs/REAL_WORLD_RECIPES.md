# Real-world Authoring Recipes

This page collects a few practical authoring patterns.
本文档整理几种更贴近真实业务的写法模式。

## 1. Start from the document, not from raw dicts

推荐先创建 `Document`，再不断 append section、registry 和内容块。
不推荐一开始就手拼嵌套 dict。

## 2. Registry first, body later

对于图片、表格、饼图数据，推荐先放到顶层 registry：

- `assets.images`
- `datasets.tables`
- `datasets.charts`

然后在正文中通过 `imageRef / tableRef / chartRef` 引用。

## 3. Use adjacent captions

当前协议更偏向“对象块 + 相邻 caption 文本块”的写法。
因此更推荐：

- `append_image_with_caption(...)`
- `append_table_with_caption(...)`
- `append_chart_with_caption(...)`

## 4. Validate early and often

在开发阶段建议频繁调用：

```python
validation = report.validate()
print(validation.to_text())
```

而在真正交给 Java 前，再调用：

```python
report.assert_valid()
```

## 5. Save JSON snapshots for regression

回测阶段建议把典型报告 JSON 保存成快照文件，便于：

- 对比结构变化
- 调试 Java 渲染问题
- 做回归测试

```python
report.save_json("build/report_snapshot.json")
```
