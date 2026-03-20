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
    citation_ref,
    footnote_ref,
    glossary_term,
)


report = create_document(
    title="OVAPortableText Step 4 Demo",
    language="en",
    documentType="report",
)

report.add_image_asset(image_asset(id="img-overview", src="https://example.com/overview.png", alt="Overview"))
report.add_table_dataset(
    table_dataset(
        id="table-summary",
        columns=[
            table_column(key="year", header="Year"),
            table_column(key="revenue", header="Revenue"),
        ],
        rows=[
            {"year": "2023", "revenue": "12.0M"},
            {"year": "2024", "revenue": "15.4M"},
        ],
    )
)
report.add_chart_dataset(
    pie_chart_from_parallel_arrays(
        id="chart-share",
        area_en=["Technology", "Finance", "Healthcare"],
        area_zh=["技术", "金融", "医疗"],
        value=[45, 30, 25],
    )
)
report.add_bibliography_entry(bibliography_entry(id="cite-1", text="Smith (2024). Demo reference."))
report.add_footnote(footnote_entry(id="fn-1", blocks=[paragraph("Footnote content goes here.")]))
report.add_glossary_entry(glossary_entry(id="term-1", term="EBITDA", definition="A common financial metric."))

intro = section(id="sec-intro", level=1, title="Introduction")
intro.append_paragraph(
    "See ",
    xref(target_type="section", target_id="sec-method"),
    " for methodology. ",
    "Source ",
    citation_ref("cite-1"),
    ", note ",
    footnote_ref("fn-1"),
    ", term ",
    glossary_term("term-1"),
    ".",
)
intro.append_image(id="fig-overview", image_ref="img-overview")
intro.append_figure_caption("Figure 1. Overview image")
intro.append_chart(id="fig-share", chart_ref="chart-share")
intro.append_figure_caption("Figure 2. Area share")
intro.append_table(id="tbl-summary", table_ref="table-summary")
intro.append_table_caption("Table 1. Summary table")

method = section(id="sec-method", level=1, title="Methodology")
method.append_paragraph("The methodology section is intentionally short in this demo.")

report.append_section(intro)
report.append_section(method)

resolver = report.build_resolver()
validation = report.validate()

print("Validation is valid:", validation.isValid)
print("Resolvable targets:", sorted(resolver.targetsById.keys()))
print(report.to_json())
