import pytest

from ova_portable_text import (
    ChartBlock,
    ImageBlock,
    block_layout,
    create_document,
    grid_table_cell,
    grid_table_dataset,
    grid_table_row,
    image_asset_url,
    image_block,
    paragraph,
    table_block,
    table_layout,
    table_column_spec_weight,
    validate_document,
)


def test_grid_cell_blocks_support_text_and_image():
    report = create_document(title="Grid Cell Image")
    report.add_image_asset(image_asset_url(id="img-1", url="https://example.com/a.png", alt="A"))
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
                            image_block(image_ref="img-1"),
                        ]
                    ),
                )
            ],
        )
    )
    sec = report.new_section(id="sec-1", level=1, title="Demo")
    sec.append_block(table_block(id="tbl-1", table_ref="table-1"))

    validation = validate_document(report)
    assert validation.is_valid, validation.to_text()


def test_grid_cell_blocks_reject_unsupported_block_objects():
    with pytest.raises(ValueError, match="TextBlock"):
        grid_table_cell(blocks=[ChartBlock(id="fig-1", chartRef="chart-1")])


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
