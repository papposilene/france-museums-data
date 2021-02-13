#!/usr/bin/env python3
import argparse
import csv
import os.path
import json
import geopy
import unidecode
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
    parser = argparse.ArgumentParser(description='Convert messy liste-et-localisation-des-musees-de-france csv files to structured file')
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
        "stats": None,
        "tags": None,
        "description": None,
        "wikidata": None
    }

def main():
    args = parse_args()
    locator = Nominatim(user_agent="fruseum-data/llmf", timeout=10)

    fieldnames = ['id', 'osm_id', 'name', 'number', 'street', 'postal_code', 'city', 'country', 'country_code',
                    'status', 'lat', 'lon', 'website', 'phone', 'fax', 'opening_days', 'closing_days', 'stats',
                    'tags', 'description', 'wikidata']

    with open(args.input, newline='') as csv_inputfile:
        csv_reader = csv.reader(csv_inputfile, delimiter=',', quotechar='"')
        headers = next(csv_reader, None)

        num_rows = 0
        entry = create_entry()

        for row in csv_reader:
            print(f"{bcolors.OKGREEN}Row #", num_rows, f"{bcolors.ENDC}")
            print(f"{bcolors.OKCYAN}Row data: ", row, f"{bcolors.ENDC}")

            entry['id'] = row[1]
            entry['name'] = row[0]

            location = locator.geocode(row[0] + ' ' + row[4], addressdetails=True)
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
            else:
                words = row[0].replace(',', ' ')
                words = words.replace('\'', ' ')
                words = words.replace('’', ' ')
                words = words.replace('-', ' ')
                words = words.split()
                words = ' '.join([w for w in words if (len(w) > 3 and len(w) < 7)])

                print(words + ' ' + row[4])
                location = locator.geocode(words + ' ' + row[4], addressdetails=True)

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
                else:
                    entry['city'] = row[4]
                    entry['country'] = 'France'
                    entry['country_code'] = 'fr'

            entry['phone'] = row[5]
            entry['fax'] = row[6]
            entry['website'] = row[7]
            entry['opening_days'] = row[9]
            entry['closing_days'] = row[8]

            if row[10] == 'R':
                entry['tags'] = 'unlabel:musee de france'
            else:
                entry['tags'] = 'label:musee de france'

            if row[10] == 'F':
                entry['status'] = 'closed'
            else:
                entry['status'] = 'open'

            # Create automatic tags with the name of the museum
            # type:ecomusee
            name = unidecode.unidecode(row[0])
            name = name.casefold()
            print(name)
            if 'archeologique' in name:
                entry['tags'] = entry['tags'] + ';type:musee archeologique;art:prehistoire'
            elif 'antique' in name:
                entry['tags'] = entry['tags'] + ';type:musee archeologique;art:antiquite'
            elif 'arts decoratifs' in name:
                entry['tags'] = entry['tags'] + ';type:musee d\'arts decoratifs'
            elif 'agricole' in name:
                entry['tags'] = entry['tags'] + ';type:musee technique et industriel'
            elif 'outil' in name:
                entry['tags'] = entry['tags'] + ';type:musee technique et industriel'
            elif 'ouvrier' in name:
                entry['tags'] = entry['tags'] + ';type:musee d\'arts populaires'
            elif 'populaire' in name:
                entry['tags'] = entry['tags'] + ';type:musee d\'arts populaires'
            elif 'prehistoire' in name:
                entry['tags'] = entry['tags'] + ';type:musee archeologique;art:prehistoire'
            elif 'atelier' in name:
                entry['tags'] = entry['tags'] + ';type:atelier d\'artiste'
            elif 'beaux-arts' in name:
                entry['tags'] = entry['tags'] + ';type:musee de beaux-arts'
            elif 'ecomusee' in name:
                entry['tags'] = entry['tags'] + ';type:ecomusee'
            elif 'geologie' in name:
                entry['tags'] = entry['tags'] + ';type:musee d\'histoire naturelle'
            elif 'industrie' in name:
                entry['tags'] = entry['tags'] + ';type:musee technique et industriel'
            elif 'technique' in name:
                entry['tags'] = entry['tags'] + ';type:musee technique et industriel'
            elif 'histoire' in name:
                entry['tags'] = entry['tags'] + ';type:musee historique'
            elif 'historique' in name:
                entry['tags'] = entry['tags'] + ';type:musee historique'
            elif 'museum' in name:
                entry['tags'] = entry['tags'] + ';type:museum'
            elif 'musee' in name:
                entry['tags'] = entry['tags'] + ';type:musee'
            else:
                entry['tags'] = entry['tags'] + ';type:a classer'

            if row[11] and row[12]:
                entry['stats'] = 'label-date:' + row[11] + ';' + 'unlabel-date:' + row[12]
            elif row[11] and not row[12]:
                entry['stats'] = 'label-date:' + row[11]
            elif row[12] and not row[11]:
                entry['stats'] = 'unlabel-date:' + row[12]
            else:
                entry['stats'] = ''

            output_file = './data/liste-et-localisation-des-musees-de-france.csv'
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
