#!/usr/bin/env python3
import argparse
import unicodecsv as csv
import json
import geopy
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
##import reverse_geocode

def parse_args():
    parser = argparse.ArgumentParser(description='Convert frequentation-des-musees-de-france csv files to strctured by year files')
    parser.add_argument('-i', '--input', type=str, required=True, help='input bordelique csv filename')
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
        "tags": None,
        "stats": None,
        "description": None
    }

def main():
    args = parse_args()
    locator = Nominatim(user_agent="fruseum-data", timeout=10)


    with open(args.output, 'wb') as csv_file:

        fieldnames = ['id', 'osm_id', 'name', 'number', 'street', 'postal_code', 'city', 'country', 'country_code',
                      'status', 'lat', 'lon', 'website', 'phone', 'fax', 'tags', 'stats', 'description']
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        csv_writer.writeheader()

        num_rows = 0
        entry = create_entry()

        for row in csv.reader(args.input, encoding='utf-8'):
            if 'id' in row: entry['ref'] = row['ref']

            coords = [(float(elem.attrib['lat']), float(elem.attrib['lon']))]
            location = locator.reverse(coords)
            print(location.raw)
            json_dump = json.dumps(str(location.raw))
            osmdata = json.loads(json_dump)

            if 'osm_id' in osmdata: entry['osm_id'] = location.raw['osm_id']
            if 'lat' in osmdata: entry['lat'] = location.raw['lat']
            if 'lon' in osmdata: entry['lon'] = location.raw['lon']
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

            csv_writer.writerow(entry)
            num_rows += 1
            entry = create_entry()
        print('wrote {} rows to {}'.format(num_rows, args.output))

if __name__ == '__main__':
    main()
