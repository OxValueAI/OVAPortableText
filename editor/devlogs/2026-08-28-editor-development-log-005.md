# OVAPortableText Editor Development Log 005

Date: 2026-08-28
Scope: Install a local Node.js/npm toolchain for editor validation, then run dependency install, tests, and builds.

## Plan

- Use a workspace-local portable Node.js install under `editor/.tools`.
- Avoid changing system PATH or installing into system directories.
- Use Node.js v22 LTS for compatibility with modern Vite, TypeScript, and Vitest.
- Add `editor/.tools/` to `.gitignore`.

## Environment Check

- `node`: not found on PATH.
- `npm`: not found on PATH.
- `winget`: not found on PATH.
- `choco`: not found on PATH.
- `scoop`: not found on PATH.
- `curl`: available at `C:\Windows\System32\curl.exe`.

## Source

- Node.js official release index confirmed `latest-v22.x` includes `node-v22.23.2-win-x64.zip`.

## Results

- Downloaded `node-v22.23.2-win-x64.zip` to `editor/.tools`.
- Verified downloaded zip SHA-256 against the official `SHASUMS256.txt`.
- Extracted Node.js v22.23.2.
- Confirmed local toolchain:
  - `node`: `v22.23.2`
  - `npm`: `10.9.8`
- First `npm install` attempt inside the sandbox stalled without output.
- Second install with logging showed sandbox network `EACCES`.
- Escalated install reached npm registry successfully.
- Install then failed because internal dependencies used `workspace:*`.
- Updated internal editor dependencies to local `file:` references:
  - `@ova/portable-text-editor-core`: `file:../editor-core`
  - `@ova/portable-text-editor-react`: `file:../../packages/editor-react`
- Removed the partial `editor/node_modules` install and reran install with the local Node directory prepended to `PATH`.
- `npm install` completed successfully and generated `editor/package-lock.json`.
- Verified `.gitignore` covers the local toolchain and generated install/build artifacts:
  - `editor/.tools/`
  - `node_modules/`
  - `**/node_modules/`
  - `.vite/`
  - `**/.vite/`
  - `editor/**/dist/`

## Validation

- `npm run test`
  - `@ova/portable-text-editor-core`: 11 tests passed.
  - Adjusted tests to compare rendered multilingual text through `displayText`.
- `npm run build`
  - `@ova/portable-text-editor-core`: TypeScript build passed.
  - `@ova/portable-text-editor-react`: TypeScript build passed.
  - `@ova/portable-text-editor-playground`: TypeScript and Vite build passed.
  - Vite output was generated under `editor/apps/playground/dist`, which is ignored by git.
- `npm run dev -- --host 127.0.0.1`
  - Initial server startup reached `http://127.0.0.1:5173/`.
  - Vite dependency optimization then hit `EPERM` writing to `apps/playground/node_modules/.vite`.
  - Updated playground `cacheDir` to `../../.vite/playground`, a root-level editor cache location already covered by `.gitignore`.
  - Reran `npm run build` after the cache path change; build passed.
- `npm run dev`
  - Started successfully after using the workspace script directly.
  - The local editor is available at `http://127.0.0.1:5173/`.
  - Note: do not append another `--host 127.0.0.1`; the playground script already includes it.

## Notes

- The toolchain is intentionally portable and workspace-local; it does not modify the system Node/npm installation state.
- On this machine, commands should be run from `editor/` after prepending the local Node directory to `PATH`:

```powershell
$env:Path = (Resolve-Path '.\.tools\node-v22.23.2-win-x64').Path + ';' + $env:Path
npm.cmd run dev
```

- The first build attempt inside the sandbox hit a filesystem permission issue while writing `dist`; rerunning the same build with approved elevated execution completed successfully.
