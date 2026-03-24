from ova_portable_text import Document, __version__, create_document


def test_runtime_version_is_exposed():
    assert isinstance(__version__, str)
    assert __version__


def test_document_from_json_roundtrip_with_extra_meta_fields():
    report = create_document(
        title="Roundtrip Demo",
        language="en",
        locale="en",
        clientName="OxValue",
    )
    report.new_section(id="sec-1", level=1, title="Intro").append_paragraph("hello")

    restored = Document.from_json(report.to_json())
    assert restored.meta.locale == "en"
    assert restored.meta.clientName == "OxValue"
    assert restored.sections[0].title == "Intro"
