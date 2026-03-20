from ova_portable_text import (
    create_document,
    link_def,
    section,
    span,
    strong,
)


def test_mark_defs_and_list_blocks_export_correctly():
    report = create_document(title="Text Demo", language="en")
    sec = section(id="sec-text", level=1, title="Text Features")

    sec.append_paragraph(
        "See ",
        span("OpenAI", marks=["m-link-openai"]),
        " and ",
        strong("important"),
        ".",
        mark_defs=[
            link_def(
                key="m-link-openai",
                href="https://openai.com",
                title="OpenAI",
                open_in_new_tab=True,
            )
        ],
    )
    sec.append_bullet_item("Point A")
    sec.append_number_item("Nested step", level=2)
    report.append_section(sec)

    data = report.to_dict()

    paragraph_block = data["sections"][0]["body"][0]["blocks"][0]
    bullet_block = data["sections"][0]["body"][1]["blocks"][0]
    number_block = data["sections"][0]["body"][2]["blocks"][0]

    assert paragraph_block["markDefs"][0]["_type"] == "link"
    assert paragraph_block["markDefs"][0]["_key"] == "m-link-openai"
    assert paragraph_block["children"][1]["marks"] == ["m-link-openai"]
    assert paragraph_block["children"][3]["marks"] == ["strong"]

    assert bullet_block["listItem"] == "bullet"
    assert bullet_block["level"] == 1
    assert number_block["listItem"] == "number"
    assert number_block["level"] == 2
