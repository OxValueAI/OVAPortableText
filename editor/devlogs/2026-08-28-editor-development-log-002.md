# OVAPortableText Editor Development Log 002

Date: 2026-08-28
Scope: Move editor implementation under `editor/` and continue P0 core transactions.

## User Direction

- Continue development.
- Keep every development step and result in a new unique development document.
- Move the editor program into `editor/` instead of keeping it at repository root.

## Migration

- Moved `apps/` to `editor/apps/`.
- Moved `packages/` to `editor/packages/`.
- Moved `fixtures/` to `editor/fixtures/`.
- Moved root frontend `package.json` to `editor/package.json`.
- Moved root frontend `tsconfig.base.json` to `editor/tsconfig.base.json`.
- Kept the repository root `.gitignore` frontend ignore additions because they apply regardless of where Node output is generated.
- Added `editor/README.md` as the local entry point for editor development.

## Core Transaction Work

- Added section transactions:
  - `addSection`
  - `deleteSection`
  - `duplicateSection`
  - `moveSection`
- Added block transactions:
  - `addParagraphBlock`
  - `addChartBlock`
  - `addTableBlock`
  - `deleteBlock`
  - `moveBlock`
  - `duplicateBlock`
- Added guarded behavior:
  - protected sections (`cover`, `toc`, `backCover`) are not deleted or moved by default transaction helpers.
  - deleting a chart/table block does not delete its registry dataset.
  - duplicating a chart/table block clones the referenced dataset by default and rewrites the duplicated block reference.
  - moving sections updates descendant `level` values.

## React Integration

- Added toolbar actions for:
  - Add Section
  - Add Subsection
  - Duplicate Section
  - Delete Section
- Added visual section actions for:
  - Add Paragraph
  - Move Block Up/Down
  - Duplicate Block
  - Delete Block
- Added visual edit locking when JSON source text is in `DRAFT` or `INVALID` state.
- Added a simple Versions panel and Save Version toolbar button wired to the versioning foundation.
- Enabled local versioning in the playground with document key `golden-fixture-company-report`.

## Versioning Foundation

- Added `editor-core/src/versioning.ts` with an IndexedDB-backed API:
  - `saveVersion`
  - `listVersions`
  - `loadVersion`
  - `renameVersion`
  - `deleteVersion`
- Version records are isolated by `namespace + documentKey`.
- The default manual version limit is `20`.
- Version metadata records schema version, validation status, timestamp, label, and approximate JSON size.

## Test Coverage Added

- Added core tests for:
  - Golden Fixture load/export.
  - section tree construction.
  - reference index counts.
  - adding a top-level section.
  - deleting a chart block without deleting its dataset.
  - duplicating a chart block with an independent cloned dataset.

## Verification

- Verified editor manifests and TypeScript config are valid JSON with `python -m json.tool`.
- Verified migrated Golden Fixture parses as UTF-8 JSON:
  - `schemaVersion`: `report.v1.3`
  - top-level sections: `12`
  - chart datasets: `13`
  - table datasets: `10`
  - SHA-256: `9a280b351539ba3717619900a1f679752ee5079f1f94e124875a230aa5d2d9a2`
- Verified root-level `apps/`, `packages/`, `fixtures/`, `package.json`, and `tsconfig.base.json` no longer exist.
- Verified `editor/apps`, `editor/packages`, and `editor/fixtures` exist.
- Verified editor app/package source does not contain the non-ASCII separator characters previously used in status text.
- Confirmed `node` and `npm` are still not available in the current environment.
- Pending: TypeScript build/test after Node.js/npm are available.
- Pending: Browser interaction check after the playground can run.
