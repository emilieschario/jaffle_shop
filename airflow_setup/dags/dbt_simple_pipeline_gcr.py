from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta
from airflow.operators.docker_operator import DockerOperator

default_args = {
    "owner": "airflow",
    "description": "Use of the DockerOperator",
    "depend_on_past": False,
    "start_date": datetime(2018, 1, 3),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    "dbt_pipeline_gcr",
    default_args=default_args,
    schedule_interval="@once",
    catchup=False,
) as dag:

    t1 = DockerOperator(
        task_id="dbt_debug",
        docker_conn_id="gcr_docker_connection",
        image="gcr.io/wam-bam-258119/dbt_docker:latest",
        api_version="auto",
        auto_remove=False,
        command="dbt debug",
        docker_url="unix://var/run/docker.sock",
        network_mode="bridge",
        volumes=[
            "/home/schung/dbt_bigquery_example/:/dbt",
            "/home/schung/dbt_bigquery_example/profiles.yml:/root/.dbt/profiles.yml",
        ],
    )
    t2 = DockerOperator(
        task_id="dbt_seed",
        docker_conn_id="gcr_docker_connection",
        image="gcr.io/wam-bam-258119/dbt_docker:latest",
        api_version="auto",
        auto_remove=False,
        command="dbt seed --show",
        docker_url="unix://var/run/docker.sock",
        network_mode="bridge",
        volumes=[
            "/home/schung/dbt_bigquery_example/:/dbt",
            "/home/schung/dbt_bigquery_example/profiles.yml:/root/.dbt/profiles.yml",
        ],
    )

    t3 = DockerOperator(
        task_id="dbt_source_freshness",
        docker_conn_id="gcr_docker_connection",
        image="gcr.io/wam-bam-258119/dbt_docker:latest",
        api_version="auto",
        auto_remove=False,
        command="dbt source snapshot-freshness",
        docker_url="unix://var/run/docker.sock",
        network_mode="bridge",
        volumes=[
            "/home/schung/dbt_bigquery_example/:/dbt",
            "/home/schung/dbt_bigquery_example/profiles.yml:/root/.dbt/profiles.yml",
        ],
    )

    t4 = DockerOperator(
        task_id="dbt_run",
        docker_conn_id="gcr_docker_connection",
        image="gcr.io/wam-bam-258119/dbt_docker:latest",
        api_version="auto",
        auto_remove=False,
        command="dbt run",
        docker_url="unix://var/run/docker.sock",
        network_mode="bridge",
        volumes=[
            "/home/schung/dbt_bigquery_example/:/dbt",
            "/home/schung/dbt_bigquery_example/profiles.yml:/root/.dbt/profiles.yml",
        ],
    )

    t5 = DockerOperator(
        task_id="dbt_test",
        docker_conn_id="gcr_docker_connection",
        image="gcr.io/wam-bam-258119/dbt_docker:latest",
        api_version="auto",
        auto_remove=False,
        command="dbt test",
        docker_url="unix://var/run/docker.sock",
        network_mode="bridge",
        volumes=[
            "/home/schung/dbt_bigquery_example/:/dbt",
            "/home/schung/dbt_bigquery_example/profiles.yml:/root/.dbt/profiles.yml",
        ],
    )

    t6 = BashOperator(
        task_id="success_message", bash_command='echo "SUCCESSFUL PIPELINE"'
    )

    t1 >> t2 >> t3 >> t4 >> t5 >> t6

