MAKEFLAGS += --always-make


start:
	export DOCKER_HOST_IP=$(hostname -I | awk '{print $1}')
	docker-compose up -d

stop:
	docker-compose down

cluster-start:
	mkdir -p cluster/node{1,2,3,4,5,6}/data
	docker compose -f docker-compose.cluster.yml up -d

cluster-stop:
	docker compose -f docker-compose.cluster.yml down

cluster-clean:
	docker compose -f docker-compose.cluster.yml down -v
	rm -rf cluster/node{1,2,3,4,5,6}/data/*

sentinel-start:
	mkdir -p sentinel/master/data sentinel/replica{1,2}/data sentinel/sentinel{1,2,3}
	docker compose -f docker-compose.sentinel.yml up -d

sentinel-stop:
	docker compose -f docker-compose.sentinel.yml down

sentinel-clean:
	docker compose -f docker-compose.sentinel.yml down -v
	rm -rf sentinel/master/data/* sentinel/replica{1,2}/data/* sentinel/sentinel{1,2,3}/*

all-start:
	docker-compose up -d
	docker compose -f docker-compose.cluster.yml up -d
	docker compose -f docker-compose.sentinel.yml up -d

all-stop:
	docker-compose down
	docker compose -f docker-compose.cluster.yml down
	docker compose -f docker-compose.sentinel.yml down

all-clean:
	docker-compose down -v
	docker compose -f docker-compose.cluster.yml down -v
	docker compose -f docker-compose.sentinel.yml down -v
	rm -rf cache_redis/*
	rm -rf cluster/node{1,2,3,4,5,6}/data/*
	rm -rf sentinel/master/data/* sentinel/replica{1,2}/data/* sentinel/sentinel{1,2,3}/*
