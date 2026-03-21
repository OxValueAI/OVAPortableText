from ova_portable_text import Document, create_document


def test_meta_theme_and_roundtrip_helpers_work():
    report = create_document(
        title="Roundtrip Demo",
        language="en",
        reportType="valuation",
        clientName="OpenAI",
        theme={
            "name": "corporate-blue",
            "styleTemplate": "clean-report",
            "customBrandColor": "#123456",
        },
    )

    sec = report.new_section(id="sec-1", level=1, title="Intro")
    sec.append_paragraph("Hello")

    data = report.to_dict()
    rebuilt_from_dict = Document.from_dict(data)
    rebuilt_from_json = Document.from_json(report.to_json())

    assert data["meta"]["reportType"] == "valuation"
    assert data["theme"]["name"] == "corporate-blue"
    assert data["theme"]["customBrandColor"] == "#123456"
    assert rebuilt_from_dict.meta.clientName == "OpenAI"
    assert rebuilt_from_json.sections[0].title == "Intro"
