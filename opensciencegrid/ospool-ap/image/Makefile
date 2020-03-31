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
	$(echotbl) "submit" "Submit host image"
	$(echo)
	$(echo) "Variables:"
	$(echo)
	$(echotbl) "NAMESPACE" "The Docker namespace (username) to tag images under [$(NAMESPACE)]"



.PHONY: submit
submit: Dockerfile condor/* start.sh supervisord.conf update-config update-secrets
	docker build -t $(NAMESPACE)/$@ .


# List all the makefile targets
# https://stackoverflow.com/a/26339924
.PHONY: list
list:
	@$(MAKE) -pRrq -f $(lastword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$'

