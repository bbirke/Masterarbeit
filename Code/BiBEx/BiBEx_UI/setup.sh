#!/bin/sh

docker build --build-arg bibex_model_endpoint=http://localhost:8000 --tag bibex_ui:latest . < ./Dockerfile