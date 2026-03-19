# OVAPortableText

OVAPortableText is a Python package for generating JSON documents that conform to the **Report Profile v1.0** protocol.

This step-1 scaffold focuses on the core authoring flow:

- create a top-level document
- create sections
- append paragraphs and subsections
- export stable JSON with `to_dict()` / `to_json()`

## Install locally

```bash
pip install -e .
```

## Quick start

```python
from ova_portable_text import Document, DocumentMeta, Section

doc = Document(meta=DocumentMeta(title="Patent Valuation Report", language="en"))

summary = Section(id="sec-1", level=1, title="Executive Summary")
summary.append_paragraph("This is the opening introduction of the chapter.")

background = Section(id="sec-1-1", level=2, title="Background")
background.append_paragraph("This is the body text of subsection 1.1.")
summary.append_subsection(background)
summary.append_paragraph("This is a concluding paragraph after subsection 1.1.")

doc.append_section(summary)

print(doc.to_json(indent=2))
```

## Included in this step

- package skeleton with modern `pyproject.toml`
- Pydantic-based models for document / section / content / text block / span
- author-friendly append methods
- minimal example and tests

## Not included yet

- inline objects such as `xref`, `citation_ref`, `footnote_ref`
- block objects such as `image`, `chart`, `table`, `math`, `callout`
- registry entry models and cross-reference resolver
- advanced validator
