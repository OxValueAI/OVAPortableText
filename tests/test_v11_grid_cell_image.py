import pytest

from ova_portable_text import (
    ChartBlock,
    ImageBlock,
    TableBlock,
    block_layout,
    create_document,
    doughnut_chart_dataset,
    grid_table_cell,
    grid_table_dataset,
    grid_table_row,
    image_asset_url,
    image_block,
    paragraph,
    pie_slice,
    table_block,
    table_layout,
    table_column_spec_weight,
    validate_document,
)


def test_grid_cell_blocks_support_text_image_and_chart():
    report = create_document(title="Grid Cell Image")
    report.add_image_asset(image_asset_url(id="img-1", url="https://example.com/a.png", alt="A"))
    report.add_chart_dataset(
        doughnut_chart_dataset(
            id="chart-1",
            value_unit="percent",
            slices=[
                pie_slice(key="a", value=35, en="A", zh="甲"),
                pie_slice(key="b", value=25, en="B", zh="乙"),
            ],
        )
    )
    report.datasets.append_table(
        grid_table_dataset(
            id="table-1",
            column_count=2,
            layout=table_layout(table_column_spec_weight(1), table_column_spec_weight(2)),
            rows=[
                grid_table_row(
                    grid_table_cell(text="Name", header=True),
                    grid_table_cell(
                        blocks=[
                            paragraph("System diagram", layout=block_layout(text_align="center")),
                            ChartBlock(chartRef="chart-1"),
                            image_block(image_ref="img-1"),
                        ]
                    ),
                )
            ],
        )
    )
    sec = report.new_section(id="sec-1", level=1, title="Demo")
    sec.append_block(table_block(table_ref="table-1", id="tbl-1"))

    validation = validate_document(report)
    assert validation.is_valid, validation.to_text()


def test_grid_cell_blocks_reject_unsupported_block_objects():
    with pytest.raises(ValueError, match="ChartBlock"):
        grid_table_cell(blocks=[TableBlock(tableRef="table-1")])


def test_grid_cell_image_ref_is_validated():
    report = create_document(title="Broken Grid Cell Image")
    report.datasets.append_table(
        grid_table_dataset(
            id="table-1",
            column_count=1,
            rows=[grid_table_row(grid_table_cell(blocks=[ImageBlock(imageRef="missing-img")]))],
        )
    )
    validation = validate_document(report)
    assert "unresolved_grid_cell_image_ref" in validation.codes()


def test_grid_cell_chart_ref_is_validated():
    report = create_document(title="Broken Grid Cell Chart")
    report.datasets.append_table(
        grid_table_dataset(
            id="table-1",
            column_count=1,
            rows=[grid_table_row(grid_table_cell(blocks=[ChartBlock(chartRef="missing-chart")]))],
        )
    )
    validation = validate_document(report)
    assert "unresolved_grid_cell_chart_ref" in validation.codes()
