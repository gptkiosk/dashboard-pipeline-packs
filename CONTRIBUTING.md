# Make your own template

This guide takes you from an idea to a template in the store. You copy an existing pack, change it, try it in your own
dashboard, run the checks, and open a pull request.

Templates run on other people's computers and their text goes to AI models, so the bar is a stable, predictable run that
cannot be steered into doing something else. The rules below are how the store keeps that promise.

## What a good template is

- **One deliverable, planned the same way every time.** The plan text names the stories in order, what each produces and
  which are a person's steps. Someone else running it with different settings should get the same shape of plan.
- **Checks that hold the shape.** Use `checks` so a plan that skips a required story or hands a person's step to an agent is
  blocked.
- **Settings, not loopholes.** Put what users may change in `customize`: numbers with a range, choices from a list, yes or no.
  Use a text setting only for facts such as a subject or audience; text settings never appear inside the plan text.
- **Short guides.** The planner reads each guide cut to about 1,600 characters (less when a template has many guides); stories
  can read the full file.
- **Examples.** At least one example per template, used by the rehearsal gate.
- **Honest requirements.** List every agent, system tool, provider, check, service and connector the template needs, using only
  names from `platform/tools.json`.

## 1. Start by copying a pack

Fork this repository, clone your fork, and copy the pack closest to what you want. `upubhub-lesson-plan` is the smallest
complete example; `upubhub-class` shows settings that change the plan; `local-website` shows media stages.

```sh
cp -R packs/upubhub-lesson-plan packs/my-template
cp -R examples/upubhub-lesson-plan examples/my-template
mv packs/my-template/project-types/upubhub-lesson-plan.json packs/my-template/project-types/my-template.json
```

Then give everything its own name:

- The pack id is the folder name: `id` in `pack.json`, `packs/<id>/` and `examples/<id>/` must all match.
- Each template's `id` matches its file name, `project-types/<id>.json`, and is listed in `pack.json` `project_types`.
- Rename the guides too. A dashboard finds a guide by name in the first installed pack that lists it, so two packs may share a
  guide name only when the files are identical; the build refuses anything else.
- Set `author` to your GitHub account and `pack_version` to `0.1.0`.

Ids are lowercase letters, digits and dashes, up to 40 characters, and must not be one the store or a dashboard already uses.

## 2. The folder layout

```
packs/<id>/
  pack.json                   the manifest (below)
  project-types/<type>.json   one file per template: plan text, checks, sign-offs, settings and requirements
  guides/<name>.md            short format and design guides the planner and stories read
examples/<id>/<name>.json     rehearsal examples; not shipped
```

Nothing else is allowed in a pack: only JSON and Markdown, no links, at most 40 files of 40 KB each.

## 3. `pack.json`, field by field

| Field | Required | What it holds |
| --- | --- | --- |
| `format`, `version` | yes | Always `"dashboard-pipeline-pack"` and `"0.1"`. |
| `id` | yes | The pack id; the folder name. |
| `pack_version` | yes | `major.minor.patch`. Raise it with every change (see Versioning). |
| `label` | yes | The name shown in the store. |
| `author` | yes | The GitHub account that maintains the pack. |
| `summary` | yes | One or two sentences for the store card: what the template produces and what stays the user's step. |
| `changes` | no | What changed in this version, at most 600 characters. Dashboards show it as **What's new** on an update. |
| `service` | no | The site the deliverable is for: `{"id", "label", "credential", "hosts"}`. `id` must be a service in `platform/tools.json`; `hosts` lists the only hosts your text may link to; leave `credential` as `null` unless a maintainer says otherwise. |
| `app_min` | yes | The oldest dashboard version the pack works with. It must be at least the `app_min` of every tool you name. |
| `project_types` | yes | The template ids in `project-types/`. |
| `guides` | no | The guide file names in `guides/`. |
| `general_guides` | no | Which of the dashboard's own general guides the planner reads (for example `readme-and-docs.md`), replacing the software defaults. Leave it out to keep the defaults. |
| `checks` | no | Dashboard checks the pack runs, such as `course-package`, which checks a course folder when its verification story is accepted. |
| `connectors` | no | Dashboard connectors the pack uses, such as `upubhub-push`, which sends finished files to upubhub after the user's final sign-off. A connector runs in the dashboard, never in a story. |

