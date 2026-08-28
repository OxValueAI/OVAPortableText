# OVAPortableText Editor Development Log 007

Date: 2026-08-28
Scope: Improve desktop scrolling behavior, clarify unintuitive block actions, add the single concise user manual, then commit.

## Plan

- Make the left outline/resources pane, center editor pane, and right properties/data pane scroll independently.
- Keep mobile behavior stacked and readable.
- Rename block-level action labels so their scope and result are clearer.
- Add one concise operation manual for common editor actions.
- Validate with tests, build, and browser smoke testing.

## Implementation

- Updated editor shell layout to use a fixed viewport-height grid on desktop.
- Set left, center, and right panes to independent `overflow: auto` scroll containers.
- Kept mobile layout stacked with bounded side panels.
- Added explicit block action labels:
  - `Move Block Up` / `上移区块`
  - `Move Block Down` / `下移区块`
  - `Duplicate Block` / `复制区块`
  - `Delete Block` / `删除区块`
- Added the single concise operation manual:
  - `docs/OVAPortableText_Editor_User_Manual.md`
- Linked the manual from `README.md`.

## Expected UX Result

- Scrolling the outline, document editor, or property/data panel no longer forces the other desktop columns to move.
- Block movement is clearer: it only changes the selected block's order inside the current section.
- A user can quickly look up what each button does and how to complete common workflows.

## Validation

- `python -m py_compile editor/tests/browser_smoke.py`: passed.
- `python -m json.tool editor/package.json`: passed.
- `npm run test`: passed.
  - `@ova/portable-text-editor-core`: 11 tests passed.
- `npm run build`: passed.
  - Core TypeScript build passed.
  - React TypeScript build passed.
  - Playground TypeScript and Vite build passed.
- `npm run browser:smoke`: passed through Playwright fallback.
  - Confirmed the editor shell renders.
  - Confirmed left, center, and right desktop panes use independent `overflow: auto`.
  - Confirmed Chinese UI switching.
  - Confirmed clearer block movement label appears.
  - Confirmed title edit, dirty state, undo, and English UI switching.
