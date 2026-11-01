# upubhub textbook format

Files, relative to the project folder:

- `course/course.json`: kind `textbook`, title, audience, level, tool, objectives[], ai_provenance (`ai_generated` or `ai_assisted`), credits[], lessons[{id, title, objectives[], sections[]}]. Each lesson is one chapter. Ids look like `01-arches`.
- `course/textbook/<id>.md`: optional intro, then one `## ` heading per section, matching `sections` exactly and in order. At most 60,000 characters.
- `course/topics.json`: {chapter id: [{section, label, kind, prompt, objective, anchor}]}. At most 12 per chapter. kind: person, historic_figure, place or subject. prompt 10 to 2,000 characters; objective 10 to 1,000.
- Anchor: plain text copied from the section, occurring exactly once there, on a line with no links, images, code or markup. Empty means an end-of-section callout.
- Images: `![alt](../../assets/img/name.jpg)`, alt text required, published in Media studio or credited with `file`.
- Credits: {what, author, licence (CC-BY-4.0, CC-BY-SA-4.0, CC0-1.0, public-domain), source_url https, file?}.
- `UPLOAD.md`: the manual upload checklist.

No lesson plans, assessments or other files under `course/`.

Provided text: `inputs/textbook.md`, a `# ` heading per chapter when there are several, a `## ` heading per section. It is copied as written.
