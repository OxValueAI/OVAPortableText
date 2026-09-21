"""Authoring helpers for report.v1.4 (snake_case arguments, protocol JSON output)."""

from __future__ import annotations

from typing import Any, TypeVar

from .base import OvaBaseModel
from .block_objects import FigureBlock
from .chart_features import (
    AxisBand,
    AxisDomain,
    AxisTick,
    BarMarkerTarget,
    ChartAnnotations,
    ChartMarker,
    DoughnutCenterContent,
    FlowEdge,
    FlowGroup,
    FlowNode,
    FunnelStage,
    LineMarkerTarget,
    PartialDate,
    RangeMarkerTarget,
    RangePoint,
    RangeSeries,
    ReferenceLine,
    Stage,
    TimelineEvent,
)
from .registry import (
    ChartAxis,
    ChartCategory,
    FlowChartDataset,
    FunnelChartDataset,
    RangeChartDataset,
    StageProgressChartDataset,
    TimelineChartDataset,
)

ModelT = TypeVar("ModelT", bound=OvaBaseModel)


def _build(model: type[ModelT], **fields: Any) -> ModelT:
    return model(**{key: value for key, value in fields.items() if value is not None})


def partial_date(value: str, *, precision: str) -> PartialDate:
    return PartialDate(value=value, precision=precision)


def timeline_event(
    *,
    key: str,
    start: PartialDate | dict[str, Any],
    label: dict[str, str],
    end: PartialDate | dict[str, Any] | None = None,
    description: dict[str, str] | None = None,
    event_type: str | None = None,
    status: str | None = None,
) -> TimelineEvent:
    return _build(
        TimelineEvent,
        key=key,
        start=start,
        label=label,
        end=end,
        description=description,
        eventType=event_type,
        status=status,
    )


def timeline_chart_dataset(
    *,
    id: str,
    events: list[TimelineEvent | dict[str, Any]],
    as_of: str | None = None,
    spacing: str = "ordinal",
    label: str | None = None,
    anchor: str | None = None,
    meta: dict[str, Any] | None = None,
) -> TimelineChartDataset:
    return _build(
        TimelineChartDataset,
        id=id,
        events=events,
        asOf=as_of,
        spacing=spacing,
        label=label,
        anchor=anchor,
        meta=meta,
    )


def stage(
    *,
    key: str,
    label: dict[str, str],
    description: dict[str, str] | None = None,
    status: str | None = None,
) -> Stage:
    return _build(Stage, key=key, label=label, description=description, status=status)


def stage_progress_chart_dataset(
    *,
    id: str,
    stages: list[Stage | dict[str, Any]],
    current_stage_key: str | None = None,
    label: str | None = None,
    anchor: str | None = None,
    meta: dict[str, Any] | None = None,
) -> StageProgressChartDataset:
    return _build(
        StageProgressChartDataset,
        id=id,
        stages=stages,
        currentStageKey=current_stage_key,
        label=label,
        anchor=anchor,
        meta=meta,
    )


def flow_node(
    *,
    key: str,
    label: dict[str, str],
    description: dict[str, str] | None = None,
    role: str | None = None,
    group_key: str | None = None,
) -> FlowNode:
    return _build(
        FlowNode, key=key, label=label, description=description, role=role, groupKey=group_key
    )


def flow_edge(
    *, key: str, source_key: str, target_key: str, label: dict[str, str] | None = None
) -> FlowEdge:
    return _build(FlowEdge, key=key, sourceKey=source_key, targetKey=target_key, label=label)


def flow_group(
    *, key: str, label: dict[str, str], description: dict[str, str] | None = None
) -> FlowGroup:
    return _build(FlowGroup, key=key, label=label, description=description)


def flow_chart_dataset(
    *,
    id: str,
    nodes: list[FlowNode | dict[str, Any]],
    edges: list[FlowEdge | dict[str, Any]],
    groups: list[FlowGroup | dict[str, Any]] | None = None,
    label: str | None = None,
    anchor: str | None = None,
    meta: dict[str, Any] | None = None,
) -> FlowChartDataset:
    return _build(
        FlowChartDataset,
        id=id,
        nodes=nodes,
        edges=edges,
        groups=groups,
        label=label,
        anchor=anchor,
        meta=meta,
    )


def funnel_stage(
    *,
    key: str,
    label: dict[str, str],
    value: float | None = None,
    description: dict[str, str] | None = None,
) -> FunnelStage:
    return _build(FunnelStage, key=key, label=label, value=value, description=description)


