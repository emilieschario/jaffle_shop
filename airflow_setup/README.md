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

- tests if dbt connnection configurations are working: `dbt debug`
- load local seed files into bigquery tables: `dbt seed --show`
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

## How to MANUALLY run a basic end to end pipeline with google container registry hosting the docker image?

- Note: this is the same example as above but connecting to and running on a gcr container vs. running it on a locally built docker container

- update the image information in [add_gcp_connection.py](/airflow_setup/dags/add_gcp_connection.py)

```python
# example: host="gcr.io/wam-bam-258119"
 host=<your project id>

```

- update the image information in [dbt_simple_pipeline_gcr.py](/airflow_setup/dags/dbt_simple_pipeline_gcr.py)

```python
# replace every image variable with the below
# example: image="gcr.io/wam-bam-258119/dbt_docker:latest",
image="gcr.io/<your project id>/dbt_docker:latest"

```

```bash
# configure gcloud for docker operations
gcloud auth configure-docker

# tag your docker image for gcr
docker images
# copy the image id of dbt_docker
docker tag <your docker image id> gcr.io/<your project id>/dbt_docker

# push docker image to your private container registry
#example: docker push gcr.io/wam-bam-258119/dbt_docker
docker push gcr.io/<your project id>/dbt_docker

# add the docker connection to airflow
airflow run add_gcp_connection add_docker_connection_python 2001-01-01

# test a simple task to see if it works
airflow test dbt_pipeline_gcr dbt_debug 2020-01-01

# run the pipeline manually
airflow backfill dbt_pipeline_gcr -s 2020-01-01 -e 2020-01-02

# run the below to view the pipeline in the airflow UI
# note: cloudshell as it is doesn't like manually triggering from the UI(likely network configs)
airflow webserver -p 8080

```

## How to setup an ad hoc airflow vm and cloud sql postgresql database backend for development?
- This is a scrappy process to get something that mimics in basic functionality the look and feel of a manual cloud setup for airflow
- I recommend using terraform for robustness
- This is meant to play around with the infrastructure quickly, so focus can be spent on pipeline development

What does this do?
- sets up a cloud sql database only accessible from private IP(no public internet traffic)
- sets up a compute engine VM to install airflow on
- connects the compute engine VM to the cloud sql database

What does this NOT do?
- template code for a production scale implementation


