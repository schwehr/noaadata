#!/usr/bin/env python
__version__ = '$Revision: 6044 $'.split()[1]
__date__ = '$Date: 2007-04-23 15:43:21 -0400 (Mon, 23 Apr 2007) $'.split()[1]
__author__ = 'Kurt Schwehr'

__doc__='''
Handling code for noaa stations data. 

The Web Services Description Language (WSDL) definition for the
query/response from the NOAA Axis server.

@see: U{NOAA Axis page<http://opendap.co-ops.nos.noaa.gov/axis/>}
@see: U{WSDL<http://opendap.co-ops.nos.noaa.gov/axis/services/ActiveStations?wsdl>}
@see: U{SOAP XML request<http://opendap.co-ops.nos.noaa.gov/axis/webservices/activestations/samples/request.xml>}
@see: U{SOAP XML response<http://opendap.co-ops.nos.noaa.gov/axis/webservices/activestations/samples/response.xml>}
@see: U{Java SOAP code<http://opendap.co-ops.nos.noaa.gov/axis/webservices/activestations/samples/client.html>}
@see: U{Web interface<http://opendap.co-ops.nos.noaa.gov/axis/webservices/activestations/index.jsp>}
@see: U{XPathTutorial<http://www.zvon.org/xxl/XPathTutorial/General/examples.html>}
@see: U{python lxml<http://codespeak.net/lxml/>}

@author: U{Kurt Schwehr<http://schwehr.org/>}
@author: '''+__author__+'''
@version: ''' + __version__ +'''
@license: GPL v2
@copyright: (C) 2006 Kurt Schwehr
@var __date__: Date of last svn commit
@undocumented: __version__ __author__ __doc__ parser success 

'''

import sys, httplib

#import os, shutil
#import time
#import socket
#import thread
#import select
#import tty,termios
#import calendar

def getActiveStationsSoappy(debug=False):
    '''
    Use the old SOAPpy interface to get the stations

    Here is the results for one station:

    print response.station[1]

    <SOAPpy.Types.structType station at 20681072>: {'parameter': ['', ''], 'metadata': <SOAPpy.Types.structType metadata at 20683272>: {'date_established': '1954-11-24', 'location': <SOAPpy.Types.structType location at 20635240>: {'lat': '21 57.3 N', 'state': 'HI', 'long': '159 21.4 W'}}}



    >>> response = getActiveStationsSoappy()
    >>> str(response.station[1].metadata.location.lat)
    '21 57.3 N'
    >>> str(response.station[1].metadata.location.long)
    '159 21.4 W'
    >>> str(response.station[1].metadata.location.state)
    'HI'

    @param debug: set to true to see more information about the transaction
    @return: a large typestring
    '''
    from SOAPpy import SOAPProxy
    url = 'http://opendap.co-ops.nos.noaa.gov/axis/services/ActiveStations'
    namespace='urn:ActiveStations' # This really can be anything.  It is ignored
    server = SOAPProxy(url,namespace)
    if debug: server.config.debug=1
    response = server.getActiveStations()
    return response


def stripNameSpaces(xmlString):
    '''
    Nuke the xmlns sections.  They cause lxml to make strange output.
    
    @bug: would be better to use regex to nuke the xmlns.  Currently very brittle.  FIX!
    '''
    xml = xmlString
    tail = 'XMLSchema-instance"'
    xml2=xml[:xml.find('xmlns')]+xml[xml.find(tail)+len(tail):]
    tail = 'wsdl"'
    xml3 = xml2[:xml2.find('xmlns')]+xml2[xml2.find(tail)+len(tail):]
    return xml3

def lonlatText2decimal(lonlatString):
    '''
    Convert positions as found in the xml into decimal lon/lat

    >>> lonlatText2decimal('21 57.3 N')
    21.954999999999998
    >>> lonlatText2decimal('159 21.4 W')
    -159.35666666666665
    '''

    fields = lonlatString.split()
    val = float(fields[0]) + float(fields[1]) / 60.
    if fields[2]=='S' or fields[2]=='W':
	val = -val
    return val

######################################################################
# Station
######################################################################

