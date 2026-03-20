from ova_portable_text import (
    bibliography_entry,
    create_document,
    footnote_entry,
    glossary_entry,
    image_asset,
    paragraph,
    pie_chart_from_parallel_arrays,
    section,
    table_column,
    table_dataset,
    xref,
    footnote_ref,
    glossary_term,
    citation_ref,
)


def test_document_validate_success_for_resolvable_document():
    report = create_document(title="Validated Demo", language="en")

    report.add_image_asset(image_asset(id="img-1", src="https://example.com/a.png", alt="A"))
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
    report.add_bibliography_entry(bibliography_entry(id="cite-1", title="Reference 1", authors=["Smith"], year=2024))
    report.add_footnote(footnote_entry(id="fn-1", blocks=[paragraph("Footnote 1")]))
    report.add_glossary_entry(glossary_entry(id="term-1", term="EBITDA", definition="A metric"))

    intro = section(id="sec-intro", level=1, title="Introduction")
    intro.append_paragraph(
        "See ",
        xref(target_type="section", target_id="sec-method"),
        ", note ",
        footnote_ref("fn-1"),
        ", term ",
        glossary_term("term-1"),
        ", and source ",
        citation_ref("cite-1"),
        ".",
    )
    intro.append_image(id="fig-1", image_ref="img-1")
    intro.append_chart(id="chart-inst-1", chart_ref="chart-1")
    intro.append_table(id="tbl-1", table_ref="table-1")

    method = section(id="sec-method", level=1, title="Method")
    method.append_paragraph("Method body")

    report.append_section(intro)
    report.append_section(method)

    validation = report.validate()

    assert validation.isValid is True
    assert validation.issues == []
    assert report.assert_valid() is report
