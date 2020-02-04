resource "google_sql_database_instance" "airflowdb-instance" {
    name             = "${var.env}-airflow-postgresql-${lower(random_string.db_suffix.result)}"
    database_version = "POSTGRES_11"
    region           = var.region
    
    settings {
        tier = var.db_size

        ip_configuration {
            ipv4_enabled = false
            private_network = data.google_compute_network.airflow.self_link
        }
    }
}

resource "google_sql_database" "airflowdb" {
    name     = "airflowdb"
    instance = google_sql_database_instance.airflowdb-instance.name
}

resource "google_sql_user" "airflow" {
    name     = "airflow"
    instance = google_sql_database_instance.airflowdb-instance.name
    password = random_password.db_pass.result

}

resource "random_string" "db_suffix" {
    length  = 6
    special = false
}

resource "random_password" "db_pass" {
    length           = 16
    special          = true
    override_special = "@$_*"
}