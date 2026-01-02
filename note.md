<!-- TẢI DOCKER -->

docker --version
docker compose version

<!-- CHUẨN BỊ THƯ MỤC -->

mkdir superset_docker
cd superset_docker

<!-- TẠO docker-compose.yml -->

version: "3.8"

services:
superset:
image: apache/superset:latest
container_name: superset
ports: - "8088:8088"
environment: - SUPERSET_SECRET_KEY=mysupersecretkey
volumes: - superset_home:/app/superset_home
command: >
/bin/bash -c "
superset db upgrade &&
superset fab create-admin
--username admin
--firstname Superset
--lastname Admin
--email admin@superset.com
--password admin &&
superset init &&
superset run -h 0.0.0.0 -p 8088
"
volumes:
superset_home:

<!-- RUN -->

docker compose up -d

<!-- XOÁ CONTEINER CŨ -->

docker compose down -v

<!-- CHECK CÁC IMAGE CHẠY -->

docker ps

<!-- cấu hình migrate database -->

docker exec -it superset superset db upgrade

<!-- TẠO ADMIN -->

docker exec -it superset superset fab create-admin --username admin --firstname Superset --lastname Admin --email admin@superset.com --password admin

<!-- khởi tạo init superset -->

docker exec -it superset superset init
