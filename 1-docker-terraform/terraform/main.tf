terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "7.19.0"
    }
  }
}

provider "google" {
  # Configuration options
  project = "dataengineeringtutorial"
  region  = "europe-west2"
}
resource "google_storage_bucket" "demo-bucket" {
  name          = "dataeng_7744102_bucket"
  location      = "EUROPE-WEST2"
  force_destroy = true

  lifecycle_rule {
    condition {
      age = 3
    }
    action {
      type = "Delete"
    }
  }
}
