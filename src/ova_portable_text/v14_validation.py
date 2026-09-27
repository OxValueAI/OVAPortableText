"""Document-wide v1.4 diagnostics, including mutable builder objects."""

from datetime import date

from pydantic import ValidationError

from .block_objects import ChartBlock, FigureBlock, ImageBlock, TableBlock
from .content import ContentItem
from .protocol_version import version_issues, chart_type_supported
from .registry import CHART_MODELS, GenericChartDataset, GridTableDataset
from .section import SubsectionItem


def _path(parts):
    result = ""
    for part in parts:
        result += f"[{part}]" if isinstance(part, int) else ("." if result else "") + str(part)
    return result


def add_model_errors(report, error, *, prefix="", chart_id=None):
    for item in error.errors():
        suffix = _path(item["loc"])
        context = item.get("ctx", {})
        local = context.get("path")
        if local:
            suffix += ("." if suffix else "") + local
        path = prefix + ("." if prefix and suffix else "") + suffix
        code = item["type"]
        if not code.startswith(("chart.", "figure.", "protocol.", "unsupported_schema_version")):
            if code == "missing":
                code = "chart.required_field"
            elif "Duplicate " in item["msg"]:
                code = "chart.duplicate_key"
            elif "does not resolve" in item["msg"]:
                code = "chart.unresolved_target"
            else:
                code = "chart.invalid_value"
        report.add_issue(
            code=code,
            message=item["msg"],
            path=path or prefix,
            contextType="chart_dataset",
            contextId=chart_id,
            chartId=chart_id,
        )


def walk_blocks(document):
    def walk(section, path):
        for i, item in enumerate(section.body):
            body_path = f"{path}.body[{i}]"
            if isinstance(item, ContentItem):
                for j, block in enumerate(item.blocks):
                    yield block, f"{body_path}.blocks[{j}]"
            elif isinstance(item, SubsectionItem):
                yield from walk(item.section, f"{body_path}.section")

    for i, section in enumerate(document.sections):
        yield from walk(section, f"sections[{i}]")


def validate_v14(document, report):
    for path, message in version_issues(document):
        report.add_issue(
            code="unsupported_schema_version"
            if path == "schemaVersion"
            else "protocol.version_mismatch",
            message=message,
            path=path,
        )
    # Revalidate known datasets after mutation. Historical unknown charts retain their data.
    for i, chart in enumerate(document.datasets.charts):
        model = CHART_MODELS.get(chart.chartType)
        if model is None or (
            isinstance(chart, GenericChartDataset)
            and getattr(chart, "_legacy_custom", False)
            and not chart_type_supported(chart.chartType, document.schemaVersion)
        ):
            continue
        path = f"datasets.charts[{i}]"
        try:
            validated = model.model_validate(chart.to_dict())
        except ValidationError as error:
            add_model_errors(report, error, prefix=path, chart_id=chart.id)
            continue
        if validated.chartType == "timeline" and validated.asOf:
            as_of = date.fromisoformat(validated.asOf)
            for j, event in enumerate(validated.events):
                if event.status == "planned" and (event.end or event.start).bounds()[1] < as_of:
                    report.add_issue(
                        code="timeline.overdue_plan",
                        severity="warning",
                        message="Plan date is before asOf; status remains planned.",
                        path=f"{path}.events[{j}].status",
                        chartId=chart.id,
                        contextId=chart.id,
                    )
        if validated.chartType == "flow":
            occupied = {node.groupKey for node in validated.nodes}
            for j, group in enumerate(validated.groups or []):
                if group.key not in occupied:
                    report.add_issue(
                        code="flow.empty_group",
                        severity="warning",
                        message="Group has no nodes.",
                        path=f"{path}.groups[{j}]",
                        chartId=chart.id,
                        contextId=chart.id,
                    )

    tables = {table.id: (i, table) for i, table in enumerate(document.datasets.tables)}
    figure_usages = {}
    all_usages = {}
    chart_usages = {}
    for block, path in walk_blocks(document):
        if isinstance(block, ChartBlock):
            chart_usages.setdefault(block.chartRef, []).append(path + ".chartRef")
        if isinstance(block, (FigureBlock, TableBlock)):
            ref = block.layoutRef if isinstance(block, FigureBlock) else block.tableRef
            all_usages.setdefault(ref, []).append(path)
        if not isinstance(block, FigureBlock):
            continue
        figure_usages.setdefault(block.layoutRef, []).append((block, path))
        entry = tables.get(block.layoutRef)
        if (
            not entry
            or not isinstance(entry[1], GridTableDataset)
            or not any(row.cells for row in entry[1].rows)
        ):
            report.add_issue(
                code="figure.invalid_layout_ref",
                message="figure.layoutRef must resolve to a nonempty grid layout.",
                path=path + ".layoutRef",
                figureId=block.id,
                usagePath=path,
                contextId=block.id,
            )
        try:
            FigureBlock.model_validate(block.to_dict())
        except ValidationError as error:
            for item in error.errors():
                report.add_issue(
                    code="figure.invalid_value",
                    message=item["msg"],
                    path=path + "." + _path(item["loc"]),
                    figureId=block.id,
                )
    for table_id, (ti, table) in tables.items():
        if not isinstance(table, GridTableDataset):
            continue
        figure_paths = figure_usages.get(table_id, [])
        for ri, row in enumerate(table.rows):
            for ci, cell in enumerate(row.cells):
                for bi, block in enumerate(cell.blocks or []):
                    suffix = f".rows[{ri}].cells[{ci}].blocks[{bi}]"
                    definition_path = f"datasets.tables[{ti}]" + suffix
                    if isinstance(block, ChartBlock):
                        paths = [
                            usage + " -> " + definition_path + ".chartRef"
                            for usage in all_usages.get(table_id, [])
                        ]
                        chart_usages.setdefault(block.chartRef, []).extend(paths)
                    if (
                        figure_paths
                        and isinstance(block, (ChartBlock, ImageBlock))
                        and (block.id is not None or block.anchor is not None)
                    ):
                        report.add_issue(
                            code="figure.child_instance_identity",
                            message="A figure layout child must omit id and anchor.",
                            path=definition_path,
                            figureId=figure_paths[0][0].id,
                            usagePath=figure_paths[0][1],
                            usagePaths=[p for _, p in figure_paths],
                        )
    for issue in report.issues:
        if issue.chartId and issue.chartId in chart_usages:
            issue.usagePaths = chart_usages[issue.chartId]
            if issue.usagePaths:
                issue.usagePath = issue.usagePaths[0]

    for issue in report.issues:
        if issue.path and issue.path.startswith("datasets.tables["):
            for table_id, (ti, _) in tables.items():
                if issue.path.startswith(f"datasets.tables[{ti}]."):
                    paths = all_usages.get(table_id, [])
                    if paths:
                        issue.usagePaths = paths
                        issue.usagePath = paths[0]
                    break
