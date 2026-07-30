set shell := ["bash", "-c"]

# Plan changes for a specific repo
plan repo:
    @tofu init
    @tofu plan -var="repo_name={{ repo }}" -var-file="profiles/manifest.tfvars" -var-file="repos/{{ repo }}.tfvars"

# Apply changes to a specific repo
apply repo:
    @tofu init
    @tofu apply -auto-approve -var="repo_name={{ repo }}" -var-file="profiles/manifest.tfvars" -var-file="repos/{{ repo }}.tfvars"

# Plan all repos (each in isolation)
plan-all:
    #!/usr/bin/env bash
    for file in repos/*.tfvars; do
        repo=$(basename "$file" .tfvars)
        tofu init 2>&1
        tofu plan -no-color -var="repo_name=$repo" -var-file="profiles/manifest.tfvars" -var-file="repos/$repo.tfvars" 2>&1 || true
        rm -rf .terraform terraform.tfstate terraform.tfstate.backup
    done

# Sync all repositories (each in isolation)
sync-all:
    #!/usr/bin/env bash
    for file in repos/*.tfvars; do
        repo=$(basename "$file" .tfvars)
        tofu init 2>&1
        tofu apply -auto-approve -no-color -var="repo_name=$repo" -var-file="profiles/manifest.tfvars" -var-file="repos/$repo.tfvars" 2>&1
        rm -rf .terraform terraform.tfstate terraform.tfstate.backup
    done
