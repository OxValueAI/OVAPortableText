from pydantic import ValidationError

import pytest

from ova_portable_text import NumberingConfig, create_document


def test_document_numbering_supports_sections_and_object_categories():
    report = create_document(title="Numbering Demo", language="en")

    sec1 = report.new_section(id="sec-1", level=1, title="Executive Summary")
    sec1.append_image_with_caption(id="fig-1", image_ref="img-1", caption="Figure caption")
    child = sec1.new_subsection(id="sec-1-1", title="Background")
    child.append_math_with_caption(id="eq-1", latex="x=y", caption="Equation caption")

    sec2 = report.new_section(id="sec-2", level=1, title="Method")
    sec2.append_table_with_caption(id="tbl-1", table_ref="table-1", caption="Table caption")

    numbering = report.build_numbering()

    assert numbering.get_display_number("sec-1") == "1"
    assert numbering.get_display_number("sec-1-1") == "1.1"
    assert numbering.get("fig-1").category == "figure"
    assert numbering.get_display_number("fig-1") == "1"
    assert numbering.get_display_number("eq-1") == "1"
    assert numbering.get_display_number("tbl-1") == "1"


def test_section_mode_numbering_resets_within_each_section():
    report = create_document(title="Numbering Demo", language="en")
    sec1 = report.new_section(id="sec-1", level=1, title="A")
    sec1.append_image(id="fig-a", image_ref="img-a")
    sec2 = report.new_section(id="sec-2", level=1, title="B")
    sec2.append_image(id="fig-b", image_ref="img-b")

    numbering = report.build_numbering(NumberingConfig(figureMode="section"))

    assert numbering.get_display_number("fig-a") == "1-1"
    assert numbering.get_display_number("fig-b") == "2-1"


def test_section_numbering_accepts_protocol_enum_values():
    report = create_document(title="Numbering Modes", language="en")

    sec_none = report.new_section(id="sec-none", level=1, title="No Number", numbering="none")
    sec_manual = report.new_section(id="sec-manual", level=1, title="Manual Number", numbering="manual")

    numbering = report.build_numbering()

    assert sec_none.numbering == "none"
    assert sec_manual.numbering == "manual"
    assert numbering.get_display_number("sec-none") is None
    assert numbering.get_display_number("sec-manual") is None


def test_section_numbering_rejects_invalid_value_early():
    report = create_document(title="Invalid Numbering", language="en")

    with pytest.raises(ValidationError):
        report.new_section(id="sec-bad", level=1, title="Bad", numbering="invalid")


def test_subsection_numbering_rejects_invalid_value_early():
    report = create_document(title="Invalid Subsection Numbering", language="en")
    sec = report.new_section(id="sec-1", level=1, title="Parent")

    with pytest.raises(ValidationError):
        sec.new_subsection(id="sec-1-1", title="Child", numbering="invalid")
