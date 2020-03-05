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
# example environment variables below
PROJECT_ID="wam-bam-258119"
SERVICE_ACCOUNT_NAME="bigquery_logs_writer"

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

# run the python script
# add flags that point to the project
# setup the bigquery dataset and create the logging table
# then create the sink into that table with a specific filter
# print that the sink is created in project, dataset, table
```
