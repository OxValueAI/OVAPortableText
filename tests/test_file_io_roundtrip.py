from __future__ import annotations

from pathlib import Path

from ova_portable_text import Document, create_document


def test_save_json_and_load_json_roundtrip(tmp_path: Path) -> None:
    report = create_document(title="Disk Round Trip", language="en")
    report.new_section(id="sec-1", level=1, title="Intro").append_paragraph("Hello disk.")

    output = report.save_json(tmp_path / "nested" / "report.json")

    restored = Document.load_json(output)
    assert restored.meta.title == "Disk Round Trip"
    assert restored.sections[0].title == "Intro"


def test_save_json_creates_parent_directories(tmp_path: Path) -> None:
    report = create_document(title="Create Parent", language="en")
    report.new_section(id="sec-1", level=1, title="Intro")

    output = report.save_json(tmp_path / "a" / "b" / "report.json")
    assert output.exists()
