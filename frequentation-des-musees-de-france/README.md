# Frequentation des Musees de France Data

The French Ministry of Culture provides a file [Fréquentation des Musées de France](https://www.data.gouv.fr/fr/datasets/frequentation-des-musees-de-france-1/) with the number of visitors, free or paid entrance, to french museums which have received the "Musée de France" label. However, this file (in CSV or JSON format) is not very structured: no postal address, no postal code, no reference external to the ministry (such as WikiData identifier or OSM ID). This python script is used to retrieve the data from this file and structure them: OSM ID, postal address (street number, street name, postal code, city), data organization (paid: number, free: number, label: museum de france) in order to allow easier re-use of this data.

## Messy CSV to structured CSV (and augment location using geolookup)

```
pip install geopy csv json
```

To convert and augment geo location data, run:
```
python frequentation-des-musees-de-france.py --input frequentation-des-musees-de-france.csv --output data/final.csv
```
