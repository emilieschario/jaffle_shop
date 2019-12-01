#!/usr/bin/env bash

# all this is intended to run within cloud shell bash

usage() { echo "Usage: bash $0 [-p PROJECT_ID] [-s SERVICE_ACCOUNT_NAME] | \
Example: bash $0 -p ferrous-weaver-256122 -s demo-service-account" 1>&2; exit 1;}

while getopts ":e:u:p:s:g:b:" o; do
    case "${o}" in
        p)
            p=${OPTARG}
        ;;
        s)
            s=${OPTARG}
        ;;
        *)
            usage
        ;;
    esac
done
shift $((OPTIND-1))

if [ -z "${e}" ] || [ -z "${u}" ] || [ -z "${p}" ] || [ -z "${s}" ] || [ -z "${g}" ] || [ -z "${b}" ]; then
    usage
fi

# set command line arguments
PROJECT_ID=${p}
SERVICE_ACCOUNT_NAME=${s}

echo "PROJECT_ID = $PROJECT_ID"
echo "SERVICE_ACCOUNT_NAME = $SERVICE_ACCOUNT_NAME"

echo "***********************"
echo "Create versioned bucket for encrypted service account json private key"
echo "***********************"
gsutil mb gs://$PROJECT_ID-secure-bucket-secrets

gsutil versioning set on gs://$PROJECT_ID-secure-bucket-secrets

echo "***********************"
echo "Create a service account"
echo "***********************"
gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
--description "service account used to launch dbt locally" \
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
echo "Add editor encryptor, and security admin role, so it has permissions to launch many kinds of terraform resources"
echo "***********************"
gcloud projects add-iam-policy-binding $PROJECT_ID \
--member serviceAccount:$SERVICE_ACCOUNT_EMAIL \
--role roles/editor

gcloud projects add-iam-policy-binding $PROJECT_ID \
--member serviceAccount:$SERVICE_ACCOUNT_EMAIL \
--role roles/cloudkms.cryptoKeyEncrypter

gcloud projects add-iam-policy-binding $PROJECT_ID \
--member serviceAccount:$SERVICE_ACCOUNT_EMAIL \
--role roles/iam.securityAdmin

gcloud projects add-iam-policy-binding $PROJECT_ID \
--member serviceAccount:$SERVICE_ACCOUNT_EMAIL \
--role roles/cloudkms.admin

echo "***********************"
echo "Check if roles updated"
echo "Note: may not be accurate even though console shows the update"
echo "***********************"
gcloud iam service-accounts get-iam-policy $SERVICE_ACCOUNT_EMAIL

echo "***********************"
echo "Download the service account key into the local directory"
echo "***********************"
gcloud iam service-accounts keys create ~/iot-python-webapp/service_account.json \
--iam-account $SERVICE_ACCOUNT_EMAIL

echo "***********************"
echo "Enable apis for first_build to work properly for a NEW project"
echo "***********************"
gcloud services enable \
cloudbuild.googleapis.com \
bigquery.googleapis.com \
cloudkms.googleapis.com


echo "***********************"
echo "Create kms keyring and key for service account json file and then encrypt it into ciphertext"
echo "***********************"
keyring_name=$PROJECT_ID-keyring
key_name=$PROJECT_ID-key

gcloud kms keyrings create $keyring_name \
--location=global

gcloud kms keys create $key_name \
--purpose=encryption \
--location=global \
--keyring=$keyring_name \
--protection-level=software

gcloud kms encrypt \
--key=$key_name \
--keyring=$keyring_name \
--location=global \
--plaintext-file=service_account.json \
--ciphertext-file=ciphertext_file.enc

echo "***********************"
echo "Copy encrypted file to cloud storage bucket"
echo "***********************"
gsutil cp ciphertext_file.enc gs://$PROJECT_ID-secure-bucket-secrets

echo "***********************"
echo "secrets file location..."
echo " "
gsutil ls -r gs://$PROJECT_ID-secure-bucket-secrets/
echo "***********************"
