# OVAPortableText Editor

Structured Visual/JSON editor for OVAPortableText `report.v1.3` documents.

## Layout

```text
editor/
  apps/playground/          # Local Vite playground
  packages/editor-core/     # Pure TypeScript document logic
  packages/editor-react/    # React component package
  fixtures/                 # Golden and edge-case JSON fixtures
  docs/                     # Design documents
  devlogs/                  # Implementation logs
```

## Development

Run from this directory after Node.js is available:

```bash
npm install
npm run test
npm run build
npm run dev
```

The current Golden Fixture is `fixtures/report-v1.3-company.json`.
