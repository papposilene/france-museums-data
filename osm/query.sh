#!/bin/bash
osmosis \
 --read-xml data/planet-170102.osm \
 --tf accept-nodes tourism=museum \
 --tf reject-ways \
 --tf reject-relations \
 --write-xml data/output-museums-nodes.osm
 
osmosis \
 --read-xml data/planet-170102.osm \
 --tf accept-ways tourism=museum \
 --tf reject-relations \
 --tf --used-node \
 --write-xml data/output-museums-ways.osm
 
osmosis \
 --rx data/output-museums-ways.osm \
 --rx data/output-museums-nodes \
 --merge \
 --wx data/output-museums-merged.osm
