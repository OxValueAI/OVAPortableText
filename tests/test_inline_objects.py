from ova_portable_text import citation_ref, create_document, footnote_ref, glossary_term, hard_break, section, xref


def test_inline_objects_output():
    report = create_document(title="Demo", language="en")
    intro = section(id="sec-intro", level=1, title="Introduction")
    intro.append_paragraph(
        "See ",
        xref(target_type="section", target_id="sec-method"),
        ".",
    )
    intro.append_paragraph(
        "EBITDA ",
        glossary_term("term-ebitda"),
        footnote_ref("fn-1"),
        citation_ref("cite-smith-2024"),
        hard_break(),
        "done",
    )
    report.append_section(intro)

    data = report.to_dict()
    second_children = data["sections"][0]["body"][1]["blocks"][0]["children"]

    assert second_children[1]["_type"] == "glossary_term"
    assert second_children[1]["targetId"] == "term-ebitda"
    assert second_children[2]["_type"] == "footnote_ref"
    assert second_children[3]["_type"] == "citation_ref"
    assert second_children[4]["_type"] == "hard_break"
