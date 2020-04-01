#!/usr/bin/make -f
NAMESPACE:=opensciencegrid


echo:=@echo
echotbl:=@printf "%-20s %s\n"

SHELL:=bash

.PHONY: help
help:
	$(echo) "Targets:"
	$(echo)
	$(echotbl) "help" "This text"
	$(echotbl) "build" "Build the submit host image"
	$(echotbl) "run" "Run a container"
	$(echotbl) "clean" "Delete the image"
	$(echo)
	$(echo) "Variables:"
	$(echo)
	$(echotbl) "NAMESPACE" "The Docker namespace (username) to tag images under [$(NAMESPACE)]"



.PHONY: build
build:
	docker build -t $(NAMESPACE)/submit-host .


.PHONY: run
run:
	-mkdir -p config/
	-mkdir -p secrets/
	-docker run --rm -v config:/root/config:ro -v secrets:/root/secrets:ro --name $(NAMESPACE)_submit_host $(NAMESPACE)/submit-host


.PHONY: clean
clean:
	-docker rmi $(NAMESPACE)/submit-host


