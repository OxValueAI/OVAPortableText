# Python 0.6.0 / report.v1.5：估值结果横幅

`valuation_result` 是正式 chartType，面向标题、估值主值和上下文三层布局。原来的单格 grid 卡片仍合法；需要原生估值横幅时显式切换到本类型。包生成 JSON，不绘制图片。

```bash
python -m pip install --upgrade "OVAPortableText==0.6.0"
```

```python
import ova_portable_text as o

report = o.create_document(title="Valuation report", language="en")
chart = o.valuation_result_chart_dataset(
    id="valuation-result",
    subject={"en": "Clean Food Group Limited"},
    title={"en": "Valuation range"},
    valuation=o.valuation_range(20_100_000, 28_400_000),
    currency="GBP",
    value_basis="equity_value",
    capital_basis="pre_money",
    as_of="2026-08-05",
    data_basis="illustrative",
    display_scale="million",
    display_precision=1,
    notes={"en": "Illustrative design sample."},
)
report.add_chart_dataset(chart)
section = report.new_section(id="summary", level=1, title="Summary")
section.append_to_last_content(o.ChartBlock(id="result-banner", chartRef=chart.id))
report.validate().raise_for_errors()
report.save_json("valuation_result.json")
```

渲染主值为 `£20.1m – £28.4m`；必须保留主体、股权价值口径、投前属性、GBP、基准日及示例提示。主值放大、居中、深蓝背景等由渲染器实现；不要添加 `backgroundColor` 等非协议字段。

## 两种金额结构

- 区间：`o.valuation_range(low, high)`，有限数值，low <= high；允许相等、零及负值。
- 单值：`o.valuation_point(value)`，不会自动推断区间。

金额始终按 GBP、USD 等基本货币单位存储。`display_scale="million"` 仅在显示时除以百万；不是说输入 20.1 就表示 20.1m。display_precision 为整数 0…6；舍入不能隐藏非零值或把不同端点合并为一个值。

`value_basis` 必填：equity_value / enterprise_value / asset_value。`capital_basis` 只有股权价值允许 pre_money / post_money。未声明投前/投后时省略，不要默认为投前。

`as_of` 为完整公历日期，`data_basis` 必填 evidence_based 或 illustrative。SDK 不验证业务证据真伪。可选 title、notes、subject 采用多语言字典；显式 null 不合法，helper 会省略其默认 None。

## 模型与引用

`ValuationResultChartDataset` 输出与 helper 相同，直接模型使用 `valueBasis / capitalBasis / asOf / dataBasis / displayScale / displayPrecision`。嵌套模型为 `ValuationPoint`、`ValuationRange`，联合别名 `ValuationAmount` 使用 kind 判别。

图表位于 datasets.charts；正文使用 ChartBlock，组合布局可以在 GridTableCell.blocks 放匿名 ChartBlock。需要图注时使用 `append_chart_with_caption`；不需要额外 FigureBlock 或图注。单个类型只表达一个主体的一项估值结论，多方法区间比较继续使用 range。

## 兼容与错误处理

默认 schemaVersion 是 report.v1.5；`create_document(schema_version="report.v1.4")` 仍可生成旧文档。新版包读取旧文件后保留原 schemaVersion。给旧作者对象添加新强类型横幅会报错，不自动升级。

历史 v1.4 或更早文件中曾存在的同名自定义图型继续原样保留。若改为 v1.5，必须先显式构建新强类型结构，不能只改版本号。v1.5 已知图型的缺字段、非法枚举、逆序金额等不会回退为 GenericChartDataset。

`report.validate()` 会重新检查已修改的 builder 对象、金额语义、版本与引用；发布前必须调用。金额、日期、字段和版本错误可由 `validate_document_payload` 转成结构化诊断。

## 渲染器验收

按 [正式协议第 22 节](../PROTOCOL.md#22-v15-valuation_result-估值结果横幅) 实现三层横幅。覆盖点值、范围、负值、零值、相等端点、长公司名、两种语言、不同倍率、舍入边界、无投前/投后属性及 notes。拒绝未知能力，不静默转为图片或文字。包单元测试不代表渲染器截图测试已通过。

完整示例：[Python](../examples/v15_valuation_result.py) / [JSON](protocol/v1.5-example.json)。v1.4 的旧指南和旧样例保持历史用途。
