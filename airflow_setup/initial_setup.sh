echo "***********************"
echo "Setup python virtual environment within already created airflow sub-directory"
sudo easy_install pip
sudo pip install virtualenv
virtualenv -p python3 py37_venv
source py37_venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "***********************"

echo "***********************"
echo "Setup airflow directory environment variable"
echo "***********************"
# this must be set in order to add dags over time to a running server
export AIRFLOW_HOME="$(pwd)"

echo "***********************"
echo "Setup airflow configs and list dags"
echo "***********************"
airflow initdb

airflow list_dags

echo "***********************"
echo "Add custom GCP connection using service account key"
echo "***********************"
airflow run add_gcp_connection add_gcp_connection_python 2001-01-01
