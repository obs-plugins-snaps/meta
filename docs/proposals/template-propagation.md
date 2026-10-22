# Proposal: automatic template propagation to plugin repositories

Every change to the [template](https://github.com/obs-plugins-snaps/template)
(bug report templates, CI improvements, README wording, ...) currently
requires manual PRs to every plugin repository. This proposal automates
that: when the template gets a new tag, a workflow opens one update PR per
managed plugin repository.

## Design

### Source of truth for the plugin list

`meta/plugins/` is the single source of truth. The propagation workflow
reads the directory listing via the GitHub API:

- `plugin_name` = record filename minus the `-obs-studio.json` suffix
  (same derivation rule as `scripts/generate.py`, documented in
  `plugins/schema.json`)
- target repository = `plugin_name` + `-obs-studio-snap`

Nothing is duplicated: adding a record to `meta/plugins/` is all it takes
to join the propagation set. If a record exists but the repository does
not yet (the creation-automation gap), the run skips it and reports it in
the job summary instead of failing.

### Trigger

`workflow_run` on completion of the template's auto-tag workflow (which
tags every merge to main with the next patch version), plus
`workflow_dispatch` with an optional tag override for manual runs.

### Per-repository flow

1. Read `.copier-answers.yml`; skip if `_commit` already equals the latest
   tag.
2. Skip if the branch `template-update-<tag>` already exists (idempotent
   re-runs).
3. Full clone, then `copier update --defaults --vcs-ref <tag>`. This is a
   three-way merge from the recorded commit, so hand-tuned parts of a
   plugin repository (build recipes, patches) are preserved; conflicts
   are marked in the files for resolution in the PR.
4. Commit, push the branch, open a pull request "Update template to
   <tag>" including the compare link between the old and new template
   versions.

A job summary table reports each plugin as skipped / updated / PR opened
/ failed, making every propagation run auditable from the template
repository's Actions tab.

### Implementation location

A single `propagate.yaml` workflow in the `template` repository. It runs
with the existing `obs-plugins-snaps-bot` GitHub App token, which now has
the required permissions (`contents: write`, `pull_requests: write`,
`workflows: write`) on all organization repositories.

## Non-goals

- No repository creation: repos without records are handled by the future
  creation automation (separate proposal).
- No release automation changes: the existing auto-tag workflow is
  untouched beyond being the trigger.

## Alternatives considered

- **Org API repo list instead of meta**: rejected — meta is the declared
  single source of truth, and an API listing would also match future
  non-plugin repositories and require name-prefix filtering anyway.
- **Per-repository dispatcher workflows**: more moving parts and one more
  file per plugin; a single workflow in template keeps the logic in one
  place.
- **Full re-render instead of `copier update`**: would discard
  hand-tuned build recipes in plugin repositories; the three-way merge is
  the whole point.

## Rollout

1. Merge this proposal and the `propagate.yaml` implementation PR.
2. Merge a template change; verify the first automatic propagation run
   opens PRs on all plugin repositories (the pending v0.0.6 update is a
   ready-made first test).
