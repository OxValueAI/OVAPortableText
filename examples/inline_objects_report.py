"""Inline object example / 行内对象示例。"""

from ova_portable_text import (
    citation_ref,
    create_document,
    footnote_ref,
    glossary_term,
    hard_break,
    section,
    xref,
)

report = create_document(
    title="Inline Object Demo",
    language="en",
    documentType="report",
)

intro = section(id="sec-intro", level=1, title="Introduction")
intro.append_paragraph(
    "See ",
    xref(target_type="section", target_id="sec-method"),
    " for methodology.",
)
intro.append_paragraph(
    "Valuation uses EBITDA ",
    glossary_term("term-ebitda"),
    " adjustments",
    footnote_ref("fn-1"),
    ".",
)
intro.append_paragraph(
    "Evidence is provided in ",
    citation_ref("cite-smith-2024", "cite-jones-2025", mode="parenthetical"),
    ".",
)
intro.append_paragraph(
    "Line 1",
    hard_break(),
    "Line 2 inside the same paragraph.",
)

method = section(id="sec-method", level=1, title="Methodology")
method.append_subheading("Key assumptions")
method.append_paragraph("Assumption A")

report.append_section(intro)
report.append_section(method)

print(report.to_json())