def funnel_chart_dataset(
    *,
    id: str,
    stages: list[FunnelStage | dict[str, Any]],
    relationship: str,
    value_unit: str | None = None,
    label: str | None = None,
    anchor: str | None = None,
    meta: dict[str, Any] | None = None,
) -> FunnelChartDataset:
    return _build(
        FunnelChartDataset,
        id=id,
        stages=stages,
        relationship=relationship,
        valueUnit=value_unit,
        label=label,
        anchor=anchor,
        meta=meta,
    )


def range_point(
    *,
    key: str,
    category_key: str,
    low: float,
    high: float,
    center: float | None = None,
    label: dict[str, str] | None = None,
    description: dict[str, str] | None = None,
    data_role: str | None = None,
) -> RangePoint:
    return _build(
        RangePoint,
        key=key,
        categoryKey=category_key,
        low=low,
        high=high,
        center=center,
        label=label,
        description=description,
        dataRole=data_role,
    )


def range_series(
    *,
    key: str,
    points: list[RangePoint | dict[str, Any]],
    label: dict[str, str] | None = None,
    description: dict[str, str] | None = None,
    data_role: str | None = None,
) -> RangeSeries:
    return _build(
        RangeSeries,
        key=key,
        points=points,
        label=label,
        description=description,
        dataRole=data_role,
    )


def range_chart_dataset(
    *,
    id: str,
    categories: list[ChartCategory | dict[str, Any]],
    series: list[RangeSeries | dict[str, Any]],
    orientation: str = "horizontal",
    range_display: str = "band",
    value_unit: str | None = None,
    x_axis: ChartAxis | dict[str, Any] | None = None,
    y_axis: ChartAxis | dict[str, Any] | None = None,
    annotations: ChartAnnotations | dict[str, Any] | None = None,
    data_basis: str | None = None,
    label: str | None = None,
    anchor: str | None = None,
    meta: dict[str, Any] | None = None,
) -> RangeChartDataset:
    return _build(
        RangeChartDataset,
        id=id,
        categories=categories,
        series=series,
        orientation=orientation,
        rangeDisplay=range_display,
        valueUnit=value_unit,
        xAxis=x_axis,
        yAxis=y_axis,
        annotations=annotations,
        dataBasis=data_basis,
        label=label,
        anchor=anchor,
        meta=meta,
    )


def axis_domain(*, min: float, max: float) -> AxisDomain:
    return AxisDomain(min=min, max=max)


def axis_tick(*, value: float, label: dict[str, str]) -> AxisTick:
    return AxisTick(value=value, label=label)


def reference_line(
    *, key: str, axis: str, value: float, role: str, label: dict[str, str] | None = None
) -> ReferenceLine:
    return _build(ReferenceLine, key=key, axis=axis, value=value, role=role, label=label)


def axis_band(
    *,
    key: str,
    axis: str,
    from_value: float,
    to: float,
    role: str,
    label: dict[str, str] | None = None,
) -> AxisBand:
    return _build(AxisBand, key=key, axis=axis, from_=from_value, to=to, role=role, label=label)


def line_marker_target(*, series_key: str, point_key: str) -> LineMarkerTarget:
    return LineMarkerTarget(seriesKey=series_key, pointKey=point_key)


def bar_marker_target(*, series_key: str, category_key: str) -> BarMarkerTarget:
    return BarMarkerTarget(seriesKey=series_key, categoryKey=category_key)


def range_marker_target(*, series_key: str, point_key: str, anchor: str) -> RangeMarkerTarget:
    return RangeMarkerTarget(seriesKey=series_key, pointKey=point_key, anchor=anchor)


def chart_marker(
    *,
    key: str,
    target: LineMarkerTarget | BarMarkerTarget | RangeMarkerTarget | dict[str, Any],
    role: str,
    label: dict[str, str] | None = None,
    description: dict[str, str] | None = None,
) -> ChartMarker:
    return _build(
        ChartMarker, key=key, target=target, role=role, label=label, description=description
    )


def chart_annotations(
    *,
    reference_lines: list[ReferenceLine | dict[str, Any]] | None = None,
    bands: list[AxisBand | dict[str, Any]] | None = None,
    markers: list[ChartMarker | dict[str, Any]] | None = None,
) -> ChartAnnotations:
    return _build(ChartAnnotations, referenceLines=reference_lines, bands=bands, markers=markers)


def doughnut_center_content(
    *, primary: dict[str, str], secondary: dict[str, str] | None = None
) -> DoughnutCenterContent:
    return _build(DoughnutCenterContent, primary=primary, secondary=secondary)


def figure_block(
    *, id: str, layout_ref: str, anchor: str | None = None, keep_together: bool = True
) -> FigureBlock:
    return _build(
        FigureBlock, id=id, layoutRef=layout_ref, anchor=anchor, keepTogether=keep_together
    )
