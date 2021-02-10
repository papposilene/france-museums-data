#!/usr/bin/env python3
import argparse
import unicodecsv as csv
import urllib.request
import json
import xml.etree.ElementTree as ET

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

        for event, elem in ET.iterparse(args.input, events=("start", "end")):
            print(f"{bcolors.OKGREEN}Row #", num_rows, f"{bcolors.ENDC}")
            print(f"{bcolors.OKCYAN}Row data: ", elem, f"{bcolors.ENDC}")
            
            if event == 'start':
                # Node element
                if elem.tag == 'node':
                    if 'id' in elem.attrib: entry['osm_id'] = elem.attrib['id']
                    if 'timestamp' in elem.attrib: entry['date_added'] = elem.attrib['timestamp']

                    osm_url = "https://nominatim.openstreetmap.org/lookup?format=jsonv2&addressdetails=1&extratags=1&namedetails=1&osm_ids=N" + elem.attrib['id']
                    osm_data = urllib.request.urlopen(url).read().decode()
                    print(osm_data)

                    if 'lat' in elem.attrib: entry['lat'] = osm_data['lat']
                    if 'lon' in elem.attrib: entry['lon'] = osm_data['lon']
                    if 'road' in osm_data: entry['street'] = osm_data['address']['road']
                    if 'postcode' in osm_data: entry['postal_code'] = location.raw['address']['postcode']
                    if 'village' in osm_data:
                        entry['city'] = osm_data['address']['village']
                    elif 'town' in osm_data:
                        entry['city'] = osm_data['address']['town']
                    elif 'municipality' in osm_data:
                        entry['city'] = osm_data['address']['municipality']
                    elif 'city' in osm_data:
                        entry['city'] = osm_data['address']['city']
                    else:
                        entry['city'] = ""
                    entry['country'] = osm_data['address']['country']
                    entry['country_code'] = osm_data['address']['country_code']
                # Way element
                elif elem.tag == 'way':
                    if 'id' in elem.attrib: entry['osm_id'] = elem.attrib['id']
                    if 'timestamp' in elem.attrib: entry['date_added'] = elem.attrib['timestamp']
                        
                    osm_url = "https://nominatim.openstreetmap.org/lookup?format=jsonv2&addressdetails=1&extratags=1&namedetails=1&osm_ids=W" + elem.attrib['id']
                    osm_data = urllib.request.urlopen(url).read().decode()
                    print(osm_data)

                    if 'lat' in elem.attrib: entry['lat'] = osm_data['lat']
                    if 'lon' in elem.attrib: entry['lon'] = osm_data['lon']
                    if 'road' in osm_data: entry['street'] = osm_data['address']['road']
                    if 'postcode' in osm_data: entry['postal_code'] = osm_data['address']['postcode']
                    if 'village' in osm_data:
                        entry['city'] = osm_data['address']['village']
                    elif 'town' in osm_data:
                        entry['city'] = osm_data['address']['town']
                    elif 'municipality' in osm_data:
                        entry['city'] = osm_data['address']['municipality']
                    elif 'city' in osm_data:
                        entry['city'] = osm_data['address']['city']
                    else:
                        entry['city'] = ""
                    entry['country'] = osm_data['address']['country']
                    entry['country_code'] = osm_data['address']['country_code']
                    
            elif event == 'end':
                if elem.tag == 'tag':
                    if 'k' in elem.attrib and elem.attrib['k'] == 'name': entry['name'] = elem.attrib['v']
                    if 'k' in elem.attrib and elem.attrib['k'] == 'website': entry['website'] = elem.attrib['v']
                    if 'k' in elem.attrib and elem.attrib['k'] == 'email': entry['email'] = elem.attrib['v']
                    if 'k' in elem.attrib and elem.attrib['k'] == 'phone': entry['phone'] = elem.attrib['v']
                    if 'k' in elem.attrib and elem.attrib['k'] == 'wikidata': entry['wikidata'] = elem.attrib['v']
                    if 'k' in elem.attrib and elem.attrib['k'] == 'description': entry['description'] = elem.attrib['v']
                elif elem.tag == 'node':

                    entry['tags'] = 'osm:museum'
                # add to csv
                csv_writer.writerow(entry)
                num_rows += 1
                entry = create_entry()
        print('wrote {} rows to {}'.format(num_rows, args.output))

if __name__ == '__main__':
    main()
