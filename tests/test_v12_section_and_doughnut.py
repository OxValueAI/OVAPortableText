from ova_portable_text import (
    ChartBlock,
    create_document,
    doughnut_chart_dataset,
    pie_slice,
    section,
    validate_document,
)


def test_doughnut_chart_dataset_serializes_v12_fields():
    chart = doughnut_chart_dataset(
        id="chart-1",
        value_unit="percent",
        total=100,
        show_remainder_track=True,
        slices=[
            pie_slice(key="novelty", value=35, en="Novelty", zh="技术新颖性"),
            pie_slice(key="market", value=25, en="Market", zh="市场适用性"),
        ],
    )
    data = chart.to_dict()
    assert data["chartType"] == "doughnut"
    assert data["total"] == 100
    assert data["showRemainderTrack"] is True


def test_section_v12_fields_roundtrip_and_optional_chart_id():
    report = create_document(title="v1.2 Section")
    report.add_chart_dataset(
        doughnut_chart_dataset(
            id="chart-1",
            value_unit="percent",
            slices=[pie_slice(key="novelty", value=60, en="Novelty", zh="技术新颖性")],
        )
    )

    sec = section(
        id="sec-cover",
        level=1,
        title="封面",
        numbering="none",
        section_role="cover",
        navigation={"includeInToc": False},
        pagination={"pageBreakBefore": "always"},
        presentation={"templateVariant": "cover", "titleBlockStyle": "lead"},
    )
    sec.append_block(ChartBlock(chartRef="chart-1"))
    report.append_section(sec)

    data = report.to_dict()
    assert data["schemaVersion"] == "report.v1.2"
    assert data["sections"][0]["sectionRole"] == "cover"
    assert data["sections"][0]["navigation"]["includeInToc"] is False
    assert data["sections"][0]["pagination"]["pageBreakBefore"] == "always"
    assert data["sections"][0]["presentation"]["titleBlockStyle"] == "lead"
    assert data["sections"][0]["body"][0]["blocks"][0]["_type"] == "chart"
    assert "id" not in data["sections"][0]["body"][0]["blocks"][0]

    validation = validate_document(report)
    assert validation.is_valid, validation.to_text()
