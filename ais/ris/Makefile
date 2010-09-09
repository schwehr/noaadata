
# Skip strutures... no other s*.xml files
AISXMLFILES:=${wildcard *.xml}

GEN:=../../scripts/aisxmlbinmsg2py.py
EXP:=../expandais.py

PP=PYTHONPATH=..:../..


%.py: %.xml ${GEN}
	xmllint --noout $< 
	${EXP} -i $< -o $<.expanded
	${GEN} -i $<.expanded -o $@
	rm -f $<.expanded
	@echo FIX: remove the dash for pychecker and make all pass
	echo skipping -pychecker -q $@
	${PP} ./$@ --verbose --unit-test

%.html: %.xml
	${EXP} -i $< -o $<.expanded
	xsltproc ../ais.xsl $<.expanded > $@
	rm $<.expanded

AISPYFILES := ${AISXMLFILES:.xml=.py}
AISHTMLFILES := ${AISXMLFILES:.xml=.html}

######################################################################
# Rules
######################################################################


default: ${AISPYFILES} ${AISHTMLFILES}

py: ${AISPYFILES}
html: ${AISHTMLFILES}

#view-html: 
#	open $<
clean:
	rm -f *expanded*.{xml,html}
	-rm -f *.pyc
	-rm -f out-ais.xml
	-rm -f ?.html
	-rm -f a.out foo* blah*
	rm -rf html
	rm -f waterlevel.py
	rm -f *_exp.xml *.html
	rm -f ais_msg_*.py
	rm -f sls_*.py

docs:
	epydoc -v *.py
	epydoc --check *.py
