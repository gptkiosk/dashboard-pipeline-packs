# upubhub lesson plan format

Files, relative to the project folder:

- `course/course.json`: kind `lesson_plan`, title, audience, level, tool, objectives[], ai_provenance (`hand_crafted` if provided, else `ai_generated` or `ai_assisted`), credits[], lessons[{id, title, objectives[]}] with exactly one lesson. The id looks like `01-bridges`.
- `course/lesson-plans/<id>.md`: a `# ` title, then these `## ` sections in order: Objectives, Materials, Activities, Check for understanding, When students struggle. Activities lists each step with its minutes; the minutes add up to the lesson length.
- Credits: {what, author, licence (CC-BY-4.0, CC-BY-SA-4.0, CC0-1.0, public-domain), source_url https}.
- `UPLOAD.md`: the manual upload checklist.

No textbook, topics, assessments or other files under `course/`.

Provided text: exactly one `.md` file in `inputs/lesson-plans/`. It is copied as written and declared `hand_crafted`; missing sections are reported to the teacher, not written for them.
