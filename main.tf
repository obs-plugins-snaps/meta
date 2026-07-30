import {
  id = var.repo_name
  to = module.repo.github_repository.this
}

import {
  id = var.repo_name
  to = module.repo.github_repository_topics.this
}

module "repo" {
  source = "./modules/repo-template"

  repo_name   = var.repo_name
  description = var.description
  org_topics  = var.org_topics
  repo_topics = var.repo_topics
}
