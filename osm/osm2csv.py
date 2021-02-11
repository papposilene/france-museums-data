#!/usr/bin/env python3
import argparse
import unicodecsv as csv
import urllib3.request
import json
import xml.etree.ElementTree as ET

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
    parser = argparse.ArgumentParser(description='Convert museum osm files to csv')
    parser.add_argument('-i', '--input', type=str, required=True, help='input osm xml filename')
    parser.add_argument('-o', '--output', type=str, required=True, help='output csv filename')
    parser.add_argument('-v', '--version', action='version', version='1.0')
    return parser.parse_args()

def create_entry():
    return {
        "osm_id": None,
        "name": None,
        "name:en": None,
        "int_name": None,
        "old_name": None,
        "old_name:en": None,
        "number": None,
        "street": None,
        "postal_code": None,
        "city": None,
        "country": None,
        "country_code": None,
        "lat": None,
        "lon": None,
        "website": None,
        "email": None,
        "phone": None,
        "fax": None,
        "tags": None,
        "description": None,
        "date_added": None,
        "wikidata": None
    }

def main():

    args = parse_args()
    #locator = Nominatim(user_agent="fruseumpy-data/osm", timeout=10)

    with open(args.output, 'wb') as csv_file:

        fieldnames = ['osm_id', 'name', 'name:en', 'int_name', 'old_name', 'old_name:en', 'number', 'street', 'postal_code',
                      'city', 'country', 'country_code', 'lat', 'lon', 'website', 'email', 'phone', 'fax', 'tags', 'description', 'date_added',
                      'wikidata']
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        csv_writer.writeheader()

        num_rows = 0
        entry = create_entry()

        http = urllib3.PoolManager()
        tree = ET.parse(args.input)
        root = tree.getroot()
        
        for node in root.findall('node'):
            print(f"{bcolors.OKGREEN}Row #", num_rows, f"{bcolors.ENDC}")
            print(f"{bcolors.OKCYAN}Node :", node, f"{bcolors.ENDC}")
            
            for tag in root.findall('tag'):
                print(f"{bcolors.OKCYAN}Tag :", tag, f"{bcolors.ENDC}")

                entry['osm_id'] = node.get('id')
                entry['date_added'] = node.get('timestamp')

                osm_url = http.request('GET', 'https://nominatim.openstreetmap.org/lookup?format=jsonv2&addressdetails=1&extratags=1&namedetails=1&osm_ids=N' + node.get('id'))
                osm_data = json.loads(osm_url.data.decode('utf-8'))

                print(osm_data)
                entry['name'] = osm_data[0]['namedetails']['name']

                entry['lat'] = osm_data[0]['lat']
                entry['lon'] = osm_data[0]['lon']
                if 'road' in osm_data[0]['address']: entry['street'] = osm_data[0]['address']['road']
                if 'postcode' in osm_data[0]['address']: entry['postal_code'] = osm_data[0]['address']['postcode']
                if 'village' in osm_data[0]['address']:
                    entry['city'] = osm_data[0]['address']['village']
                elif 'town' in osm_data[0]['address']:
                    entry['city'] = osm_data[0]['address']['town']
                elif 'municipality' in osm_data[0]['address']:
                    entry['city'] = osm_data[0]['address']['municipality']
                elif 'city' in osm_data[0]['address']:
                    entry['city'] = osm_data[0]['address']['city']
                else:
                    entry['city'] = ""
                if 'country' in osm_data[0]['address']: entry['country'] = osm_data[0]['address']['country']
                if 'country_code' in osm_data[0]['address']: entry['country_code'] = osm_data[0]['address']['country_code']

                if 'k' in tag and tag['k'] == 'website': entry['website'] = tag.find('v').text
                if 'k' in tag and tag['k'] == 'email': entry['email'] = tag.find('v').text
                if 'k' in tag and tag['k'] == 'phone': entry['phone'] = tag.find('v').text
                if 'k' in tag and tag['k'] == 'wikidata': entry['wikidata'] = tag.find('v').text
                if 'k' in tag and tag['k'] == 'description': entry['description'] = tag.find('v').text

                entry['tags'] = 'osm:museum'

                # add to csv
                csv_writer.writerow(entry)

            else:
                print('Skipped')

            num_rows += 1
            entry = create_entry()
        print('wrote {} rows to {}'.format(num_rows, args.output))

if __name__ == '__main__':
    main()
