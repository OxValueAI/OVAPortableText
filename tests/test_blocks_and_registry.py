from ova_portable_text import (
    bibliography_entry,
    create_document,
    footnote_entry,
    glossary_entry,
    image_asset_url,
    pie_chart_from_parallel_arrays,
    paragraph,
    section,
    table_column,
    table_dataset,
)


def test_document_can_hold_registry_entries_and_block_objects():
    report = create_document(title="Demo", language="en")

    report.add_image_asset(
        image_asset_url(
            id="img-1",
            url="https://example.com/a.png",
            alt="Example image",
        )
    )
    report.add_table_dataset(
        table_dataset(
            id="table-1",
            columns=[table_column(key="year", header="Year")],
            rows=[{"year": "2024"}],
        )
    )
    report.add_chart_dataset(
        pie_chart_from_parallel_arrays(
            id="chart-1",
            area_en=["Technology", "Finance"],
            area_zh=["技术", "金融"],
            value=[60, 40],
        )
    )
    report.add_bibliography_entry(bibliography_entry(id="cite-1", display_text="Demo Reference"))
    report.add_footnote(footnote_entry(id="fn-1", blocks=[paragraph("Footnote content")]))
    report.add_glossary_entry(glossary_entry(id="term-1", term="EBITDA", definition="Demo definition"))

    sec = section(id="sec-1", level=1, title="Section 1")
    sec.append_image(id="fig-1", image_ref="img-1")
    sec.append_table(id="tbl-1", table_ref="table-1")
    sec.append_chart(id="chart-inst-1", chart_ref="chart-1")
    sec.append_math(id="eq-1", latex="x = y + z")
    report.append_section(sec)

    data = report.to_dict()

    assert data["assets"]["images"][0]["id"] == "img-1"
    assert data["datasets"]["tables"][0]["id"] == "table-1"
    assert data["datasets"]["charts"][0]["chartType"] == "pie"
    assert data["bibliography"][0]["id"] == "cite-1"
    assert data["footnotes"][0]["id"] == "fn-1"
    assert data["glossary"][0]["id"] == "term-1"
    assert data["sections"][0]["body"][0]["blocks"][0]["_type"] == "image"
    assert data["sections"][0]["body"][1]["blocks"][0]["_type"] == "table"
    assert data["sections"][0]["body"][2]["blocks"][0]["_type"] == "chart"
    assert data["sections"][0]["body"][3]["blocks"][0]["_type"] == "math_block"
