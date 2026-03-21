from ova_portable_text import create_document, section, xref


def test_validation_issue_contains_context_fields() -> None:
    report = create_document(title="Context Demo", language="en")
    sec = section(id="sec-a", level=1, title="Section A")
    sec.append_paragraph("See ", xref(target_type="figure", target_id="fig-missing"), ".")
    report.append_section(sec)

    validation = report.validate()

    assert validation.isValid is False
    assert validation.error_count >= 1
    issue = next(issue for issue in validation.issues if issue.code == "unresolved_xref")
    assert issue.sectionId == "sec-a"
    assert issue.sectionTitle == "Section A"
    assert issue.contextType == "xref"
    assert issue.suggestion is not None
    assert "targetType" in issue.message


def test_validation_report_to_text_contains_summary() -> None:
    report = create_document(title="Context Demo", language="en")
    sec = section(id="sec-a", level=1, title="Section A")
    sec.append_paragraph("See ", xref(target_type="bad_type", target_id="x"), ".")
    report.append_section(sec)

    text = report.validate().to_text()
    assert "OVAPortableText validation report:" in text
    assert "errors=" in text
    assert "section=sec-a (Section A)" in text
    assert "suggestion=" in text
