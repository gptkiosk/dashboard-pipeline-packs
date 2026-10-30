# Dashboard pipeline packs

## Functionality at a glance

A data-only catalog of optional planner/project packs for the [Mac Control Dashboard](https://github.com/gptkiosk/mac-control-dashboard) and [Raspberry Pi Control Dashboard](https://github.com/gptkiosk/rbp-control-dashboard).

- Packs contain JSON project definitions and Markdown guides, not executable agent code or a hosted service.
- Dashboards install release archives after verifying the signed index, archive digests, and supported format.
- The upubhub class pack guides creation of compatible course deliverables. Installing it does not establish a shared login or automatically publish content to upubhub; export/import and any service credentials remain explicit operator steps.

Optional add-ons for the Mac and Raspberry Pi control dashboards (MCD and RCD). A pack teaches the dashboard's planner one kind of deliverable for one service, for example a upubhub.com class: its project type, the settings a user may choose, sign-offs and short format guides.

You add a pack inside the dashboard, in **Settings → Installs & updates → Pipeline packs**. Nothing here needs to be downloaded by hand.

## What a pack is

A pack is data only: JSON and Markdown. It never contains code that runs on your computer. Checks and service connectors are part of the dashboard itself; a pack names the ones it uses, and a dashboard that does not have them refuses the pack and asks you to update.

```
packs/<id>/
  pack.json                   id, pack_version, label, summary, service, app_min, project_types, guides, general_guides, checks, connectors
  project-types/<type>.json   the same schema as the dashboard's built-in project types
  guides/<name>.md            short format guides the planner and stories read
```

The full format is described in the dashboard's `docs/configuration/pipeline-packs.md`.

## How packs are released and trusted

1. Change a pack under `packs/` and raise its `pack_version`. The **Check packs** workflow validates every pack and builds it twice to confirm the archives are reproducible.
2. Push a tag such as `v2026.11.01`. The **Release packs** workflow builds one archive per pack and the index `pipeline-packs.json` (each archive with its sha256), signs the index with the `dashboard-release` key and opens a **draft** release.
3. Check the draft, then publish it. Dashboards read only the latest published release.

A dashboard checks the index signature against the release public key built into its own verified code (the same key as in [allowed_signers](allowed_signers)), then each archive against the signed sha256, then every file, before installing anything.

The release workflow needs the repository secret `RELEASE_SSH_PRIVATE_KEY` (the `dashboard-release` private key used by the dashboard releases). Optionally set the repository variable `DASHBOARD_REPOSITORY` (for example `gptkiosk/rbp-control-dashboard`) to also run every pack through that dashboard's own validator at release.

To test locally:

```sh
python3 -m unittest discover -s tests
python3 tools/build.py --dashboard ../rcd-checkout
```
