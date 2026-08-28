# OVAPortableText Editor Development Log 015

Date: 2026-08-28

## Goal

Fix Risk scan table rendering where row-spanned cells did not truly span rows and some cells appeared height-misaligned.

## Changes

- Replaced the table data editor's div-based grid with a native HTML table for table datasets.
- Native `td` elements now receive `colSpan` and `rowSpan`, so merged cells are handled by the browser table layout engine.
- Kept auto-growing textareas inside table cells so long content still expands the table naturally.
- Updated browser smoke tests to click the actual Risk Scan table block, not the Table of Contents text entry.
- Added a Risk Scan-specific smoke assertion for native `rowSpan` cells.

## Validation

- `npm run test` passed.
- `python -m py_compile editor/tests/browser_smoke.py` passed.
- `npm run build` passed.
- `npm run browser:smoke` passed through the Playwright fallback after Selenium was unavailable.
