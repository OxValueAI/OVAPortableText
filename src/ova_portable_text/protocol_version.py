"""Explicit protocol version boundaries; no implicit migrations."""

from .registry import NEW_CHART_TYPES, V15_CHART_TYPES, GenericChartDataset

SUPPORTED_VERSIONS = frozenset(
    {"report.v1", "report.v1.0", "report.v1.1", "report.v1.2", "report.v1.3", "report.v1.4", "report.v1.5"}
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


def chart_type_supported(kind, version):
    if kind in V15_CHART_TYPES:
        return version == "report.v1.5"
    if kind in NEW_CHART_TYPES:
        return version in {"report.v1.4", "report.v1.5"}
    return True


def chart_version_issue(chart, version):
    if isinstance(chart, GenericChartDataset) and getattr(chart, "_legacy_custom", False):
        if chart_type_supported(chart.chartType, version):
            return "Explicitly convert historical custom data to its typed chart before upgrading."
        return None
    if chart.chartType in V15_CHART_TYPES and version != "report.v1.5":
        return "This chart requires schemaVersion=report.v1.5; no implicit upgrade is performed."
    if version not in {"report.v1.4", "report.v1.5"} and chart_uses_v14(chart):
        return "This chart requires schemaVersion=report.v1.4 or report.v1.5."
    return None


def version_issues(document):
    from .block_objects import FigureBlock
    from .content import ContentItem
    from .section import SubsectionItem

    if document.schemaVersion not in SUPPORTED_VERSIONS:
        yield "schemaVersion", f"Unsupported protocol version: {document.schemaVersion!r}."
        return
    for i, chart in enumerate(document.datasets.charts):
        issue = chart_version_issue(chart, document.schemaVersion)
        if issue:
            yield f"datasets.charts[{i}]", issue
    if document.schemaVersion in {"report.v1.4", "report.v1.5"}:
        return

    def walk(section, path):
        for i, item in enumerate(section.body):
            if isinstance(item, ContentItem):
                for j, block in enumerate(item.blocks):
                    if isinstance(block, FigureBlock):
                        yield (
                            f"{path}.body[{i}].blocks[{j}]",
                            "figure requires schemaVersion=report.v1.4 or report.v1.5.",
                        )
            elif isinstance(item, SubsectionItem):
                yield from walk(item.section, f"{path}.body[{i}].section")

    for i, section in enumerate(document.sections):
        yield from walk(section, f"sections[{i}]")
