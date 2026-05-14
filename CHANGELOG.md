# Changelog

**All notable changes to this project will be documented in this file.**  ** **本项目的重要变更会记录在此文件中。

## [Unreleased]

## [0.4.0] - 2026-05-14

### Added

* aligned the package with `report.v1.3`
* added typed chart models for `bar`, `line`, and `matrix_bubble` datasets
* added shared `ChartAxis`, `ChartCategory`, `MatrixBubbleCategory`, and `SizeMetric` models
* added chart helper functions for bar, horizontal bar, line, and matrix bubble datasets
* added validation coverage for v1.3 chart category references, series keys, and matrix bubble size values
* added tests covering v1.3 schema defaults, `pie.slices[].colorHint`, bar variants, line points, and matrix bubble output

### Changed

* default `schemaVersion` is now `report.v1.3`
* package metadata and public version now reflect `v0.4.0` / `report.v1.3`
* `datasets.charts` now has first-class Python models for all v1.3 formal chart types while keeping the generic chart fallback

### Fixed

* preserved `pie.slices[].colorHint` while avoiding new visual-style fields for v1.3 chart types
* normalized legacy `sizeMetric.valueUnit` input to `sizeMetric.unit` without emitting `valueUnit` in new matrix-bubble output
* avoided any `chartType = "bubble"` helper for v1.3; classification bubble charts now use `chartType = "matrix_bubble"`

## [0.3.0] - 2026-04-08

### Added

* aligned the package with `report.v1.2`
* added `DoughnutChartDataset` and `doughnut_chart_dataset(...)`
* added section-level models and helpers for `sectionRole`, `navigation`, `pagination`, and `presentation`
* added support for `_type="chart"` inside `GridTableCell.blocks`
* added validation coverage for doughnut constraints, grid-cell chart refs, and `presentation.titleBlockStyle`
* added tests covering v1.2 doughnut datasets, section fields, and grid-cell charts

### Changed

* default `schemaVersion` is now `report.v1.2`
* `ChartBlock.id`, `TableBlock.id`, `MathBlock.id`, and `CalloutBlock.id` are now optional to match the protocol's instance-layer rules
* `Section`, `Document.new_section(...)`, and `section(...)` now accept v1.2 section fields
* chart / table / math helper functions now accept optional instance ids
* public exports and packaging metadata now reflect `v0.3.0` / `report.v1.2`

### Fixed

* fixed the protocol mismatch where grid-cell chart blocks were still rejected by the Python models and validator
* fixed the resolver mismatch where optional chart / table / math / callout instance ids could break target indexing
* fixed the validation gap where grid-cell `chartRef` values were not resolved

## [0.2.0] - 2026-04-01

### Added

* aligned the package with `report.v1.1`
* added `theme.blockStyleDefaults` models and helpers
* added block-level `layout` support for `TextBlock` and paragraph helpers
* added table-level `layout.columnSpecs[]` with `auto | weight` width modes
* added helper functions: `block_layout`, `length_em`, `length_pt`, `table_column_spec_auto`, `table_column_spec_weight`, `table_layout`
* added support for `_type="image"` inside `GridTableCell.blocks`
* added validation coverage for grid-cell image refs and v1.1 table/theme features
* added `examples/v11_layout_and_cell_image_demo.py`

### Changed

* default `schemaVersion` is now `report.v1.1`
* `ImageBlock.id` and `ImageBlock.anchor` are now optional
* `image_block(...)` and `Section.append_image(...)` now accept optional instance ids
* `record` and `grid` table datasets both accept table-level `layout`
* API docs and quickstart examples now reflect the v1.1 contract

### Fixed

* fixed the protocol mismatch where image instances incorrectly required `id`
* fixed the protocol mismatch where grid-cell `blocks` only accepted text blocks
* fixed the validation gap where grid-cell `imageRef` values were not resolved

## [0.1.4] - 2026-03-25

### Added

* **bilingual end-user and developer documentation, including a restructured **`README.md`
* **protocol-aligned table authoring helpers for both **`record` and `grid` table modes
* **generic chart registry support so non-**`pie` chart entries can remain in `datasets.charts[]` without pretending to follow the `pie` schema
* **richer example coverage for image sources, grid tables, references, marks, and end-to-end report generation**
* **resolver support for the generic **`asset` target alias in cross-references

### Changed

* **synchronized the package with the latest **`report.v1.0` protocol wording and data contracts
* **standardized document schema version handling to **`report.v1.0`
* **aligned **`meta` handling with the latest protocol field set, including stronger enum / format validation where the protocol now defines it
* **aligned bibliography generation with the latest protocol by treating **`displayText` as the primary display field
* **aligned image registries (**`images`, `logos`, `backgrounds`, `icons`) around the current `imageSource` model and helper flow
* **aligned inline reference models around **`targetId`
* **expanded validator coverage for **`grid` tables, protocol-native image sources, and newer registry / reference rules
* **refreshed examples and tests to use the current protocol instead of older transitional shapes**

### Fixed

* **corrected remaining mismatches between protocol examples and package-generated JSON structures**
* **corrected resolver / validator gaps around newer reference and asset resolution behaviors**
* **corrected helper / example inconsistencies that could force manual post-processing for some protocol features**

## [0.1.3]

### Added

* **formal image-source helpers: **`image_asset_url(...)`, `image_asset_embedded(...)`, and `image_asset_from_file(...)`
* **typed image source models: **`ImageSourceUrl`, `ImageSourceEmbedded`, and discriminated `ImageSource`

### Changed

* `assets.images` now follows the pure `imageSource` protocol and no longer depends on legacy `src`
* **image-related examples, tests, and docs now use the new protocol-native image helpers**

## [0.1.2]

### Added

* **optional **`strict_ids=True` fail-early duplicate-ID checks for common authoring paths
* **continuous-content helpers on **`Section`:
  * `append_to_last_content()`
  * `append_blocks_to_last_content()`
  * `append_text_block_to_last_content()`
  * `append_paragraph_to_last_content()`
* **release-facing docs now explain the implemented v1.0 protocol subset more explicitly**

### Changed

* **packaging and release metadata were aligned for a cleaner publication flow**
* `Section.numbering` now accepts only protocol-approved values: `auto`, `none`, and `manual`
* **publishing checklist now includes changelog layout and sdist verification guidance**

## [0.1.1]

### Added

* **improved authoring ergonomics for local save/load and batch section writing**
* **more release-prep docs and smoke-test coverage**

## [0.1.0]

### Added

* **document / section tree builder**
* **text blocks, spans, marks, markDefs, and list semantics**
* **inline refs: **`xref`, `citation_ref`, `footnote_ref`, `glossary_term`, `hard_break`
* **block objects: **`image`, `chart`, `table`, `math_block`, `callout`
* **registries: assets, datasets, bibliography, footnotes, glossary**
* **numbering helpers, resolver, validator, and round-trip helpers**
