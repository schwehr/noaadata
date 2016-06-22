SHELL := /bin/bash
PKG := noaadata
VERSION := ${shell cat noaadata/__init__.py | grep version | cut -d\' -f2}

default:
	@echo
	@echo "  *** Welcome to ${PKG}-py ${VERSION} ***"
	@echo
	@echo "         NOAA Co-ops and AIS"
	@echo "            Python Library"
	@echo
	@echo "  clean  -  Remove temporary files"
	@echo "  test   -  Run the unittests"
	@echo "  check  -  Look for rough spots"
	@echo "  sdist  -  Build a source distribution tar ball"
	@echo
	@echo " WARNING: this Makefile is for the maintainer.  See INSTALL"

#	@echo "  wikipedia -  Open the wikipedia entry on ${PKG}"

#PYFILES_ALL := ${shell ls *.py}
#PYFILES := ${shell ls *.py | grep -v version}

.PHONY: variables
variables:
	@echo ${PKG}-py version: ${VERSION}
	@echo PYTHONPATH $$PYTHONPATH
	@echo SHELL ${SHELL}
#	@echo PYFILES_ALL ${PYFILES_ALL}
#	@echo PYFILES ${PYFILES}

.PHONY: wikipedia
wikipedia:
	open http://en.wikipedia.org/wiki/Automatic_Identification_System

.PHONY: help
help:
	@echo This only works on Mac OSX
	open html/index.html

.PHONY: clean
clean:
	rm -f ${PKG}-py.info MANIFEST
	find . -name \*.pyc | xargs rm -f
	find . -name \*~ | xargs rm -f
	find . -name .DS_Store | xargs rm -f
	cd ${PKG} && make clean

.PHONY: real-clean
real-clean: clean
	rm -f MANIFEST  [0-9]*.html *.info
	rm -rf build dist
	rm -rf html*
	rm -f 8*.{ais,txt,html} current.ais all.ais
	find . -name .DS_Store | xargs rm 


.PHONY: test tests
test:
	cd test && make test
	cd ${PKG} && make test
	@echo
	@echo "All tests passed!  (Except those that are known to fail.)"


.PHONY: check
check:
	@grep -n FIX Makefile */Makefile | grep -v grep
	@grep -n FIX */*.py 
	@echo
	pychecker ${PKG}
	find . -name \*.py | xargs egrep '@(todo|bug)'
#	pylint
#	pychecker ${PKG} scripts

build: test
	@echo
	@echo Building locally...
	@echo
	(cd ais;make)
	(cd ais/sls;make)
	(cd ais/ris;make)
	-find . -name \*.pyc | xargs rm
	rm -f MANIFEST
	./setup.py build

install-home: build
	@echo
	@echo Installing in home area...
	@echo
	./setup.py install --prefix ${HOME}

sdist: test 
	@echo
	@echo Building a source distribution...
	@echo
	(cd ais; make)
	(cd ais/sls; make)
	(cd ais/ris; make)
	-find . -name \*.pyc | xargs rm
	rm -f MANIFEST
	./setup.py sdist --formats=bztar

DIST_TAR=dist/${PKG}-py-${VERSION}.tar.bz2
fink: ${PKG}-py.info
.PHONY: ${PKG}-py.info
${PKG}-py.info: ${PKG}-py.info.in Makefile #${DIST_TAR}
	perl -p -e "s/\@VERSION\@/${VERSION}/g" $< > fink.tmp
	MD5=`md5 dist/${PKG}-py-${VERSION}.tar.bz2| awk '{print $$4}'` \
	      && perl -p -e "s/\@MD5\@/$$MD5/g" fink.tmp > $@
	rm -f fink.tmp

.PHONY: install-fink
install-fink: ${PKG}-py.info ${DIST_TAR} dist/${PKG}-py-${VERSION}.tar.bz2
	cp ${PKG}-py.info /sw/fink/10.10/local/main/finkinfo/libs/pythonmods/
	cp ${DIST_TAR} /sw/src
	fink rebuild ${PKG}-py27

upload:
	scp ${PKG}-py.info ${DIST_TAR} vislab-ccom:www/software/noaadata/downloads/
	scp ChangeLog.html vislab-ccom:www/software/noaadata/

register:
	./setup.py register

upload-pypi:
	python setup.py sdist --formats=bztar upload
