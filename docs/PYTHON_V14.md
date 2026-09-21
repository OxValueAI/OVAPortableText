# Python 0.5.0 / report.v1.4

0.5.0 提供 v1.4 的生成、读取、结构和语义校验。新建文档默认 `report.v1.4`，已有 v1.3 文档读取和保存时保留原版本。Figure 6.2 所需的误差棒／中心点连线不在本版范围。

本包输出 JSON；图形绘制、可见的示意提示、图例和分页由下游渲染器实现。Python 校验通过不能替代渲染验收，也不会把新图自动转换成旧图或图片。

## 开始使用

```python
from ova_portable_text import (
    create_document, section, partial_date,
    timeline_event, timeline_chart_dataset,
)

report = create_document(title="企业报告", language="zh")
report.add_chart_dataset(timeline_chart_dataset(
    id="chart-milestones",
    as_of="2026-09-01",
    events=[timeline_event(
        key="founded",
        start=partial_date("2020", precision="year"),
        label={"zh": "企业成立"},
        status="occurred",
    )],
))
summary = section(id="sec-summary", level=1, title="企业概况")
summary.append_chart_with_caption(
    id="fig-milestones", chart_ref="chart-milestones", caption="企业里程碑",
)
report.append_section(summary)
report.assert_valid().save_json("report.json")
```

[完整 Python 示例](../examples/v14_report.py) 演示 timeline、range 和组合 figure。运行：

```bash
python examples/v14_report.py /tmp/v14-report.json
```

[正式 JSON 示例](protocol/v1.4-example.json) 包含全部十种图型，共 13 个数据集，可直接使用 `Document.load_json(...)` 读取。

## 新增公开 API

模型使用协议字段名，如 `currentStageKey`；helpers 使用 snake_case，如 `current_stage_key`。所有新增 API 均从 `ova_portable_text` 导入。

| 图型 | 模型 | 构建 helpers |
| --- | --- | --- |
| timeline | `TimelineChartDataset`, `TimelineEvent`, `PartialDate` | `timeline_chart_dataset`, `timeline_event`, `partial_date` |
| stage_progress | `StageProgressChartDataset`, `Stage` | `stage_progress_chart_dataset`, `stage` |
| flow | `FlowChartDataset`, `FlowNode`, `FlowEdge`, `FlowGroup` | `flow_chart_dataset`, `flow_node`, `flow_edge`, `flow_group` |
| funnel | `FunnelChartDataset`, `FunnelStage` | `funnel_chart_dataset`, `funnel_stage` |
| range | `RangeChartDataset`, `RangeSeries`, `RangePoint` | `range_chart_dataset`, `range_series`, `range_point` |
| figure 正文实例 | `FigureBlock` | `figure_block`, `Section.append_figure`, `Section.append_figure_with_caption` |

`range.categories` 接受 `chart_category(...)` 或包含非空 `key`、语言对象 `label` 的字典；它要求的标签比旧 bar 分类更严格。新 helper 的语言字段使用 `label={"zh": "文本"}`，无需重复提供不同语言参数。

- `axis_domain(min=..., max=...)`、`axis_tick(value=..., label=...)`，通过 `chart_axis(domain=..., ticks=..., value_type="number")` 使用。
- `reference_line`、`axis_band(from_value=..., to=...)`、`chart_marker`，通过 `chart_annotations(reference_lines=..., bands=..., markers=...)` 组合。
- `line_marker_target(series_key=..., point_key=...)`、`bar_marker_target(series_key=..., category_key=...)`、`range_marker_target(series_key=..., point_key=..., anchor="center")`。
- line/bar 的数据集 helper 新增 `data_basis` 和 `annotations`；序列及观测 helper 新增 `data_role`。range 同样支持这些字段。
- bar helper 新增 `normalization="percent"`，必须搭配 `bar_mode="stacked"`；输入保留原始数量。
- doughnut helper 新增 `center_content=doughnut_center_content(primary={...}, secondary={...})`。

省略的 `normalization` 在模型中为 `None`，语义为 `none`，导出时省略，以免把新增字段写入旧文档。可选字段一般用 helper 的 `None` 表示省略；直接传入协议字典时，新增可选字段不能显式写 `null`。

## 组合图

将不含实例 `id/anchor` 的 `ChartBlock(chartRef=...)` 或 `ImageBlock(imageRef=...)` 放入 grid 单元格，然后由正文 `FigureBlock` 的 `layoutRef` 引用 grid 数据集。grid 至少有一个实际单元格；record 表不能作为 figure 布局。

组合图与普通 chart/image 共用图号。内部数据集、布局和子图不额外编号；相同布局可以被多个 figure 复用。

`Section.append_figure_with_caption(...)` 在同一个 content 中创建 figure 和紧邻的 caption。`ContentItem.figure_captions(figure_id)` 只返回紧随该实例的连续 `figure_caption` 文本块，遇到其他块即停止。编号不会改写 caption 文本。

## 校验与兼容

构造已知图型时结构和图表局部语义错误会抛出 Pydantic `ValidationError`，不会回退到 `GenericChartDataset`。

可变 builder 的追加和属性修改完成后，调用 `report.validate()` 检查整份报告，或 `report.assert_valid()` 阻止错误文档交付。引用、共享布局、版本、编号条件与局部语义由文档层核对。

对尚未构造成功的 JSON 字典，可用 `validate_document_payload(payload)` 获得 `ValidationReport`。新增图表错误映射为协议 `chart.*` 类别；版本错误使用 `unsupported_schema_version` / `protocol.version_mismatch`。问题包含字段路径；文档校验还附图表 ID 和可达使用路径。现有字段的旧错误 code 保留兼容。

```python
from ova_portable_text import create_document, Document

legacy = create_document(schema_version="report.v1.3")
loaded = Document.load_json("existing-v13.json")
assert loaded.schemaVersion == "report.v1.3"
```

v1.3 中曾作为自定义类型保存的 timeline 等仍按未知扩展保留。升级须显式转换并通过 v1.4 校验。`add_chart_dataset` 拒绝将新增能力加入 v1.3 文档；通过直接修改列表绕过追加检查的输入，会在文档校验和 `to_dict/to_json/save_json` 版本检查中被拒绝。未识别的自定义 chartType 可以保存，但不代表渲染器支持它。
