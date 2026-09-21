"""Build a generic v1.4 report with a timeline and a composed valuation figure.

Run: python examples/v14_report.py /tmp/v14-report.json
"""

import sys
from pathlib import Path

from ova_portable_text import (
    ChartBlock,
    axis_domain,
    chart_axis,
    chart_category,
    create_document,
    grid_table_cell,
    grid_table_dataset,
    grid_table_row,
    partial_date,
    range_chart_dataset,
    range_point,
    range_series,
    section,
    timeline_chart_dataset,
    timeline_event,
)


def build_report():
    report = create_document(title="Example company report", language="en")
    timeline = timeline_chart_dataset(
        id="chart-history",
        as_of="2026-09-01",
        events=[
            timeline_event(
                key="founded",
                start=partial_date("2020", precision="year"),
                label={"en": "Company founded"},
                status="occurred",
            ),
            timeline_event(
                key="pilot",
                start=partial_date("2027-03", precision="month"),
                label={"en": "Planned pilot"},
                status="planned",
            ),
        ],
    )
    valuation = range_chart_dataset(
        id="chart-value",
        value_unit="GBP million",
        data_basis="illustrative",
        categories=[chart_category(key="method-a", en="Method A")],
        x_axis=chart_axis(value_type="number", domain=axis_domain(min=0, max=20)),
        series=[
            range_series(
                key="valuation",
                label={"en": "Illustrative valuation range"},
                data_role="estimated",
                points=[range_point(key="a", category_key="method-a", low=10, high=15, center=12)],
            )
        ],
    )
    report.add_chart_dataset(timeline).add_chart_dataset(valuation)
    report.add_table_dataset(
        grid_table_dataset(
            id="layout-overview",
            column_count=2,
            rows=[
                grid_table_row(
                    grid_table_cell(blocks=[ChartBlock(chartRef=timeline.id)]),
                    grid_table_cell(blocks=[ChartBlock(chartRef=valuation.id)]),
                )
            ],
        )
    )
    overview = section(id="sec-overview", level=1, title="Overview")
    overview.append_figure_with_caption(
        id="fig-overview",
        layout_ref="layout-overview",
        caption="Company milestones and illustrative valuation; values are not measured data.",
    )
    report.append_section(overview)
    return report.assert_valid()


if __name__ == "__main__":
    destination = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("v14-report.json")
    print(build_report().save_json(destination))
