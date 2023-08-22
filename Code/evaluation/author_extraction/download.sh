#!/bin/sh

curl -sS https://hyperion.bbirke.de/data/ma/author_extraction_data.zip > file.zip && \
tar xvfj file.zip                                                                 && \
rm file.zip