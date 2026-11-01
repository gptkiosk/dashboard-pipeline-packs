# Dashboard template store

## Functionality at a glance

A data-only catalog of optional planner/project packs for the [Mac Control Dashboard](https://github.com/gptkiosk/mac-control-dashboard) and [Raspberry Pi Control Dashboard](https://github.com/gptkiosk/rbp-control-dashboard).

- Packs contain JSON project definitions and Markdown guides, not executable agent code or a hosted service.
- Dashboards install release archives after verifying the signed index, archive digests, and supported format.
- The upubhub packs (class, textbook, lesson plan) guide creation of compatible deliverables. Installing one does not establish a shared login or publish anything: content reaches upubhub only when the user pushes it from the dashboard after a final sign-off (connector `upubhub-push`, dashboard 0.6.90 or newer, with the user's own saved upubhub token) or uploads it by hand. Pushed items land as private drafts.

Templates for the Mac and Raspberry Pi control dashboards (MCD and RCD). A template turns a short brief into a predictable,
repeatable project run for one kind of deliverable, for example a upubhub.com class: the stories to plan, the checks a plan
must pass, where a person signs off, and short format guides.

Each template has a fixed part and a few **settings**. The fixed part is what makes runs repeatable and is the same for
everyone. The settings (numbers, choices, yes or no, and a little short text) are what you personalize, and they cannot
change the fixed part.

You add templates inside the dashboard, in **Settings → Template store**. Nothing here needs to be downloaded by hand.
Templates are published in packs; this repository keeps its original name so existing dashboards keep finding it.

## What a pack is

A pack is data only: JSON and Markdown. It never contains code that runs on your computer. Checks and service connectors are
part of the dashboard itself; a pack names the ones it uses, and a dashboard that does not have them refuses the pack and asks
you to update.

```
packs/<id>/
  pack.json                   id, pack_version, label, author, summary, changes, service, app_min, project_types, guides, general_guides, checks, connectors
  project-types/<type>.json   the template: plan text, checks, sign-offs, settings (customize) and requires
  guides/<name>.md            short format guides the planner and stories read
```

The template format is described in the dashboard's `docs/configuration/project-types.md`; packs in
`docs/configuration/pipeline-packs.md`.

## Submit a template

Anyone can offer a template. [CONTRIBUTING.md](CONTRIBUTING.md) is the full guide: copy an existing pack, describe every field,
try it in your own dashboard with **Settings → Template store → Import a template**, run the local checks and open a pull
request. Accepted templates are listed as **Community** with your account name.

## How templates are checked

Every pull request runs these checks before a maintainer reviews it:

1. **Format**: every pack and template must load in the dashboard's own validator, stay within size limits, and list only
   approved tools (below) that are old enough for its `app_min`.
2. **Injection scan** (`tools/scan.py`, rules in `security/`): all template text reaches a model, so all of it is scanned for
   hidden characters, encoded payloads, instructions aimed at the model, secret handling, network and host commands, links to
   unlisted hosts, and changes that weaken a template's checks or sign-offs.
3. **Model review** (advisory, when a maintainer adds the `review` label): a reviewer model reads the change for hidden intent,
   scope creep, weakened safety, spend and data risks, and posts a comment. It cannot approve anything.
4. **Rehearsal** (when a maintainer adds the `rehearse` label): the dashboard builds its real planner prompt for each of the
   template's examples (`examples/<pack id>/*.json`), a model plans each one three times, and the dashboard judges every plan
   with its own validation and the template's plan checks. A template passes when every run passes.

Both run this repository's own tools on the pull request's files as data, and only on a maintainer's label, so a contribution
cannot run code or spend on its own. They need the repository secret `OPENROUTER_API_KEY`, the variables `REVIEW_MODEL`,
`REHEARSAL_MODEL` and `DASHBOARD_REPOSITORY`, and the labels `review` and `rehearse`; until those exist they say what is missing
in their comment.

A merge alone ships nothing. Only a signed release reaches a dashboard.

## How packs are released and trusted

1. Change a pack under `packs/` and raise its `pack_version`. The **Check packs** workflow validates every pack, scans it,
   checks this README's catalog and builds every pack twice to confirm the archives are reproducible.
2. Push a tag such as `v2026.11.01`. The **Release packs** workflow builds one archive per pack and the index
   `pipeline-packs.json` (each archive with its sha256, plus the approved tools), signs the index with the `dashboard-release`
   key and opens a **draft** release.
3. Check the draft, then publish it. Dashboards read only the latest published release.

A dashboard checks the index signature against the release public key built into its own verified code (the same key as in
[allowed_signers](allowed_signers)), then each archive against the signed sha256, then every file, before installing anything.

The release workflow needs the repository secret `RELEASE_SSH_PRIVATE_KEY` (the `dashboard-release` private key used by the
dashboard releases). Optionally set the repository variable `DASHBOARD_REPOSITORY` (for example
`gptkiosk/rbp-control-dashboard`) to also run every pack through that dashboard's own validator at release.

To test locally:

```sh
python3 -m unittest discover -s tests
python3 tools/build.py --dashboard ../rcd-checkout
python3 tools/scan.py --base-ref origin/main
python3 tools/readme.py --check
OPENROUTER_API_KEY=... python3 tools/rehearse.py --dashboard ../rcd-checkout --model <model> --pack <id>
```

<!-- catalog:start (generated by tools/readme.py; do not edit by hand) -->

## Approved templates

### GCP hosted app (containerized application on Google Cloud)

`gcp-hosted-app` in pack `gcp-hosted-app` 1.0.0 · Official, by gptkiosk · dashboard 0.6.88 or newer

A containerized application deployed to an explicitly named Google Cloud target such as Cloud Run, with runtime verification and delivery evidence.

Settings you choose: Main workflows, Platform and delivery, Data and integrations, Google Cloud hosting.

Needs: one of the agents claude, codex, grok, openclaw.

### GCP hosted website (illustrated site deployed to Google Cloud)

`gcp-hosted-website` in pack `gcp-hosted-website` 1.0.0 · Official, by gptkiosk · dashboard 0.6.88 or newer

An original illustrated website with themed pages and generated media, delivered through an explicitly planned Google Cloud deployment and dashboard-managed preview review.

Settings you choose: Pages and interactions, Look and references, Media source, Artwork and media details, Google Cloud hosting.

Needs: one of the agents claude, codex, grok, openclaw; system tools node.

### Local website (illustrated site reviewed on this host)

`local-website` in pack `local-website` 1.0.0 · Official, by gptkiosk · dashboard 0.6.88 or newer

An original, illustrated static website with themed pages, generated media, and dashboard-managed local preview review. It is not cloud hosted by this project.

Settings you choose: Pages and interactions, Look and references, Media source, Artwork and media details.

Needs: one of the agents claude, codex, grok, openclaw; system tools docker, node.

### Other (does not exactly fit)

`other` in pack `other` 1.0.0 · Official, by gptkiosk · dashboard 0.6.88 or newer

A project that does not exactly fit a listed type. It is planned from the brief and the general practices, and the plan says which listed type it resembles and which of that type's gates still apply.

Settings you choose: Finished result, What is different?.

Needs: one of the agents claude, codex, grok, openclaw.

### Packaged app (local install from a public GitHub release)

`packaged-app` in pack `packaged-app` 1.0.0 · Official, by gptkiosk · dashboard 0.6.88 or newer

An application people install on their own machine from a signed package published as a GitHub release. Not cloud deployed. Examples: the Mac and Raspberry Pi control dashboards.

Settings you choose: Main workflows, Platform and delivery, Data and integrations.

Needs: one of the agents claude, codex, grok, openclaw.

### upubhub class (textbook, lesson plans, assessments)

`upubhub-class` in pack `upubhub-class` 0.3.0 · Official, by gptkiosk · dashboard 0.6.90 or newer

A short course a teacher teaches from on upubhub.com: a textbook with discussion topics, one lesson plan per lesson and class assessment settings. The text is written new or converted from the teacher's own files. After the teacher's final sign-off the dashboard can push it to upubhub as private drafts and an invite-only class.

Settings you choose: Content source, Subject code, Level, Class name, Subject and scope, Number of lessons, Sources, Illustrate the lessons, Illustration style, Assessment attempts, Grading strictness, Assessment emphasis.

Needs: dashboard checks course-package; services upubhub; connectors upubhub-push.

### upubhub lesson plan (one lesson)

`upubhub-lesson-plan` in pack `upubhub-lesson-plan` 0.1.0 · Official, by gptkiosk · dashboard 0.6.90 or newer

One lesson plan for upubhub.com: objectives, materials, timed activities, a check for understanding and notes for when students struggle, written new or converted from the teacher's own Markdown. After the teacher's final sign-off the dashboard can push it to upubhub as a private draft.

Settings you choose: Content source, Lesson title, Topic and scope, Level, Lesson length (minutes), Approach, Sources.

Needs: services upubhub; connectors upubhub-push.

### upubhub textbook (chapters with discussion topics)

`upubhub-textbook` in pack `upubhub-textbook` 0.1.0 · Official, by gptkiosk · dashboard 0.6.90 or newer

One textbook for upubhub.com: chapters with "## " sections and discussion (chat-out) topics anchored in the text, written new or converted from the author's own Markdown. After the author's final sign-off the dashboard can push it to upubhub as a private draft.

Settings you choose: Content source, Textbook title, Subject and scope, Level, Number of chapters, Discussion topics per chapter, Sources, Illustrate the chapters, Illustration style.

Needs: services upubhub; connectors upubhub-push.

## Approved tools

A template may require only these. Asking for a new one is its own pull request to `platform/tools.json`.

### Agents

| Name | Id | Since | What it does |
|---|---|---|---|
| Claude Code | `claude` | 0.6.0 | Anthropic's coding agent, run on your Claude membership or API key. Writes and edits files in a story's workspace. |
| Codex | `codex` | 0.6.0 | OpenAI's coding agent, run on your ChatGPT membership or API key. Writes and edits files in a story's workspace. |
| Grok | `grok` | 0.6.0 | xAI's coding agent. Writes and edits files in a story's workspace. |
| OpenClaw | `openclaw` | 0.6.0 | Open agent runtime for any OpenRouter model; used for cheaper read-only and review stories. |
| Hermes | `hermes` | 0.6.0 | The coordinator: plans and follows a project, never writes code itself. |

### System tools

| Name | Id | Since | What it does |
|---|---|---|---|
| Python 3 | `python3` | 0.6.0 | Runs Python scripts and tests in a story's workspace. |
| Node.js | `node` | 0.6.0 | Runs JavaScript builds and tests; installed with the agent tools. |
| FFmpeg | `ffmpeg` | 0.6.0 | Converts and trims audio and video for media stories. |
| Docker CLI | `docker` | 0.6.0 | Builds and runs containers; a host step, never inside an agent story. |
| Colima | `colima` | 0.6.0 | The local container engine Docker uses on a Mac. |
| GitHub CLI | `gh` | 0.6.0 | The dashboard's own repository and pull request steps; stories never call it. |
| Gitleaks | `gitleaks` | 0.6.61 | Scans a workspace for committed secrets. |
| CSS check | `csstree-validator` | 0.6.61 | Checks stylesheets for invalid CSS. |
| Playwright | `playwright` | 0.6.85 | Drives a browser for screenshots and page checks. |

### Providers

| Name | Id | Since | What it does |
|---|---|---|---|
| OpenRouter | `openrouter` | 0.6.0 | API access to many models, billed per use with your own key. |
| fal | `fal` | 0.6.13 | Image and video generation in Media studio, billed per use with your own key after you approve the spend. |

### Dashboard checks

| Name | Id | Since | What it does |
|---|---|---|---|
| Course package check | `course-package` | 0.6.87 | Checks a course folder against upubhub's import and class-setup limits before the verification story is accepted. |

### Services

| Name | Id | Since | What it does |
|---|---|---|---|
| upubhub.com | `upubhub` | 0.6.87 | Publishing and classroom site. Packs prepare files for it; the user uploads them, or pushes them with the upubhub-push connector after signing off. |

### Connectors

| Name | Id | Since | What it does |
|---|---|---|---|
| Push to upubhub | `upubhub-push` | 0.6.90 | After your final sign-off, the dashboard pushes a course, textbook or lesson plan to upubhub.com as private drafts with your saved upubhub token. Agents never hold the token. |

<!-- catalog:end -->
