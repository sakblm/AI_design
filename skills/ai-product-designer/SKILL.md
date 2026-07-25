---
name: ai-product-designer
description: Register and reuse local design systems, select a design project type, analyze existing product UI and user flows, and create validated design artifacts that follow the selected system. Use when Codex is asked to register or list design systems, create a wireframe, UI mockup, HTML slide proposal, UX audit, user flow, component specification, design-system audit, implementation handoff, critique or improve a web or app UI, compare design directions, or turn requirements and screenshots into reviewable artifacts.
---

# AI Product Designer

Turn product questions into reviewable design decisions and local HTML evidence. Treat the output as a design proposal, not as validated user research or production-ready code.

## Use chat as the default interface

When the user invokes `$ai-product-designer`, conduct intake and revisions in the Codex chat. Do not launch the Design Console unless the user explicitly asks for it.

Read `references/chat-intake.md`. Ask only for missing information and do not repeat questions already answered by the prompt, attachments, or prior messages. Start by resolving the working folder. Accept a typed path, the current project, or—only when the user prefers it—the native macOS chooser:

```bash
python3 <skill-dir>/scripts/select_workspace.py
```

Initialize the folder non-destructively:

```bash
python3 <skill-dir>/scripts/initialize_workspace.py "<workspace>"
```

Resolve the design system, current UI or evidence, desired outcome, artifact type, output level, directions, viewports, interaction, and font policy in chat. For screen-design work, always ask the user to choose one of these three output levels unless they have already stated it unambiguously:

- `structural-wireframe`: 構造ワイヤー
- `detailed-wireframe`: 詳細ワイヤー
- `ui-mockup`: UIモックアップ

Do not expose `low` / `mid` / `high` fidelity as the user-facing choice. Map the selected output level to the internal project type and fidelity. Summarize the intake before generation when material choices remain.

Write the resolved intake to a temporary JSON file with this shape:

```json
{
  "title": "Project title",
  "prompt": "User outcome and requested change",
  "designSystem": {
    "name": "Company Product",
    "sourcePath": "/path/to/design-system"
  },
  "outputLevel": "detailed-wireframe",
  "settings": {
    "viewports": ["390x844", "1440x1000"],
    "compareDirections": 3,
    "interactive": false,
    "allowGoogleFonts": true
  },
  "evidencePaths": ["/path/to/current-ui.png"]
}
```

Create and claim the request directly from chat:

```bash
python3 <skill-dir>/scripts/start_chat_request.py \
  --workspace "<workspace>" \
  --spec "<intake-json>"
```

Treat the returned request JSON and generated `work/<request-id>/design-request.json` as authoritative. Generate the artifact in that work folder. Do not wait for a separate UI submission.

For a wireframe, read `references/design-plan-contract.md` and `references/design-quality-benchmark.md`. Write `exploration/design-plan.json` before editing HTML. Validate it:

```bash
python3 <skill-dir>/scripts/validate_design_plan.py \
  "<workdir>/design-request.json" \
  "<workdir>/exploration/design-plan.json"
```

Create the request-specific unresolved review board only after the plan passes:

```bash
python3 <skill-dir>/scripts/scaffold_wireframe.py \
  --request "<workdir>/design-request.json" \
  --plan "<workdir>/exploration/design-plan.json" \
  --output "<workdir>/wireframe"
```

Replace every unresolved screen with a complete UI. Remove `data-template-state="unresolved"` and all `data-template-placeholder` attributes only after their content is implemented.

Open the HTML entrypoint directly when local file viewing works. When an HTTP preview is needed, start the preserved local server and open the request's direct preview URL; do not send the user to the console intake screen.

Do not stop after creating the request or scaffold. Continue through reports, rendering, validation, and finalization in the same task. If generation fails, mark the request `error` with a concise actionable message. Never leave a request in `generating` when the turn ends.

Read `references/design-system-registry.md` before registering a system. Read `references/project-types.md` after selecting a type.

## Continue or revise in chat

Treat `<workspace>/project.json` → `activeRequestId` as the current design unless the user names another request. For ordinary feedback, mark that request `generating`, update the design plan when the strategy or screen coverage changes, edit the existing files in `work/<request-id>/`, rerun visual QA and all validation, then finalize it again. Preserve history and do not create a new request or repeat intake.

