#!/usr/bin/env python3
import argparse
import os.path
import csv
import json
import geopy
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
##import reverse_geocode

def parse_args():
    parser = argparse.ArgumentParser(description='Convert messy frequentation-des-musees-de-france csv files to structured by year files')
    parser.add_argument('-i', '--input', type=str, required=True, help='input messy csv filename')
    #parser.add_argument('-o', '--output', type=str, required=True, help='input structured csv filename')
    parser.add_argument('-v', '--version', action='version', version='1.0')
    return parser.parse_args()

def create_entry():
    return {
        "id": None,
        "osm_id": None,
        "name": None,
        "number": None,
        "street": None,
        "postal_code": None,
        "city": None,
        "country": None,
        "country_code": None,
        "status": None,
        "lat": None,
        "lon": None,
        "website": None,
        "phone": None,
        "fax": None,
        "annee": None,
        "stats": None,
        "tags": None,
        "description": None
    }

def main():
    args = parse_args()
    locator = Nominatim(user_agent="fruseum-data/fdmdf", timeout=10)

    fieldnames = ['id', 'osm_id', 'name', 'number', 'street', 'postal_code', 'city', 'country', 'country_code',
                    'status', 'lat', 'lon', 'website', 'phone', 'fax', 'annee', 'stats', 'tags', 'description']

    with open(args.input, newline='') as csv_inputfile:
        csv_reader = csv.reader(csv_inputfile, delimiter=';', quotechar='|')
        headers = next(csv_reader, None)

        num_rows = 0
        entry = create_entry()

        for row in csv_reader:
            print(row)

            entry['id'] = row[0]
            entry['name'] = row[1]

            print(row[1])
            location = locator.geocode(row[1] + ' ' + row[3], addressdetails=True)
            if hasattr(location, 'raw'):
                print(location.raw)
                json_dump = json.dumps(str(location.raw))
                osmdata = json.loads(json_dump)

                if 'osm_id' in osmdata: entry['osm_id'] = location.raw['osm_id']
                if 'lat' in osmdata: entry['lat'] = location.raw['lat']
                if 'lon' in osmdata: entry['lon'] = location.raw['lon']
                if 'house_number' in osmdata: entry['number'] = location.raw['address']['house_number']
                if 'road' in osmdata: entry['street'] = location.raw['address']['road']
                if 'postcode' in osmdata: entry['postal_code'] = location.raw['address']['postcode']
                if 'village' in osmdata:
                    entry['city'] = location.raw['address']['village']
                elif 'town' in osmdata:
                    entry['city'] = location.raw['address']['town']
                elif 'municipality' in osmdata:
                    entry['city'] = location.raw['address']['municipality']
                elif 'city' in osmdata:
                    entry['city'] = location.raw['address']['city']
                else:
                    entry['city'] = ""
                if 'country' in osmdata: entry['country'] = location.raw['address']['country']
                if 'country_code' in osmdata:  entry['country_code'] = location.raw['address']['country_code']

            if row[10] == 'F':
                entry['status'] = 'closed'
            else:
                entry['status'] = 'open'

            entry['annee'] = row[4]
            entry['stats'] = 'payant:' + row[7]
            entry['stats'] = entry['stats'] + ';' + 'gratuit:' + row[8]
            entry['tags'] = 'label:musee de france'

            output_file = './data/data-for-' + row[4] + '.csv'
            if os.path.isfile(output_file):
                with open(output_file, 'a+', newline='') as csv_outputfile:
                    csv_writer = csv.DictWriter(csv_outputfile, fieldnames=fieldnames)
                    csv_writer.writerow(entry)
            else:
                with open(output_file, 'a+', newline='') as csv_outputfile:
                    csv_writer = csv.DictWriter(csv_outputfile, fieldnames=fieldnames)
                    csv_writer.writeheader()
                    csv_writer.writerow(entry)

            num_rows += 1
            entry = create_entry()

        print('wrote {} rows to {}'.format(num_rows, args.output))

if __name__ == '__main__':
    main()
