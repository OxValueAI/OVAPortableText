"""References and markDefs demo / 引用系统与 markDefs 示例。"""

from __future__ import annotations

from ova_portable_text import (
    bibliography_entry,
    citation_ref_def,
    create_document,
    footnote_entry,
    footnote_ref_def,
    glossary_entry,
    glossary_term_def,
    inline_math_def,
    link_def,
    paragraph,
    span,
    xref_def,
)


def main() -> None:
    report = create_document(
        title="References and Marks Demo",
        language="en",
        documentType="valuationReport",
        strict_ids=True,
    )

    report.add_bibliography_entry(
        bibliography_entry(
            id="cite-fu-2026",
            display_text="Fu et al. (2026)",
            type="article",
            title="Patent valuation under technical utility theory",
            authors=["Fu", "Wang"],
            year=2026,
            journal="Journal of Patent Studies",
        )
    )

    report.add_footnote(
        footnote_entry(
            id="fn-1",
            blocks=[paragraph("This footnote is stored in the top-level footnotes registry.")],
        )
    )

    report.add_glossary_entry(
        glossary_entry(
            id="term-dcf",
            term="DCF",
            definition="Discounted Cash Flow",
            aliases=["Discounted cash flow"],
        )
    )

    sec = report.new_section(id="sec-intro", level=1, title="Introduction")
    sec.append_paragraph(
        span("Open the project site", marks=["m-link"]),
        ". See ",
        span("the methodology section", marks=["m-xref"]),
        ", cite ",
        span("Fu et al. (2026)", marks=["m-cite"]),
        ", review note", 
        span("1", marks=["m-footnote"]),
        ", and hover ",
        span("DCF", marks=["m-term"]),
        ". Inline math: ",
        span("E = mc^2", marks=["m-math"]),
        ".",
        mark_defs=[
            link_def(key="m-link", href="https://example.com"),
            xref_def(key="m-xref", target_id="sec-method", target_type="section"),
            citation_ref_def(key="m-cite", target_id="cite-fu-2026"),
            footnote_ref_def(key="m-footnote", target_id="fn-1"),
            glossary_term_def(key="m-term", target_id="term-dcf"),
            inline_math_def(key="m-math", latex="E = mc^2"),
        ],
    )

    method = sec.new_subsection(id="sec-method", title="Methodology")
    method.append_paragraph("This subsection exists so the xref target resolves correctly.")

    report.assert_valid()
    print(report.to_json(indent=2))


if __name__ == "__main__":
    main()
