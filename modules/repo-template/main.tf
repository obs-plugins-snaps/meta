locals {
  repo_name = "${var.snap_name}-snap"
}

resource "github_repository" "this" {
  name         = local.repo_name
  description  = var.summary
  homepage_url = "https://snapcraft.io/${var.snap_name}"
  visibility   = "public"

  has_issues              = true
  has_discussions         = false
  delete_branch_on_merge  = true

  lifecycle {
    prevent_destroy = true
  }
}

resource "github_branch_protection" "this" {
  repository_id = github_repository.this.node_id
  pattern       = var.default_branch

  # Commits pushed to matching refs must have verified signatures.
  require_signed_commits = true

  # Signatures are required for everyone, including administrators.
  enforce_admins = true
}

resource "github_repository_topics" "this" {
  repository = local.repo_name
  topics     = distinct(concat(var.org_topics, var.repo_topics))
}

resource "github_actions_secret" "snapcraft_store_edge" {
  repository      = github_repository.this.name
  secret_name     = "SNAPCRAFT_STORE_EDGE"
  plaintext_value = var.snapcraft_store_edge_secret
}
