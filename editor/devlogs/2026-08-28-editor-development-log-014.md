# OVAPortableText Editor Development Log 014

Date: 2026-08-28

## Goal

Fix table grid alignment, Patent list cell display, Text block height, and recursive section block counts.

## Changes

- Table grid rendering now computes the table column count from each row's `colSpan` total.
- Table cells now apply `grid-column: span N`, so merged cells align with the rest of the grid.
- Table cell display now reads `cell.blocks` when `cell.text` is empty, fixing Attachment / Patent list content visibility.
- Text block editing now uses the auto-growing textarea component.
- Section block counts now include all nested child-section blocks, not only direct blocks.
- Browser smoke tests now assert:
  - synced data row heights,
  - rendered colSpan cells,
  - Patent list block-based cell content.

## Validation

- `npm run test` passed.
- `python -m py_compile editor/tests/browser_smoke.py` passed.
- `npm run build` passed before smoke-test updates.
- `npm run browser:smoke` passed through the Playwright fallback after Selenium was unavailable.
