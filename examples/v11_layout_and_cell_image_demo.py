from ova_portable_text import (
    block_layout,
    create_document,
    grid_table_cell,
    grid_table_dataset,
    grid_table_row,
    image_asset_url,
    image_block,
    length_em,
    length_pt,
    paragraph,
    table_block,
    table_column_spec_weight,
    table_layout,
)


report = create_document(
    title="OVAPortableText v1.1 demo",
    language="en",
    theme={
        "blockStyleDefaults": {
            "normal": {
                "layout": {
                    "textAlign": "justify",
                    "firstLineIndent": {"unit": "em", "value": 2},
                    "spaceAfter": {"unit": "pt", "value": 6},
                }
            },
            "table_caption": {
                "layout": {"textAlign": "center"}
            },
        }
    },
)

report.add_image_asset(
    image_asset_url(
        id="img-system-overview",
        url="https://example.com/system-overview.png",
        alt="System overview",
        mimeType="image/png",
    )
)

report.datasets.append_table(
    grid_table_dataset(
        id="table-demo-grid",
        column_count=2,
        layout=table_layout(
            table_column_spec_weight(3),
            table_column_spec_weight(7),
        ),
        rows=[
            grid_table_row(
                grid_table_cell(text="Item", header=True, align="center"),
                grid_table_cell(text="Detail", header=True, align="center"),
            ),
            grid_table_row(
                grid_table_cell(text="Diagram", vertical_align="middle"),
                grid_table_cell(
                    blocks=[
                        paragraph(
                            "Image inside a grid cell.",
                            layout=block_layout(text_align="center", space_after=length_pt(4)),
                        ),
                        image_block(image_ref="img-system-overview"),
                    ]
                ),
            ),
        ],
    )
)

sec = report.new_section(id="sec-demo", level=1, title="Demo")
sec.append_paragraph(
    "This paragraph overrides the default block style layout.",
    layout=block_layout(text_align="center", first_line_indent=length_em(0)),
)
sec.append_block(table_block(id="tbl-demo-1", table_ref="table-demo-grid"))
sec.append_table_caption("Table 1. Grid table with weighted columns and a cell image.")

report.assert_valid()
print(report.to_json(indent=2))
