set shell := ["bash", "-c"]

# Plan changes for a specific repo
plan repo:
    @tofu init
    @tofu plan -var="repo_name={{repo}}" -var-file="profiles/manifest.tfvars" -var-file="repos/{{repo}}.hcl"

# Apply changes to a specific repo
apply repo:
    @tofu init
    @tofu apply -auto-approve -var="repo_name={{repo}}" -var-file="profiles/manifest.tfvars" -var-file="repos/{{repo}}.hcl"

# Sync all repositories
sync-all:
    #!/usr/bin/env bash
    for file in repos/*.hcl; do
        repo=$(basename "$file" .hcl)
        just apply "$repo"
    done
