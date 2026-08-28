# OVAPortableText Editor Development Log 016

Date: 2026-08-28

## Goal

Make the first integration path clear for embedding the OVAPortableText editor into other frontend projects.

## Changes

- Added host-controlled `className` and `style` props to the React editor shell.
- Re-exported core integration types from `@ova/portable-text-editor-react`.
- Added `docs/OVAPortableText_Editor_Integration_Guide.md` with:
  - minimal React usage,
  - save callback flow,
  - imperative ref API,
  - local versioning setup,
  - sizing recommendations,
  - package integration options.
- Linked the integration guide from `editor/README.md`.

## Validation

- `npm run test` passed.
- `python -m py_compile editor/tests/browser_smoke.py` passed.
- `npm run build` passed.
- `npm run browser:smoke` passed through the Playwright fallback after Selenium was unavailable.
