# Python 0.7.0 / report.v1.6

Python 0.7.0 新增 v1.6 模型、构建方法、版本检查和显式 caption 解析。协议与 SDK 已冻结，见[正式协议](protocol/v1.6.md)及[冻结记录](protocol/v1.6-freeze.md)。渲染器当前无法测试，渲染验收延期；本发布不声称 PDF 渲染器已经通过验收。默认新建文档仍为 report.v1.5；使用新协议必须显式传入 schema_version="report.v1.6"。

安装指定版本：

```bash
python -m pip install "OVAPortableText==0.7.0"
```

## 构建与校验

完整可运行代码见 [v16_layout_report.py](../examples/v16_layout_report.py)。从仓库运行：

```bash
PYTHONPATH=src python examples/v16_layout_report.py > /tmp/v16-layout-report.json
```

```python
import ova_portable_text as o

report = o.create_document(
    schema_version="report.v1.6",
    title="Layout example",
    theme=o.PageThemeConfig(page=o.page_settings("portrait")),
)
data = o.record_table_dataset(
    id="values",
    columns=[o.table_column(key="amount", header="GBP")],
    rows=[{"amount": 1200000}],
    layout=o.table_layout(
        o.table_column_spec_auto(align="right"),
        header_defaults=o.cell_alignment(align="center"),
    ),
)
report.add_table_dataset(data)
section = report.new_section(id="summary", level=1, title="Summary")
section.append_object_with_captions(
    o.table_block(
        id="summary-table", table_ref=data.id,
        page=o.page_settings("landscape"),
        pagination=o.object_pagination(
            page_break_before="always", page_break_after="always",
        ),
    ),
    before="Financial summary",
    after="Illustrative figures.",
    before_layout=o.block_layout(text_align="center"),
)
report.assert_valid()
payload = report.to_dict()
```

页面方向与分页是渲染合同，SDK 不计算实际页数。只声明 page 不要求独占页面；before/after 同时 always 才显式要求前后页面边界。对象组包括显式 caption；表格跨页、方向恢复及同页约束由分页渲染器验收。

## 公共 API

| 功能 | API |
| --- | --- |
| 页面方向 | PageSettings / page_settings(orientation) |
| 文档页面默认值 | PageThemeConfig(page=...)；v1.6 中也可传入 theme 字典 |
| 对象前后分页 | ObjectPagination / object_pagination(page_break_before=..., page_break_after=...) |
| 单元格默认对齐 | CellAlignment / cell_alignment(align=..., vertical_align=...) |
| 显式绑定 | CaptionBinding / caption_binding(target_ref=..., position=...) |
| caption 文本块 | caption_block(..., target_ref=..., position=..., style=..., layout=...) |
| 表格默认值 | table_layout(..., cell_defaults=..., header_defaults=...) |
| 列对齐 | table_column_spec_auto/weight(..., align=..., vertical_align=..., header=...) |
| 章节方向 | section / Document.new_section / Section.new_subsection 的 page 参数 |
| 对象方向与分页 | image/chart/table/figure_block 与 Section.append_image/chart/table/figure 的 page、pagination 参数 |
| 原子追加前后组 | Section.append_object_with_captions(block, before=..., after=..., before_layout=..., after_layout=...) |
| 解析组内 caption | ContentItem.captions_for(id, position=None或before或after) |
| 解析显式目标 | report.build_resolver().resolve_caption(caption_block, content_item) |

需要多段 caption 时，先构建 caption_block，再用 Section.append_blocks 将前组、对象和后组放入同一个 content.blocks。append_paragraph 等方法可能创建新的 content；显式绑定不允许跨 content。

旧 append_*_with_caption 方法继续生成无显式绑定的后置文本。旧 figure_captions 方法保留隐式后置规则，遇到新显式绑定时按新组解析。读取器仅解析已有组，不自动修复错误的数组顺序；先 assert_valid，再解析和传递下游。

## 兼容与错误

- 新字段写入旧版文档时报告 protocol.version_mismatch；不自动升级版本。v1.4/v1.5 图型在 v1.6 中继续合法。
- 新字段显式 null、错误枚举、错误位置以及不合法 caption 目标/顺序均会被诊断。直接构建错误模型会抛出 Pydantic 错误；validate_document_payload 返回带字段路径的报告。
- 对象仍可逐步修改；validate/assert_valid 会重新检查新字段与 caption 引用。导出前必须校验，不能把单纯 to_json 成功当作完整验收。
- PageThemeConfig 是新类型。旧 ThemeConfig 中历史自定义 page 字典保持原样，不追溯应用 v1.6 语义；显式升级为 v1.6 后按新合同校验。
- 表头和数据对齐默认值只是 JSON 配置，SDK 不覆盖现有 grid 的显式 align、文本布局或模板。columnSpecs.width 仍必填。
- 本版没有 record 单元格 rowIndex 覆盖；cellOverrides 不是支持字段。

实现和验收范围见 [v1.6 实现记录](protocol/v1.6-implementation.md)。
