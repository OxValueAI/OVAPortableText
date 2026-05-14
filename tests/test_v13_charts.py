from __future__ import annotations

from ova_portable_text import (
    Document,
    bar_chart_dataset,
    bar_data_point,
    bar_series,
    chart_axis,
    chart_category,
    create_document,
    horizontal_bar_chart_dataset,
    line_chart_dataset,
    line_point,
    line_series,
    matrix_bubble_category,
    matrix_bubble_chart_dataset,
    matrix_bubble_point,
    matrix_bubble_series,
    pie_chart_dataset,
    pie_slice,
    section,
    size_metric,
    validate_document,
)


def test_default_schema_version_is_report_v13() -> None:
    assert create_document(title="v1.3").to_dict()["schemaVersion"] == "report.v1.3"


def test_pie_color_hint_is_preserved() -> None:
    chart = pie_chart_dataset(
        id="chart-pie",
        value_unit="percent",
        slices=[pie_slice(key="tech", value=60, en="Technology", zh="技术", color_hint="#3366cc")],
    )

    data = chart.to_dict()
    assert data["chartType"] == "pie"
    assert data["slices"][0]["colorHint"] == "#3366cc"


def test_vertical_grouped_and_stacked_bar_chart_datasets() -> None:
    categories = [
        chart_category(key="2024", en="2024", zh="2024"),
        chart_category(key="2025", en="2025", zh="2025"),
    ]
    applications = bar_series(
        key="applications",
        en="Patent Applications",
        zh="申请专利数量",
        data=[
            bar_data_point(category_key="2024", value=7),
            bar_data_point(category_key="2025", value=9),
        ],
    )
    publications = bar_series(
        key="publications",
        en="Patent Publications",
        zh="公开专利数量",
        data=[
            bar_data_point(category_key="2024", value=5),
            bar_data_point(category_key="2025", value=8),
        ],
    )

    grouped = bar_chart_dataset(
        id="chart-bar-grouped",
        value_unit="count",
        categories=categories,
        series=[applications, publications],
        x_axis=chart_axis(en="Application Year", zh="申请年", value_type="year"),
        y_axis=chart_axis(en="Patent Count", zh="专利数量", value_type="number", unit="count"),
    ).to_dict()
    stacked = bar_chart_dataset(
        id="chart-bar-stacked",
        value_unit="count",
        bar_mode="stacked",
        categories=categories,
        series=[applications, publications],
    ).to_dict()

    assert grouped["chartType"] == "bar"
    assert grouped["orientation"] == "vertical"
    assert grouped["barMode"] == "grouped"
    assert grouped["categories"][0]["key"] == "2024"
    assert grouped["series"][0]["data"][0]["categoryKey"] == "2024"
    assert grouped["series"][0]["data"][0]["value"] == 7
    assert stacked["barMode"] == "stacked"


def test_horizontal_bar_uses_bar_chart_type_not_horizontal_bar() -> None:
    chart = horizontal_bar_chart_dataset(
        id="chart-horizontal-bar",
        value_unit="count",
        categories=[chart_category(key="cat-a", en="Category A", zh="类别A")],
        series=[
            bar_series(
                key="count",
                en="Count",
                zh="数量",
                data=[bar_data_point(category_key="cat-a", value=120)],
            )
        ],
        x_axis=chart_axis(en="Count", zh="数量", value_type="number", unit="count"),
        y_axis=chart_axis(en="Category", zh="类别", value_type="category"),
    ).to_dict()

    assert chart["chartType"] == "bar"
    assert chart["orientation"] == "horizontal"
    assert chart["chartType"] != "horizontal_bar"


