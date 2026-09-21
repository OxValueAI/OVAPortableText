"""Chart-local checks shared by construction and document validation.

No display coordinates or inferred observations are written into the document.
"""

from collections import deque
from datetime import date
from itertools import pairwise

from .chart_features import (
    BarMarkerTarget,
    LineMarkerTarget,
    RangeMarkerTarget,
    fail,
    number,
)


def unique(items, path, attr="key", *, skip_none=False):
    seen = set()
    for i, item in enumerate(items):
        value = getattr(item, attr)
        if skip_none and value is None:
            continue
        if value in seen:
            fail(f"{path}[{i}].{attr}", f"Duplicate {attr}: {value!r}.", "chart.duplicate_key")
        seen.add(value)
    return seen


def validate_new_chart(chart):
    kind = chart.chartType
    if kind == "timeline":
        unique(chart.events, "events")
        if chart.asOf is not None:
            as_of = date.fromisoformat(chart.asOf)
            for i, event in enumerate(chart.events):
                if event.status in ("occurred", "ongoing") and event.start.bounds()[0] > as_of:
                    fail(f"events[{i}].start", "Event starts after asOf.")
                if event.end:
                    lo, hi = event.end.bounds()
                    if event.status == "occurred" and lo > as_of:
                        fail(f"events[{i}].end", "Occurred interval ends after asOf.")
                    if event.status == "ongoing" and hi < as_of:
                        fail(f"events[{i}].end", "Ongoing interval ends before asOf.")
    elif kind == "stage_progress":
        unique(chart.stages, "stages")
        if chart.currentStageKey is not None:
            current = next((s for s in chart.stages if s.key == chart.currentStageKey), None)
            if current is None:
                fail("currentStageKey", "Unknown stage.", "chart.unresolved_target")
            if current.status in ("not_started", "skipped"):
                fail("currentStageKey", "Current stage cannot be not_started or skipped.")
    elif kind == "flow":
        nodes = unique(chart.nodes, "nodes")
        unique(chart.edges, "edges")
        groups = unique(chart.groups or [], "groups")
        for i, node in enumerate(chart.nodes):
            if node.groupKey is not None and node.groupKey not in groups:
                fail(f"nodes[{i}].groupKey", "Unknown group.", "chart.unresolved_target")
        pairs = set()
        outgoing = {k: [] for k in nodes}
        degree = dict.fromkeys(nodes, 0)
        for i, edge in enumerate(chart.edges):
            for attr in ("sourceKey", "targetKey"):
                if getattr(edge, attr) not in nodes:
                    fail(f"edges[{i}].{attr}", "Unknown node.", "chart.unresolved_target")
            pair = edge.sourceKey, edge.targetKey
            if pair[0] == pair[1]:
                fail(f"edges[{i}]", "Self edges are not allowed.")
            if pair in pairs:
                fail(f"edges[{i}]", "Duplicate source/target pair.", "chart.duplicate_key")
            pairs.add(pair)
            outgoing[pair[0]].append(pair[1])
            degree[pair[1]] += 1
        ready = deque(k for k in nodes if not degree[k])
        visited = 0
        while ready:
            visited += 1
            for target in outgoing[ready.popleft()]:
                degree[target] -= 1
                if not degree[target]:
                    ready.append(target)
        if visited != len(nodes):
            fail("edges", "Flow must be acyclic.")
    elif kind == "funnel":
        unique(chart.stages, "stages")
        previous = None
        for i, stage in enumerate(chart.stages):
            if stage.value is not None:
                if previous is not None and stage.value > previous:
                    fail(
                        f"stages[{i}].value", "Known inner values cannot exceed known outer values."
                    )
                previous = stage.value
    elif kind == "range":
        categories = unique(chart.categories, "categories")
        unique(chart.series, "series")
        for i, series in enumerate(chart.series):
            unique(series.points, f"series[{i}].points")
            unique(series.points, f"series[{i}].points", "categoryKey")
            for j, point in enumerate(series.points):
                if point.categoryKey not in categories:
                    fail(
                        f"series[{i}].points[{j}].categoryKey",
                        "Unknown category.",
                        "chart.unresolved_target",
                    )
        validate_cartesian(chart)
    return chart


def checked_number(value, path):
    try:
        return number(value)
    except ValueError as exc:
        fail(path, str(exc))


