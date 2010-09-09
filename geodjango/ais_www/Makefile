# Author: Kurt Schwehr
# Contact: http://schwehr.org
# Copyright: 2008
# License: GPL

default:
	@echo "         djano web interface to the noaadata AIS database"
	@echo "         ------------------------------------------------"
	@echo
	@echo "  open            - on mac, open a web browser to the web app"
	@echo "  shell           - start a django ipython shell"
	@echo "  start           - run the server"
	@echo "  start-all-hosts - Attach to 0.0.0.0 so not just localhost"
	@echo "  validate        - make sure the system is okay"
	@echo "  real-clean      - remove all pyc files"
	@echo "  syncdb          - Create/modify the database"

# FIX: make a start in background
open:
	open http://localhost:8000

shell:
	ipython manage.py shell

start:
	python manage.py runserver

start-all-hosts:
	python manage.py runserver 0.0.0.0

validate:
	python manage.py validate

real-clean:
	find . -name \*.pyc | xargs rm

syncdb:
	python manage.py syncdb

rebuilddb:
	dropdb ais
	createdb ais
	psql -f /sw/share/doc/postgis83/lwpostgis.sql -d ais
	psql -f /sw/share/doc/postgis83/spatial_ref_sys.sql -d ais
	python manage.py syncdb
	psql ais < define_ais/dac.sql 
	psql ais < define_ais/preload.sql 
	echo SKIPPING ais_build_postgis.py --with-create small.12345 

# ######################################################################
# .PHONY: check
# check:
#         @grep -n -H FIX Makefile | grep -v grep
#         @egrep -n 'FIX|\@bug|\@todo:' *.py 

# ######################################################################
# .PHONY: lint
# lint:
#         pychecker --moduledoc --classdoc --funcdoc *.py
#         pylint --max-line-length=200
#         epydoc -v --check *.py

# ######################################################################
# .PHONY: doc html docs
# doc: docs
# html: docs

# docs:
#         epydoc -v *.py
#         epydoc -v --check *.py

# # Mac OSX only:
# open-docs: docs
#         open html/index.html
