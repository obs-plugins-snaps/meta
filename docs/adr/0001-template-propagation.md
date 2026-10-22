# ADR-0001: Automatic template propagation to plugin repositories

Date: 2026-10-22
Status: Accepted

## Context

Plugin repositories are generated from the
[template](https://github.com/obs-plugins-snaps/template) via Copier and
record the template version they were generated from in
`.copier-answers.yml`. The template auto-tags every merge to main with the
next patch version, so improvements to the shared scaffolding (bug report
templates, CI workflows, README wording) are available as a new tag
immediately.

Without automation, propagating a template update means manually opening
one PR per plugin repository — repetitive, error-prone, and easily
forgotten, which lets the scaffolding drift apart across repositories.

## Decision

1. **meta `plugins/` is the source of truth for the plugin list.** The
   propagation workflow reads the directory listing via the GitHub API at
   runtime; every `plugins/<plugin_name>-obs-studio.json` record maps to
   the repository `<plugin_name>-obs-studio-snap` — the same derivation
   rule used by `scripts/generate.py` and documented in
   `plugins/schema.json`. An org API repository listing was rejected: it
   would include non-plugin repositories and duplicates knowledge that
   already lives here.

2. **The propagation workflow lives in the template repository**
   (`propagate.yaml` + a stdlib-only Python driver). It is triggered by
   `workflow_run` after the auto-tag workflow completes on main, and can
   be run manually via `workflow_dispatch` with an explicit tag. A single
   workflow keeps the logic in one place; per-repository dispatcher
   workflows were rejected as unnecessary moving parts.

3. **Updates use `copier update` (three-way merge), not re-rendering.**
   Plugin repositories carry hand-tuned build recipes that must survive
   template updates; conflicts are expected and surface in the PRs for
   human resolution.

4. **Idempotency and observability.** A run skips repositories already on
   the target tag (read from `.copier-answers.yml`), skips ones with an
   existing `template-update-<tag>` branch or open PR, and writes a
   per-plugin summary table to the workflow run. Repositories that do not
   exist yet (record present, repo not created — the creation-automation
   gap) are skipped and reported, not fatal.

5. **Permissions.** The `obs-plugins-snaps-bot` GitHub App carries
   `contents: write`, `pull_requests: write` and `workflows: write` on all
   organization repositories. The `workflows` scope is required because
   template updates modify `.github/workflows/*` files, which GitHub gates
   separately from ordinary content pushes.

## Non-goals

- Repository creation from records (separate future automation).
- Changes to the template's auto-tag workflow (it is only consumed as a
  trigger).

## Consequences

- Merging any change to the template now results in update PRs on every
  managed plugin repository within minutes; maintainers only review.
- Plugin repositories may hold open update PRs during active work;
  merging them is a maintainer decision per repository.
- The first live run propagates v0.0.6 (bug report issue template) to all
  four existing repositories.