## 4. The template, field by field

A template is `project-types/<id>.json`. Everything in it reaches the planner model, so write it as a description of the
project, never as instructions to a model about itself.

| Field | What it holds |
| --- | --- |
| `id`, `label`, `summary` | The template's id, its name in the type picker, and what the user gets. |
| `suggest` | Patterns (regular expressions, lowercase) that suggest this template when a brief matches them. A suggestion only; the user chooses. |
| `keys` | Saved keys a story may use, such as `agent`, `openrouter` or `fal`. Shown to the user; it grants nothing. |
| `guides` | Which of the pack's guides the planner and stories read. |
| `planner_text` | The heart of the template: the deliverable, the settings in use, and the stories in order with who does each. May name a non-text setting as `{{setting_id}}`. |
| `failure_points` | Short lessons from runs that went wrong, so the planner avoids them. |
| `visual_checks` | What a person looks at before accepting the work. |
| `human_signoffs` | The decisions only a person makes. Each becomes a human story in the plan. |
| `checks` | Plan checks, below. |
| `media_default_tiers` | Optional starting quality for generated media: `{"image": "draft"}`; values `draft`, `standard` or `premium`. |
| `customize` | The settings, below. |
| `requires` | What the template needs, below. |

### Plan checks

Each check has an `id`, a `kind`, a `severity` (`block` stops the plan from being submitted; `warn` and `info` are listed) and
a `message` that tells the user how to fix the plan. Patterns are regular expressions matched against lowercase text.

- `has_story`: some story's title matches `match`. Add `"assignee": "human"` or `"agent"` to require who does it.
- `order`: every story whose title matches `then` comes after (depends on) a story whose title matches `first`.
- `not_agent_for`: no agent story matches `match` in its title, description or acceptance. Use it for steps that must stay a
  person's, such as uploading, publishing, paying or deploying.
- `requires_story`: when any story matches `match`, some story's title matches `requires_match`.

`has_story` and `order` read story titles, so name the stories in `planner_text` with the exact titles your checks look for
("a story titled \"Verify lesson plan files\""). Test the patterns against your examples; a pattern that is too broad blocks
good plans.

### Settings (`customize`)

Up to 12 settings, each with `id` (lowercase letters, digits, underscores), `label`, `type`, and optional `prompt`, `default`
and `required`.

- `integer`: `min` and `max`.
- `choice` and `multi`: `options`, 2 to 40 entries, without commas.
- `boolean`: yes or no.
- `text`: `max` up to 1,200 characters (default 400). At most four text settings. Text never enters the plan text: it reaches
  the planner as project facts, marked as data from the user.

`planner_text`, `failure_points`, `human_signoffs` and `visual_checks` may name any non-text setting as `{{id}}`; the planner
sees the chosen value or the default. A template that names a text setting, an unknown setting or a malformed placeholder does
not load. A setting that changes the plan, such as `content_source` in the upubhub templates, describes both paths in
`planner_text` ("Content source write: ... Content source provided: ...").

### Requirements (`requires`)

`app_min` (a version), and up to 12 names each under `agents`, `system_tools`, `providers`, `checks` and `services`. The type
picker shows anything the user's computer lacks, with a link to fix it. Agents are alternatives: any one installed is enough.
Connectors are named in `pack.json`, not here.

### Examples

Each template needs at least one `examples/<pack id>/<name>.json`:

```json
{
  "type": "my-template",
  "title": "A short project title",
  "brief": "What a user would type in New project.",
  "answers": {"level": "6", "approach": "hands-on"},
  "expect": {"stories_min": 7, "stories_max": 14, "titles": ["verify lesson plan files", "approve the lesson plan"]}
}
```

