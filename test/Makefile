######################################################################
# $Id$
# 
# AUTHOR: Kurt Schwehr
# COPYRIGHT: 2006 University of New Hampshire, Center for Coastal and Ocean Mapping
######################################################################

SHELL:=bash

help:
	@echo
	@echo " Welcome to the AIS python module test central:"
	@echo 

	@echo "  make test      - run all tests"

	@echo "e.g."
	@echo "  "
	@echo "  make test TEST_VERBOSITY=--noisy"
	@echo "  "
	@echo "  "


TEST_VERBOSITY:=-v
.PHONY: test
# FIX: this should be a for script in test_*.py
test:
	@echo "FIX: enable me"

#	export PYTHONPATH=.. && for file in test_*.py; do echo; echo "Running $$file";echo;\
#	                 ./$$file --test ${TEST_VERBOSITY}; done
#	-./tests.bash
#	@echo
#	@echo "All tests passed. (FIX: make tests.bash work)"


docs:
	PYTHONPATH=.. epydoc -v test*.py

clean:
	rm -f *.pyc
