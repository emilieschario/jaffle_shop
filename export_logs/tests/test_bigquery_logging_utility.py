# -*- coding: utf-8 -*-
#!/usr/bin/env python3

"""
This script is intended to test basic functionality of the export log utility
"""

from google.cloud import bigquery, logging
from export_logs.bigquery_logging_utility import export_logs_utility
import os
import subprocess
from google.cloud.exceptions import NotFound

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "bigquery-logs-writer-key.json"


test_variables = {
    "sink_name": "test_log_utility",
    "project_id": "wam-bam-258119",
    "dataset_name": "test_logs_dataset",
    "dataset_location": "US",
    "filter_": r'protoPayload.metadata."@type"="type.googleapis.com/google.cloud.audit.BigQueryAuditMetadata"',
}


def test_list_sinks(capfd):
    try:
        # run the function
        logs_operator = export_logs_utility(
            test_variables["sink_name"],
            test_variables["project_id"],
            test_variables["dataset_name"],
            test_variables["dataset_location"],
            "list",
            test_variables["filter_"],
        )

        logs_operator.list_sinks()
        out, err = capfd.readouterr()
        # assert that the print message exists in the terminal output
        assert out == "No sinks.\n"
    except AssertionError:
        assert "Sink Name:" in out
        assert "Logs Filter:" in out
        assert "Sink Destination:" in out


def test_create_bigquery_dataset():
    try:
        # expected result
        expected_result = "Dataset(DatasetReference('{}', '{}'))".format(
            test_variables["project_id"], test_variables["dataset_name"]
        )
        # run the function
        logs_operator = export_logs_utility(
            test_variables["sink_name"],
            test_variables["project_id"],
            test_variables["dataset_name"],
            test_variables["dataset_location"],
            "create",
            test_variables["filter_"],
        )
        logs_operator.create_bigquery_dataset()

        # assert if the dataset actually exists
        bigquery_client = bigquery.Client(test_variables["project_id"])
        dataset_id = test_variables["dataset_name"]
        result = str(bigquery_client.get_dataset(dataset_id))
        assert result == expected_result
    except NotFound:
        assert False


def test_create_sink(capfd):
    try:
        # run the function
        logs_operator = export_logs_utility(
            test_variables["sink_name"],
            test_variables["project_id"],
            test_variables["dataset_name"],
            test_variables["dataset_location"],
            "create",
            test_variables["filter_"],
        )

        logs_operator.create_sink()
        out, err = capfd.readouterr()

        logging_client = logging.Client()
        sink = logging_client.sink(logs_operator.sink_name)
        # assert that the sink exists
        assert sink.exists()
        # assert that the print message exists in the terminal output
        assert out == "Created sink {}\n".format(test_variables["sink_name"])
    except AssertionError:
        # assert that the sink exists
        assert sink.exists()
        assert out == "Sink {} already exists.\n".format(test_variables["sink_name"])


def test_update_sink(capfd):
    # setup sink creation
    logs_operator = export_logs_utility(
        test_variables["sink_name"],
        test_variables["project_id"],
        test_variables["dataset_name"],
        test_variables["dataset_location"],
        "create",
        test_variables["filter_"],
    )
    # create sink
    logs_operator.create_sink()

    # setup sink update
    test_filter = "severity>=INFO"
    logs_operator = export_logs_utility(
        test_variables["sink_name"],
        test_variables["project_id"],
        test_variables["dataset_name"],
        test_variables["dataset_location"],
        "update",
        test_filter,
    )
    # update sink
    logs_operator.update_sink()

    # reload the sink
    logging_client = logging.Client()
    sink = logging_client.sink(logs_operator.sink_name)
    sink.reload()

    out, err = capfd.readouterr()
    # assert that the print message exists in the terminal output
    assert "Updated sink {}\n".format(test_variables["sink_name"]) in out

    # check if the sink filter matches the value we input to update
    assert sink.filter_ == test_filter


def test_delete_sink(capfd):
    # run the function
    logs_operator = export_logs_utility(
        test_variables["sink_name"],
        test_variables["project_id"],
        test_variables["dataset_name"],
        test_variables["dataset_location"],
        "delete",
        test_variables["filter_"],
    )

    # create sink
    logs_operator.create_sink()
    logging_client = logging.Client()
    sink = logging_client.sink(logs_operator.sink_name)
    # assert that the sink exists
    assert sink.exists()

    # delete sink
    logs_operator.delete_sink()
    out, err = capfd.readouterr()

    # assert that the print message exists in the terminal output
    assert "Deleted sink {}\n".format(test_variables["sink_name"]) in out

    # assert that it does not exist
    assert not sink.exists()

