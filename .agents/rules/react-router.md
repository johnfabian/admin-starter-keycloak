---
id: react-router
paths:
  [
    "web/app/**/*.{ts,tsx,css}",
    "web/react-router.config.ts",
    "web/vite.config.ts",
    "web/tsconfig.json",
    "web/package.json",
  ]
applies_to:
  [
    "web/app/**/*.{ts,tsx,css}",
    "web/react-router.config.ts",
    "web/vite.config.ts",
    "web/tsconfig.json",
    "web/package.json",
  ]
owner: unassigned
enforcement: ["eslint", "react-router-typegen", "typescript", "react-router-build"]
wiki:
  [
    "/architecture/react-router-bff.md",
    "/architecture/access-control-model.md",
    "/conventions/repository-tooling.md",
  ]
config:
  [
    "/web/eslint.config.mjs",
    "/web/tsconfig.json",
    "/web/react-router.config.ts",
    "/web/vite.config.ts",
    "/web/package.json",
    "/package.json",
  ]
---

# React Router rules

## Required

- Keep browser-specific composition and session handling in the React Router server boundary.
- Keep route modules slim; centralize route strings/modules in `web/app/lib/app-settings.shared.ts` and use server guards for protected loaders.
- Keep server-only code in `.server.ts` modules and SQL in `web/app/lib/server/data/` repositories.
- Keep bearer and refresh tokens out of browser-readable storage, loader/action payloads, and rendered markup.
- Preserve accessible semantics and keyboard behavior for UI changes.

## Prohibited

- Do not duplicate downstream domain logic in route components or browser code.
- Do not hardcode route paths, role names, or module paths outside the established settings boundary.
- Do not return raw authentication or dependency errors directly to the UI.

## Checks

- Run `corepack pnpm --dir web lint`.
- Run `corepack pnpm web:typecheck`.
- Run `corepack pnpm web:build` when route, server/client boundary, or build configuration changes.
