#!/usr/bin/make -f
NAMESPACE:=matyasosg


echo:=@echo
echotbl:=@printf "%-20s %s\n"

SHELL:=bash

.PHONY: help
help:
	$(echo) "Targets:"
	$(echo)
	$(echotbl) "help" "This text"
	$(echotbl) "list" "List all targets"
	$(echotbl) "image" "Build the submit host image"
	$(echotbl) "run" "Run a container"
	$(echo)
	$(echo) "Variables:"
	$(echo)
	$(echotbl) "NAMESPACE" "The Docker namespace (username) to tag images under [$(NAMESPACE)]"



.PHONY: image
image: image/* image/condor/*
	docker build -t $(NAMESPACE)/$@ image


.PHONY: run
run:
	-docker run --rm --name $(NAMESPACE)_submit $(NAMESPACE)/submit


# List all the makefile targets
# https://stackoverflow.com/a/26339924
.PHONY: list
list:
	@$(MAKE) -pRrq -f $(lastword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$'

