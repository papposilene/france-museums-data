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
        "email": None,
        "year": None,
        "stats": None,
        "tags": None,
        "description": None,
        "wikidata": None,
        "museofile": None,
        "mhs": None,
    }

def main():
    args = parse_args()
    locator = Nominatim(user_agent="fruseum-data/fdmdf", timeout=10)

    fieldnames = ['id', 'osm_id', 'name', 'number', 'street', 'postal_code', 'city', 'country', 'country_code',
                    'status', 'lat', 'lon', 'website', 'phone', 'fax', 'email', 'year', 'stats', 'tags', 'description',
                    'wikidata', 'museofile', 'mhs']

    with open(args.input, newline='') as csv_inputfile:
        csv_reader = csv.reader(csv_inputfile, delimiter=';', quotechar='|')
        headers = next(csv_reader, None)

        num_rows = 0
        entry = create_entry()

        for row in csv_reader:
            print(f"{bcolors.OKGREEN}Row #", num_rows, f"{bcolors.ENDC}")
            print(f"{bcolors.OKCYAN}Row data: ", row, f"{bcolors.ENDC}")

            entry['id'] = row[0]

            #print(row[1])
            location = locator.geocode(row[1] + ' ' + row[3], addressdetails=True)
            if hasattr(location, 'raw'):
                print(location.raw)
                json_dump = json.dumps(str(location.raw))
                osmdata = json.loads(json_dump)

                # Official name or name in the CSV
                if 'namedetails' in osmdata:
                    entry['name'] = location.raw['namedetails']['name']
                else:
                    entry['name'] = row[1]

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

                # Official website or contact:website
                if 'contact:website' in osmdata:
                    entry['website'] = location.raw['extratags']['contact:website']
                elif 'website' in osmdata:
                    entry['website'] = location.raw['extratags']['website']
                else:
                    entry['website'] = ''

                # Official phone or contact:phone
                if 'contact:phone' in osmdata:
                    entry['phone'] = location.raw['extratags']['contact:phone']
                elif 'phone' in osmdata:
                    entry['phone'] = location.raw['extratags']['phone']
                else:
                    entry['phone'] = ''

                # Official fax or contact:fax
                if 'contact:fax' in osmdata:
                    entry['fax'] = location.raw['extratags']['contact:fax']
                elif 'fax' in osmdata:
                    entry['fax'] = location.raw['extratags']['fax']
                else:
                    entry['fax'] = ''

                # Official email or contact:email
                if 'contact:email' in osmdata:
                    entry['email'] = location.raw['extratags']['contact:email']
                elif 'email' in osmdata:
                    entry['email'] = location.raw['extratags']['email']
                else:
                    entry['email'] = ''

                if 'wikidata' in osmdata: entry['wikidata'] = location.raw['extratags']['wikidata']
                if 'ref:mhs' in osmdata: entry['mhs'] = location.raw['extratags']['ref:mhs']
                if 'ref:FR:museofile' in osmdata: entry['museofile'] = location.raw['extratags']['ref:FR:museofile']
            else:
                words = row[1].replace(',', ' ')
                words = words.replace('\'', ' ')
                words = words.replace('’', ' ')
                words = words.replace('-', ' ')
                words = words.split()
                words = ' '.join([w for w in words if (len(w) > 3 and len(w) < 7)])

                print(words + ' ' + row[3])
                location = locator.geocode(words + ' ' + row[3], addressdetails=True, extratags=True, namedetails=True)

                if hasattr(location, 'raw'):
                    print(location.raw)
                    json_dump = json.dumps(str(location.raw))
                    osmdata = json.loads(json_dump)

                    # Official name or name in the CSV
                    if 'namedetails' in osmdata:
                        entry['name'] = location.raw['namedetails']['name']
                    else:
                        entry['name'] = row[1]

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

                    # Official website or contact:website
                    if 'contact:website' in osmdata:
                        entry['website'] = location.raw['extratags']['contact:website']
                    elif 'website' in osmdata:
                        entry['website'] = location.raw['extratags']['website']
                    else:
                        entry['website'] = ''

                    # Official phone or contact:phone
                    if 'contact:phone' in osmdata:
                        entry['phone'] = location.raw['extratags']['contact:phone']
                    elif 'phone' in osmdata:
                        entry['phone'] = location.raw['extratags']['phone']
                    else:
                        entry['phone'] = ''

                    # Official fax or contact:fax
                    if 'contact:fax' in osmdata:
                        entry['fax'] = location.raw['extratags']['contact:fax']
                    elif 'fax' in osmdata:
                        entry['fax'] = location.raw['extratags']['fax']
                    else:
                        entry['fax'] = ''

                    # Official email or contact:email
                    if 'contact:email' in osmdata:
                        entry['email'] = location.raw['extratags']['contact:email']
                    elif 'email' in osmdata:
                        entry['email'] = location.raw['extratags']['email']
                    else:
                        entry['email'] = ''

                    if 'wikidata' in osmdata: entry['wikidata'] = location.raw['extratags']['wikidata']
                    if 'ref:mhs' in osmdata: entry['mhs'] = location.raw['extratags']['ref:mhs']
                    if 'ref:FR:museofile' in osmdata: entry['museofile'] = location.raw['extratags']['ref:FR:museofile']
                else:
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

            if entry['mhs'] is not None:
                entry['tags'] = entry['tags'] + ';label:monuments-historiques'

            entry['year'] = row[4]

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
                entry['stats'] = entry['stats'] + ';' + 'label-date:' + row[6]

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

            num_rows += 1
            entry = create_entry()

        print('wrote {} rows.'.format(num_rows))

if __name__ == '__main__':
    main()
