from __future__ import annotations

"""
Save/load JSON demo for OVAPortableText.
OVAPortableText 的 JSON 落盘与读回示例。
"""

from pathlib import Path
from tempfile import TemporaryDirectory

from ova_portable_text import Document, create_document


def main() -> None:
    report = create_document(title="Save Load Demo", language="en", documentType="report")
    report.new_section(id="sec-1", level=1, title="Introduction").append_paragraph(
        "This JSON file will be written to disk and loaded back."
    )

    with TemporaryDirectory() as tmp_dir:
        output_path = Path(tmp_dir) / "report.json"
        report.save_json(output_path)

        restored = Document.load_json(output_path)
        restored.assert_valid()

        print(output_path)
        print(restored.meta.title)


if __name__ == "__main__":
    main()
