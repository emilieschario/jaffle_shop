# export_logs

## What does this do?

- exports logs related to any bigquery operations in scope for auditing
- streams filtered bigquery dataset logs into bigquery dataset of choice
- assumes you're working within google cloud shell and have permissions to create service accounts and grant other service account's permissions
- unit tests for basic functionality

## What does this NOT do?

- any specific transformations
- unit tests for flag arguments

## How to run this?

[documentation](https://cloud.google.com/logging/docs/api/tasks/exporting-logs)

```bash
# clone repo
git clone https://github.com/sungchun12/dbt_bigquery_example.git
cd dbt_bigquery_example/cd export_logs

# create a virtual environment if not done already
python3 -m venv py37_venv
source py37_venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# setup a service account with "Logging/Logs Configuration Writer" permissions
# example environment variables below
PROJECT_ID="wam-bam-258119"
SERVICE_ACCOUNT_NAME="bigquery-logs-writer"

echo "***********************"
echo "Create a service account"
echo "***********************"
gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
--description "service account used to deploy export log functionality" \
--display-name $SERVICE_ACCOUNT_NAME

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
# print that the sink is created in project and dataset

#explains each variable
python3 bigquery_logging_utility.py --help

python3 bigquery_logging_utility.py \
    -s bigquery_audit_logs \
    -p wam-bam-258119 \
    -d bigquery_logs_dataset \
    -l US \
    -o create \
    -f protoPayload.metadata."@type"="type.googleapis.com/google.cloud.audit.BigQueryAuditMetadata"

python3 bigquery_logging_utility.py \
    -s bigquery_audit_logs \
    -p wam-bam-258119 \
    -d bigquery_logs_dataset \
    -l US \
    -o list \
    -f protoPayload.metadata."@type"="type.googleapis.com/google.cloud.audit.BigQueryAuditMetadata"

python3 bigquery_logging_utility.py \
    -s bigquery_audit_logs \
    -p wam-bam-258119 \
    -d bigquery_logs_dataset \
    -l US \
    -o update \
    -f protoPayload.metadata."@type"="type.googleapis.com/google.cloud.audit.BigQueryAuditMetadata"

python3 bigquery_logging_utility.py \
    -s bigquery_audit_logs \
    -p wam-bam-258119 \
    -d bigquery_logs_dataset \
    -l US \
    -o delete \
    -f protoPayload.metadata."@type"="type.googleapis.com/google.cloud.audit.BigQueryAuditMetadata"

# add roles to the generated log writer service account created automatically
# ex: p903473854152-104564@gcp-sa-logging.iam.gserviceaccount.com
LOG_EXPORT_SERVICE_ACCOUNT_EMAIL=$(gcloud beta logging sinks describe bigquery_audit_logs | grep "serviceAccount:" | head -n 1 | awk '{print $2}' | cut -d':' -f2)

gcloud projects add-iam-policy-binding $PROJECT_ID \
--member serviceAccount:$LOG_EXPORT_SERVICE_ACCOUNT_EMAIL \
--role roles/bigquery.dataEditor

gcloud projects add-iam-policy-binding $PROJECT_ID \
--member serviceAccount:$LOG_EXPORT_SERVICE_ACCOUNT_EMAIL \
--role roles/logging.logWriter

#automated tests to see if basic operations work
# tests do NOT cover flag parsers
pytest tests/test_bigquery_logging_utility.py

```

> Note: After you perform some query actions in your respective BigQuery project, you can run the below example queries

```sql
  -- standardSQL
  -- What are the most popular datasets only?
  SELECT
    REGEXP_EXTRACT(protopayload_auditlog.resourceName, '^projects/[^/]+/datasets/([^/]+)/tables') AS datasetRef,
    COUNT(DISTINCT REGEXP_EXTRACT(protopayload_auditlog.resourceName, '^projects/[^/]+/datasets/[^/]+/tables/(.*)$')) AS active_tables,
    COUNTIF(JSON_EXTRACT(protopayload_auditlog.metadataJson, "$.tableDataRead") IS NOT NULL) AS dataReadEvents,
    COUNTIF(JSON_EXTRACT(protopayload_auditlog.metadataJson, "$.tableDataChange") IS NOT NULL) AS dataChangeEvents
  FROM `MYPROJECTID.MYDATASETID.cloudaudit_googleapis_com_data_access_2019*` --replace with the relevant flags you used for the utility
  WHERE
    JSON_EXTRACT(protopayload_auditlog.metadataJson, "$.tableDataRead") IS NOT NULL
    OR JSON_EXTRACT(protopayload_auditlog.metadataJson, "$.tableDataChange") IS NOT NULL
  GROUP BY datasetRef
  ORDER BY datasetRef

  -- What are the most popular datasets and tables?
  SELECT
    REGEXP_EXTRACT(protopayload_auditlog.resourceName, '^projects/[^/]+/datasets/([^/]+)/tables') AS datasetRef,
    REGEXP_EXTRACT(protopayload_auditlog.resourceName, '^projects/[^/]+/datasets/[^/]+/tables/(.*)$') AS active_table_names,
    COUNT(DISTINCT REGEXP_EXTRACT(protopayload_auditlog.resourceName, '^projects/[^/]+/datasets/[^/]+/tables/(.*)$')) AS active_tables,
    COUNTIF(JSON_EXTRACT(protopayload_auditlog.metadataJson, "$.tableDataRead") IS NOT NULL) AS dataReadEvents,
    COUNTIF(JSON_EXTRACT(protopayload_auditlog.metadataJson, "$.tableDataChange") IS NOT NULL) AS dataChangeEvents
  FROM `MYPROJECTID.MYDATASETID.cloudaudit_googleapis_com_data_access_2020*` --replace with the relevant flags you used for the utility
  WHERE
    JSON_EXTRACT(protopayload_auditlog.metadataJson, "$.tableDataRead") IS NOT NULL
    OR JSON_EXTRACT(protopayload_auditlog.metadataJson, "$.tableDataChange") IS NOT NULL
  GROUP BY datasetRef, active_table_names
  ORDER BY datasetRef, dataReadEvents desc
```
