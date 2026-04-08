from ova_portable_text import create_document, section


def test_minimal_report_structure():
    report = create_document(title="Demo", language="en")
    intro = section(id="sec-intro", level=1, title="Introduction")
    intro.append_paragraph("Hello world")
    report.append_section(intro)

    data = report.to_dict()

    assert data["schemaVersion"] == "report.v1.2"
    assert data["meta"]["title"] == "Demo"
    assert data["sections"][0]["id"] == "sec-intro"
    assert data["sections"][0]["body"][0]["itemType"] == "content"
    assert data["sections"][0]["body"][0]["blocks"][0]["_type"] == "block"
    assert data["sections"][0]["body"][0]["blocks"][0]["children"][0]["_type"] == "span"