class Station:
    '''
    A single station
    '''
    def __init__(self,et):
	'''
	Create a station object from an element tree
	@param et: Element Tree for one station
	'''

	station = et
	fields = {}
	fields['name'] = station.attrib['name']
	fields['ID'] = station.attrib['ID']
	fields['lonStr'] = station.xpath('metadata/location/long')[0].text
	fields['latStr'] = station.xpath('metadata/location/lat')[0].text
	fields['state'] = station.xpath('metadata/location/state')[0].text
	# date_established
	parameters = []
	for param in station.xpath('parameter'):
	    paramDict={}

	    paramDict['DCP'] = param.attrib['DCP']
	    paramDict['name'] = param.attrib['name']
	    paramDict['sensorID'] = param.attrib['sensorID']
	    
	    if '0'==param.attrib['status']: paramDict['status']=False
	    else: paramDict['status']=True
	    
	    parameters.append(paramDict)

	self.fields = fields
	self.parameters = parameters


    def getName(self):
	return self.fields['name']
    def getID(self):
	return self.fields['ID']

    def getLon(self):
	lonFields = self.fields['lonStr'].split()
	lon = float(lonFields[0]) + float(lonFields[1])/60.
	if lonFields[2] == 'W': lon = -lon
	return lon

    def getLat(self):
	latFields = self.fields['latStr'].split()
	lat = float(latFields[0]) + float(latFields[1])/60.
	if latFields[2] == 'S': lat = -lat
	return lat



    def hasSensor(self,name="Water Level", status=True, sensorID=None,DCP=None):
	'''
	Return true if the station has that particular sensor type
	'''

#	for p in self.parameters:
#	    if name and p['name']==name: return True
	for p in self.parameters:
	    # FIX: make this more general 
	    if name     and p['name']    !=name:     continue
	    if status   and p['status']  !=status:   continue
	    if sensorID and p['sensorID']!=sensorID: continue
	    if DCP      and p['DCP']     !=DCP:      continue
	    return True

	return False




    def printMe(self):
	f,params = self.fields,self.parameters
	print f['name'],':',f
	for p in params:
	    print '    ',p

######################################################################
# ActiveStations class
######################################################################

class ActiveStations:
    '''
    Custom wrapper around the ActiveStations that allows the system to
    fail back to a precaptured list of stations and instruments
    '''

    SERVER_ADDR = "opendap.co-ops.nos.noaa.gov"
    '''Host name for the NOAA Axis soap server'''
    SERVER_PORT = 80
    '''Axis sits on the normal Apache http port 80'''
    NS = "http://opendap.co-ops.nos.noaa.gov/axis/services/ActiveStations"
    '''The exact location of the soap call.  This may be ignored.'''


    def __init__(self,allowCache=True, forceCache=False):
	'''
	Fetch the stations from the NOAA web services or a cache.

	@param allowCache: if true, the class will fallback on a
	precaptured list of stations.
	'''
	xml=None
	if forceCache:
	    #print '__file__',__file__
	    # FIX: is there a __path__ like thing that I can use like ais-py/ais/__init__.py?
	    # FIX: this will not work on Windows!!!
	    localDir = __file__[:__file__.rfind('/')+1]
	    xml = open(localDir+'stations-soap.xml').read()
	else:
	    if allowCache:
		try:
		    xml = self.getStationXmlFromSoap()
		except:
		    xml = open('stations-soap.xml').read()
	    else:
		xml = self.getStationXmlFromSoap()

	xml = stripNameSpaces(xml)

	from lxml import etree
	from StringIO import StringIO

	# Dig past the top wrappers.  FIX: use xpath instead to get the ActiveStations node
	self.stationsET = etree.parse(StringIO(xml)).getroot()[0][0][0]
	
	#print stationsET.tag
	#print 'stationsET', [ el.tag for el in stationsET ]
	
    def getStationsNameNumb(self):
	'''
	Get a nice lookup table of station ID to name translations
	'''
	stationsDict={}