`answers` are text, keyed by your setting ids. `expect.titles` are patterns some story title must match. Give an example for
each path a choice setting opens, the way `upubhub-class` has one for `write` and one for `provided`.

## 5. Versioning

Every change to a pack raises `pack_version` and rewrites `changes` for the new version:

- **patch** (`1.0.1`): wording, a guide fix, a new example.
- **minor** (`1.1.0`): a new setting, a new story or check, a new template in the pack.
- **major** (`2.0.0`): a change that plans existing projects differently, or removes or renames a setting.

Write `changes` for the user deciding whether to update: what they get, and anything that now needs a newer dashboard. Raise
`app_min` when you start using a tool, check or connector that needs one. Old versions stay on the user's computer, so they
can switch back.

## 6. Test it in your own dashboard

Build an archive of your pack folder and import it:

```sh
COPYFILE_DISABLE=1 tar -czf my-template.tar.gz -C packs my-template
```

In the dashboard, open **Settings → Template store → Import a template**, read the notice, tick that you accept the risk, and
choose the archive (`COPYFILE_DISABLE=1` keeps macOS from adding hidden `._` files). Then create a project from your template and plan it.

- An import is local and **unvetted**: the store's scan, model review and rehearsal did not run on it, and its text goes to
  your AI models. Import only templates you wrote or have read.
- An import may not use a store or built-in id, so keep your own id. A store id is refused.
- It shows as **Local · unvetted** and never receives store updates. Import again with a higher `pack_version` to replace it
  while you iterate.

Plan each of your examples a few times. If plans keep missing a story, say it more plainly in `planner_text` or add a check.

## 7. Run the local checks

```sh
python3 -m unittest discover -s tests
python3 tools/build.py --check-only
python3 tools/scan.py --base-ref origin/main
python3 tools/readme.py
```

`build.py` validates every pack and example and the approved tools. `scan.py` looks for injection points (below) and, against
the base branch, for weakened gates. `readme.py` rewrites the catalog in `README.md`; commit that change with your pack. With a
dashboard checkout, `python3 tools/build.py --dashboard ../rcd-checkout` also runs the dashboard's own validator.

## What is refused

- Anything that is not JSON or Markdown, links, or more than 40 files.
- Text aimed at the model rather than the project: overriding instructions, role tags, hiding things from the user.
- Hidden characters, HTML, encoded strings, links to hosts the pack does not declare.
- Commands: network tools, sudo, global installs, pushing code, paths outside the project folder, reading secrets.
- Weakening an existing template: removing or downgrading a blocking check, a "not an agent step" rule or a human sign-off.

`tools/scan.py` checks all of this. If it flags something your template truly needs, say why in the pull request; only a
maintainer can accept a finding (`security/allow.json`).

## Needing a new tool

If your template needs an agent, system tool, provider, check, service or connector that is not in `platform/tools.json`, open
a separate pull request that adds it, with what it does and why. Checks and connectors are dashboard code, so they need a
dashboard release first; the maintainer will say so. Your template's pull request waits for that one.

## 8. Open the pull request

Push your branch and open a pull request against `main`. Fill in the template: what the template produces, who it is for, and
what you saw when you planned your examples. Then it passes these gates:

1. **Format, scan and catalog** run automatically on every pull request: the same checks as step 7, plus a reproducible build.
   Fix anything they report.
2. **Model review and rehearsal** run when a maintainer adds the `review` or `rehearse` label. The review model reads the change
   for hidden intent, scope creep, weakened safety, spend and data risks, and comments; it cannot approve anything. Rehearsal
   plans every example several times with the dashboard's real planner and fails if any plan breaks the template's checks or
   the example's `expect`.
3. **A maintainer reviews** every change and may ask for edits.
4. **A signed release** is the only way a template reaches dashboards. Merging alone ships nothing; a maintainer tags a
   release, checks the draft and publishes it.

Templates from maintainers are listed as **Official**. Accepted templates from anyone else are listed as **Community**, with
your account name: they passed every gate above, and you remain their author. Every later change, yours or anyone's, goes
through the same pull request and gates.
