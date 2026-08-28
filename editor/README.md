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

On this workspace, a portable Node.js toolchain is installed under `.tools/`.
In PowerShell:

```powershell
$env:Path = (Resolve-Path '.\.tools\node-v22.23.2-win-x64').Path + ';' + $env:Path
npm.cmd run dev
```

## Browser Smoke Test

With the dev server running at `http://127.0.0.1:5173/`:

```powershell
python tests/browser_smoke.py
```

The script tries Selenium first, then falls back to Python Playwright with an installed local browser.

The concise user manual is `docs/OVAPortableText_Editor_User_Manual.md`.
The frontend integration guide is `docs/OVAPortableText_Editor_Integration_Guide.md`.
The current UX redesign proposal is `docs/OVAPortableText_Editor_UX_Redesign_v0.2.md`.

The current Golden Fixture is `fixtures/report-v1.3-company.json`.
