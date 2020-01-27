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

# change to  your airflow working directory
cd dbt_bigquery_example/airflow_setup/

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

# update volumes path with YOUR specific mounted volume paths within dbt_operations.py


```

```python3

# within dbt_operations.py file, update the below volumes paths
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
```

```bash
# airflow webserver and airflow scheduler has to be launched from separate terminals if running locally in cloud shell

airflow webserver -p 8080

# open another terminal

airflow scheduler

```

## Notes

- docker operator works without including the volumes parameter
- when I give absolute paths to the dbt directory within cloud shell, everything works
- mounts denied on mac because of folder permissions
- will have to think through how a production airflow deployment will retrieve the service account
- [for ease of development, we can simply build the dbt docker image locally until google container registry details are figured out](https://stackoverflow.com/questions/58733579/airflow-pull-docker-image-from-private-google-container-repository)
