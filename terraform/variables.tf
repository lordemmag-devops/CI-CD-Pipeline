variable "gcp_project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "gcp_region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

variable "gcp_zone" {
  description = "GCP zone for free tier resources"
  type        = string
  default     = "us-central1-a"
}

variable "docker_image" {
  description = "Docker image URI"
  type        = string
  default     = "gcr.io/google-containers/pause:3.2"
}