import json
from copy import deepcopy
from pathlib import Path

import pytest
from pydantic import ValidationError

from ova_portable_text import (
    AxisDomain,
    ChartBlock,
    Document,
    FigureBlock,
    FlowChartDataset,
    GenericChartDataset,
    PartialDate,
    RangeChartDataset,
    StageProgressChartDataset,
    TimelineChartDataset,
    axis_band,
    axis_domain,
    axis_tick,
    chart_annotations,
    chart_axis,
    chart_category,
    chart_dataset,
    chart_marker,
    create_document,
    doughnut_center_content,
    doughnut_chart_dataset,
    figure_block,
    flow_chart_dataset,
    flow_edge,
    flow_group,
    flow_node,
    funnel_chart_dataset,
    funnel_stage,
    line_chart_dataset,
    line_marker_target,
    line_point,
    line_series,
    paragraph,
    partial_date,
    pie_slice,
    range_chart_dataset,
    range_point,
    range_series,
    reference_line,
    section,
    stage,
    stage_progress_chart_dataset,
    timeline_chart_dataset,
    timeline_event,
    validate_document_payload,
)

FIXTURE = Path(__file__).parents[1] / "docs/protocol/v1.4-example.json"


def payload(kind):
    data = json.loads(FIXTURE.read_text())
    return deepcopy(next(c for c in data["datasets"]["charts"] if c["chartType"] == kind))


def load_chart(data, version="report.v1.4"):
    return Document.from_dict(
        {"schemaVersion": version, "datasets": {"charts": [data]}}
    ).datasets.charts[0]


def line(**extra):
    return {
        "id": "l",
        "chartType": "line",
        "series": [{"key": "s", "points": [{"key": "p", "xValue": 1, "yValue": 2}]}],
        **extra,
    }


def bar(values=(2, 3), **extra):
    return {
        "id": "b",
        "chartType": "bar",
        "categories": [{"key": "c"}],
        "series": [
            {"key": f"s{i}", "data": [{"categoryKey": "c", "value": value}]}
            for i, value in enumerate(values)
        ],
        **extra,
    }


def marker(target, key="m", role="highlight"):
    return {"key": key, "target": target, "role": role}


def test_full_official_fixture_roundtrip_numbering_and_captions():
    original = json.loads(FIXTURE.read_text())
    doc = Document.from_dict(original)
    assert len(doc.datasets.charts) == 13
    assert len({c.chartType for c in doc.datasets.charts}) == 10
    assert all(not isinstance(c, GenericChartDataset) for c in doc.datasets.charts)
    assert doc.validate().is_valid
    restored = Document.from_json(doc.to_json())
    assert restored.to_dict() == doc.to_dict()
    content = doc.sections[0].body[0]
    figure = next(b for b in content.blocks if isinstance(b, FigureBlock))
    assert doc.build_numbering().get_display_number(figure.id) == "14"
    assert doc.build_numbering().get(figure.layoutRef) is None
    assert doc.build_resolver().resolve_xref(target_type="figure", target_id=figure.id)
    assert len(content.figure_captions(figure.id)) == 1
    assert content.figure_captions("missing") == []
    assert json.loads(FIXTURE.read_text()) == original


@pytest.mark.parametrize("kind", ["timeline", "stage_progress", "flow", "funnel", "range"])
def test_known_types_never_fall_through_and_historical_custom_types_survive(kind):
    raw = {"id": "x", "chartType": kind, "customHistory": [3, 1]}
    with pytest.raises(ValidationError):
        load_chart(raw)
    historical = Document.from_dict({"schemaVersion": "report.v1.3", "datasets": {"charts": [raw]}})
    assert isinstance(historical.datasets.charts[0], GenericChartDataset)
    assert historical.validate().is_valid
    assert Document.from_json(historical.to_json()).to_dict() == historical.to_dict()
    historical.schemaVersion = "report.v1.4"
    with pytest.raises(ValueError):
        historical.to_json()


