# OVAPortableText Editor Development Log 017

Date: 2026-08-28

## Goal

Clarify and implement the simple host integration save flow: host passes raw JSON in, editor returns current JSON on Save.

## Changes

- `Save` now shows a confirmation dialog before calling `onSave(document)`.
- Added bilingual save-confirmation text.
- Rewrote the integration guide as a concise bilingual document.
- The documented integration contract is now:
  - host passes raw JSON through `initialValue`;
  - editor owns the editing state internally;
  - user clicks Save;
  - editor confirms;
  - editor calls `onSave(currentJson)`;
  - host sends the returned JSON to its backend.

## Validation

- `npm run test` passed.
- `python -m py_compile editor/tests/browser_smoke.py` passed.
- `npm run build` passed.
- `npm run browser:smoke` passed through the Playwright fallback after Selenium was unavailable.
