import pytest

from ova_portable_text import DocumentValidationError, create_document, xref


def test_document_validation_error_contains_issue_context_text():
    report = create_document(title="Broken", language="en")
    sec = report.new_section(id="sec-1", level=1, title="Intro")
    sec.append_paragraph("See ", xref(target_type="section", target_id="missing-sec"))

    with pytest.raises(DocumentValidationError) as exc_info:
        report.assert_valid()

    message = str(exc_info.value)
    assert "unresolved_xref" in message
    assert "sec-1" in message