def validate_cartesian(chart):
    kind = chart.chartType
    annotations = getattr(chart, "annotations", None)
    axes = {axis: getattr(chart, axis + "Axis", None) for axis in ("x", "y")}
    numeric_axis = "x" if getattr(chart, "orientation", None) == "horizontal" else "y"
    if kind == "matrix_bubble":
        for name, axis in axes.items():
            if axis and (axis.domain is not None or axis.ticks is not None):
                fail(
                    name + "Axis",
                    "matrix_bubble does not support numeric axis extensions.",
                    "chart.axis_mismatch",
                )
        return chart

    refs = annotations.referenceLines or [] if annotations else []
    bands = annotations.bands or [] if annotations else []
    markers = annotations.markers or [] if annotations else []
    extended_axes = {
        name
        for name, axis in axes.items()
        if axis and (axis.domain is not None or axis.ticks is not None)
    }
    extended_axes.update(item.axis for item in refs + bands)
    for name in extended_axes:
        axis = axes[name]
        if (
            (kind != "line" and name != numeric_axis)
            or axis is None
            or axis.valueType not in ("number", "year")
        ):
            fail(
                name + "Axis",
                "Numeric extensions require an explicit number/year axis.",
                "chart.axis_mismatch",
            )

    def within(name, value, path):
        checked_number(value, path)
        axis = axes[name]
        if axis and axis.domain and not axis.domain.min <= value <= axis.domain.max:
            fail(path, "Coordinate lies outside the declared domain.")

    for name, axis in axes.items():
        if axis and axis.ticks is not None:
            last = None
            for i, tick in enumerate(axis.ticks):
                if last is not None and tick.value <= last:
                    fail(f"{name}Axis.ticks[{i}].value", "Ticks must be strictly increasing.")
                within(name, tick.value, f"{name}Axis.ticks[{i}].value")
                last = tick.value
    seen = set()
    for collection, entries in (("referenceLines", refs), ("bands", bands), ("markers", markers)):
        for i, item in enumerate(entries):
            if item.key in seen:
                fail(
                    f"annotations.{collection}[{i}].key",
                    "Annotation keys must be unique across all collections.",
                    "chart.duplicate_key",
                )
            seen.add(item.key)
    for i, item in enumerate(refs):
        within(item.axis, item.value, f"annotations.referenceLines[{i}].value")
    for i, item in enumerate(bands):
        within(item.axis, item.from_, f"annotations.bands[{i}].from")
        within(item.axis, item.to, f"annotations.bands[{i}].to")
    for axis in ("x", "y"):
        for role in ("stage", "forecast", "assessment"):
            ordered = sorted(
                ((i, b) for i, b in enumerate(bands) if b.axis == axis and b.role == role),
                key=lambda pair: pair[1].from_,
            )
            for (_, previous), (i, current) in pairwise(ordered):
                if previous.to > current.from_:
                    fail(
                        f"annotations.bands[{i}].from",
                        "Bands on the same axis with the same role overlap.",
                    )
    if sum(m.role == "current_position" for m in markers) > 1:
        fail("annotations.markers", "At most one current_position marker is allowed.")

    if kind == "line":
        for i, series in enumerate(chart.series):
            for j, point in enumerate(series.points):
                path = f"series[{i}].points[{j}]"
                if point.dataRole is not None:
                    if series.dataRole is None:
                        fail(path + ".dataRole", "A point role requires a series role.")
                    if point.dataRole != series.dataRole and not (
                        series.dataRole == "forecast"
                        and j == 0
                        and point.dataRole in ("observed", "estimated")
                    ):
                        fail(path + ".dataRole", "Role changes require separate line series.")
                for name in extended_axes:
                    value = getattr(point, name + "Value")
                    if type(value) not in (int, float):
                        fail(
                            path + "." + name + "Value",
                            "Numeric extensions require JSON number coordinates.",
                            "chart.axis_mismatch",
                        )
                    within(name, value, path + "." + name + "Value")
    elif kind == "range":
        for i, series in enumerate(chart.series):
            for j, point in enumerate(series.points):
                for attr in ("low", "high"):
                    within(numeric_axis, getattr(point, attr), f"series[{i}].points[{j}].{attr}")
    elif kind == "bar":
        percent = chart.normalization == "percent"
        if percent:
            if chart.barMode != "stacked" or not chart.categories or not chart.series:
                fail(
                    "normalization", "Percent requires stacked mode and nonempty categories/series."
                )
            axis = axes[numeric_axis]
            if axis and axis.unit is not None and axis.unit != "percent":
                fail(
                    numeric_axis + "Axis.unit",
                    "Percent axis unit must be percent.",
                    "chart.axis_mismatch",
                )
            if axis and axis.domain and (axis.domain.min != 0 or axis.domain.max != 100):
                fail(numeric_axis + "Axis.domain", "Percent domain must be [0, 100].")
            keys = {c.key for c in chart.categories}
            for i, series in enumerate(chart.series):
                provided = unique(series.data, f"series[{i}].data", "categoryKey")
                if provided != keys:
                    fail(
                        f"series[{i}].data",
                        "Percent needs exactly one observation per category.",
                        "chart.required_field",
                    )
                for j, point in enumerate(series.data):
                    checked_number(point.value, f"series[{i}].data[{j}].value")
                    if point.value < 0:
                        fail(f"series[{i}].data[{j}].value", "Percent values must be nonnegative.")
        if extended_axes or percent:
            for i, series in enumerate(chart.series):
                for j, point in enumerate(series.data):
                    checked_number(point.value, f"series[{i}].data[{j}].value")
            if chart.barMode == "stacked":
                for category in chart.categories:
                    positive = negative = 0
                    for i, series in enumerate(chart.series):
                        for j, point in enumerate(series.data):
                            if point.categoryKey != category.key:
                                continue
                            path = f"series[{i}].data[{j}].value"
                            if point.value < 0:
                                negative = checked_number(negative + point.value, path)
                                outer = negative
                            else:
                                positive = checked_number(positive + point.value, path)
                                outer = positive
                            if point.value != 0 and not percent:
                                within(numeric_axis, outer, path)
            else:
                for i, series in enumerate(chart.series):
                    for j, point in enumerate(series.data):
                        within(numeric_axis, point.value, f"series[{i}].data[{j}].value")

    series_by_key = {s.key: (i, s) for i, s in enumerate(chart.series)}
    expected_target = {
        "line": LineMarkerTarget,
        "bar": BarMarkerTarget,
        "range": RangeMarkerTarget,
    }[kind]
    for i, marker in enumerate(markers):
        target = marker.target
        path = f"annotations.markers[{i}].target"
        if type(target) is not expected_target:
            fail(path, "Marker target structure does not match chart type.")
        if target.seriesKey not in series_by_key:
            fail(path + ".seriesKey", "Unknown series.", "chart.unresolved_target")
        si, series = series_by_key[target.seriesKey]
        if kind == "bar":
            unique(series.data, f"series[{si}].data", "categoryKey")
            point = next((p for p in series.data if p.categoryKey == target.categoryKey), None)
        else:
            unique(series.points, f"series[{si}].points", skip_none=True)
            point = next((p for p in series.points if p.key == target.pointKey), None)
        if point is None:
            fail(path, "Unknown observation.", "chart.unresolved_target")
        if kind == "range" and target.anchor == "center" and point.center is None:
            fail(path + ".anchor", "The target has no center.", "chart.unresolved_target")
        if kind == "bar":
            total = positive = negative = 0
            outer = None
            for s in chart.series:
                for p in s.data:
                    if p.categoryKey != target.categoryKey:
                        continue
                    checked_number(p.value, path)
                    total = checked_number(total + p.value, path)
                    if p.value < 0:
                        negative = checked_number(negative + p.value, path)
                        position = negative
                    else:
                        positive = checked_number(positive + p.value, path)
                        position = positive
                    if s is series:
                        outer = position if chart.barMode == "stacked" else p.value
            if chart.normalization == "percent":
                if total == 0:
                    fail(
                        path,
                        "Zero-total categories have no percentage position.",
                        "chart.undefined_position",
                    )
                checked_number((outer / total) * 100, path)
    return chart


