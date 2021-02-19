#!/usr/bin/env python3
import argparse
import os.path
import csv
import json
import geopy
from datetime import datetime
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
##import reverse_geocode

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def parse_args():
    parser = argparse.ArgumentParser(description='Convert messy frequentation-des-musees-de-france csv files to structured by year files')
    parser.add_argument('-i', '--input', type=str, required=True, help='input messy csv filename')
    parser.add_argument('-y', '--year', type=str, required=False, help='extract data for ths given year (format: xxxx)')
    parser.add_argument('-v', '--version', action='version', version='1.0')
    return parser.parse_args()

def create_entry():
    return {
        "id": None,
        "osm_id": None,
        "name": None,
        #"number": None,
        #"street": None,
        #"postal_code": None,
        "city": None,
        "country": None,
        "country_code": None,
        "status": None,
        #"lat": None,
        #"lon": None,
        #"website": None,
        #"phone": None,
        #"fax": None,
        #"email": None,
        "year": None,
        "stats": None,
        "tags": None,
        #"description": None,
        #"wikidata": None,
        #"museofile": None,
        #"mhs": None,
    }

def main():
    args = parse_args()

    fieldnames = ['id', 'osm_id', 'name', 'city', 'country', 'country_code', 'status', 'year', 'stats', 'tags']

    with open(args.input, newline='') as csv_inputfile:
        # Setup counters (data,skipped and total)
        rows_total = 0
        rows_data = 0
        rows_skipped = 0

        # Initiate CSV reader
        csv_reader = csv.reader(csv_inputfile, delimiter=';', quotechar='|')
        headers = next(csv_reader, None)

        # Initiate entry
        entry = create_entry()

        for row in csv_reader:
            rows_total += 1
            print(f"{bcolors.OKGREEN}Row #", rows_total, f": analyzing data...{bcolors.ENDC}")

            # Extract only frequentation for this year
            if args.year and (row[4] != args.year):
                    rows_skipped += 1
                    print(f"{bcolors.FAIL}Row #", rows_total, f": skipped for unmatched year.{bcolors.ENDC}")
                    continue

            # If row not skipped, let's go!
            print(f"{bcolors.OKCYAN}Row data:", row, f"{bcolors.ENDC}")

            entry['year'] = row[4]
            entry['id'] = row[0]
            entry['name'] = row[1]
            entry['city'] = row[3]
            entry['country'] = 'France'
            entry['country_code'] = 'fr'

            if row[10] == 'F':
                entry['status'] = 'closed'
            else:
                entry['status'] = 'open'

            if row[10] == 'R':
                entry['tags'] = 'unlabel:musee de france'
            else:
                entry['tags'] = 'label:musee de france'

            if row[7]:
                entry['stats'] = 'payant:' + row[7]
            else:
                entry['stats'] = 'payant:0'

            if row[8]:
                entry['stats'] = entry['stats'] + ';' + 'gratuit:' + row[8]
            else:
                entry['stats'] = entry['stats'] + ';' + 'gratuit:0'

            entry['stats'] = entry['stats'] + ';' + 'total:' + row[9]

            if row[6]:
                entry['stats'] = entry['stats'] + ';' + 'mdf-date:' + row[6]

            output_file = './data/frequentation-des-musees-de-france-pour-' + row[4] + '.csv'
            if os.path.isfile(output_file):
                with open(output_file, 'a+', newline='') as csv_outputfile:
                    csv_writer = csv.DictWriter(csv_outputfile, fieldnames=fieldnames)
                    csv_writer.writerow(entry)
            else:
                with open(output_file, 'a+', newline='') as csv_outputfile:
                    csv_writer = csv.DictWriter(csv_outputfile, fieldnames=fieldnames)
                    csv_writer.writeheader()
                    csv_writer.writerow(entry)

            rows_data += 1
            entry = create_entry()

        print('Wrote {0} rows for {1}, with {2} extracted and {3} skipped.'.format(rows_total, args.year, rows_data, rows_skipped))

if __name__ == '__main__':
    main()
