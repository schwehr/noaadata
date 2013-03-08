# -*- makefile -*-
# Simple makefile so I don't have to remember how to run this stuff
GEN:=../scripts/aisxmlbinmsg2py.py

AISXMLFILES:=
AISXMLFILES += ais_msg_1.xml # position, Class A
AISXMLFILES += ais_msg_2.xml # position, Class A
AISXMLFILES += ais_msg_3.xml # position, Class A
AISXMLFILES += ais_msg_4.xml # base station report
AISXMLFILES += ais_msg_5.xml # ship and cargo
AISXMLFILES += ais_msg_6.xml # Addressed binary message
AISXMLFILES += ais_msg_7.xml # ACK for address binary message
AISXMLFILES += ais_msg_8.xml # binary message
AISXMLFILES += ais_msg_9.xml # SAR position
AISXMLFILES += ais_msg_10.xml # utcquery
AISXMLFILES += ais_msg_11.xml # 
AISXMLFILES += ais_msg_12.xml # asrm
#AISXMLFILES += ais_msg_13.xml # 
AISXMLFILES += ais_msg_14.xml # srbm
AISXMLFILES += ais_msg_15.xml # Interrogation
#AISXMLFILES += ais_msg_16.xml # 
AISXMLFILES += ais_msg_17.xml # A - GNSS differential corrections
AISXMLFILES += ais_msg_18.xml # Class B position report
AISXMLFILES += ais_msg_19.xml # Class B extended position and ship type report
AISXMLFILES += ais_msg_20.xml # Data Link management
AISXMLFILES += ais_msg_21.xml # AidsToNavReport
AISXMLFILES += ais_msg_22.xml
AISXMLFILES += ais_msg_23.xml # GroupAssignmentCommand
#AISXMLFILES += ais_msg_24.xml # StaticDataReport
#AISXMLFILES += ais_msg_25.xml # SingleSlotBinaryMessage - addressed or broadcast
#AISXMLFILES += ais_msg_26.xml # Multi slot binary message with comm state

# FIX: move to an IMO or IALA subdir
AISXMLFILES += imo_001_11.xml
AISXMLFILES += imo_001_13.xml
AISXMLFILES += imo_001_14.xml

# Move to a prototypes subdir
AISXMLFILES += waterlevel.xml
AISXMLFILES += waterlevel2.xml
AISXMLFILES += whalenotice.xml
AISXMLFILES += whalenotice1.xml
AISXMLFILES += whalenotice2.xml
AISXMLFILES += timed_circular_notice.xml # Whale notice for J. Arroyo

AISXMLFILES += allaistypes.xml

AISPYFILES := ${AISXMLFILES:.xml=.py} ais_msg_2_handcoded.py
AISHTMLFILES := ${AISXMLFILES:.xml=.html}

######################################################################
# Rules
######################################################################

default: ${AISHTMLFILES} ${AISPYFILES}

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
	rm -f ais_msg_[0-9].py
	rm -f ais_msg_[0-9][0-9].py

docs:
	epydoc -v *.py
	epydoc --check *.py


######################################################################
# Transformations
######################################################################

# Messages 2 and 3 are basically the same as 1
ais_msg_2.xml: ais_msg_1.xml
	perl -p -e 's|aismsgnum\=\"1\"|aismsgnum\=\"2\"|' $<  | perl -p -e 's|required\>1\<|required\>2\<|' > $@
ais_msg_3.xml: ais_msg_1.xml
	perl -p -e 's|aismsgnum\=\"1\"|aismsgnum\=\"3\"|' $<  | perl -p -e 's|required\>1\<|required\>3\<|' > $@

ais_msg_11.xml: ais_msg_4.xml
	perl -p -e 's|aismsgnum\=\"4\"|aismsgnum\=\"11\"|' $<  | perl -p -e 's|required\>4\<|required\>11\<|' > $@

ais_msg_2_handcoded.py:
	ln -s ais_msg_1_handcoded.py ais_msg_2_handcoded.py

%.py: %.xml ${GEN}
	xmllint --noout $< 
	./expandais.py -i $< -o $<.expanded
	${GEN} -i $<.expanded -o $@
	rm -f $<.expanded
	@echo FIX: remove the dash for pychecker and make all pass
	echo skipping -pychecker -q $@
	./$@ --verbose --unit-test

%.html: %.xml
	./expandais.py -i $< -o $<.expanded
	xsltproc ais.xsl $<.expanded > $@
	rm $<.expanded

.PHONY: test
test:
	./binary.py --test