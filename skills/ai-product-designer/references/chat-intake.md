# Chat-first intake

Ask only for information that is still missing. Ask no more than three concise questions in one message.

## Required

1. Working folder
2. Intended user outcome or problem to improve
3. Artifact type
4. Design-system name or local path

For wireframes and mockups, also establish:

- Current UI or reference material
- Target viewports
- Output level: 構造ワイヤー / 詳細ワイヤー / UIモックアップ
- Number of directions
- Whether interaction and Google Fonts are allowed

Always ask for the output level when screen design is requested and the user has not already selected one. Ask in plain language:

> 仕上がりはどれにしますか？  
> 構造ワイヤー（構造・導線の確認）／詳細ワイヤー（実在コピー・状態まで検討）／UIモックアップ（デザインシステムを反映した完成見本）

Do not ask a second fidelity question. Internally map:

| Output level | `outputLevel` | Project type | Fidelity |
|---|---|---|---|
| 構造ワイヤー | `structural-wireframe` | `wireframe` | `low` |
| 詳細ワイヤー | `detailed-wireframe` | `wireframe` | `mid` |
| UIモックアップ | `ui-mockup` | `ui-mockup` | `high` |

## Defaults

Offer defaults instead of blocking on reversible choices:

- Output level: no silent default; ask when missing
- Directions: 1 for a specific solution, 3 for exploration
- Viewports: 390×844 and 1440×1000
- Interactive: No. Enable only for an explicitly requested prototype or a hypothesis that depends on state change.
- Google Fonts: Allowed

Do not ask the user to repeat files, screenshots, paths, or requirements already supplied in the task.

## Confirmation

Before generation, summarize the resolved intake in a compact list. Continue immediately when the user has already authorized autonomous execution. Ask for confirmation only when a missing choice would materially change the user, primary flow, product strategy, or deliverable type.

## Revisions

Use the active request from `project.json` unless the user names another request. Treat ordinary feedback as a revision to the existing artifact. Do not create a new request or ask the full intake again.
