AISXMLFILES:=${wildcard *.xml}

EXP:=../expandais.py

PP=PYTHONPATH=..:../..

%.html: %.xml
	${EXP} -i $< -o $<.expanded
	xsltproc ../ais.xsl $<.expanded > $@
	rm $<.expanded

AISHTMLFILES := ${AISXMLFILES:.xml=.html}

default: ${AISHTMLFILES}

html: ${AISHTMLFILES}

clean:
	rm -f *expanded*.{xml,html}
	-rm -f *.pyc
	-rm -f out-ais.xml
	-rm -f ?.html
	-rm -f a.out foo* blah*
	rm -rf html
	rm -f *_exp.xml *.html
