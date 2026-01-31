# Documentation Standards

All `.md` files in the `docs/` directory must adhere to the `meta-audit` Gold Standards.

## YAML Frontmatter
Each file must start with a YAML frontmatter block containing:
- `version`: Current semantic version (e.g., 1.1.0).
- `last_modified`: The date of the last edit in YYYY-MM-DD format.
- `status`: One of `active`, `draft`, `archived`.

Example:
```yaml
---
version: 1.1.0
last_modified: 2026-01-31
status: active
---
```

## Breadcrumbs
Files within subdirectories should include a breadcrumb or "back to" link to facilitate navigation (e.g., `[← Research Hub](README.md)`).

## Connectivity
- All documents must be linked from either the main `README.md` or a subdirectory `README.md`.
- No isolated files are allowed.
