from ova_portable_text import create_document, section, span


def test_validation_reports_unresolved_mark_reference():
    report = create_document(title="Broken Marks", language="en")
    sec = section(id="sec-1", level=1, title="Marks")
    sec.append_paragraph("Visit ", span("OpenAI", marks=["missing-link-key"]), ".")
    report.append_section(sec)

    validation = report.validate()
    codes = {issue.code for issue in validation.issues}

    assert validation.isValid is False
    assert "unresolved_mark_reference" in codes
