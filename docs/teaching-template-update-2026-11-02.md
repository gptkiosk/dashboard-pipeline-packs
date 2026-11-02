# Teaching templates and store descriptions

Unreleased implementation, 2026-11-02, branch `codex/textbook-feature-guidance`,
base `2c8bd3b`. No installed template, model or production class was changed.

- All eight manifests and project types have matching, clearer summaries:
  deliverable, when to choose it and what remains a human decision.
- Software packs: 1.0.1; class: 0.4.0; textbook and lesson plan: 0.2.0.
- All three teaching packs include byte-identical
  `textbook-learning-features.md`: source-to-plan workflow, evidence and source
  appendix, named editable chat-outs, bounded text-grounded assessments and
  provisional grades reviewed by teachers. `GEOL` joins existing subject codes.
- Interactive visuals remain reviewed specifications until both the published
  application contract and dashboard payload validators support them. No fake
  observations, arbitrary executable visual code or unsupported push payload.

Prompt footprint: each teaching `planner_text` grows exactly 419 characters:
class 4,437 → 4,856, lesson plan 2,757 → 3,176, textbook 3,587 → 4,006. The shared
guide is 2,440 characters; the existing ~1,600-character planner guide excerpt
budget is unchanged. Essential visual-format limitations are also in planner
text so truncating the guide cannot imply unsupported capabilities. Stories
read the full guide. No model or paid rehearsal ran for these text changes.

Checks: 26 unit tests; all eight packs build/check and security scan; generated
README current; both MCD and RCD validator builds produce byte-identical outputs.
Dashboard 0.6.91 adds icons and untruncated installed/offline card descriptions;
the existing 0.6.90 minimum remains valid for the unchanged connector format.

Release gates: PR review, CI including the normal model-review/rehearsal gates,
explicit maintainer publish approval, signed pack release, then an intentional
store update. A merge alone does not update installed templates. Paired dashboard
package releases and installation are separate steps. Preserve existing projects
and their frozen template versions. The live earthquake class rename is a
separate authenticated operator action, not an effect of updating this pack.
