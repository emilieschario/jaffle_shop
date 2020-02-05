import json

from airflow import DAG, settings
from airflow.models import Connection
from airflow.operators.python_operator import PythonOperator
from datetime import datetime

# from common.utils import get_default_google_cloud_connection_id

# airflow run add_gcp_connection add_gcp_connection_python 2001-01-01

default_args = {
    "owner": "airflow",
    "email": ["airflow@example.com"],
    "depends_on_past": False,
    "start_date": datetime(2001, 1, 1),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 5,
    "priority_weight": 1000,
}


def add_gcp_connection(ds, **kwargs):
    """"Add a airflow connection for GCP"""
    new_conn = Connection(
        conn_id="my_gcp_connection",  # TODO: parameterize
        conn_type="google_cloud_platform",
    )
    scopes = [
        "https://www.googleapis.com/auth/cloud-platform",
    ]
    conn_extra = {
        "extra__google_cloud_platform__scope": ",".join(scopes),
        "extra__google_cloud_platform__project": "wam-bam-258119",  # TODO: parameterize
        "extra__google_cloud_platform__key_path": "service_account.json",  # TODO: parameterize
    }
    conn_extra_json = json.dumps(conn_extra)
    new_conn.set_extra(conn_extra_json)

    session = settings.Session()
    if not (
        session.query(Connection).filter(Connection.conn_id == new_conn.conn_id).first()
    ):
        session.add(new_conn)
        session.commit()
    else:
        msg = "\n\tA connection with `conn_id`={conn_id} already exists\n"
        msg = msg.format(conn_id=new_conn.conn_id)
        print(msg)


# https://github.com/apache/airflow/blob/master/airflow/models/connection.py
def add_docker_connection(ds, **kwargs):
    """"Add a airflow connection for google container registry"""
    new_conn = Connection(
        conn_id="gcr_docker_connection",  # TODO: parameterize
        conn_type="docker",
        host="gcr.io/wam-bam-258119",  # TODO: parameterize
        login="_json_key",  # TODO: parameterize
    )

    # save contents of service account key into encrypted password field
    with open("service_account.json", "r") as file:
        data = file.read().replace("\n", "")  # replace new lines
        new_conn.set_password(data)

    session = settings.Session()
    if not (
        session.query(Connection).filter(Connection.conn_id == new_conn.conn_id).first()
    ):
        session.add(new_conn)
        session.commit()
    else:
        msg = "\n\tA connection with `conn_id`={conn_id} already exists\n"
        msg = msg.format(conn_id=new_conn.conn_id)
        print(msg)


with DAG(
    "add_gcp_connection", default_args=default_args, schedule_interval="@once"
) as dag:

    # Task to add a google cloud connection
    t1 = PythonOperator(
        task_id="add_gcp_connection_python",
        python_callable=add_gcp_connection,
        provide_context=True,
    )

    # Task to add a google container registry connection
    t2 = PythonOperator(
        task_id="add_docker_connection_python",
        python_callable=add_docker_connection,
        provide_context=True,
    )
