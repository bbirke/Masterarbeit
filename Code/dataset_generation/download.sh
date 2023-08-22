#!/bin/sh

curl -sS https://hyperion.bbirke.de/data/ma/dataset_generation.zip > file.zip && \
tar xvfj file.zip                                                             && \
rm file.zip