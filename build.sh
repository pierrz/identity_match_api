#!/bin/bash

docker build -t id_match_api_image .
docker run -d --name id_match_api_container --expose 80:80 id_match_api_image
