MAKEFLAGS += --always-make


start:
	export DOCKER_HOST_IP=$(hostname -I | awk '{print $1}')
	docker-compose up -d

stop:
	docker-compose down