A Skill cannot wake Codex after a task has ended, so revisions must arrive through chat. State this plainly if the user expects a local page to trigger Agent work.

## Preserve the optional HTML tool

Read `references/design-console.md` only when the user explicitly asks to open, test, or develop the existing tool. Keep its HTML/CSS/JavaScript and server scripts intact for future standalone productization. Do not use it as the default intake or revision interface.

## Select the operating mode

- **Audit**: Inspect an existing UI and return prioritized findings. Do not create a wireframe unless requested.
- **Explore**: Produce 2–3 materially different directions with tradeoffs and a recommendation.
- **Wireframe**: Create a reviewable HTML flow from an agreed direction.
- **End-to-end**: Run intake, audit, exploration, wireframe, and QA.
- **Design-system check**: Compare UI artifacts with supplied tokens, components, and usage rules.

Default to end-to-end for broad requests such as “improve this UI.” For small or explicit requests, use the narrowest matching mode.

## Establish the evidence boundary

1. Locate the brief, current UI, relevant flow, design system, device targets, and business or user goal.
2. Read `references/intake-contract.md`.
3. Separate:
   - **Observed**: directly visible in supplied artifacts.
   - **Reported**: stated by the requester or research.
   - **Inferred**: plausible but unverified.
4. Never invent analytics, research findings, component availability, technical constraints, or accessibility compliance.
5. Replace production personal data, credentials, and confidential values with realistic samples.
6. Read `references/security.md` before using URLs, external assets, remote fonts, package downloads, or production data. Google Fonts may be used when the requester or company policy allows it; record that network dependency.

If important inputs are missing, continue with labeled assumptions when the decision is reversible. Ask for direction before a missing choice would materially change the product strategy, target user, or primary flow.

## Create a design workspace

Run:

```bash
python3 scripts/init_design_work.py <output-directory> --title "<project title>"
```

This copies the local wireframe kit and creates the delivery structure without overwriting existing files. Keep input evidence separate from generated output.

When a Design Console request exists, use its generated `work/<request-id>/` workspace instead. Treat `design-request.json` as the authoritative selection of design system, project type, fidelity, viewports, and output options.

Use this structure:

```text
design-work/
├── brief.md
├── evidence/
├── design-system/
├── exploration/
├── wireframe/
├── renders/
└── reports/
```

## Run the workflow

### 1. Frame the problem

Write the intended user, situation, user job, current friction, desired behavior, business outcome, scope, constraints, and success signal in `brief.md`.

Do not begin from visual styling. Start from the decision or task the interface must help the user complete.

### 2. Audit the current experience

Map the relevant path from entry to outcome. For each finding, record:

- Evidence and location
- User consequence
- Severity: blocker, high, medium, or low
- Confidence: high, medium, or low
- Design principle involved
- Candidate response

Read `references/review-framework.md`. Prioritize causal issues and decision bottlenecks over cosmetic inconsistencies.

### 3. Explore directions

Read `references/design-plan-contract.md` and create the validated design plan before building UI.

Create 2–3 directions only when they differ in interaction model, information architecture, or decision strategy. Do not present minor styling variants as separate concepts.

For every direction include:

- Core hypothesis
- What changes
- What remains
- User and business benefit
- Risks and dependencies
- What would falsify the hypothesis

Recommend one direction and explain why. Pause for selection when the choice changes product behavior materially, unless the requester explicitly asked for autonomous execution.

### 4. Build the wireframe

Read `references/deliverable-contract.md`. Start from `assets/wireframe-kit/`.
Read `references/implementation-choice.md` when deciding between the default vanilla kit and a framework prototype.
Read `references/wireframe-quality-contract.md` and `references/design-quality-benchmark.md`; satisfy them literally. Generate the scaffold from the validated plan. When multiple directions are requested, build a complete marked wireframe for every direction; never use prose-only placeholders for the non-recommended directions.

- Use semantic HTML and the supplied design tokens.
- Keep CSS and JavaScript local.
- Represent the complete critical path, including important empty, loading, error, and recovery states.
- Keep the artifact static when `interactive` is false.
- When `interactive` is true, implement a meaningful state-changing interaction and its rendered result in every direction.
- Annotate design intent next to the interface rather than hiding it in a separate document.
- Mark simulated data and unimplemented actions.
- Preserve traceability from each major UI change to an audit finding or requirement.

