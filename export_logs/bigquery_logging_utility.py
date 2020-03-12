# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import os
import argparse

from google.cloud import bigquery, logging
from google.cloud.exceptions import NotFound, Conflict

# TODO: (developer)-update this based on testing needs
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "bigquery-logs-writer-key.json"


class export_logs_utility:
    def __init__(
        self, sink_name, project_id, dataset_name, dataset_location, operation, filter_
    ):
        self.sink_name = sink_name
        self.project_id = project_id
        # setup bigquery config
        self.dataset_name = dataset_name
        self.bigquery_client = bigquery.Client(self.project_id)
        self.dataset = bigquery.DatasetReference(self.project_id, self.dataset_name)
        self.dataset_location = dataset_location
        self.operation = operation
        # https://cloud.google.com/bigquery/docs/reference/auditlogs#auditdata_examples
        self.filter_ = filter_

    def operation_sink(self):
        """Main handler that generates or creates sink end to end
        """
        if self.operation == "create":
            self.create_bigquery_dataset()
            self.create_sink()
            print("create operation is completed")
        elif self.operation == "list":
            self.list_sinks()
            print("list operation is completed")
        elif self.operation == "update":
            self.update_sink()
            print("update operation is completed")
        elif self.operation == "delete":
            # do NOT delete dataset and tables in case they need to remain for audit purposes
            self.delete_sink()
            print(
                f"Dataset: {self.dataset_name} will NOT be deleted to maintain an audit archive"
            )
            print("delete operation is completed")

    def list_sinks(self):
        """Lists all sinks."""
        logging_client = logging.Client()

        sinks = list(logging_client.list_sinks())

        if not sinks:
            print("No sinks.")

        for sink in sinks:
            print(
                "Sink Name: {}, Logs Filter: {} -> Sink Destination: {}".format(
                    sink.name, sink.filter_, sink.destination
                )
            )

    def create_bigquery_dataset(self):
        """Create an empty dataset"""
        try:
            # Specify the geographic location where the dataset should reside.
            self.dataset.location = self.dataset_location
            # Send the dataset to the API for creation.
            # Raises google.api_core.exceptions.Conflict if the Dataset already
            # exists within the project.
            dataset = self.bigquery_client.create_dataset(
                self.dataset
            )  # Make an API request.
            print(
                "Created dataset {}.{}".format(
                    self.bigquery_client.project, dataset.dataset_id
                )
            )
        except Conflict:
            print("Dataset already exists '{}'.".format(self.dataset_name))

    def create_sink(self):
        """Creates a sink to export logs to the given Cloud Storage bucket.

        The filter determines which logs this sink matches and will be exported
        to the destination. For example a filter of 'severity>=INFO' will send
        all logs that have a severity of INFO or greater to the destination.
        See https://cloud.google.com/logging/docs/view/advanced_filters for more
        filter information.
        """
        logging_client = logging.Client()

        # The destination can be a Cloud Storage bucket, a Cloud Pub/Sub topic,
        # or a BigQuery dataset. In this case, it is a Cloud Storage Bucket.
        # See https://cloud.google.com/logging/docs/api/tasks/exporting-logs for
        # information on the destination format.
        destination = f"bigquery.googleapis.com/projects/{self.project_id}/datasets/{self.dataset_name}"

        sink = logging_client.sink(self.sink_name, self.filter_, destination)

        if sink.exists():
            print("Sink {} already exists.".format(sink.name))
            return

        sink.create(unique_writer_identity=True)
        print("Created sink {}".format(sink.name))

    # TODO: update sink functionality
    def update_sink(self):
        """Changes a sink's filter.

        The filter determines which logs this sink matches and will be exported
        to the destination. For example a filter of 'severity>=INFO' will send
        all logs that have a severity of INFO or greater to the destination.
        See https://cloud.google.com/logging/docs/view/advanced_filters for more
        filter information.
        """
        logging_client = logging.Client()
        sink = logging_client.sink(self.sink_name)

        sink.reload()

        sink.filter_ = self.filter_
        sink.update(unique_writer_identity=True)
        print("Updated sink {}".format(sink.name))
        print(f"New Filter: {sink.filter_}")

    def delete_sink(self):
        """Deletes a sink."""
        logging_client = logging.Client()
        sink = logging_client.sink(self.sink_name)

        sink.delete()

        print("Deleted sink {}".format(sink.name))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Usage: %prog -s sink_name -p project_id -d dataset_name -l dataset_location -o operation"
    )
    parser.add_argument(
        "-s",
        action="store",
        type=str,
        dest="sink_name",
        help="name of sink for exporting logs",
        required=True,
    )
    parser.add_argument(
        "-p",
        action="store",
        type=str,
        dest="project_id",
        help="name of Google Cloud project that will create the export logs",
        required=True,
    )
    parser.add_argument(
        "-d",
        action="store",
        type=str,
        dest="dataset_name",
        help="Name of dataset to create or already existing to store exported logs",
        required=True,
    )
    parser.add_argument(
        "-l",
        action="store",
        type=str,
        dest="dataset_location",
        help="Location of dataset to create to store exported logs",
        required=True,
    )
    parser.add_argument(
        "-o",
        action="store",
        type=str,
        dest="operation",
        help="Whether to create, delete, list, or update the sink",
        required=True,
    )
    parser.add_argument(
        "-f",
        action="store",
        type=str,
        dest="filter",
        help="Filter for the sink export-this variable will only apply to the create/update operations",
        required=True,
    )

    options = parser.parse_args()

    print(options)

    sink_name = options.sink_name
    project_id = options.project_id
    dataset_name = options.dataset_name
    dataset_location = options.dataset_location
    operation = options.operation
    filter_ = options.filter

    # define the class utility and run the script
    logs_operator = export_logs_utility(
        sink_name, project_id, dataset_name, dataset_location, operation, filter_
    )

    # perform log operation based on operation flag
    logs_operator.operation_sink()
