from ova_portable_text import Document, DocumentMeta, Section


def build_report() -> Document:
    doc = Document(meta=DocumentMeta(title="Patent Valuation Report", language="en"))

    section = Section(id="sec-1", level=1, title="Executive Summary")
    section.append_paragraph("This is the opening introduction of the chapter.")

    subsection = Section(id="sec-1-1", level=2, title="Background")
    subsection.append_paragraph("This is the body text of subsection 1.1.")
    section.append_subsection(subsection)

    section.append_paragraph("This is a concluding paragraph after subsection 1.1.")
    doc.append_section(section)
    return doc


if __name__ == "__main__":
    print(build_report().to_json(indent=2))
