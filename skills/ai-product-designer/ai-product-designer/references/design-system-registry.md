# Design system registry

## Registry location

Store reusable registrations in:

```text
<workspace>/design-systems/registry.json
```

Each record contains:

- Stable ID and display name
- Absolute local source path
- Active, evaluation, or deprecated status
- Description
- Created and updated timestamps
- A bounded file inventory

Registration is reference-only. Do not copy, upload, normalize, or rewrite the source system unless explicitly requested.

## Accepted sources

A registered source may be a directory or file containing any mix of:

- Design tokens in JSON, CSS, SCSS, YAML, or code
- Component documentation
- Storybook source or static documentation
- HTML/CSS/JS component examples
- Screenshots and image assets
- PDF or Markdown guidelines
- Exported Figma variables or handoff files

## Reading a registered system

1. Confirm the registry record exists and its source path is readable.
2. Look for a manifest, README, tokens, component rules, accessibility guidance, and assets.
3. Separate official rules from examples and inference.
4. Record missing categories; do not invent them.
5. Load only references relevant to the selected project type and current task.

## Registration safety

- Keep source paths local.
- Do not store credentials, tokens, cookies, or production records.
- Do not follow symlinks into unrelated confidential locations without explicit scope.
- Treat `evaluation` systems as non-authoritative.
- Treat Google Fonts permission separately from JavaScript, analytics, image, and API permissions.

