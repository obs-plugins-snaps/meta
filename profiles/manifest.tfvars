# Org-wide policy manifest
# This file is the single source of truth for policies every repository
# in the organization SHALL carry. One PR changing this file propagates
# the change to all repositories on the next reconciliation run.
#
# Adding an item here adds it to every repo (visible in PR plan diff).
# Removing an item here removes it from every repo (unless the repo
# declares its own override in repos/<name>.hcl).
#
# Per-repo overrides are declared in repos/<name>.hcl.
# The effective set is: distinct(concat(org_topics, repo_topics))

org_topics = [
  "obs",
  "obs-studio",
  "linux",
  "snap",
]
