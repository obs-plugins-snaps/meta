variable "repo_name" {
  type = string
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