@pytest.mark.parametrize("kind", ["pie", "doughnut", "bar", "line", "matrix_bubble"])
def test_invalid_old_known_chart_cannot_be_generic(kind):
    data = payload(kind)
    data["normalization" if kind != "bar" else "centerContent"] = "wrong-position"
    with pytest.raises(ValidationError):
        load_chart(data)


def test_unknown_custom_chart_roundtrips():
    data = {"id": "x", "chartType": "custom_xyz", "samples": [2, 1]}
    assert load_chart(data).to_dict()["samples"] == [2, 1]


@pytest.mark.parametrize(
    "value,precision",
    [
        ("2023-02-29", "day"),
        ("0000", "year"),
        ("10000", "year"),
        ("2025-13", "month"),
        ("2025-1", "month"),
        ("2025-01", "year"),
        ("2025-01-01T00:00:00Z", "day"),
    ],
)
def test_partial_dates_reject_invalid_input(value, precision):
    with pytest.raises(ValidationError):
        PartialDate(value=value, precision=precision)


def test_timeline_precision_order_asof_and_warning():
    events = [
        timeline_event(
            key="future",
            start=partial_date("2027", precision="year"),
            label={"en": "Future"},
            status="planned",
        ),
        timeline_event(
            key="past",
            start=partial_date("2020-02-29", precision="day"),
            label={"en": "Past"},
            status="planned",
        ),
    ]
    c = timeline_chart_dataset(id="t", events=events, as_of="2026-06-01")
    doc = Document(datasets={"charts": [c]})
    assert [e.key for e in doc.datasets.charts[0].events] == ["future", "past"]
    assert doc.validate().codes() == ["timeline.overdue_plan"]
    overlap = {
        "id": "t",
        "events": [
            {
                "key": "a",
                "start": {"value": "2026", "precision": "year"},
                "label": {"en": "A"},
                "status": "occurred",
            }
        ],
        "asOf": "2026-01-01",
    }
    TimelineChartDataset(**overlap)
    overlap["events"][0]["end"] = {"value": "2027", "precision": "year"}
    with pytest.raises(ValidationError):
        TimelineChartDataset(**overlap)
    overlap["events"][0]["status"] = "ongoing"
    TimelineChartDataset(**overlap)
    overlap["asOf"] = "2028-01-01"
    with pytest.raises(ValidationError):
        TimelineChartDataset(**overlap)


@pytest.mark.parametrize("status", ["not_started", "skipped"])
def test_stage_current_rejects_contradiction(status):
    with pytest.raises(ValidationError):
        stage_progress_chart_dataset(
            id="s", stages=[stage(key="a", label={"en": "A"}, status=status)], current_stage_key="a"
        )


def test_stage_completed_current_and_unknown_position():
    c = stage_progress_chart_dataset(
        id="s",
        stages=[stage(key="a", label={"en": "A"}, status="completed")],
        current_stage_key="a",
    )
    assert c.currentStageKey == "a"
    data = c.to_dict()
    data["currentStageKey"] = "missing"
    with pytest.raises(ValidationError):
        StageProgressChartDataset(**data)


@pytest.mark.parametrize(
    "edges",
    [
        [("a", "a")],
        [("a", "b"), ("a", "b")],
        [("a", "b"), ("b", "a")],
        [("missing", "b")],
    ],
)
def test_flow_rejects_bad_topology(edges):
    with pytest.raises(ValidationError):
        flow_chart_dataset(
            id="f",
            nodes=[flow_node(key=k, label={"en": k}) for k in ["a", "b"]],
            edges=[
                flow_edge(key=str(i), source_key=a, target_key=b) for i, (a, b) in enumerate(edges)
            ],
        )


def test_flow_isolation_and_empty_group_warning():
    c = flow_chart_dataset(
        id="f",
        nodes=[flow_node(key="a", label={"en": "A"})],
        edges=[],
        groups=[flow_group(key="empty", label={"en": "Empty"})],
    )
    assert Document(datasets={"charts": [c]}).validate().codes() == ["flow.empty_group"]
    raw = c.to_dict()
    raw.pop("edges")
    with pytest.raises(ValidationError):
        FlowChartDataset(**raw)


