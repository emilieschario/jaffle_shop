# export_logs

## What does this do?

- exports logs related to bigquery dataset in scope for auditing
- streams filtered bigquery dataset logs into bigquery dataset and table of choice

## What does this NOT do?

- any specific transformations

## How to run this?

[documentation](https://cloud.google.com/logging/docs/api/tasks/exporting-logs)

```bash
# setup a service account with "Logging/Logs Configuration Writer" permissions
cd export_logs
# example environment variables below
PROJECT_ID="wam-bam-258119"
SERVICE_ACCOUNT_NAME="bigquery-logs-writer"

echo "***********************"
echo "Create a service account"
echo "***********************"
gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
--description "service account used to launch terraform locally" \
--display-name $SERVICE_ACCOUNT_NAME

echo "***********************"
echo "Wait for the service account to be created"
echo "***********************"
sleep 10s

echo "***********************"
echo "List service account to verify creation and capture email"
echo "***********************"
SERVICE_ACCOUNT_EMAIL=$(gcloud iam service-accounts list --filter=$SERVICE_ACCOUNT_NAME | grep -v "^NAME"  | head -n 1 | awk '{print $2}')

echo "***********************"
echo "Enable newly created service account based on what's listed"
echo "***********************"
gcloud beta iam service-accounts enable $SERVICE_ACCOUNT_EMAIL

echo "***********************"
echo "Add Logging/Logs Configuration Writer"
echo "***********************"
gcloud projects add-iam-policy-binding $PROJECT_ID \
--member serviceAccount:$SERVICE_ACCOUNT_EMAIL \
--role roles/logging.configWriter

gcloud projects add-iam-policy-binding $PROJECT_ID \
--member serviceAccount:$SERVICE_ACCOUNT_EMAIL \
--role roles/bigquery.admin

echo "***********************"
echo "Download the private service account key locally into export_logs folder"
echo "***********************"
gcloud iam service-accounts keys create bigquery-logs-writer-key.json \
--iam-account=$SERVICE_ACCOUNT_EMAIL \
--key-file-type="json"


# run the python script
# add flags that point to the project
# setup the bigquery dataset and create the logging table
# then create the sink into that table with a specific filter
# print that the sink is created in project, dataset, table
# resource.type="audited_resource"
# timestamp>="2020-03-05T17:37:54.386Z"
# resource.type="bigquery_dataset" resource.labels.dataset_id="dbt_bq_example"

python3 bigquery_logging_utility.py -s dbt_logs -p wam-bam-258119 -d bigquery_logs_dataset -l US -o create

python3 bigquery_logging_utility.py -s dbt_logs -p wam-bam-258119 -d bigquery_logs_dataset -l US -o list

python3 bigquery_logging_utility.py -s dbt_logs -p wam-bam-258119 -d bigquery_logs_dataset -l US -o update

python3 bigquery_logging_utility.py -s dbt_logs -p wam-bam-258119 -d bigquery_logs_dataset -l US -o delete

# add roles to the generated log writer service account created by the python code
# ex: p903473854152-104564@gcp-sa-logging.iam.gserviceaccount.com
#TODO: get this email automatically based on the latest one created similar to the earlier bash command
export LOG_EXPORT_SERVICE_ACCOUNT_EMAIL="p903473854152-104564@gcp-sa-logging.iam.gserviceaccount.com"
gcloud projects add-iam-policy-binding $PROJECT_ID \
--member serviceAccount:$LOG_EXPORT_SERVICE_ACCOUNT_EMAIL \
--role roles/bigquery.dataEditor

gcloud projects add-iam-policy-binding $PROJECT_ID \
--member serviceAccount:$SERVICE_ACCOUNT_EMAIL \
--role roles/logging.logWriter
```
