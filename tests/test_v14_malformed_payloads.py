"""Malformed external JSON must produce diagnostics, not internal exceptions."""

from copy import deepcopy

import pytest

from ova_portable_text import validate_document_payload

BAD_CONTAINERS = [None, False, 7, "invalid", {}, [None]]


def chart(kind):
    if kind == "line":
        return {
            "id": "c",
            "chartType": kind,
            "dataBasis": "illustrative",
            "series": [{"key": "s", "points": [{"xValue": 1, "yValue": 2}]}],
        }
    return {
        "id": "c",
        "chartType": kind,
        "dataBasis": "illustrative",
        "categories": [{"key": "a"}],
        "series": [{"key": "s", "data": [{"categoryKey": "a", "value": 2}]}],
    }


@pytest.mark.parametrize("kind", ["line", "bar"])
@pytest.mark.parametrize("bad", BAD_CONTAINERS)
@pytest.mark.parametrize("field", ["series", "observations", "xAxis"])
def test_malformed_chart_containers_return_diagnostics(kind, bad, field):
    data = chart(kind)
    if field == "observations":
        field = "points" if kind == "line" else "data"
        data["series"][0][field] = deepcopy(bad)
    else:
        data[field] = deepcopy(bad)
    report = validate_document_payload({"datasets": {"charts": [data]}})
    # An omitted-equivalent legacy axis or empty axis remains legal.
    if field == "xAxis" and (bad is None or bad == {}):
        assert report.is_valid
    else:
        assert not report.is_valid
        assert any(field in issue.path for issue in report.issues)


@pytest.mark.parametrize("version", ["report.v1.3", "report.v1.4"])
@pytest.mark.parametrize("bad", BAD_CONTAINERS)
def test_invalid_chart_discriminators_return_diagnostics(version, bad):
    report = validate_document_payload(
        {
            "schemaVersion": version,
            "datasets": {"charts": [{"id": "c", "chartType": deepcopy(bad)}]},
        }
    )
    if bad == "invalid":  # Unknown custom chart names are intentionally preserved.
        assert report.is_valid
    else:
        assert not report.is_valid


@pytest.mark.parametrize("bad", [None, False, 7, "invalid", {}])
def test_malformed_legacy_chart_registry_is_not_rewritten(bad):
    report = validate_document_payload(
        {"schemaVersion": "report.v1.3", "datasets": {"charts": bad}}
    )
    assert not report.is_valid


@pytest.mark.parametrize("bad", [[], {}])
def test_unhashable_schema_version_is_reported(bad):
    assert not validate_document_payload({"schemaVersion": bad}).is_valid
