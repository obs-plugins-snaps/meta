# OBS Plugins snaps - Meta

## Repo automation

This repo contains stateless GitOps repo reconciliation
using OpenTofu (`import`-on-demand) and `just`.

For now, it helps keeping existing repos in sync.

## Records and decisions

`plugins/` holds the per-plugin records (the single source of truth for
creation-time metadata), projected into `repos/*.tfvars` by
`scripts/generate.py` — see `plugins/schema.json`. Significant design
decisions are recorded as ADRs in [`docs/adr/`](docs/adr/).
