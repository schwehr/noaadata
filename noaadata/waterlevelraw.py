#!/usr/bin/env python2.4
__version__ = '$Revision: 4762 $'.split()[1]
__date__ = '$Date: 2006-09-19 14:56:22 -0400 (Tue, 19 Sep 2006) $'.split()[1]
__author__ = 'Kurt Schwehr'

__doc__='''
Handling code for noaa tide station data. 

The Web Services Description Language (WSDL) definition for the
query/response from the NOAA Axis server.

@see: U{NOAA Axis page<http://opendap.co-ops.nos.noaa.gov/axis/>}
@see: U{WSDL<http://opendap.co-ops.nos.noaa.gov/axis/services/WaterLevelRawSixMin?wsdl>}
@see: U{SOAP XML request<http://opendap.co-ops.nos.noaa.gov/axis/webservices/activestations/samples/request.xml>}
@see: U{SOAP XML response<http://opendap.co-ops.nos.noaa.gov/axis/webservices/activestations/samples/response.xml>}
@see: U{Java SOAP code<http://opendap.co-ops.nos.noaa.gov/axis/webservices/activestations/samples/client.html>}
@see: U{Web interface<http://opendap.co-ops.nos.noaa.gov/axis/webservices/activestations/index.jsp>}
@see: U{XPathTutorial<http://www.zvon.org/xxl/XPathTutorial/General/examples.html>}
@see: U{python lxml<http://codespeak.net/lxml/>}

@author: U{'''+__author__+'''<http://schwehr.org/>}
@license: GPL v2
@copyright: (C) 2006 Kurt Schwehr
@version: ''' + __version__ +'''

@var __date__: Date of last svn commit
@undocumented: __version__ __author__ __doc__ parser success 

'''

import sys, httplib

# FIX: document the datums
datumList = ['MLLW','MSL','MHW','STND','IGLD','NGVD','NAVD']
unitList = ['Meters','Feet']

import datetime

def getWaterLevelSoappyNow(stationId,debug=False):
    '''
    Use OLD SOAPpy interface to get the waterlevel for a station
    '''

    d = datetime.datetime.utcnow()

    print 'FIX: do this in seconds space!!!!  This is crap!'

    startD = d + datetime.timedelta(minutes=-20)
    endD = d + datetime.timedelta(minutes=10)
    #startMin = int(d.minute) - 6
    #endMin = int(d.minute) + 1
    print startD,endD,d

    beginDate = str(startD.year)+('%02d' % startD.month)+('%02d' % startD.day)+' '+ ('%02d' % (startD.hour))+':'+('%02d' % (startD.minute))
    endDate = str(endD.year)+('%02d' % endD.month)+('%02d' % endD.day)+' '+ ('%02d' % (endD.hour))+':'+('%02d' % (endD.minute))
    #print beginDate,endDate

    from SOAPpy import SOAPProxy
    url = 'http://opendap.co-ops.nos.noaa.gov/axis/services/WaterLevelRawSixMin'
    namespace='urn:WaterLevelRawSixMin' # This really can be anything.  It is ignored
    server = SOAPProxy(url,namespace)
    if debug: server.config.debug=1
    #response = server.getWaterLevelRawSixMin(stationId=str(stationId),beginDate='20051201 00:00',endDate='20051201 00:18',datum='MLLW',unit=0,timeZone=0)


    response = server.getWaterLevelRawSixMin(stationId=str(stationId),beginDate=beginDate,endDate=endDate,datum='MLLW',unit=0,timeZone=0)
    # only return the last entry
    return response.item[-1]


######################################################################

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
	if options.verbosity>=VERBOSE: sys.argv.append('-v')
	import doctest
	numfail,numtests=doctest.testmod()
	if numfail==0: print 'ok'
	else: 
	    print 'FAILED'
	    success=False

    print getWaterLevelSoappyNow(8639348)

    if not success:
	sys.exit('Something Failed')

