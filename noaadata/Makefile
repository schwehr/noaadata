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
	@echo "FIX: enable test"

#	@echo "FIX: this is not passing back failures"
#	export PYTHONPATH=.. && for file in [a-z]*.py; do \
#	                 ./$$file --test ${TEST_VERBOSITY}; done
#	@echo
#	@echo "All tests passed. (FIX: make tests.bash work)"

.PHONY: check
check:
	pychecker --stdlib -T *.py
#	pychecker --stdlib -T msg.py


.PHONY: check
check-fix:
	@grep -n -H FIX Makefile | grep -v grep
	@grep -n FIX *.py *.{xml,xsd}
	@egrep -n '\@bug|\@todo:' *.py *.{xml,xsd}


# FIX: make these depend on which are installed
# FIX: create a python program to validate additional info/logic in the xml
# FIX: validate the XML Schema against the schema schema
#.PHONY: xml-validate
#xml-validate:
#	xmllint --noout ais.xsd
#	xmllint --noout ais.xml
#	xml val -e ais.xml
#	xml val -e ais.xsd
#	xmllint --noout --schema ais.xsd ais.xml
#	xsv ais.xml ais.xsd
#	xml val -e --xsd ais.xsd ais.xml