def test_line_uses_x_value_y_value_and_label_not_categories() -> None:
    chart = line_chart_dataset(
        id="chart-lifecycle-line",
        value_unit="count",
        x_axis=chart_axis(en="Patent Count", zh="专利数量", value_type="number", unit="count"),
        y_axis=chart_axis(en="Applicant Count", zh="申请人数量", value_type="number", unit="count"),
        series=[
            line_series(
                key="lifecycle",
                en="Application time, applicant count and patent count",
                zh="申请时间、申请人数量、专利数量",
                points=[
                    line_point(key="2016", x_value=300, y_value=180, en="2016", zh="2016"),
                    line_point(key="2017", x_value=700, y_value=400, en="2017", zh="2017"),
                ],
            )
        ],
    ).to_dict()

    assert chart["chartType"] == "line"
    assert "categories" not in chart
    assert chart["series"][0]["points"][0]["xValue"] == 300
    assert chart["series"][0]["points"][0]["yValue"] == 180
    assert chart["series"][0]["points"][0]["label"] == {"en": "2016", "zh": "2016"}


def test_matrix_bubble_uses_category_keys_size_metric_unit_and_size_value() -> None:
    chart = matrix_bubble_chart_dataset(
        id="chart-category-matrix-bubble",
        x_axis=chart_axis(en="Technology Category", zh="技术分类", value_type="category"),
        y_axis=chart_axis(en="Market Region", zh="市场区域", value_type="category"),
        x_categories=[matrix_bubble_category(key="ai", en="AI", zh="人工智能")],
        y_categories=[matrix_bubble_category(key="china", en="China", zh="中国")],
        size_metric=size_metric(en="Patent Count", zh="专利数量", unit="count"),
        series=[
            matrix_bubble_series(
                key="patent-count",
                en="Patent Count",
                zh="专利数量",
                points=[
                    matrix_bubble_point(
                        key="ai-china",
                        x_category_key="ai",
                        y_category_key="china",
                        size_value=45,
                    )
                ],
            )
        ],
    ).to_dict()

    assert chart["chartType"] == "matrix_bubble"
    assert chart["chartType"] != "bubble"
    assert "valueUnit" not in chart
    assert chart["sizeMetric"]["unit"] == "count"
    assert "valueUnit" not in chart["sizeMetric"]
    assert chart["series"][0]["points"][0]["xCategoryKey"] == "ai"
    assert chart["series"][0]["points"][0]["yCategoryKey"] == "china"
    assert chart["series"][0]["points"][0]["sizeValue"] == 45
    assert "xValue" not in chart["series"][0]["points"][0]
    assert "yValue" not in chart["series"][0]["points"][0]


def test_legacy_size_metric_value_unit_input_roundtrips_to_unit_output() -> None:
    restored = Document.from_dict(
        {
            "schemaVersion": "report.v1.3",
            "meta": {},
            "theme": {},
            "assets": {"images": [], "logos": [], "backgrounds": [], "icons": [], "attachments": []},
            "datasets": {
                "charts": [
                    {
                        "id": "chart-legacy-size-unit",
                        "chartType": "matrix_bubble",
                        "sizeMetric": {"label": {"en": "Patent Count"}, "valueUnit": "count"},
                        "xCategories": [{"key": "ai", "label": {"en": "AI"}}],
                        "yCategories": [{"key": "china", "label": {"en": "China"}}],
                        "series": [
                            {
                                "key": "patent-count",
                                "label": {"en": "Patent Count"},
                                "points": [
                                    {"xCategoryKey": "ai", "yCategoryKey": "china", "sizeValue": 1}
                                ],
                            }
                        ],
                    }
                ],
                "tables": [],
                "metrics": [],
            },
            "bibliography": [],
            "footnotes": [],
            "glossary": [],
            "sections": [],
        }
    )

    chart = restored.to_dict()["datasets"]["charts"][0]
    assert chart["sizeMetric"]["unit"] == "count"
    assert "valueUnit" not in chart["sizeMetric"]


def test_v13_chart_example_document_serializes_and_validates() -> None:
    report = create_document(title="v1.3 charts", language="en")
    report.add_chart_dataset(
        line_chart_dataset(
            id="chart-line",
            series=[line_series(key="s", en="Series", points=[line_point(x_value=1, y_value=2)])],
        )
    )
    sec = section(id="sec-charts", level=1, title="Charts")
    sec.append_chart(chart_ref="chart-line")
    report.append_section(sec)

    data = report.to_dict()
    assert data["schemaVersion"] == "report.v1.3"
    assert data["datasets"]["charts"][0]["chartType"] == "line"
    assert validate_document(report).is_valid
