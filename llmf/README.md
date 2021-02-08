# Liste et Localisation des Musées de France Data

The French Ministry of Culture provides a file [Liste et Localisation des Musées de France](https://data.culture.gouv.fr/explore/dataset/liste-et-localisation-des-musees-de-france/information/) of french museums which have received the "Musée de France" label. However, this file (in CSV or JSON format) lacks of stable informations: no reference external to the ministry (such as WikiData identifier or OSM ID). This python script is used to retrieve the data from this file and structure them: OSM ID, postal address (street number, street name, postal code, city), data organization (label: museum de france) in order to allow easier re-use of this data.

## Messy CSV to structured CSV (and augment location using geolookup)

```
pip install geopy csv json
```

To convert and augment geo location data, run:
```
python3 liste-et-localisation-des-musees-de-france.py --input liste-et-localisation-des-musees-de-france.csv
```
