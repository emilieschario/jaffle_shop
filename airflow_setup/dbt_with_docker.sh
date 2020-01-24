
usage() { echo "Usage: bash $0 [-p DBT_PROFILE_PATH]| \
Example: bash $0 -p /Users/sung/Desktop/repos/dbt_bigquery_example/profiles.yml " 1>&2; exit 1;}

while getopts ":e:u:p:s:g:b:" o; do
    case "${o}" in
        p)
            p=${OPTARG}
        ;;
        *)
            usage
        ;;
    esac
done
shift $((OPTIND-1))

if [ -z "${p}" ]; then
    usage
fi

# set command line arguments
DBT_PROFILE_PATH=${p}
echo "DBT_PROFILE_PATH = $DBT_PROFILE_PATH"

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
dbt_docker:latest dbt run

# /home/realsww123/dbt_bigquery_example/profiles.yml