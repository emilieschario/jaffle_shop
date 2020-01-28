# airflow_setup

## What does this do?

- basic airflow setup with Google cloud shell for DEVELOPMENT purposes

## What does this NOT do?

- full production scale setup
- setup database other than default sqlite

## How to run this?

- download a service account and place in dbt root directory and within the `airflow_setup/` directory named: `service_account.json`(this will be gitignored)
- open up cloud shell using the console

```bash
# clone repo
git clone https://github.com/sungchun12/dbt_bigquery_example.git

# change to your airflow working directory
cd dbt_bigquery_example/airflow_setup/
```

```python3
# update volumes path with YOUR specific mounted volume paths within dbt_operations.py
t2 = DockerOperator(
    task_id="docker_command",
    image="dbt_docker:latest",
    api_version="auto",
    auto_remove=False,
    command="dbt debug",
    docker_url="unix://var/run/docker.sock",
    network_mode="bridge",
    volumes=[
        "/home/<your-gcp-username>/dbt_bigquery_example/:/dbt",
        "/home/<your-gcp-username>/dbt_bigquery_example/profiles.yml:/root/.dbt/profiles.yml",
    ],

# example
t2 = DockerOperator(
    task_id="docker_command",
    image="dbt_docker:latest",
    api_version="auto",
    auto_remove=False,
    command="dbt debug",
    docker_url="unix://var/run/docker.sock",
    network_mode="bridge",
    volumes=[
        "/home/realsww123/dbt_bigquery_example/:/dbt",
        "/home/realsww123/dbt_bigquery_example/profiles.yml:/root/.dbt/profiles.yml",
    ],
)

# update gcp project name in add_gcp_connection.py
 "extra__google_cloud_platform__project": <your-project-name>

# example
 "extra__google_cloud_platform__project": "wam-bam-258119"
```

```bash
# setup python virtual environment
sudo easy_install pip
sudo pip install virtualenv
virtualenv -p python3 py37_venv
source py37_venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# setup airflow environment
bash ./initial_setup.sh

#build docker image locally to run dbt commands
# you may need to rebuild this each time you start a new cloud shell terminal
docker build -t dbt_docker .

# change directory to root of dbt_bigquery_example
cd ..

# run below command to test dbt commands within docker
docker run --rm -it \
-v $PWD:/dbt \
-v <path to profiles.yml file>:/root/.dbt/profiles.yml \
dbt_docker:latest dbt <dbt command>

# example
# docker run --rm -it \
# -v $PWD:/dbt \
# -v /Users/sung/Desktop/repos/dbt_bigquery_example/profiles.yml:/root/.dbt/profiles.yml \
# dbt_docker:latest dbt test

# test the specific airflow dbt task-if no error messages then SUCCESS
airflow test dbt_dag docker_command 2020-01-01

# airflow webserver and airflow scheduler has to be launched from separate terminals if running locally in cloud shell
airflow webserver -p 8080

# run the scheduler to automate all dags
airflow scheduler
```

## How to MANUALLY run a basic end to end pipeline?

Pre-requisites:

- all the above steps
- replace the DockerOperator volume paths similar to the above dbt_operations.py step within [dbt_simple_pipeline.py](/airflow_setup/dags/dbt_simple_pipeline.py)

What does the pipeline exactly do?

- load local seed files into bigquery tables: `dbt seed --show`
- tests if dbt connnection configurations are working: `dbt debug`
- how fresh is the data?: `dbt source snapshot-freshness`
- perform transformations: `dbt run`
- test transformation outputs: `dbt test`
- prints a success message: `echo "SUCCESSFUL PIPELINE"`

```bash

# ensure your airflow home path is set
export AIRFLOW_HOME="$(pwd)"

# list out the dag steps in the simple pipeline
airflow list_tasks dbt_pipeline --tree

# example output
# <Task(DockerOperator): dbt_debug>
#     <Task(DockerOperator): dbt_seed>
#         <Task(DockerOperator): dbt_source_freshness>
#             <Task(DockerOperator): dbt_run>
#                 <Task(DockerOperator): dbt_test>
#                     <Task(BashOperator): success_message>

# run the pipeline manually
airflow backfill dbt_pipeline -s 2020-01-01 -e 2020-01-02

# run the below to view the pipeline in the airflow UI
# note: cloudshell as it is doesn't like manually triggering from the UI(likely network configs)
airflow webserver -p 8080

```

## Notes

- docker operator works without including the volumes parameter
- when I give absolute paths to the dbt directory within cloud shell, everything works
- mounts denied on mac because of folder permissions
- will have to think through how a production airflow deployment will retrieve the service account
- [for ease of development, we can simply build the dbt docker image locally until google container registry details are figured out](https://stackoverflow.com/questions/58733579/airflow-pull-docker-image-from-private-google-container-repository)
