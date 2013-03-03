# GNU -*- makefile -*- for emacs
# Created by Kurt Schwehr (schwehr _at_ ccom.unh.edu)

SHELL:=/bin/bash
PKG:=noaadata
VERSION := ${shell cat noaadata/__init__.py | grep version | cut -d\' -f2}

default:
	@echo
	@echo "  *** Welcome to ${PKG}-py ${VERSION} ***"
	@echo
	@echo "         NOAA Co-ops data and AIS"
	@echo "              Python Library"
	@echo
	@echo "  docs      -  Build documentation (html)"
	@echo "  help      -  Open the documentation"
	@echo
	@echo "  clean  -  Remove temporary files"
	@echo "  test   -  Run the unittests"
	@echo "  check  -  Look for rough spots"
	@echo "  sdist  -  Build a source distribution tar ball"
	@echo "  variables  - Print key make variables"
	@echo
	@echo "  NOTE: ccom offers no support without a prior agreement"
	@echo
	@echo
	@echo " WARNING: this Makefile is for the maintainer.  See INSTALL"

#	@echo "  trac      -  Open the TRAC wiki and bug system"
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

#.PHONY: trac
#trac:
#	@echo "These only work inside of ccom.  sorry..."
#	open https://albatross.ccom.nh/GeoZui4D/wiki/DevArea/${PKG}Info
#	open https://albatross.ccom.nh/GeoZui4D

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
	@echo "FIX enable: cd scripts && make clean"

.PHONY: real-clean
real-clean: clean
	rm -f MANIFEST  [0-9]*.html *.info
	rm -rf build dist
	rm -rf html*
	rm -f 8*.{ais,txt,html} current.ais all.ais


# FIX: doctest or unittest first?
.PHONY: test tests
tests: test
test:
	cd test && make test
	@echo
	@echo " === ${PKG} module doc tests ==="
	@echo
	cd ${PKG} && make test
	@echo
	@echo "All tests passed! (Accept those that are known to fail)"


# Look for rough spots
.PHONY: check
check:
	@grep -n FIX Makefile */Makefile | grep -v grep
	@grep -n FIX */*.py 
	@echo
	pychecker ${PKG}
	find . -name \*.py | xargs egrep '@(todo|bug)'
#	pylint
#	pychecker ${PKG} scripts


# Why does MANIFEST get correctly rebuilt?
sdist: test 
	@echo
	@echo Building a source distribution...
	@echo
	(cd ais;make)
	(cd ais/sls;make)
	(cd ais/ris;make)
	-find . -name \*.pyc | xargs rm
	rm -f MANIFEST
	./setup.py sdist --formats=bztar


#	make docs


sdist-minimal:
	find . -name .DS_Store | xargs rm 
	./setup.py sdist --formats=bztar

sdist-notests: docs
	@echo
	@echo Building a source distribution...
	@echo
	./setup.py sdist --formats=bztar



.PHONY: docs
docs:
	rm -rf man html-scripts html-test html-man
	@echo skip "rm -f ${PKG}/*.pyc"
	echo "skipping (cd ais && make waterlevel.py && make waterlevel.html)"
	echo "skipping graphing until font issue fixed epydoc -v ${PKG} --graph=all ais/*.py"
	PYTHONPATH=`pwd`:`pwd`/ais epydoc -v ${PKG} ais/*.py aisutils ais/*/*.py

	@echo "FIX enable: cd scripts && make man"
	@echo "FIX enable: cd scripts && make docs"
	@echo "skipping cd test && make docs"
	@echo "FIX enable: mv scripts/man ."
	@echo  "mkdir html-man"
	@echo "FIX enable: mv man/*.html html-man"
	@echo "FIX enable: mv scripts/html html-scripts"
	@echo "FIX enable: mv test/html html-test"


.PHONY: test-docs
test-docs:
	rm -rf html-test
	cd test && PYTHONPATH=.. epydoc -v -o html-test *.py
	@echo "FIX enable: mv test/html-test ."

##############################
# Fink package file
DIST_TAR=dist/${PKG}-py-${VERSION}.tar.bz2
fink: ${PKG}-py.info
info: ${PKG}-py.info
.PHONY: ${PKG}-py.info
${PKG}-py.info: ${PKG}-py.info.in Makefile #${DIST_TAR}
	perl -p -e "s/\@VERSION\@/${VERSION}/g" $< > fink.tmp
	MD5=`md5 dist/${PKG}-py-${VERSION}.tar.bz2| awk '{print $$4}'` \
	      && perl -p -e "s/\@MD5\@/$$MD5/g" fink.tmp > $@
	rm -f fink.tmp

${DIST_TAR}: sdist

.PHONY: install-fink
install-fink: ${PKG}-py.info ${DIST_TAR} dist/${PKG}-py-${VERSION}.tar.bz2
	cp ${PKG}-py.info /sw/fink/10.4-transitional/ccom/main/finkinfo/sci/
	cp ${DIST_TAR} /sw/src
	fink rebuild ${PKG}-py24
#	fink install ${PKG}-py24

.PHONY: tags etags
tags: etags
etags:
	etags ${PKG}/*.py

upload:
	scp ${PKG}-py.info ${DIST_TAR} vislab-ccom:www/software/noaadata/downloads/
	scp ChangeLog.html vislab-ccom:www/software/noaadata/

# Does not work for Darwin/Fink...
# Create a deb for ubuntu
#DEB_ARCH:=${shell echo `dpkg-architecture -qDEB_HOST_ARCH`}
deb:
	rm -rf build
	rm -rf python-noaadata-${VERSION}
	mkdir -p python-noaadata-${VERSION}/DEBIAN
	perl -p -e "s|\@VERSION\@|${VERSION}|" < control.in > python-noaadata-${VERSION}/DEBIAN/control
	./setup.py install --root=python-noaadata-${VERSION}
	dpkg-deb -b python-noaadata-${VERSION} python-noaadata-${VERSION}.deb
#perl -pi -e "s|@ARCHITECTURE@|${DEB_ARCH}|" python-noaadata-${VERSION}/DEBIAN/control

svn-branch:
	svn cp https://cowfish.unh.edu/projects/schwehr/trunk/src/noaadata https://cowfish.unh.edu/projects/schwehr/branches/noaadata/noaadata-${VERSION}

register:
	./setup.py register
