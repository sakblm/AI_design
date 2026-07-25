# Visual QA loop

Render before claiming completion. Use the available Codex browser surface against a local HTTP preview.

## Required loop

1. Start a local server bound to `127.0.0.1`.
2. Open every direction with `?direction=<direction-id>`.
3. Inspect every requested viewport.
4. Save one representative screenshot for every direction and viewport under `renders/`.
5. Fix visible defects and repeat. Use at most three focused passes before reporting a remaining limitation.
6. Record each accepted screenshot with `scripts/record_visual_check.py`.

## Inspect

- Hierarchy and first-read clarity
- Information density and realistic Japanese wrapping
- Spacing rhythm and alignment
- Overflow, clipping, overlap, and accidental empty space
- Component and token consistency
- Whether each direction looks materially different
- Whether each screen answers its stated user decision
- Required empty, loading, error, and recovery states
- Focus visibility, labels, and touch target size when interaction is enabled

## Evidence rules

- Do not mark `inspected: true` without actually viewing the rendered screenshot.
- Keep notes specific, for example: `390pxで料金行の折返しを修正し、CTAを画面下部へ固定`.
- Do not use a screenshot of the unresolved scaffold.
- If rendering is unavailable, mark the request `error` with the missing capability. Do not silently downgrade it to ready.
