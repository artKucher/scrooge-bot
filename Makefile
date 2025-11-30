CONTAINER_NAME = scrooge-bot

build:
	docker compose -f compose.yml build
up:
	docker compose -f compose.yml up -d --remove-orphans $(CONTAINER_NAME)
logs:
	docker compose -f compose.yml logs -f $(CONTAINER_NAME)
down:
	docker compose -f compose.yml down
restart:
	docker compose -f compose.yml restart $(CONTAINER_NAME)
exec:
	docker compose -f compose.yml exec $(CONTAINER_NAME) /bin/bash

pre-commit:
	docker compose -f compose.yml run --rm $(CONTAINER_NAME) bash -c 'PRE_COMMIT_HOME=.precomcache pre-commit run --all-files'