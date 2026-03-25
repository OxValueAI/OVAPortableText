from __future__ import annotations

"""
A more business-shaped report example.
一个更接近业务报告形态的样例。

This is still only a protocol-construction demo, not a final PDF layout demo.
这仍然只是协议构造示例，不是最终 PDF 排版示例。
"""

from ova_portable_text import (
    bibliography_entry,
    create_document,
    footnote_entry,
    glossary_entry,
    image_asset_url,
    paragraph,
    pie_chart_from_parallel_arrays,
    table_column,
    table_dataset,
    xref,
)


def main() -> None:
    report = create_document(
        title="Patent Valuation Report",
        subtitle="Illustrative protocol example",
        language="en",
        documentType="valuationReport",
        author="OVA Demo",
        confidentiality="internal",
    )

    report.add_image_asset(
        image_asset_url(
            id="img-market-map",
            url="https://example.com/market-map.png",
            alt="Market landscape image",
            label="Market landscape",
        )
    )

    report.add_table_dataset(
        table_dataset(
            id="table-financial-summary",
            label="Financial summary table",
            columns=[
                table_column(key="year", header="Year"),
                table_column(key="revenue", header="Revenue"),
                table_column(key="ebitda", header="EBITDA"),
            ],
            rows=[
                {"year": "2023", "revenue": "11.2", "ebitda": "2.6"},
                {"year": "2024", "revenue": "13.1", "ebitda": "3.4"},
            ],
        )
    )

    report.add_chart_dataset(
        pie_chart_from_parallel_arrays(
            id="chart-area-share",
            label="Area share pie chart",
            area_en=["Technology", "Finance", "Healthcare"],
            area_zh=["技术", "金融", "医疗"],
            value=[52, 28, 20],
            description_en=[
                "Technology contributes the largest share.",
                "Finance is the second largest segment.",
                "Healthcare remains meaningful but smaller.",
            ],
            description_zh=[
                "技术板块占比最高。",
                "金融板块位居第二。",
                "医疗板块占比较小但仍具意义。",
            ],
            value_unit="percent",
        )
    )

    report.add_bibliography_entry(
        bibliography_entry(
            id="bib-market-2025",
            display_text="Research Team. Global Patent Market Review. 2025.",
            title="Global Patent Market Review",
            authors=["Research Team"],
            year=2025,
            type="report",
        )
    )
    report.add_footnote(footnote_entry(id="fn-1", blocks=[paragraph("Illustrative footnote only.")]))
    report.add_glossary_entry(
        glossary_entry(id="term-ip", term="IP", definition="Intellectual Property", short="IP")
    )

    sec = report.new_section(id="sec-1", level=1, title="Executive Summary")
    sec.append_lead("This report provides an illustrative valuation-oriented summary.")
    sec.append_paragraphs(
        "The company shows strong concentration in technology-related patent assets.",
        "Revenue quality and market position are reflected in both financial and IP indicators.",
    )
    sec.append_chart_with_caption(
        id="fig-area-share",
        chart_ref="chart-area-share",
        caption="Area share of portfolio value drivers.",
    )
    sec.append_paragraph("See ", xref(target_type="figure", target_id="fig-area-share"), " for the market-share view.")

    methodology = sec.new_subsection(id="sec-1-1", title="Methodology")
    methodology.append_bullet_items(
        "Review market and patent positioning.",
        "Cross-check financial and legal indicators.",
        "Aggregate value drivers into a structured report model.",
    )
    methodology.append_table_with_caption(
        id="tbl-financial-summary",
        table_ref="table-financial-summary",
        caption="Financial summary used in the illustrative analysis.",
    )

    appendix = report.new_section(id="sec-2", level=1, title="Appendix")
    appendix.append_image_with_caption(
        id="fig-market-map",
        image_ref="img-market-map",
        caption="Market landscape example image.",
    )

    validation = report.validate()
    print(validation.to_text())
    report.assert_valid()
    print(report.to_json()[:500])


if __name__ == "__main__":
    main()
