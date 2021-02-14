#!/bin/bash
osmosis \
 --read-xml raw/france-latest.osm \
 --tf accept-nodes tourism=museum \
 --tf reject-ways \
 --tf reject-relations \
 --write-xml museums-data/france-nodes.osm

osmosis \
 --read-xml raw/france-latest.osm \
 --tf accept-ways tourism=museum \
 --tf reject-relations \
 --tf --used-node \
 --write-xml museums-data/france-ways.osm

osmosis \
 --rx museums-data/france-ways.osm \
 --rx museums-data/france-nodes \
 --merge \
 --wx museums-data/france-merged.osm
