import pytest

from ova_portable_text import (
    DocumentValidationError,
    create_document,
    image_asset,
    paragraph,
    section,
    xref,
    citation_ref,
    footnote_ref,
    glossary_term,
)


def test_unresolved_references_are_reported():
    report = create_document(title="Broken Demo", language="en")
    report.add_image_asset(image_asset(id="img-1", src="https://example.com/a.png"))

    intro = section(id="sec-1", level=1, title="Introduction")
    intro.append_paragraph(
        "Missing refs: ",
        xref(target_type="section", target_id="sec-missing"),
        citation_ref("cite-missing"),
        footnote_ref("fn-missing"),
        glossary_term("term-missing"),
    )
    intro.append_image(id="fig-1", image_ref="img-missing")
    report.append_section(intro)

    validation = report.validate()
    codes = {issue.code for issue in validation.issues}

    assert validation.isValid is False
    assert "unresolved_xref" in codes
    assert "unresolved_citation_ref" in codes
    assert "unresolved_footnote_ref" in codes
    assert "unresolved_glossary_term" in codes
    assert "unresolved_image_ref" in codes


def test_duplicate_ids_are_reported_and_assert_valid_raises():
    report = create_document(title="Duplicate Demo", language="en")

    sec1 = section(id="sec-1", level=1, title="A")
    sec2 = section(id="sec-1", level=1, title="B")
    report.append_section(sec1)
    report.append_section(sec2)

    validation = report.validate()

    assert validation.isValid is False
    assert any(issue.code == "duplicate_id" for issue in validation.issues)

    with pytest.raises(DocumentValidationError):
        report.assert_valid()


def test_invalid_subsection_level_is_reported():
    report = create_document(title="Level Demo", language="en")

    parent = section(id="sec-1", level=1, title="Parent")
    child = section(id="sec-1-1", level=3, title="Child")
    child.append_paragraph("Bad level")
    parent.append_subsection(child)
    report.append_section(parent)

    validation = report.validate()

    assert validation.isValid is False
    assert any(issue.code == "invalid_section_level" for issue in validation.issues)