#	for loc in self.stationsET.xpath('station/metadata/location'):
#	    print [ el.tag for el in loc ]
	for station in self.stationsET.xpath('station'):
	    stationsDict[station.attrib['ID']] = station.attrib['name']
	return stationsDict

    def getStationsInBBox(self, lowerleft, upperright):
	'''
	Specify a bounding box and get the points in that region
	'''
	stations=[]
	# FIX: assert the bounding box is sane
	for station in self.stationsET.xpath('station'):
	    
	    lonStr = station.xpath('metadata/location/long')[0].text
	    latStr = station.xpath('metadata/location/lat')[0].text
	    #print 'pos strings',lonStr, latStr
	    try:
		lon = lonlatText2decimal(lonStr)
		lat = lonlatText2decimal(latStr)
		#print lon,lat, 'is it in ',lowerleft,upperright
		if lon >= lowerleft[0] and lon <= upperright[0] and lat >= lowerleft[1] and lat <= upperright[1]:
		    #print 'adding station',station.attrib['ID']
		    stations.append(station.attrib['ID'])
	    except IndexError:
		# Must have been empty
		pass

	return stations


    def getStation(self,ID):
	'''
	Return a station class object
	'''
	xpathExpr = "station[@ID='"+str(ID)+"']"
	#print xpathExpr
	stationTree = self.stationsET.xpath(xpathExpr)[0]
	station = Station(stationTree)
	return station


    def getStationXmlFromSoap(self):
	'''
	Speak soap to the NOAA axis server and return the SOAP xml.
	The xmlns make lxml do weird things.

	'''

	BODY_TEMPLATE = '''<SOAP-ENV:Envelope
  xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
  xmlns:s="'''+NS+'''"
  xmlns:xsi="http://www.w3.org/1999/XMLSchema-instance"
  xmlns:xsd="http://www.w3.org/1999/XMLSchema"
  SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
  <SOAP-ENV:Body>
    <s:getActiveStations>
    </s:getActiveStations>
  </SOAP-ENV:Body>
</SOAP-ENV:Envelope>'''

	body = BODY_TEMPLATE
	blen = len(body)
	requestor = httplib.HTTP(SERVER_ADDR, SERVER_PORT)
	requestor.putrequest("POST", "/axis/services/ActiveStations")
	requestor.putheader("Host", SERVER_ADDR)
	requestor.putheader("Content-Type", 'text/plain; charset="utf-8"')
	requestor.putheader("Content-Length", str(blen))
	requestor.putheader("SOAPAction", NS)
	requestor.endheaders()
	requestor.send(body)
	(status_code, message, reply_headers) = requestor.getreply()
	reply_body = requestor.getfile().read()

	#print "status code:", status_code
	#print "status message:", message
	#print "HTTP reply body:\n", reply_body
	return reply_body

    #def 

hamptonRoadsBBox=[(-77.5,36.5),(-74.5,38.0)]

def getWaterLevelStationsBBox(ll,ur):
    '''
    Return a list of Station Class objects.  Hides the fetch of the Active Stations
    '''
    s = ActiveStations(forceCache=True)
    #s.getStationsNameNumb()
    #print 'Found stations: ',s.getStationsInBBox((-159.5,21),(-159.0,22))
    #aStation = s.getStation('1611400')
    #print aStation.fields, aStation.parameters

    stationIDs = s.getStationsInBBox(ll,ur)
    #print stationIDs
    stations=[]
    for stationID in stationIDs:
	station = s.getStation(stationID)
	if station.hasSensor('Water Level'):
#	    station.printMe()
	    stations.append(station)
#	else:
#	    print 'NO WATER LEVEL'
    return stations

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options]",version="%prog "+__version__)
    parser.add_option('--test','--doc-test',dest='doctest',default=False,action='store_true',
                        help='run the documentation tests')
    parser.add_option('-v','--verbose',dest='verbose',default=False,action='store_true',
		      help='Make the test output verbose')
    (options,args) = parser.parse_args()

    success=True

    if options.doctest:
	import os; print os.path.basename(sys.argv[0]), 'doctests ...',
	sys.argv= [sys.argv[0]]
	if options.verbose: sys.argv.append('-v')
	import doctest
	numfail,numtests=doctest.testmod()
	if numfail==0: print 'ok'
	else: 
	    print 'FAILED'
	    success=False

    hrStations = getWaterLevelStationsBBox(hamptonRoadsBBox[0],hamptonRoadsBBox[1])
    print [ (s.getName(),s.getID()) for s in hrStations]
    print [s.getID() for s in hrStations]
    del hrStations

    if not success:
	sys.exit('Something Failed')

