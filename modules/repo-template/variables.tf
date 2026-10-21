variable "repo_name" {
  type = string
}

variable "default_branch" {
  description = "Branch to which signed-commit protection is applied."
  type        = string
  default     = "main"
}

variable "description" {
  type    = string
  default = ""
}

variable "org_topics" {
  type    = list(string)
  default = []
}

variable "repo_topics" {
  type    = list(string)
  default = []
}
