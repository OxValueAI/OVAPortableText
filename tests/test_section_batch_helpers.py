from __future__ import annotations

from ova_portable_text import create_document


def test_section_batch_helpers_append_expected_blocks() -> None:
    report = create_document(title="Batch Helpers", language="en")
    sec = report.new_section(id="sec-1", level=1, title="Intro")

    sec.append_paragraphs("P1", "P2")
    sec.append_bullet_items("B1", "B2")
    sec.append_number_items("N1", "N2", level=2)

    content_items = [item for item in sec.body if item.itemType == "content"]
    assert len(content_items) == 6

    blocks = [item.blocks[0] for item in content_items]
    assert blocks[0].children[0].text == "P1"
    assert blocks[1].children[0].text == "P2"
    assert blocks[2].listItem == "bullet"
    assert blocks[3].listItem == "bullet"
    assert blocks[4].listItem == "number"
    assert blocks[4].level == 2
    assert blocks[5].children[0].text == "N2"
