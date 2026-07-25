# Optional Design Console

The bundled Design Console is preserved as an HTML prototype and optional local viewer. It is not the default intake or revision surface.

Use it only when the user explicitly asks to open the console, inspect the prototype, browse registered systems or history, or test a future standalone-tool direction.

Start it with:

```bash
python3 scripts/design_console.py --workspace "<workspace>" --port 0
```

Open the printed localhost URL. Requests created in this optional console still require an active Codex task; the console cannot wake Codex after a task ends.

Preserve these implementation assets for future productization:

- `assets/design-console/index.html`
- `assets/design-console/styles.css`
- `assets/design-console/app.js`
- `scripts/design_console.py`
- Agent bridge and request-status scripts
