from ova_portable_text import create_document, section, xref


report = create_document(
    title="Validation Context Demo",
    language="en",
    documentType="valuationReport",
)

sec = section(id="sec-ctx", level=1, title="Context Aware Validation")
sec.append_paragraph(
    "See ",
    xref(target_type="figure", target_id="fig-missing"),
    " for the missing figure reference.",
)
report.append_section(sec)

validation = report.validate()
print(validation.to_text())