def validate_cartesian_input(data):
    """Check raw coordinates before Pydantic's legacy numeric coercion."""

    def plain(value):
        return value.to_dict() if hasattr(value, "to_dict") else value

    raw_series = data.get("series", [])
    if not isinstance(raw_series, (list, tuple)):
        return  # Field validation reports malformed containers at their own paths.
    series = [plain(s) for s in raw_series]
    for item in series:
        if not isinstance(item, dict):
            return
        for collection in ("points", "data"):
            points = item.get(collection, [])
            if not isinstance(points, (list, tuple)):
                return
            if any(not isinstance(plain(point), dict) for point in points):
                return
    axes = [plain(data.get(name)) for name in ("xAxis", "yAxis")]
    enabled = any(key in data for key in ("dataBasis", "annotations", "normalization"))
    enabled |= any(
        isinstance(axis, dict) and any(key in axis for key in ("domain", "ticks")) for axis in axes
    )
    enabled |= any(
        "dataRole" in s
        or any("dataRole" in plain(p) for p in list(s.get("points", [])) + list(s.get("data", [])))
        for s in series
    )
    if not enabled:
        return
    for i, s in enumerate(series):
        for collection in ("points", "data"):
            for j, point in enumerate(s.get(collection, [])):
                p = plain(point)
                for field in ("value", "yValue", "xValue"):
                    if field not in p or (field == "xValue" and isinstance(p[field], str)):
                        continue
                    checked_number(p[field], f"series[{i}].{collection}[{j}].{field}")
