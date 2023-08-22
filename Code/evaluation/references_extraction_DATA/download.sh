#!/bin/sh

curl -sS https://hyperion.bbirke.de/data/ma/references_extraction_DATA.zip > file.zip && \
tar xvfj file.zip                                                                     && \
rm file.zip