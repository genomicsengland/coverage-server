#!/bin/python
import argparse
import requests
import logging
import sys


def main():

    parser = argparse.ArgumentParser(description='Calypso data dropper. This script deletes all data from the database')
    parser.add_argument('--host', metavar='host',
                        help='The Calypso host where the REST API is available [required]',
                        required=True)
    parser.add_argument('--protocol', metavar='protocol',
                        help='The Calypso protocol for the REST API [default:http]', default="http")
    parser.add_argument('--verbose', dest='verbose',
                        help='Verbose logs in standard output', action='store_true')
    parser.add_argument('--force', dest='force',
                        help='Avoids asking for confirmation', action='store_true')

    args = parser.parse_args()
    if not args.force:
        while True:
            sys.stdout.write(
                "This operation will delete all coverage data in Calypso. Are you sure you want to continue? [y/n]")
            choice = input().lower()
            if choice == 'y':
                break
            elif choice == 'n':
                return
            else:
                sys.stdout.write("Please respond with 'y' or 'n'.\n")
    if args.verbose:
        logging.basicConfig(level='DEBUG')
    rest_api = requests.session()
    url_base = "{}://{}/api/".format(args.protocol, args.host)
    response = rest_api.get(url_base + "sample-ingestion/")
    samples = response.json()
    for sample in samples:
        sample_name = sample['name']
        gene_collection = sample['gene_collection']
        response = rest_api.delete(url_base + "sample-ingestion/{}-{}/".format(
            sample_name.lower(), gene_collection.lower()))
        # TODO: there is no way to check if deletion was successful as delete operation always returns 404
        logging.debug("Successfully deleted sample {} form collection {}".format(sample_name, gene_collection))


if __name__ == '__main__':
    main()