```bash
#!/bin/bash

# https://cloud.google.com/vpc/docs/configure-private-services-access#allocating-range
# https://github.com/mikeghen/airflow-tutorial/blob/master/README.md

# update the environment variables below
HOST_PROJECT="wam-bam-258119"
ADDRESS_NAME="airflow-network" # do not choose "default"
NETWORK_NAME="default"
COMPUTE_INSTANCE_NAME="airflow-vm"

SQL_INSTANCE_NAME="airflow-test" # if you run the below commands multiple times, this must change each time
SQL_INSTANCE_TIER="db-g1-small" # "db-n1-standard-4" is not a shared core tier type, MUST use shared core type
SQL_INSTANCE_ZONE="us-east4-a"
SQL_DATABASE_NAME="airflow-db-demo"
SQL_USER_NAME="airflow"
SQL_USER_PASS="airflow"

# Enable the Services Networking API in host project
gcloud services enable servicenetworking.googleapis.com \
    --project=$HOST_PROJECT

# Create an address allocation for CloudSQL private IP access
gcloud compute addresses create $ADDRESS_NAME \
    --global \
    --purpose=VPC_PEERING \
    --prefix-length=24 \
    --network=$NETWORK_NAME \
    --project=$HOST_PROJECT

# check if the address was created
gcloud compute addresses list --global --filter="purpose=VPC_PEERING"

# example output
# NAME             ADDRESS/RANGE   TYPE      PURPOSE      NETWORK  REGION  SUBNET  STATUS
# airflow-network  10.26.211.0/24  INTERNAL  VPC_PEERING  default                  RESERVED

# Create services connection or update if you messed up the first time
# gcloud services vpc-peerings update \
#     --service=servicenetworking.googleapis.com \
#     --network=$NETWORK_NAME \
#     --project=$HOST_PROJECT \
#     --ranges=$ADDRESS_NAME \
#     --force
gcloud services vpc-peerings connect \
    --service=servicenetworking.googleapis.com \
    --network=$NETWORK_NAME \
    --project=$HOST_PROJECT \
    --ranges=$ADDRESS_NAME

# Build a new CloudSQL instance in the host VPC
gcloud beta sql instances create $SQL_INSTANCE_NAME \
    --project=$HOST_PROJECT \
    --network="projects/${HOST_PROJECT}/global/networks/${NETWORK_NAME}" \
    --no-assign-ip \
    --tier=$SQL_INSTANCE_TIER \
    --database-version="POSTGRES_11" \
    --zone=$SQL_INSTANCE_ZONE \
    --storage-size=10

# example output-is not a real private IP-DUH!
# NAME                   DATABASE_VERSION  LOCATION    TIER         PRIMARY_ADDRESS  PRIVATE_ADDRESS  STATUS
# airflow-demonstration  POSTGRES_11       us-east4-a  db-g1-small  -                10.20.30.3       RUNNABLE

# Create a new database and user
gcloud beta sql databases create $SQL_DATABASE_NAME \
    --instance=$SQL_INSTANCE_NAME

gcloud beta sql users create $SQL_USER_NAME \
    --instance=$SQL_INSTANCE_NAME \
    --password=$SQL_USER_PASS

# create a compute engine instance
# note: rhel(red hat enterprise linux) is common in enterprise setups
gcloud compute instances create $COMPUTE_INSTANCE_NAME \
    --image-family centos-8 \
    --image-project centos-cloud \
    --network=$NETWORK_NAME \
    --zone=$SQL_INSTANCE_ZONE

# ssh into the VM
gcloud compute ssh --project $HOST_PROJECT --zone $SQL_INSTANCE_ZONE $COMPUTE_INSTANCE_NAME

# set the environment variables above again into the VM

# test if you can connect through compute engine airflow vm
sudo yum install postgresql
# example: psql -h 10.18.16.5 -d $SQL_DATABASE_NAME -U $SQL_USER_NAME 
psql -h [CLOUD_SQL_PRIVATE_IP_ADDR] -d $SQL_DATABASE_NAME -U $SQL_USER_NAME 

# exit out with below
ctrl+z

# install git
sudo yum install git 

# clone the repo
git clone https://github.com/sungchun12/dbt_bigquery_example.git

# set environment variable for database connection
export AIRFLOW__CORE__SQL_ALCHEMY_CONN="postgresql://$SQL_USER_NAME:$SQL_USER_PASS@3$private_ip:5432/$SQL_DATABASE_NAME"

# https://developers.redhat.com/blog/2018/08/13/install-python3-rhel/
# https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/8/html-single/considerations_in_adopting_rhel_8/index
# specific to rhel
# for some reason, rhel does not like working with virtual environemnts compared to other linux distros
# sudo yum -y install gcc gcc-c++
# sudo dnf update annobin -y
# sudo yum -y install rh-python36
# sudo yum install -y python3-devel.x86_64
# sudo pip3 install -r requirements.txt
# sudo useradd airflow-user
# sudo passwd airflow-user
# <enter a password>
# sudo usermod -aG wheel airflow-user
# su airflow-user -
# <enter a password>
# scl enable rh-python36 bash
# sudo subscription-manager repos --enable rhel-7-server-optional-rpms \
#   --enable rhel-server-rhscl-7-rpms
# sudo yum install gcc
# sudo yum install gcc-c++
# sudo yum install libev-devel
# sudo yum -y install @development #ensures you have gcc

# sudo yum install platform-python-devel platform-python-pip platform-python-setuptools python3-pip-wheel

sudo yum install gcc
python3 -m venv py36-venv
source py36-venv/bin/activate
sudo python3 -m pip install -r requirements.txt



# setup airflow environment
sudo bash ./initial_setup.sh


# change executor to LocalExecutor in airflow.cfg file using bash
sed -i 's/executor = SequentialExecutor/executor = LocalExecutor/' /home/realsww123/dbt_bigquery_example/airflow_setup/airflow.cfg

# reinitialize the database
airflow initdb

# run an example DAG with parallel tasks to test if things are working correctly
airflow backfill dbt_pipeline_gcr -s 2020-01-01 -e 2020-01-02

# delete your infrastructure
gcloud beta sql instances delete $SQL_INSTANCE_NAME

gcloud compute instances delete $COMPUTE_INSTANCE_NAME



```

```bash

instance_name=airflow

db_type=postgresql

username=airflow

password=airflow

db_name=airflow_sung

# export AIRFLOW__CORE__SQL_ALCHEMY_CONN="postgresql://${google_sql_user.airflow.name}:${random_password.db_pass.result}@${google_sql_database_instance.airflowdb-instance.private_ip_address}:5432/${google_sql_database.airflowdb.name}"
```

## Notes

- docker operator works without including the volumes parameter
- when I give absolute paths to the dbt directory within cloud shell, everything works
- mounts denied on mac because of folder permissions
- will have to think through how a production airflow deployment will retrieve the service account
- [for ease of development, we can simply build the dbt docker image locally until google container registry details are figured out](https://stackoverflow.com/questions/58733579/airflow-pull-docker-image-from-private-google-container-repository)
- [cloud sql connection](https://airflow.apache.org/docs/stable/howto/connection/gcp_sql.html)
