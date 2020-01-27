#!/usr/bin/env bash

echo "***********************"
echo "Setup airflow directory environment variable"
echo "***********************"
# this must be set in order to add dags over time to a running server
export AIRFLOW_HOME="$(pwd)"

echo "***********************"
echo "Setup airflow configs and list dags"
echo "***********************"
airflow initdb

airflow list_dags

echo "***********************"
echo "Add custom GCP connection using service account key"
echo "***********************"
airflow run add_gcp_connection add_gcp_connection_python 2001-01-01
