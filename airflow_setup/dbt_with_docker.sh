#!/usr/bin/env bash

usage() { echo "Usage: bash $0 [-p DBT_PROFILE_PATH] [-c DBT_COMMAND] must be run within the directory containing dbt_project.yml file | \
Example: bash $0 -p /Users/sung/Desktop/repos/dbt_bigquery_example/profiles.yml -c run" 1>&2; exit 1;}

while getopts ":p:c:" o; do
    case "${o}" in
        p)
            p=${OPTARG}
        ;;
        c)
            c=${OPTARG}
        ;;
        *)
            usage
        ;;
    esac
done
shift $((OPTIND-1))

if [ -z "${p}" ] || [ -z "${c}" ]; then
    usage
fi

# set command line arguments
DBT_PROFILE_PATH=${p}
DBT_COMMAND=${c}
echo "DBT_PROFILE_PATH = $DBT_PROFILE_PATH"
echo "DBT_COMMAND = dbt $DBT_COMMAND"

# run
docker run --rm -it \
-v $PWD:/dbt \
-v $DBT_PROFILE_PATH:/root/.dbt/profiles.yml \
dbt_docker:latest dbt deps

docker run --rm -it \
-v $PWD:/dbt \
-v $DBT_PROFILE_PATH:/root/.dbt/profiles.yml \
dbt_docker:latest dbt debug

docker run --rm -it \
-v $PWD:/dbt \
-v $DBT_PROFILE_PATH:/root/.dbt/profiles.yml \
dbt_docker:latest dbt $DBT_COMMAND

# /home/realsww123/dbt_bigquery_example/profiles.yml