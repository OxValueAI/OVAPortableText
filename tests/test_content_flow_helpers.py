from __future__ import annotations

from ova_portable_text import create_document, paragraph


def test_append_to_last_content_reuses_existing_content_item() -> None:
    report = create_document(title="Content Flow", language="en")
    sec = report.new_section(id="sec-1", level=1, title="Intro")

    sec.append_paragraph("P1")
    sec.append_paragraph_to_last_content("P2")

    content_items = [item for item in sec.body if item.itemType == "content"]
    assert len(content_items) == 1
    assert len(content_items[0].blocks) == 2
    assert content_items[0].blocks[0].children[0].text == "P1"
    assert content_items[0].blocks[1].children[0].text == "P2"


def test_append_to_last_content_creates_new_content_after_subsection() -> None:
    report = create_document(title="Content Flow", language="en")
    sec = report.new_section(id="sec-1", level=1, title="Intro")

    sec.new_subsection(id="sec-1-1", title="Child")
    sec.append_paragraph_to_last_content("Tail paragraph")

    assert sec.body[0].itemType == "subsection"
    assert sec.body[1].itemType == "content"
    assert sec.body[1].blocks[0].children[0].text == "Tail paragraph"


def test_append_blocks_to_last_content_preserves_single_flow() -> None:
    report = create_document(title="Content Flow", language="en")
    sec = report.new_section(id="sec-1", level=1, title="Intro")

    sec.append_paragraph("Lead")
    sec.append_blocks_to_last_content(
        paragraph("Caption 1", style="caption"),
        paragraph("Caption 2", style="caption"),
    )

    content_items = [item for item in sec.body if item.itemType == "content"]
    assert len(content_items) == 1
    assert [block.style for block in content_items[0].blocks] == ["normal", "caption", "caption"]
