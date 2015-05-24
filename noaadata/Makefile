SHELL := /bin/bash

help:
	@echo
	@echo " Welcome to the AIS python module:"
	@echo 
	@echo "  make clean        - Clean up all the moose droppings"
	@echo "  make real-clean   - Get out the extra scrub brush"
	@echo
	@echo "  make test         - Get some exercise"
	@echo "  make check        - Look for trouble spots"
	@echo "  make xml-validate - Cross check the XML and XML Schema"

.PHONY: clean
clean:
	rm -f *.pyc

.PHONY: real-clean
real-clean: clean
	rm -rf html

full-test: check xml-validate test

TEST_VERBOSITY:=-v
.PHONY: test
test:
	@echo "TODO(schwehr): enable test"

.PHONY: check
check:
	pychecker --stdlib -T *.py

.PHONY: check
check-fix:
	@grep -n -H FIX Makefile | grep -v grep
	@grep -n FIX *.py *.{xml,xsd}
	@egrep -n 'TODO' *.py
