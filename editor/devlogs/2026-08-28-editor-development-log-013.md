# OVAPortableText Editor Development Log 013

Date: 2026-08-28

## Goal

Fix remaining data editor row height inconsistency where textareas could grow independently inside the same chart/table row.

## Changes

- Added a row-level height synchronizer for data editor rows.
- The synchronizer measures every textarea, input, and span in a row, then applies the largest rendered height to the whole row's controls.
- Kept individual textarea auto-growth, but made it cooperate with row-level sizing.
- Updated the browser smoke test to expand the navigator, find an editable chart/table row, and assert row cell heights differ by no more than 1px.

## Validation

- `npm run test` passed.
- `python -m py_compile editor/tests/browser_smoke.py` passed.
- `npm run build` passed.
- `npm run browser:smoke` passed through the Playwright fallback after Selenium was unavailable.
