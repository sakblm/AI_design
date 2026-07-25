# Deliverable contract

## Required HTML characteristics

- Opens locally without a build step.
- Has no required network dependency, except approved Google Fonts with a functional system-font fallback.
- Keeps CSS and JavaScript local in the editable source bundle; the portable single-file export may inline them.
- Has a title, language, viewport metadata, one `main` landmark, and visible focus.
- Includes a page-level statement of scope, fidelity, and verification status.
- Keeps internal verification vocabulary out of the prominent visual header; place it in reports or a compact disclosure.
- Keeps annotations associated with the relevant screen or flow.
- Uses realistic but non-production sample data.
- Contains no unresolved scaffold markers or starter copy.
- Traces every screen to the validated design plan.

## Packaging

- Preserve `index.html`, local CSS, local JavaScript, and local assets together.
- For structural and detailed wireframes, make a self-contained single HTML the primary download.
- Inline local CSS, JavaScript, images, and CSS assets. Approved Google Fonts may remain external with a system-font fallback.
- Package the complete work folder as ZIP as the editable source delivery.
- Never label a detached `index.html` that references missing sibling files as a single-file export.
- For UI mockups, keep ZIP as the primary delivery and create a single-file snapshot only when requested.

## Status vocabulary

- **Draft**: incomplete proposal.
- **Review-ready**: critical path is represented and static checks pass.
- **Visually inspected**: target viewports and critical interactions were rendered and checked.
- **Stakeholder-aligned**: responsible human selected the direction.
- **Research-supported**: relevant research or behavioral evidence supports the hypothesis.
- **Production-ready**: engineering, accessibility, content, analytics, security, and product review are complete.

These statuses are cumulative only when their conditions are actually met.

## Required reports

### UX audit

Scope, evidence, prioritized findings, unknowns, and recommended next investigation.

### Design rationale

Problem framing, alternatives considered, selected hypothesis, traceability to findings, tradeoffs, and human-owned decisions.

### QA report

Environment, viewports, interactions checked, static-check result, visual findings, fixed issues, remaining issues, and verification status.

## Required render evidence

- `renders/render-manifest.json`
- One recorded image for every design direction and requested viewport
- `inspected: true` and a specific inspection note for every image

The request cannot become `ready` without the required reports and render evidence.
