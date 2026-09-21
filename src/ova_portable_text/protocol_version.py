"""Explicit protocol version boundaries; no implicit migrations."""

from .registry import NEW_CHART_TYPES, GenericChartDataset

SUPPORTED_VERSIONS = frozenset(
    {"report.v1", "report.v1.0", "report.v1.1", "report.v1.2", "report.v1.3", "report.v1.4"}
)


def chart_uses_v14(chart):
    if chart.chartType in NEW_CHART_TYPES:
        return not (
            isinstance(chart, GenericChartDataset) and getattr(chart, "_legacy_custom", False)
        )
    if isinstance(chart, GenericChartDataset):
        return False
    data = chart.to_dict()
    if any(key in data for key in ("annotations", "dataBasis", "normalization", "centerContent")):
        return True
    for name in ("xAxis", "yAxis"):
        if any(key in data.get(name, {}) for key in ("domain", "ticks")):
            return True
    for series in data.get("series", []):
        if "dataRole" in series or any(
            "dataRole" in point for point in series.get("points", []) + series.get("data", [])
        ):
            return True
    return False


def version_issues(document):
    from .block_objects import FigureBlock
    from .content import ContentItem
    from .section import SubsectionItem

    if document.schemaVersion not in SUPPORTED_VERSIONS:
        yield "schemaVersion", f"Unsupported protocol version: {document.schemaVersion!r}."
        return
    if document.schemaVersion == "report.v1.4":
        for i, chart in enumerate(document.datasets.charts):
            if isinstance(chart, GenericChartDataset) and chart.chartType in NEW_CHART_TYPES:
                yield (
                    f"datasets.charts[{i}]",
                    "Explicitly convert historical custom data to the v1.4 typed chart before upgrading.",
                )
        return
    for i, chart in enumerate(document.datasets.charts):
        if chart_uses_v14(chart):
            yield f"datasets.charts[{i}]", "This chart requires schemaVersion=report.v1.4."

    def walk(section, path):
        for i, item in enumerate(section.body):
            if isinstance(item, ContentItem):
                for j, block in enumerate(item.blocks):
                    if isinstance(block, FigureBlock):
                        yield (
                            f"{path}.body[{i}].blocks[{j}]",
                            "figure requires schemaVersion=report.v1.4.",
                        )
            elif isinstance(item, SubsectionItem):
                yield from walk(item.section, f"{path}.body[{i}].section")

    for i, section in enumerate(document.sections):
        yield from walk(section, f"sections[{i}]")
