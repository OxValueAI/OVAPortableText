import pytest

from ova_portable_text import paragraph


def test_allowed_style():
    block = paragraph("Hello", style="subheading")
    assert block.style == "subheading"


def test_disallow_heading_styles():
    with pytest.raises(ValueError):
        paragraph("Heading", style="h1")
