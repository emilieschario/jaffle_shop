# airflow_setup

## What does this do?

- basic airflow setup on your LOCAL machine

## What does this NOT do?

## How to run this?

```bash
# change to  your airflow working directory
cd <airflow_setup directory>

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

```
