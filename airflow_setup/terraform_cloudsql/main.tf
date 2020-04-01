provider "google" {
    credentials = var.key_file
    project     = var.project
    region      = var.region
    zone        = var.zone
    version     = "~> 3.0.0"
}

data "google_compute_network" "airflow" {
    name = var.network_name
}

data "google_compute_subnetwork" "airflow" {
    name   = var.subnet_name
    region = var.region
}