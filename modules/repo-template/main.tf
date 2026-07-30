resource "github_repository" "this" {
  name        = var.repo_name
  description = var.description
  visibility  = "public"

  has_issues              = true
  has_discussions         = false
  delete_branch_on_merge  = true

  lifecycle {
    prevent_destroy = true
  }
}

resource "github_repository_topics" "this" {
  repository = var.repo_name
  topics     = distinct(concat(var.org_topics, var.repo_topics))
}
