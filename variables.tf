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
