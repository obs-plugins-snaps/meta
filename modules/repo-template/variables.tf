variable "snap_name" {
  description = "Snapcraft package name; the repository name is derived as '<snap_name>-snap'."
  type        = string
}

variable "summary" {
  description = "One-line summary, used as the GitHub repository description."
  type        = string
  default     = ""
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

variable "snapcraft_store_edge_secret" {
  description = "Value of the SNAPCRAFT_STORE_EDGE Actions secret set on every repository."
  type        = string
  sensitive   = true
  default     = ""
}
