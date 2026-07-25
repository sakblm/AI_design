# Design plan contract

Create and validate `exploration/design-plan.json` before editing the HTML artifact. Treat the plan as the bridge between evidence and screens. Use the request's `settings.outputLevel` as the authoritative finish level.

## Required shape

```json
{
  "schemaVersion": 1,
  "problemStatement": "The product problem to solve",
  "primaryUserDecision": "The decision or task the UI must help complete",
  "evidenceSummary": [
    {
      "id": "E1",
      "source": "/path/to/current-screen.png",
      "observation": "What is directly visible",
      "confidence": "high"
    }
  ],
  "requirements": [
    {
      "id": "R1",
      "statement": "A testable interface requirement",
      "sources": ["E1"]
    }
  ],
  "directions": [
    {
      "id": "direction-a",
      "name": "Human-readable direction name",
      "hypothesis": "How this direction changes user behavior or judgment",
      "strategy": "The distinct interaction model or information strategy",
      "solves": ["R1"],
      "risks": ["What may not work"],
      "screens": [
        {
          "id": "a-1",
          "name": "Screen or state name",
          "userDecision": "What the user understands or decides here",
          "state": "default",
          "requirements": ["R1"],
          "mediaStructure": {
            "required": true,
            "role": "候補を視覚的に識別し、比較密度を確認する",
            "kind": "image",
            "count": 1,
            "aspectRatio": "4:3",
            "showMissingState": true
          }
        }
      ]
    }
  ],
  "recommendedDirection": "direction-a"
}
```

## Quality rules

- Base observations on supplied evidence. Label reported and inferred information in the audit rather than presenting it as observed.
- Write requirements as interface outcomes, not visual treatments.
- Make every direction differ in interaction model, information architecture, or decision strategy.
- Use one screen or state per direction for `structural-wireframe`, two for `detailed-wireframe`, and three for `ui-mockup`.
- Use multiple states of one screen when the task is genuinely single-screen. Do not invent unrelated navigation merely to reach the count.
- Give every screen a concrete user decision and trace it to one or more requirement IDs.
- Give every screen a `mediaStructure` decision. When media is required, state its role, kind, count, aspect ratio, and whether a missing-media state must be shown. When it is not required, use `{"required": false, "reason": "..."}`.
- Treat real photos and decorative imagery separately from media structure. Structural wireframes prohibit the former but retain neutral slots for the latter.
- If supplied evidence contains image-led cards, galleries, avatars, maps, or video, at least one relevant screen must preserve that structure. To deliberately remove all observed media, add a top-level `mediaDecision` with `{"removeObservedMedia": true, "reason": "concrete product reason"}`.
- Cover the critical path and the most important uncertainty or recovery state.
- Recommend one direction only after its tradeoffs are explicit.

Validate the plan with `scripts/validate_design_plan.py`. Do not generate the wireframe scaffold until the plan passes.
