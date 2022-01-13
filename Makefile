service:=noterest-auth
project:=noterest

.PHONY: start
start:
	docker-compose -p ${project} up -d

.PHONY: stop
stop:
	docker-compose -p ${project} down

.PHONY: restart
restart: stop start

.PHONY: ps
ps:
	docker-compose -p ${project} ps

.PHONY: logs
logs:
	docker-compose -p ${project} logs -f

.PHONY: logs-app
logs-app:
	docker-compose -p ${project} logs -f ${service}

.PHONY: lock
stop:
	pipenv lock -r > requirements.txt

.PHONY: build
build:
	docker-compose -p ${project} build --no-cache