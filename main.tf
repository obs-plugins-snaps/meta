import {
  id = "${var.snap_name}-snap"
  to = module.repo.github_repository.this
}

import {
  id = "${var.snap_name}-snap"
  to = module.repo.github_repository_topics.this
}

import {
  id = "${var.snap_name}-snap:main"
  to = module.repo.github_branch_protection.this
}

module "repo" {
  source = "./modules/repo-template"

  snap_name   = var.snap_name
  summary     = var.summary
  org_topics  = var.org_topics
  repo_topics = var.repo_topics

  snapcraft_store_edge_secret = var.snapcraft_store_edge_secret
}
