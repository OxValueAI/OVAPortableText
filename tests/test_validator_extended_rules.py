from ova_portable_text import DocumentValidationError, create_document, footnote_entry, section, xref


def test_duplicate_anchor_becomes_warning_but_document_can_still_be_valid():
    report = create_document(title="Anchor Warning Demo", language="en")
    report.append_section(section(id="sec-1", level=1, title="A", anchor="same-anchor"))
    report.append_section(section(id="sec-2", level=1, title="B", anchor="same-anchor"))

    validation = report.validate()

    assert validation.isValid is True
    assert any(issue.code == "duplicate_anchor" and issue.severity == "warning" for issue in validation.issues)


def test_empty_footnote_blocks_is_an_error():
    report = create_document(title="Footnote Demo", language="en")
    report.add_footnote(footnote_entry(id="fn-1", blocks=[]))

    validation = report.validate()

    assert validation.isValid is False
    assert any(issue.code == "empty_footnote_blocks" for issue in validation.issues)


def test_unsupported_xref_target_type_is_an_error():
    report = create_document(title="Xref Demo", language="en")
    sec = section(id="sec-1", level=1, title="Intro")
    sec.append_paragraph("Bad ref: ", xref(target_type="unknown_type", target_id="abc"))
    report.append_section(sec)

    validation = report.validate()

    assert validation.isValid is False
    assert any(issue.code == "unsupported_xref_target_type" for issue in validation.issues)

    try:
        report.assert_valid()
    except DocumentValidationError as exc:
        assert "unsupported_xref_target_type" in str(exc)
    else:
        raise AssertionError("Expected DocumentValidationError to be raised")
