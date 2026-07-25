# Design quality benchmark

Use this benchmark for review-board wireframes and UI explorations. It captures the transferable qualities of strong design-tool output without copying a particular product's visual style.

## Review-board structure

For each problem area:

1. Name the decision problem.
2. Present each direction with a stable ID and a one-sentence strategy.
3. Explain the current friction and the proposed response in realistic language.
4. Show the requirements or user problems the direction solves.
5. Place two or more complete screens or states directly below the hypothesis.
6. Add a short caption explaining the design decision demonstrated by each screen.
7. End with tradeoffs, a recommendation, and the next useful refinement.

## Product-design depth

- Show how the user enters, understands, compares, decides, recovers, and returns when those moments are in scope.
- Resolve a real decision bottleneck in every screen. Avoid decorative components with no stated job.
- Use realistic Japanese content, prices, dates, labels, uncertainty, and content density.
- Preserve media structure when images, galleries, avatars, maps, or video affect recognition, comparison, trust, or layout. Removing real imagery must not remove its information slot.
- Preserve context across screens; do not present disconnected mockups.
- Make uncertainty visible and give the user a useful next action.

## Visual quality

- Keep the artifact header subordinate to the proposed UI.
- Establish a clear hierarchy among problem, direction, hypothesis, screen, and annotation.
- Use a deliberate canvas, type scale, spacing rhythm, border treatment, and restrained accent color.
- Follow the registered design system only to the depth allowed by `settings.outputLevel`.
- Avoid oversized headings, large empty areas, generic dashboard cards, and repeated placeholder layouts.
- Make mobile screens feel like complete products rather than collections of boxes.

High design quality is independent of visual finish:

- **構造ワイヤー** may be visually plain but must still have strong information order, complete critical states, and labeled media skeletons where media matters.
- **詳細ワイヤー** must be realistic and precise while remaining neutral; gradients, decorative shadows, real imagery, and production-like brand polish are out of scope. Media skeletons are in scope.
- **UIモックアップ** may use the full visual system and production-like finish.

## Interaction restraint

- Default wireframes and explorations to static review artifacts.
- Add working interaction only when the requester asks for a prototype or the hypothesis depends on state change.
- Do not add toasts, tabs, menus, or buttons merely to demonstrate that JavaScript works.
- When interaction is requested, make at least one critical interaction work in every direction and show its resulting state.

## Acceptance examples

A three-direction detailed-wireframe exploration should normally contain at least six complete screens or states, realistic content, distinct strategies, screen-level annotations, neutral visual treatment, and rendered evidence at every requested viewport. Passing HTML syntax checks alone is never sufficient.
