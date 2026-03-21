"""Minimal example / 最小示例。"""

from ova_portable_text import create_document, section


report = create_document(
    title="Demo Report",
    language="en",
    documentType="report",
)

intro = section(id="sec-intro", level=1, title="Introduction")
intro.append_paragraph("This is the first paragraph.")

background = section(id="sec-background", level=2, title="Background")
background.append_paragraph("This is a nested subsection paragraph.")
intro.append_subsection(background)

report.append_section(intro)

print(report.to_json())
