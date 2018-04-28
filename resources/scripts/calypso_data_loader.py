#!/bin/python
import argparse
import requests
import logging
from celery import states
import time


def main():

    parser = argparse.ArgumentParser(description='Calypso data loader')
    parser.add_argument('--input', metavar='input', help='Tab-separated values file with three columns: sample name, '
                                                         'path to coverage JSON (available in host) and '
                                                         'gene collection (this must exist and it can only be added '
                                                         'through the admin console) [required]',
                        required=True)
    parser.add_argument('--host', metavar='host',
                        help='The Calypso host where the REST API is available [required]',
                        required=True)
    parser.add_argument('--protocol', metavar='protocol',
                        help='The Calypso protocol for the REST API [default:http]', default="http")
    parser.add_argument('--verbose', dest='verbose',
                        help='Verbose logs in standard output', action='store_true')

    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(level='DEBUG')
    rest_api = requests.session()
    url_base = "{}://{}/api/".format(args.protocol, args.host)
    with open(args.input, "r") as input_data:
        for entry in input_data:
            sample_name, json_path, group_name = entry.strip().split("\t")
            post_data = {
                "name": sample_name,
                "input_file": json_path,
                "gene_collection": group_name
            }
            # posts to Calypso
            response = rest_api.post(url_base + "sample-ingestion/", json=post_data)
            if response.status_code != 201:
                logging.error("Failed to send data to Calypso: {}".format(str(post_data)))
                raise ValueError("Calypso load error: {}".format(str(response.content)))
            logging.debug("Sample '{}' for gene collection '{}' sent to Calypso".format(sample_name, group_name))
            # checks for the status of the data ingestion
            ingestion_status = states.PENDING
            while ingestion_status != states.SUCCESS:
                response = rest_api.get(
                    url_base + "sample-ingestion/{}-{}/".format(sample_name.lower(), group_name.lower()))
                if response.status_code != 200:
                    logging.error("Failed to find sent data in Calypso: {}-{}".format(
                        sample_name.lower(), group_name.lower()))
                    raise ValueError("Calypso failed to retrieve sent data: {}".format(str(response.content)))
                ingestion_status = response.json()["status"]
                if ingestion_status == states.FAILURE:
                    logging.error("Calypso failed to ingest data: {}".format(str(response.content)))
                    raise ValueError("Calypso failed to ingest data: {}".format(str(response.content)))
                if ingestion_status != states.SUCCESS:
                    logging.debug("Waiting for data in state '{}'...".format(ingestion_status))
                    time.sleep(2)
            logging.debug("Ingestion for {}-{} was successful!".format(sample_name.lower(), group_name.lower()))


if __name__ == '__main__':
    main()