def test_funnel_checks_across_unknown_values():
    c = funnel_chart_dataset(
        id="f",
        relationship="containment",
        stages=[
            funnel_stage(key=str(i), label={"en": str(i)}, value=v)
            for i, v in enumerate([10, None, 5])
        ],
    )
    assert "value" not in c.to_dict()["stages"][1]
    c.stages[-1].value = 11
    report = Document(datasets={"charts": []})
    report.datasets.charts.append(c)
    issue = report.validate().issues[0]
    assert issue.code == "chart.invalid_value"
    assert issue.path == "datasets.charts[0].stages[2].value"


@pytest.mark.parametrize("bad", [True, "3", float("nan"), float("inf")])
def test_strict_numbers(bad):
    with pytest.raises(ValidationError):
        range_point(key="p", category_key="c", low=bad, high=4)
    with pytest.raises(ValidationError):
        AxisDomain(min=0, max=bad)
    raw = bar(normalization="percent", barMode="stacked")
    raw["series"][0]["data"][0]["value"] = bad
    with pytest.raises(ValidationError):
        load_chart(raw)


@pytest.mark.parametrize(
    "raw",
    [
        {"key": " ", "categoryKey": "c", "low": 0, "high": 1},
        {"key": "p", "categoryKey": "c", "low": 2, "high": 1},
        {"key": "p", "categoryKey": "c", "low": 0, "high": 1, "center": 2},
        {"key": "p", "categoryKey": "c", "low": 0, "high": 1, "center": None},
        {"key": "p", "categoryKey": "c", "low": 0, "high": 1, "label": {}},
    ],
)
def test_range_invalid_points(raw):
    from ova_portable_text import RangePoint

    with pytest.raises(ValidationError):
        RangePoint(**raw)


def test_range_sparse_equal_endpoints_and_missing_center():
    c = range_chart_dataset(
        id="r",
        categories=[chart_category(key="a", en="A"), chart_category(key="b", en="B")],
        series=[
            range_series(key="s", points=[range_point(key="p", category_key="b", low=2, high=2)])
        ],
    )
    assert len(c.series[0].points) == 1
    assert "center" not in c.to_dict()["series"][0]["points"][0]
    raw = c.to_dict()
    raw["annotations"] = {
        "markers": [marker({"seriesKey": "s", "pointKey": "p", "anchor": "center"})]
    }
    with pytest.raises(ValidationError):
        RangeChartDataset(**raw)
    raw["annotations"]["markers"][0]["target"]["anchor"] = "low"
    RangeChartDataset(**raw)
    raw["rangeDisplay"] = "point_interval"
    with pytest.raises(ValidationError):
        RangeChartDataset(**raw)


def test_line_role_boundaries():
    raw = line()
    raw["series"][0]["dataRole"] = "forecast"
    raw["series"][0]["points"][0]["dataRole"] = "observed"
    load_chart(raw)
    raw["series"][0]["points"].append({"xValue": 2, "yValue": 3, "dataRole": "estimated"})
    with pytest.raises(ValidationError):
        load_chart(raw)
    raw["series"][0].pop("dataRole")
    with pytest.raises(ValidationError):
        load_chart(raw)


def test_line_markers_allow_string_coordinates_but_axis_extensions_do_not():
    raw = line(annotations={"markers": [marker({"seriesKey": "s", "pointKey": "p"})]})
    raw["series"][0]["points"][0]["xValue"] = "2025"
    load_chart(raw)
    raw["xAxis"] = {"valueType": "year", "domain": {"min": 2020, "max": 2030}}
    with pytest.raises(ValidationError):
        load_chart(raw)


@pytest.mark.parametrize(
    "axis",
    [
        {"domain": {"min": 0, "max": 10}},
        {"valueType": "category", "ticks": []},
        {
            "valueType": "number",
            "ticks": [{"value": 2, "label": {"en": "Two"}}, {"value": 1, "label": {"en": "One"}}],
        },
        {"valueType": "number", "domain": {"min": 3, "max": 4}},
    ],
)
def test_line_axis_constraints(axis):
    with pytest.raises(ValidationError):
        load_chart(line(yAxis=axis))


