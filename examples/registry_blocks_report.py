from ova_portable_text import (
    bibliography_entry,
    create_document,
    footnote_entry,
    glossary_entry,
    paragraph,
    pie_chart_from_parallel_arrays,
    section,
    table_column,
    table_dataset,
    xref,
    image_asset,
)


report = create_document(
    title="OVAPortableText Step 3 Demo",
    language="en",
    documentType="report",
)

# Add registry entries / 追加顶层 registry 条目
report.add_image_asset(
    image_asset(
        id="img-pipeline-overview",
        label="Pipeline overview image",
        src="https://example.com/pipeline-overview.png",
        alt="Pipeline overview",
    )
)

report.add_table_dataset(
    table_dataset(
        id="table-financial-summary",
        label="Financial summary table",
        columns=[
            table_column(key="year", header="Year"),
            table_column(key="revenue", header="Revenue"),
            table_column(key="margin", header="Margin"),
        ],
        rows=[
            {"year": "2022", "revenue": "12.3M", "margin": "18%"},
            {"year": "2023", "revenue": "15.8M", "margin": "21%"},
        ],
    )
)

report.add_chart_dataset(
    pie_chart_from_parallel_arrays(
        id="chart-area-share",
        label="Area share pie chart",
        value_unit="percent",
        area_en=["Technology", "Finance", "Healthcare"],
        area_zh=["技术", "金融", "医疗"],
        value=[42.5, 31.2, 26.3],
        description_en=[
            "Technology contributes the largest share.",
            "Finance is the second largest segment.",
            "Healthcare remains an important contributor.",
        ],
        description_zh=[
            "技术板块占比最高。",
            "金融板块位居第二。",
            "医疗板块仍然是重要贡献来源。",
        ],
    )
)

report.add_bibliography_entry(
    bibliography_entry(id="cite-smith-2024", text="Smith (2024). Valuation methodology overview.")
)
report.add_footnote(
    footnote_entry(id="fn-1", blocks=[paragraph("Adjusted EBITDA excludes certain non-recurring items.")])
)
report.add_glossary_entry(
    glossary_entry(id="term-ebitda", term="EBITDA", definition="Earnings before interest, taxes, depreciation and amortization.")
)

# Add body content / 追加正文内容
intro = section(id="sec-intro", level=1, title="Introduction")
intro.append_paragraph("This section introduces the report.")
intro.append_image(id="fig-pipeline-overview", image_ref="img-pipeline-overview")
intro.append_figure_caption("Figure 1. Pipeline overview")
intro.append_chart(id="fig-area-share", chart_ref="chart-area-share")
intro.append_figure_caption("Figure 2. Area share pie chart")
intro.append_table(id="tbl-financial-summary", table_ref="table-financial-summary")
intro.append_table_caption("Table 1. Financial summary")
intro.append_paragraph("See ", xref(target_type="section", target_id="sec-method"), " for more details.")

method = section(id="sec-method", level=1, title="Methodology")
method.append_subheading("DCF core equation")
method.append_math(id="eq-dcf-core", latex=r"V = \sum_{t=1}^{n} \frac{CF_t}{(1+r)^t}")
method.append_equation_caption("Equation 1. Core DCF formula")

report.append_section(intro)
report.append_section(method)

print(report.to_json())
