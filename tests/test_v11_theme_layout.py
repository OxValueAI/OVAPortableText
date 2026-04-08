from ova_portable_text import (
    Document,
    block_layout,
    create_document,
    length_em,
    length_pt,
    paragraph,
    validate_document,
)


def test_theme_block_style_defaults_and_block_layout_roundtrip():
    report = create_document(
        title="Layout Demo",
        theme={
            "blockStyleDefaults": {
                "normal": {
                    "layout": {
                        "textAlign": "justify",
                        "firstLineIndent": {"unit": "em", "value": 2},
                        "spaceAfter": {"unit": "pt", "value": 6},
                    }
                }
            }
        },
    )
    sec = report.new_section(id="sec-1", level=1, title="Intro")
    sec.append_paragraph(
        "Centered paragraph",
        layout=block_layout(text_align="center", first_line_indent=length_em(0), space_after=length_pt(4)),
    )

    rebuilt = Document.from_dict(report.to_dict())
    block = rebuilt.sections[0].body[0].blocks[0]
    assert block.layout is not None
    assert block.layout.textAlign == "center"
    assert rebuilt.theme.blockStyleDefaults["normal"].layout.textAlign == "justify"
    assert validate_document(rebuilt).is_valid


def test_invalid_theme_block_style_default_is_reported():
    report = create_document(theme={"blockStyleDefaults": {"not_real": {"layout": {"textAlign": "left"}}}})
    validation = validate_document(report)
    assert "invalid_theme_block_style_default" in validation.codes()