def test_band_overlap_duplicate_annotation_keys_and_marker_shape():
    bands = [
        {"key": "right", "axis": "x", "from": 1, "to": 2, "role": "stage"},
        {"key": "left", "axis": "x", "from": 0, "to": 1, "role": "stage"},
    ]
    raw = line(xAxis={"valueType": "number"}, annotations={"bands": bands})
    assert load_chart(raw).annotations.bands[0].key == "right"
    bands[1]["to"] = 1.1
    with pytest.raises(ValidationError):
        load_chart(raw)
    bands[1]["to"] = 1
    raw["annotations"]["markers"] = [marker({"seriesKey": "s", "pointKey": "p"}, key="left")]
    with pytest.raises(ValidationError):
        load_chart(raw)
    raw["annotations"]["markers"] = [marker({"seriesKey": "s", "categoryKey": "c"})]
    with pytest.raises(ValidationError):
        load_chart(raw)


def test_percent_complete_nonnegative_and_zero_marker_rules():
    raw = bar((0, 0), normalization="percent", barMode="stacked")
    assert load_chart(raw).series[0].data[0].value == 0
    raw["annotations"] = {"markers": [marker({"seriesKey": "s0", "categoryKey": "c"})]}
    report = validate_document_payload({"datasets": {"charts": [raw]}})
    assert report.codes() == ["chart.undefined_position"]
    assert "annotations.markers[0].target" in report.issues[0].path
    raw["series"][0]["data"][0]["value"] = 1000
    raw["yAxis"] = {"valueType": "number", "unit": "percent", "domain": {"min": 0, "max": 100}}
    assert load_chart(raw).series[0].data[0].value == 1000
    raw["series"][1]["data"] = []
    with pytest.raises(ValidationError):
        load_chart(raw)


def test_stacked_domain_uses_positive_negative_outer_endpoints_and_not_baseline():
    raw = bar(
        (2, 3), barMode="stacked", yAxis={"valueType": "number", "domain": {"min": 1, "max": 4}}
    )
    with pytest.raises(ValidationError):
        load_chart(raw)
    raw["yAxis"]["domain"]["max"] = 5
    load_chart(raw)
    raw["series"][0]["data"][0]["value"] = 0
    load_chart(raw)  # A zero segment does not introduce a false out-of-domain observation.
    raw = bar(
        (-2, -3), barMode="stacked", yAxis={"valueType": "number", "domain": {"min": -4, "max": 0}}
    )
    with pytest.raises(ValidationError):
        load_chart(raw)


def test_percent_overflow_rejected():
    with pytest.raises(ValidationError):
        load_chart(bar((1e308, 1e308), normalization="percent", barMode="stacked"))


def test_version_gates_on_authoring_and_save_without_implicit_upgrade():
    c = load_chart(payload("timeline"))
    old = create_document(schema_version="report.v1.3")
    with pytest.raises(ValueError):
        old.add_chart_dataset(c)
    old.datasets.charts.append(c)
    assert "protocol.version_mismatch" in old.validate().codes()
    with pytest.raises(ValueError):
        old.to_json()
    assert old.schemaVersion == "report.v1.3"
    with pytest.raises(ValidationError):
        Document(schemaVersion="report.v9")
    assert create_document().schemaVersion == "report.v1.4"


def test_figure_shared_layout_identity_dependency_and_caption_boundaries():
    doc = Document.load_json(FIXTURE)
    content = doc.sections[0].body[0]
    fig = next(b for b in content.blocks if isinstance(b, FigureBlock))
    content.append_block(figure_block(id="fig-copy", layout_ref=fig.layoutRef))
    content.append_block(paragraph("First", style="figure_caption"))
    content.append_block(paragraph("Second", style="figure_caption"))
    content.append_block(paragraph("Stop"))
    content.append_block(paragraph("Unrelated", style="figure_caption"))
    assert len(content.figure_captions("fig-copy")) == 2
    assert doc.validate().is_valid
    assert doc.build_numbering().get_display_number("fig-copy") == "15"
    grid = next(t for t in doc.datasets.tables if t.id == fig.layoutRef)
    child = next(
        b
        for row in grid.rows
        for cell in row.cells
        for b in cell.blocks or []
        if isinstance(b, ChartBlock)
    )
    child.id = "forbidden"
    issues = [i for i in doc.validate().issues if i.code == "figure.child_instance_identity"]
    assert len(issues) == 1
    assert len(issues[0].usagePaths) == 2
    child.id = None
    child.chartRef = "missing"
    assert "unresolved_grid_cell_chart_ref" in doc.validate().codes()
    assert (
        len(
            next(
                i for i in doc.validate().issues if i.code == "unresolved_grid_cell_chart_ref"
            ).usagePaths
        )
        == 2
    )
    fig.layoutRef = "missing"
    assert "figure.invalid_layout_ref" in doc.validate().codes()


