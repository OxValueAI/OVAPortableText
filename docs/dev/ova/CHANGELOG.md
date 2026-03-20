# Changelog

All notable changes to this project will be documented in this file.
本项目的重要变更会记录在此文件中。

## [Unreleased]

### Added
- publish-readiness improvements for packaging, CI, docs, and edge tests
- runtime `__version__` single source module
- `py.typed` marker for typed package consumers
- release-oriented docs: API reference and publishing checklist
- file-based round-trip helpers: `save_json()` / `load_json()`
- section batch helpers: `append_paragraphs()` / `append_bullet_items()` / `append_number_items()`
- additional real-world docs, smoke examples, and regression-oriented tests

## [0.1.1]

### Added
- improved authoring ergonomics for local save/load and batch section writing
- more release-prep docs and smoke-test coverage

## [0.1.0]

### Added
- document / section tree builder
- text blocks, spans, marks, markDefs, and list semantics
- inline refs: `xref`, `citation_ref`, `footnote_ref`, `glossary_term`, `hard_break`
- block objects: `image`, `chart`, `table`, `math_block`, `callout`
- registries: assets, datasets, bibliography, footnotes, glossary
- numbering helpers, resolver, validator, and round-trip helpers
