"""Grid-table demo / grid 表格示例。"""

from __future__ import annotations

from ova_portable_text import (
    create_document,
    grid_table_cell,
    grid_table_dataset,
    grid_table_row,
    paragraph,
    table_block,
    table_column,
    table_dataset,
)


def main() -> None:
    report = create_document(
        title="Grid Table Demo",
        language="en",
        documentType="valuationReport",
        strict_ids=True,
    )

    report.add_table_dataset(
        table_dataset(
            id="table-record",
            columns=[
                table_column(key="score_a", header="Score"),
                table_column(key="score_b", header="Score"),
                table_column(key="comment", header="Comment"),
            ],
            rows=[
                {"score_a": 82, "score_b": 88, "comment": "Duplicate headers are allowed."},
                {"score_a": 79, "score_b": 85, "comment": "Column keys stay unique."},
            ],
            label="Record table with duplicate headers",
        )
    )

    report.add_table_dataset(
        grid_table_dataset(
            id="table-grid",
            column_count=3,
            rows=[
                grid_table_row(
                    grid_table_cell(text="Module", header=True),
                    grid_table_cell(text="Metric", header=True),
                    grid_table_cell(text="Note", header=True),
                ),
                grid_table_row(
                    grid_table_cell(text="Technology", row_span=2),
                    grid_table_cell(text="Novelty"),
                    grid_table_cell(text="Measures differentiation"),
                ),
                grid_table_row(
                    grid_table_cell(text="Stability"),
                    grid_table_cell(blocks=[paragraph("Rendered from `blocks` inside a grid cell.")]),
                ),
            ],
            label="Grid table with rowSpan and irregular rows",
        )
    )

    sec = report.new_section(id="sec-tables", level=1, title="Tables")
    sec.append_paragraph("This section shows both `record` and `grid` table datasets.")
    sec.append_table_with_caption(
        id="tbl-record-instance",
        table_ref="table-record",
        caption="Table: Record-mode dataset with duplicate display headers.",
    )
    sec.append_table_with_caption(
        id="tbl-grid-instance",
        table_ref="table-grid",
        caption="Table: Grid-mode dataset with irregular row shapes.",
    )

    report.assert_valid()
    print(report.to_json(indent=2))


if __name__ == "__main__":
    main()
