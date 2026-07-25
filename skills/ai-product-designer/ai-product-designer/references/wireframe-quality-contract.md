# Wireframe quality contract

Read `design-quality-benchmark.md` before planning or building a wireframe.

## Design-system use

- Inspect the registered source before designing. Read its `SKILL.md`, README, tokens, component guidance, and the reference screens relevant to the requested flow when present.
- Reuse only the design-system dimensions allowed by the selected output level. Structural and detailed wireframes may reuse typography scale, spacing, component anatomy, content tone, and media structure, but must suppress brand polish. UI mockups may also reuse brand color, radius, elevation, real imagery, and visual assets.
- Record any deliberate divergence in `reports/design-rationale.md`.

## Direction completeness

When `compareDirections` is greater than one, every direction must be reviewable as a UI—not a prose-only concept.

- Wrap each direction in an element with `data-design-direction="<stable-id>"`.
- Put at least one complete key screen or flow inside every direction and mark each rendered screen with `data-wireframe-screen`.
- Give every direction a distinct interaction model, information architecture, or decision strategy.
- A description card, heading, or list of tradeoffs does not count as a wireframe.
- Make direction switching functional when interactive output is requested.
- Give every screen a stable `data-screen-id`, `data-requirement-ids`, and a nearby `data-screen-caption`.
- Use at least one screen or state per direction for `structural-wireframe`, two for `detailed-wireframe`, and three for `ui-mockup`.

## Output level

### 構造ワイヤー (`structural-wireframe`)

Show complete structure, information order, navigation, and major states.

- Use grayscale or neutral colors and at most one restrained semantic accent.
- Use simple borders and flat surfaces.
- Do not use real photos, decorative imagery, gradients, decorative shadows, glass effects, or brand polish.
- Treat media placeholders as information architecture, not decorative imagery. When media affects recognition, comparison, trust, content density, or layout, show neutral skeletons for every meaningful image slot.
- Preserve the intended number, placement, crop behavior, and aspect ratio of image, gallery, avatar, map, or video slots. Label placeholders such as `画像 4:3`; do not leave ambiguous empty rectangles.
- Mark each media container with `data-media-slot`, `data-media-kind`, and `data-aspect-ratio`. In structural and detailed wireframes, also mark the neutral skeleton with `data-media-placeholder`.
- Show a `data-media-state="missing"` state when a missing image changes the card height, hierarchy, fallback content, or user decision.
- Use representative labels; realistic long-form copy is optional when it does not affect layout.

### 詳細ワイヤー (`detailed-wireframe`)

Meet all structural-wireframe requirements, then add:

- Realistic Japanese copy and representative data density.
- Deliberate typography, spacing, information hierarchy, component anatomy, and restrained state colors.
- Primary, secondary, empty, loading, error, and recovery states relevant to the flow.
- At least one meaningful interaction in every proposed direction when interactive output is requested.
- Responsive behavior for every requested viewport.
- At least two complete screens or meaningful states in every direction.
- Screen-level captions that explain the design decision being demonstrated.
- Traceability from every screen to a requirement in `exploration/design-plan.json`.

Detailed wireframes are not concept boards and must not use prose-only directions. They must remain visually neutral: no gradients, decorative shadows, real hero imagery, or final-brand finish. Neutral media skeletons remain required wherever image structure matters.

### UIモックアップ (`ui-mockup`)

Meet all detailed-wireframe requirements, include at least three screens or meaningful states in every direction, then apply the selected design system accurately: brand color, typography, radii, elevation, imagery, responsive variants, visual assets, and implementation-adjacent states.

## Template and content integrity

- Remove `data-template-state="unresolved"` and every `data-template-placeholder` before validation.
- Reject generic starter copy such as “Design exploration”, “State the design hypothesis”, “画面タイトル”, “ここに画面を実装”, or “Replace with”.
- Use realistic Japanese content and enough information density to review the decision.
- Do not leave a request in `generating` after stopping work.

## Interaction policy

- Default wireframes and explorations to `interactive: false`.
- Add controls only when they support the user decision or an explicitly requested prototype.
- When `interactive: true`, implement at least one meaningful state-changing interaction per direction and render the resulting state.
- Do not add sample toasts, tabs, or buttons merely as prototype decoration.

## Artifact header

- Keep the header subordinate to the proposed UI.
- Use a single-line project label, an `h1` no larger than `clamp(28px, 4vw, 42px)`, and one short summary.
- Do not put internal labels such as `Review-ready`, `Observed + Inferred`, “状態”, or “根拠” in a prominent metadata card.
- Put evidence boundaries and verification vocabulary in the reports or a compact collapsible note.

## Acceptance

Before marking ready:

1. Validate `exploration/design-plan.json`.
2. Run `validate_wireframe.mjs`.
3. Run `validate_delivery.py` with the request JSON and entrypoint.
4. Open every direction at every requested viewport.
5. Save and record every required render.
6. Confirm that no requested direction is prose-only, its visual treatment matches `settings.outputLevel`, and every media requirement in the design plan is represented.
7. Use `finalize_request.py`; do not call a bare status update to bypass the quality gate.