Use the selected output level literally:

- **構造ワイヤー**: Complete structure, information order, navigation, media roles, and major states. Use grayscale or neutral colors and one restrained semantic accent at most. Do not use real photos, decorative imagery, gradients, decorative shadows, or brand polish. When images affect recognition, comparison, density, or layout, show neutral image skeletons with their count, placement, and aspect ratio; include an image-missing state when its absence changes the decision or layout.
- **詳細ワイヤー**: Keep the neutral wireframe treatment while adding realistic copy, representative data density, precise hierarchy, spacing, responsive behavior, and relevant component states. Use design-system structure and content patterns, but do not make it look production-finished.
- **UIモックアップ**: Apply the selected design system accurately, including brand color, typography, radii, elevation, imagery, responsive variants, and implementation-adjacent states.

High design quality does not mean high visual polish. Preserve strong information architecture, complete screens, realistic content, and rigorous QA at every output level.

For project types other than wireframe, follow the routing and deliverable rules in `references/project-types.md`. Do not silently substitute a wireframe for a selected slide, audit, flow, specification, or handoff.

### 5. Validate

Validate the plan first:

```bash
python3 scripts/validate_design_plan.py \
  <request-json> \
  <workdir>/exploration/design-plan.json
```

Run deterministic checks:

```bash
node scripts/validate_wireframe.mjs <path-to-wireframe/index.html>
```

When Google Fonts are explicitly allowed:

```bash
node scripts/validate_wireframe.mjs <path-to-wireframe/index.html> --allow-google-fonts
```

Read `references/visual-qa-loop.md`. Open the result through a local HTTP preview and inspect every direction, target viewport, and critical interaction. Check:

- Overflow, clipping, overlap, and unexpected wrapping
- Keyboard focus and visible focus state
- Touch targets and control labels
- Empty, loading, error, and recovery states
- Long Japanese text and realistic content density
- Token and component consistency
- Whether the proposed flow actually addresses the stated problem

Run the request-specific completeness check:

```bash
python3 scripts/validate_delivery.py <request-json> <path-to-wireframe/index.html>
```

Save every accepted screenshot under `renders/` and record it:

```bash
python3 scripts/record_visual_check.py \
  --workdir "<workdir>" \
  --direction "<direction-id>" \
  --viewport "<width>x<height>" \
  --image "<image-file>" \
  --notes "<specific visual finding and fix>"
```

Do not mark the request ready when the plan, requested direction count, required screen count, reports, or any direction/viewport render is missing.

Do not claim visual validation unless the rendered page was inspected. Record unverified items explicitly.

### 6. Deliver

Provide:

- `wireframe/`: a local HTML/CSS/JS bundle whose relative paths remain intact
- `exports/<request-id>.html`: the primary, self-contained export for structural and detailed wireframes
- `renders/`: representative viewport screenshots
- `reports/ux-audit.md`
- `reports/design-rationale.md`
- `reports/qa-report.md`
- A short list of decisions the human designer still owns

For structural and detailed wireframes, deliver a self-contained single HTML file as the primary artifact. Inline local CSS, JavaScript, and assets with `scripts/create_single_file_html.py`; an `index.html` that still depends on missing sibling files is not a single-file export. Also retain the multi-file source bundle in the ZIP for later editing. For UI mockups, use the ZIP as the primary artifact and create a single-file snapshot only when requested.

Finalize with the quality-gated command. It marks the request `error` instead of leaving it in `generating` when any gate fails:

```bash
python3 scripts/finalize_request.py \
  --workspace "<workspace>" \
  --request-id "<request-id>" \
  --entrypoint "wireframe/index.html"
```

Use the status terms in `references/deliverable-contract.md`. Do not label a proposal “validated” merely because static checks pass.

## Guardrails

- Do not replace research with model opinion.
- Do not optimize only for conversion when user trust, comprehension, safety, or reversibility would degrade.
- Do not add UI complexity without identifying the decision or failure it resolves.
- Do not silently diverge from the design system; document necessary exceptions.
- Do not fetch remote code dependencies merely for visual polish. Approved Google Fonts are the explicit exception.
- Do not edit the source product while working on a wireframe unless explicitly asked.
