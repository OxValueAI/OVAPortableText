from __future__ import annotations

from ova_portable_text import (
    bar_chart_dataset,
    bar_data_point,
    bar_series,
    chart_axis,
    chart_category,
    create_document,
    line_chart_dataset,
    line_point,
    line_series,
    matrix_bubble_category,
    matrix_bubble_chart_dataset,
    matrix_bubble_point,
    matrix_bubble_series,
    section,
    size_metric,
)


def build_report():
    report = create_document(title="OVA Portable Text v1.3 Charts Demo", language="en")

    bar = bar_chart_dataset(
        id="chart-patent-counts-by-year",
        value_unit="count",
        categories=[
            chart_category(key="2024", en="2024", zh="2024"),
            chart_category(key="2025", en="2025", zh="2025"),
        ],
        series=[
            bar_series(
                key="applications",
                en="Patent Applications",
                zh="申请专利数量",
                data=[
                    bar_data_point(category_key="2024", value=7),
                    bar_data_point(category_key="2025", value=9),
                ],
            )
        ],
        x_axis=chart_axis(en="Application Year", zh="申请年", value_type="year"),
        y_axis=chart_axis(en="Patent Count", zh="专利数量", value_type="number", unit="count"),
    )

    line = line_chart_dataset(
        id="chart-lifecycle-line",
        value_unit="count",
        x_axis=chart_axis(en="Patent Count", zh="专利数量", value_type="number", unit="count"),
        y_axis=chart_axis(en="Applicant Count", zh="申请人数量", value_type="number", unit="count"),
        series=[
            line_series(
                key="lifecycle",
                en="Lifecycle",
                zh="生命周期",
                points=[
                    line_point(key="2016", x_value=300, y_value=180, en="2016", zh="2016"),
                    line_point(key="2017", x_value=700, y_value=400, en="2017", zh="2017"),
                ],
            )
        ],
    )

    matrix = matrix_bubble_chart_dataset(
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
    )

    report.add_chart_dataset(bar).add_chart_dataset(line).add_chart_dataset(matrix)

    charts = section(id="sec-v13-charts", level=1, title="v1.3 Charts")
    charts.append_chart(chart_ref="chart-patent-counts-by-year")
    charts.append_chart(chart_ref="chart-lifecycle-line")
    charts.append_chart(chart_ref="chart-category-matrix-bubble")
    report.append_section(charts)
    return report


if __name__ == "__main__":
    print(build_report().to_json())
