# Changelog

All notable changes to this project will be documented in this file.
本项目的重要变更会记录在此文件中。

## [Unreleased]

## [0.1.3]

### Added
- formal image-source helpers: `image_asset_url(...)`, `image_asset_embedded(...)`, and `image_asset_from_file(...)`
- typed image source models: `ImageSourceUrl`, `ImageSourceEmbedded`, and discriminated `ImageSource`

### Changed
- `assets.images` now follows the pure `imageSource` protocol and no longer depends on legacy `src`
- image-related examples, tests, and docs now use the new protocol-native image helpers

## [0.1.2]

### Added
- optional `strict_ids=True` fail-early duplicate-ID checks for common authoring paths
- continuous-content helpers on `Section`:
  - `append_to_last_content()`
  - `append_blocks_to_last_content()`
  - `append_text_block_to_last_content()`
  - `append_paragraph_to_last_content()`
- release-facing docs now explain the implemented v1.0 protocol subset more explicitly

### Changed
- packaging and release metadata were aligned for a cleaner publication flow
- `Section.numbering` now accepts only protocol-approved values: `auto`, `none`, and `manual`
- publishing checklist now includes changelog layout and sdist verification guidance

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
