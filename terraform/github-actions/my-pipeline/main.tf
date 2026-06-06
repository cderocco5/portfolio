resource "github_repository" "repo" {
  name        = var.repo_name
  description = "Repo managed by Terraform with GitHub Actions"
  visibility  = "private"
}

resource "github_repository_file" "github_action" {
  repository = github_repository.repo.name
  file       = ".github/workflows/terraform.yml"
  branch     = "main"

  content = <<EOF
name: Terraform CI

on:
  push:
    branches: [ "main" ]
  pull_request:

jobs:
  terraform:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3

      - name: Terraform Init
        run: terraform init

      - name: Terraform Validate
        run: terraform validate
EOF

  commit_message = "Add GitHub Actions workflow"
  overwrite_on_create = true
}