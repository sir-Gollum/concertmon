APP_CONTAINER_NAME   ?= sg-concerts-monitor

.PHONY: help h
.DEFAULT_GOAL := help

help:
	@echo "Usage: ${YELLOW}make${RESET} ${GREEN}<target(s)>${RESET}"
	@echo Targets:
	@awk '/^[a-zA-Z\/\-\_0-9]+:/ { \
		helpMessage = match(lastLine, /^## (.*)/); \
		if (helpMessage) { \
			helpCommand = substr($$1, 0, index($$1, ":")-1); \
			helpMessage = substr(lastLine, RSTART + 3, RLENGTH); \
			printf "  %-20s %s\n", helpCommand, helpMessage; \
		} \
	} \
	{ lastLine = $$0 }' $(MAKEFILE_LIST)

.PHONY: image
## Make a docker image and tag it
image:
	docker build -t ${APP_CONTAINER_NAME}:latest .


.PHONY: compose
## Run the monitor in docker, using compose for env vars
compose:
	docker-compose up
