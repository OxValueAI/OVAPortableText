# OVAPortableText Editor Development Log 012

Date: 2026-08-28

## Goal

Improve the redesigned editor after hands-on feedback around navigator labels, section collapse behavior, and data editor height.

## Changes

- Navigator block labels now prioritize human-readable content:
  - text blocks use block title/label first, then a text excerpt.
  - chart blocks use the linked chart label first.
  - table blocks use the linked table label first.
- Section expand/collapse is no longer forced open by the selected section, so a parent section can be collapsed while editing one of its child blocks.
- Chart and table text-like data cells now use auto-growing textareas instead of fixed-height single-line inputs.
- Data editor rows stretch as a unit so grid table rows keep consistent height when one cell wraps.
- Updated the browser smoke test to cover collapsing a selected parent section.
- Updated the concise user manual with the new navigator behavior.

## Validation

- `npm run test` passed.
- `python -m py_compile editor/tests/browser_smoke.py` passed.
- `npm run build` passed.
- `npm run browser:smoke` passed through the Playwright fallback after Selenium was unavailable.
