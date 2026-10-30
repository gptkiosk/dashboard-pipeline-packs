# upubhub class package format

Files, relative to the project folder:

- `course/course.json`: title, audience, level, tool, objectives[], ai_provenance (`ai_generated` or `ai_assisted`), credits[], lessons[{id, title, objectives[], sections[]}]. Lesson ids look like `01-forces`.
- `course/textbook/<id>.md`: optional intro, then one `## ` heading per section, matching `sections` exactly and in order. At most 60,000 characters.
- `course/topics.json`: {lesson id: [{section, label, kind, prompt, objective, anchor}]}. At most 12 per lesson. kind: person, historic_figure, place or subject. prompt 10 to 2,000 characters; objective 10 to 1,000.
- Anchor: plain text copied from the section, occurring exactly once there, on a line with no links, images, code or markup. Empty means an end-of-section callout.
- `course/lesson-plans/<id>.md`: one per lesson.
- `course/assessments/<id>.json`: objectives (10 to 3,000), topics (labels from topics.json), question_target 1 to 10, assessment_length 1 to 10, max_attempts 1 to 3, grading_strictness lenient/balanced/strict, accuracy_weight, reasoning_weight, application_weight 1 to 5, rubric_notes.
- Images: `![alt](../../assets/img/name.jpg)`, alt text required, published in Media studio or credited with `file`.
- Credits: {what, author, licence (CC-BY-4.0, CC-BY-SA-4.0, CC0-1.0, public-domain), source_url https, file?}.
- `UPLOAD.md`: the teacher's upload and class-setup checklist.

No other files under `course/`.
