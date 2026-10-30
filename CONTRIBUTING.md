# Offering a template

Thank you for helping. Templates run on other people's computers and their text goes to AI models, so the bar is a stable,
predictable run that cannot be steered into doing something else. These rules are how the store keeps that promise.

## What a good template is

- **One deliverable, planned the same way every time.** The plan text names the stories in order, what each produces and
  which are a person's steps. Someone else running it with different settings should get the same shape of plan.
- **Checks that hold the shape.** Use `checks` (`has_story`, `order`, `not_agent_for`, `requires_story`) so a plan that skips a
  required story or hands a person's step to an agent is blocked.
- **Settings, not loopholes.** Put what users may change in `customize`: numbers with a range, choices from a list, yes or no.
  Use a text setting only for facts such as a subject or audience; text settings never appear inside the plan text.
- **Short guides.** Each guide is cut at about 1,600 characters in the planner's prompt; stories can read the full file.
- **Honest requirements.** List every agent, system tool, provider, check and service the template needs in `requires`, using
  only names from `platform/tools.json`.

## What is refused

- Anything that is not JSON or Markdown, links, or more than 40 files.
- Text aimed at the model rather than the project: overriding instructions, role tags, hiding things from the user.
- Hidden characters, HTML, encoded strings, links to hosts the pack does not declare.
- Commands: network tools, sudo, global installs, pushing code, paths outside the project folder, reading secrets.
- Weakening an existing template: removing or downgrading a blocking check, a "not an agent step" rule or a human sign-off.

`tools/scan.py` checks all of this. If it flags something your template truly needs, say why in the pull request; only a
maintainer can accept a finding (`security/allow.json`).

## Needing a new tool

If your template needs an agent, system tool, provider, check or service that is not in `platform/tools.json`, open a
separate pull request that adds it, with what it does and why. Some tools need a dashboard change first; the maintainer will
say so. Your template's pull request waits for that one.

## How a pull request is reviewed

1. **Format, scan and catalog** run automatically on every pull request. Fix anything they report.
2. **Model review and rehearsal** run when a maintainer adds a label (being built; until then a maintainer reviews and test-plans
   by hand).
3. A maintainer reviews every change. Merging does not publish: only a signed release, published by a maintainer, reaches
   dashboards. Accepted templates are listed as **Community** with your account name.

Run the same checks locally first:

```sh
python3 -m unittest discover -s tests
python3 tools/build.py --check-only
python3 tools/scan.py --base-ref origin/main
python3 tools/readme.py
```
