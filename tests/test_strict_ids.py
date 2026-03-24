import pytest

from ova_portable_text import create_document, image_asset, paragraph, section


def test_strict_ids_reject_duplicate_top_level_section_immediately():
    report = create_document(title="Strict IDs", language="en", strict_ids=True)

    report.append_section(section(id="sec-1", level=1, title="A"))

    with pytest.raises(ValueError, match="Duplicate global id"):
        report.append_section(section(id="sec-1", level=1, title="B"))


def test_strict_ids_reject_cross_registry_conflict_with_existing_section():
    report = create_document(title="Strict IDs", language="en", strict_ids=True)
    report.new_section(id="dup-1", level=1, title="Intro")

    with pytest.raises(ValueError, match="Duplicate global id"):
        report.add_image_asset(image_asset(id="dup-1", src="https://example.com/a.png"))


def test_strict_ids_reject_duplicate_ids_inside_pending_section_subtree():
    report = create_document(title="Strict IDs", language="en", strict_ids=True)

    root = section(id="sec-1", level=1, title="Root")
    root.append_image(id="fig-1", image_ref="img-1")
    root.append_subsection(section(id="fig-1", level=2, title="Conflicts with figure id"))

    with pytest.raises(ValueError, match=r"Duplicate id\(s\) inside"):
        report.append_section(root)


def test_strict_ids_flag_is_not_serialized():
    report = create_document(title="Strict IDs", language="en", strict_ids=True)
    data = report.to_dict()

    assert "strict_ids" not in data


def test_default_mode_still_defers_duplicate_detection_to_validation():
    report = create_document(title="Compat Mode", language="en")
    report.append_section(section(id="sec-1", level=1, title="A"))
    report.append_section(section(id="sec-1", level=1, title="B"))

    validation = report.validate()

    assert validation.isValid is False
    assert any(issue.code == "duplicate_id" for issue in validation.issues)
