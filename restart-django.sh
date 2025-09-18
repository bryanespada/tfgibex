#!/bin/sh
sudo docker stop tfgibex-app &&
sudo docker rm tfgibex-app &&
# sudo docker stop tfgibex-db &&
# sudo docker rm tfgibex-db &&
# sudo docker volume rm tfgibex-db ; true &&
sudo docker compose up -d --force-recreate --build tfgibex-db &&
sudo docker compose up -d --force-recreate --build tfgibex-app &&
sudo docker logs -n 100 -f tfgibex-app