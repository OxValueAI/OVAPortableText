from ova_portable_text import ImageBlock, image_block


def test_image_block_accepts_optional_id():
    block = ImageBlock(imageRef="img-1")
    assert block.id is None
    assert block.anchor is None
    assert block.to_dict() == {"_type": "image", "imageRef": "img-1"}


def test_image_block_accepts_anchor_without_id():
    block = ImageBlock(anchor="fig-inline", imageRef="img-1")
    assert block.id is None
    assert block.anchor == "fig-inline"


def test_image_block_id_still_backfills_anchor():
    block = image_block(id="fig-1", image_ref="img-1")
    assert block.id == "fig-1"
    assert block.anchor == "fig-1"
