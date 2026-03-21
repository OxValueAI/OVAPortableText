# OVAPortableText Step 1

This delivery contains the first implementation step for the `OVAPortableText` Python package.

## Scope of this step

1. Establish a modern Python package scaffold based on `pyproject.toml`
2. Use `pydantic v2` as the modeling foundation
3. Support the primary authoring flow:
   - create a top-level document
   - create sections
   - append paragraphs
   - append subsections
   - export JSON
4. Match the core Report Profile v1.0 skeleton:
   - `schemaVersion`
   - `meta`
   - `theme`
   - `assets`
   - `datasets`
   - `bibliography`
   - `footnotes`
   - `glossary`
   - `sections`
5. Keep the API ergonomic for report construction

## Included models

- `Document`
- `DocumentMeta`
- `Section`
- `ContentItem`
- `SubsectionItem`
- `TextBlock`
- `Span`

## Ergonomic API included now

- `Document.append_section(section)`
- `Section.append_paragraph(text)`
- `Section.append_subsection(section)`
- `to_dict()`
- `to_json()`
- `create_document(...)`
- `paragraph(...)`

## Intentionally deferred to later steps

- inline objects: `xref`, `citation_ref`, `footnote_ref`, `glossary_term`, `hard_break`
- block objects: `image`, `chart`, `table`, `math`, `callout`
- dedicated registry entry models
- reference resolver / global id index
- validator for cross-reference integrity
- pie chart dataset model

## Suggested next step

Implement the text-layer expansion:

1. richer block styles enum
2. inline object framework
3. first validation rules for text content
