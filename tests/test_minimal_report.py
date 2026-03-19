from ova_portable_text import Document, DocumentMeta, Section


def test_minimal_report_shape() -> None:
    doc = Document(meta=DocumentMeta(title="Patent Valuation Report", language="en"))

    summary = Section(id="sec-1", level=1, title="Executive Summary")
    summary.append_paragraph("This is the opening introduction of the chapter.")

    background = Section(id="sec-1-1", level=2, title="Background")
    background.append_paragraph("This is the body text of subsection 1.1.")
    summary.append_subsection(background)

    summary.append_paragraph("This is a concluding paragraph after subsection 1.1.")
    doc.append_section(summary)

    data = doc.to_dict()

    assert data["schemaVersion"] == "report.v1"
    assert data["meta"]["title"] == "Patent Valuation Report"
    assert data["sections"][0]["id"] == "sec-1"
    assert data["sections"][0]["body"][0]["itemType"] == "content"
    assert data["sections"][0]["body"][1]["itemType"] == "subsection"
    assert data["sections"][0]["body"][2]["blocks"][0]["children"][0]["text"] == (
        "This is a concluding paragraph after subsection 1.1."
    )
