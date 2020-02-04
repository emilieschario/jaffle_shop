output "sql_conn_string" {
    value = "postgresql://${google_sql_user.airflow.name}:${random_password.db_pass.result}@${google_sql_database_instance.airflowdb-instance.private_ip_address}:5432/${google_sql_database.airflowdb.name}"
}

