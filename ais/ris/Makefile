
AISXMLFILES:=${wildcard *.xml}

GEN:=../../scripts/aisxmlbinmsg2py.py
EXP:=../expandais.py

PP=PYTHONPATH=..:../..


%.html: %.xml
	${EXP} -i $< -o $<.expanded
	xsltproc ../ais.xsl $<.expanded > $@
	rm $<.expanded

AISPYFILES := ${AISXMLFILES:.xml=.py}
AISHTMLFILES := ${AISXMLFILES:.xml=.html}


default: ${AISPYFILES} ${AISHTMLFILES}

py: ${AISPYFILES}
html: ${AISHTMLFILES}

clean:
	rm -f *expanded*.{xml,html}
	-rm -f *.pyc
	-rm -f out-ais.xml
	-rm -f ?.html
	-rm -f a.out foo* blah*
	rm -rf html
	rm -f *_exp.xml *.html
