"""Opt-in v1.6 authoring example. This emits JSON; it does not render pages."""

import ova_portable_text as o


def build_report():
    report = o.create_document(
        schema_version="report.v1.6",
        title="Layout integration example",
        language="en",
        theme=o.PageThemeConfig(page=o.page_settings("portrait")),
    )
    data = o.record_table_dataset(
        id="financial-data",
        columns=[
            o.table_column(key="year", header="Year"),
            o.table_column(key="value", header="GBP"),
        ],
        rows=[{"year": "Year 1", "value": 1200000}, {"year": "Year 2", "value": 1500000}],
        layout=o.table_layout(
            o.table_column_spec_auto(align="left"),
            o.table_column_spec_weight(2, align="right"),
            header_defaults=o.cell_alignment(align="center"),
        ),
    )
    report.add_table_dataset(data)
    section = report.new_section(id="analysis", level=1, title="Financial analysis")
    section.append_paragraph("Portrait introduction. All amounts are illustrative.")
    section.append_object_with_captions(
        o.table_block(
            id="financial-table",
            table_ref=data.id,
            page=o.page_settings("landscape"),
            pagination=o.object_pagination(page_break_before="always", page_break_after="always"),
        ),
        before="Illustrative financial summary",
        after="Fictional example data; amounts in GBP.",
        before_layout=o.block_layout(text_align="center"),
        after_layout=o.block_layout(text_align="right"),
    )
    section.append_paragraph("Portrait content resumes here.")
    report.assert_valid()
    return report


if __name__ == "__main__":
    print(build_report().to_json())
