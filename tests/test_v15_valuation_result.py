import json
from copy import deepcopy
from pathlib import Path

import pytest
from pydantic import ValidationError

import ova_portable_text as o


def result(**extra):
    return dict(
        id="value",
        chartType="valuation_result",
        subject={"en": "Company"},
        valuation={"kind": "range", "low": 20_100_000, "high": 28_400_000},
        currency="GBP",
        valueBasis="equity_value",
        capitalBasis="pre_money",
        asOf="2026-08-05",
        dataBasis="illustrative",
        displayScale="million",
        **extra,
    )


def document(chart, version="report.v1.5"):
    return o.Document.from_dict({"schemaVersion": version, "datasets": {"charts": [chart]}})


def test_native_banner_roundtrip_resolver_numbering_and_grid():
    c = o.valuation_result_chart_dataset(
        id="value",
        subject={"en": "Company", "zh": "公司"},
        valuation=o.valuation_range(20_100_000, 28_400_000),
        currency="GBP",
        value_basis="equity_value",
        capital_basis="pre_money",
        as_of="2026-08-05",
        data_basis="illustrative",
        display_scale="million",
    )
    d = o.create_document()
    d.add_chart_dataset(c)
    assert d.schemaVersion == "report.v1.5"
    sec = d.new_section(id="sec", level=1, title="Summary")
    sec.append_chart_with_caption(id="banner", chart_ref=c.id, caption="Result")
    grid = o.GridTableDataset(
        id="layout",
        columnCount=1,
        rows=[o.GridTableRow(cells=[o.GridTableCell(blocks=[o.ChartBlock(chartRef=c.id)])])],
    )
    d.add_table_dataset(grid)
    sec.append_figure_with_caption(id="combo", layout_ref=grid.id, caption="Combination")
    assert d.validate().is_valid and not d.validate().issues
    assert d.build_numbering().get_display_number("banner") == "1"
    assert d.build_numbering().get_display_number("combo") == "2"
    assert d.build_resolver().resolve_xref(target_type="figure", target_id="banner")
    assert o.Document.from_json(d.to_json()).to_dict() == d.to_dict()
    assert c.valuation.low == 20_100_000  # never stored as 20.1
    assert c.to_dict()["displayScale"] == "million"


@pytest.mark.parametrize(
    "field,value",
    [
        ("currency", "gbp"),
        ("currency", "GB"),
        ("currency", "GBP\n"),
        ("currency", " USD"),
        ("currency", 123),
        ("asOf", "2026-02-29"),
        ("asOf", "2026-08"),
        ("asOf", "2026-08-05T00:00:00Z"),
        ("asOf", None),
        ("subject", {}),
        ("subject", {"en": " "}),
        ("displayScale", "millions"),
        ("displayPrecision", True),
        ("displayPrecision", 1.0),
        ("displayPrecision", -1),
        ("displayPrecision", 7),
        ("valueBasis", "unknown"),
        ("capitalBasis", "unknown"),
        ("dataBasis", "observed"),
        ("title", {}),
        ("notes", None),
        ("backgroundColor", "blue"),
        ("valueBasis", "enterprise_value"),
    ],
)
def test_invalid_banner_field_is_not_generic(field, value):
    raw = result()
    raw[field] = value
    with pytest.raises(ValidationError):
        document(raw)
    report = o.validate_document_payload(
        {"schemaVersion": "report.v1.5", "datasets": {"charts": [raw]}}
    )
    assert not report.is_valid
    assert any("datasets.charts[0]" in (i.path or "") for i in report.issues)


@pytest.mark.parametrize(
    "amount",
    [
        {"kind": "range", "low": 2, "high": 1},
        {"kind": "range", "low": 1},
        {"kind": "range", "low": "1", "high": 2},
        {"kind": "range", "low": True, "high": 2},
        {"kind": "range", "low": 1, "high": float("inf")},
        {"kind": "point", "value": float("nan")},
        {"kind": "point", "value": 1, "low": 0, "high": 2},
        {"kind": "point", "value": None},
        {"value": 1},
        {"kind": "range", "low": 0, "high": 1, "center": 0.5},
    ],
)
def test_invalid_amount(amount):
    raw = result()
    raw["valuation"] = amount
    with pytest.raises(ValidationError):
        document(raw)


@pytest.mark.parametrize("value", [0, -1, 0.125, 10**15])
def test_point_and_degenerate_range_preserve_values(value):
    raw = result()
    raw["valuation"] = o.valuation_point(value).to_dict()
    assert document(raw).datasets.charts[0].valuation.value == value
    raw["valuation"] = o.valuation_range(value, value).to_dict()
    assert document(raw).datasets.charts[0].valuation.low == value


@pytest.mark.parametrize(
    "field", ["subject", "valuation", "currency", "valueBasis", "asOf", "dataBasis"]
)
def test_required_semantics(field):
    raw = result()
    del raw[field]
    with pytest.raises(ValidationError):
        document(raw)


@pytest.mark.parametrize(
    "version",
    ["report.v1", "report.v1.0", "report.v1.1", "report.v1.2", "report.v1.3", "report.v1.4"],
)
def test_old_custom_roundtrip_but_typed_authoring_requires_v15(version):
    raw = {"id": "custom", "chartType": "valuation_result", "oldPayload": [3, 1]}
    d = document(raw, version)
    assert isinstance(d.datasets.charts[0], o.GenericChartDataset)
    assert d.validate().is_valid
    assert o.Document.from_json(d.to_json()).to_dict() == d.to_dict()
    d.schemaVersion = "report.v1.5"
    assert not d.validate().is_valid
    with pytest.raises(ValueError):
        d.to_json()
    old = o.create_document(schema_version=version)
    typed = o.ValuationResultChartDataset(**result())
    with pytest.raises(ValueError, match="report.v1.5"):
        old.add_chart_dataset(typed)
    old.datasets.charts.append(typed)
    assert "protocol.version_mismatch" in old.validate().codes()
    with pytest.raises(ValueError):
        old.to_json()


def test_explicit_v14_stays_v14_and_v14_fixtures_load_in_v15():
    raw = json.loads((Path(__file__).parents[1] / "docs/protocol/v1.4-example.json").read_text())
    old = o.Document.from_dict(raw)
    assert o.Document.from_json(old.to_json()).schemaVersion == "report.v1.4"
    raw["schemaVersion"] = "report.v1.5"
    d = o.Document.from_dict(raw)
    assert d.validate().is_valid
    assert o.Document.from_json(d.to_json()).to_dict() == d.to_dict()


def test_invalid_known_generic_and_post_mutation_errors():
    generic = o.GenericChartDataset(id="bad", chartType="valuation_result", extraData=1)
    with pytest.raises(ValidationError):
        o.create_document().add_chart_dataset(generic)
    d = document(result())
    d.datasets.charts[0].valuation.low = 99_000_000
    r = d.validate()
    assert not r.is_valid and any("high" in (i.path or "") for i in r.issues)
    d = document(result())
    d.datasets.charts[0].capitalBasis = "post_money"
    d.datasets.charts[0].valueBasis = "asset_value"
    assert not d.validate().is_valid


def test_input_is_not_modified_and_unknown_types_remain_generic():
    raw = result()
    original = deepcopy(raw)
    document(raw)
    assert raw == original
    assert isinstance(
        document({"id": "x", "chartType": "external-widget"}).datasets.charts[0],
        o.GenericChartDataset,
    )
