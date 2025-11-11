terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region
}

# Enable required APIs
resource "google_project_service" "container" {
  service = "container.googleapis.com"
}

resource "google_project_service" "artifactregistry" {
  service = "artifactregistry.googleapis.com"
}

# VPC Network
resource "google_compute_network" "main" {
  name                    = "cicd-network"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "main" {
  name          = "cicd-subnet"
  ip_cidr_range = "10.0.0.0/16"
  region        = var.gcp_region
  network       = google_compute_network.main.id

  secondary_ip_range {
    range_name    = "pods"
    ip_cidr_range = "10.1.0.0/16"
  }

  secondary_ip_range {
    range_name    = "services"
    ip_cidr_range = "10.2.0.0/16"
  }
}

# Artifact Registry
resource "google_artifact_registry_repository" "app" {
  location      = var.gcp_region
  repository_id = "cicd-app"
  description   = "CI/CD application container registry"
  format        = "DOCKER"
}

# GKE Autopilot Cluster (Free tier eligible)
resource "google_container_cluster" "main" {
  name     = "cicd-cluster"
  location = "us-central1"  # Regional cluster

  network    = google_compute_network.main.name
  subnetwork = google_compute_subnetwork.main.name

  # Enable Autopilot for free tier
  enable_autopilot = true

  # Minimal configuration for free tier
  initial_node_count = 1

  depends_on = [
    google_project_service.container,
    google_project_service.artifactregistry
  ]

  
}

# Service Account for CI/CD (Autopilot manages node service accounts)
resource "google_service_account" "cicd" {
  account_id   = "cicd-pipeline"
  display_name = "CI/CD Pipeline Service Account"
}

resource "google_project_iam_member" "cicd" {
  for_each = toset([
    "roles/artifactregistry.writer",
    "roles/container.developer"
  ])

  project = var.gcp_project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.cicd.email}"
}

# Service Account Key for CI/CD
resource "google_service_account_key" "cicd" {
  service_account_id = google_service_account.cicd.name
}