@pytest.mark.parametrize("bad", [0, 1, "true", None])
def test_figure_keep_together_is_strict(bad):
    with pytest.raises(ValidationError):
        FigureBlock(id="f", layoutRef="g", keepTogether=bad)


def test_helpers_build_public_v14_fields():
    axis = chart_axis(
        value_type="number",
        domain=axis_domain(min=0, max=10),
        ticks=[axis_tick(value=5, label={"en": "Five"})],
    )
    annotations = chart_annotations(
        reference_lines=[reference_line(key="ref", axis="y", value=4, role="threshold")],
        bands=[axis_band(key="band", axis="x", from_value=0, to=3, role="stage")],
        markers=[
            chart_marker(
                key="m",
                target=line_marker_target(series_key="s", point_key="p"),
                role="current_position",
            )
        ],
    )
    c = line_chart_dataset(
        id="line",
        x_axis=axis,
        y_axis=axis,
        annotations=annotations,
        data_basis="illustrative",
        series=[
            line_series(
                key="s",
                data_role="forecast",
                points=[line_point(key="p", x_value=1, y_value=2, data_role="observed")],
            )
        ],
    )
    assert c.dataBasis == "illustrative"
    assert (
        chart_dataset(
            id="t",
            chart_type="timeline",
            events=[
                timeline_event(
                    key="e", start=partial_date("2025", precision="year"), label={"en": "E"}
                )
            ],
        ).chartType
        == "timeline"
    )
    doughnut = doughnut_chart_dataset(
        id="d",
        slices=[pie_slice(key="a", value=50)],
        center_content=doughnut_center_content(primary={"en": "Team"}, secondary={"zh": "团队"}),
    )
    assert doughnut.centerContent.primary["en"] == "Team"
    s = section(id="sec", level=1, title="Composition")
    s.append_figure_with_caption(id="fig", layout_ref="grid", caption="Caption")
    assert s.body[0].figure_captions("fig")[0].style == "figure_caption"


def test_duplicate_referenced_line_point_reports_original_array_index():
    raw = line(annotations={"markers": [marker({"seriesKey": "s", "pointKey": "p"})]})
    raw["series"][0]["points"] = [
        {"xValue": 0, "yValue": 1},
        {"key": "p", "xValue": 1, "yValue": 2},
        {"key": "p", "xValue": 2, "yValue": 3},
    ]
    report = validate_document_payload({"datasets": {"charts": [raw]}})
    assert report.codes() == ["chart.duplicate_key"]
    assert report.issues[0].path == "datasets.charts[0].series[0].points[2].key"


def test_legacy_document_rejects_figure_section_on_append():
    legacy = create_document(schema_version="report.v1.3")
    s = section(id="s", level=1, title="S")
    s.append_figure(id="f", layout_ref="layout")
    with pytest.raises(ValueError, match="report.v1.4"):
        legacy.append_section(s)
    assert legacy.sections == []


def test_wrong_version_and_missing_required_chart_report_separately():
    assert validate_document_payload({"schemaVersion": "report.v99"}).codes() == [
        "unsupported_schema_version"
    ]
    assert validate_document_payload(
        {
            "datasets": {
                "charts": [
                    {"id": "f", "chartType": "flow", "nodes": [{"key": "a", "label": {"en": "A"}}]}
                ]
            }
        }
    ).codes() == ["chart.required_field"]
