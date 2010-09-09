#!/usr/bin/env python
__author__    = 'Kurt Schwehr'
__version__   = '$Revision: 9918 $'.split()[1]
__revision__  = __version__ # For pylint
__date__ = '$Date: 2008-07-21 14:12:23 -0400 (Mon, 21 Jul 2008) $'.split()[1]
__copyright__ = '2008'
__license__   = 'GPL v3'
__contact__   = 'kurt@ccom.unh.edu'

__doc__ ='''
Produce a summary of vessels from the ais msg 5, shipdata.  Designed based
on requirements discussed with Leila Hatch for NOPP report.

@requires: U{Python<http://python.org/>} >= 2.5
@requires: U{epydoc<http://epydoc.sourceforge.net/>} >= 3.0.1
@requires: U{psycopg2<http://http://initd.org/projects/psycopg2/>} >= 2.0.6

@undocumented: __doc__
@since: 2008-July-21
@status: under development
@organization: U{CCOM<http://ccom.unh.edu/>} 
'''

import sys
import os
import datetime
import psycopg2 as psycopg
import pyExcelerator as excel
from ais.ais_msg_5 import shipandcargoDecodeLut as shipandcargo_lut


def main():
    '''
    FIX: document main
    '''
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options]",
                          version="%prog "+__version__+' ('+__date__+')')

    parser.add_option('-d','--database-name',dest='databaseName',default='ais',
                      help='Name of database within the postgres server [default: %default]')
    parser.add_option('-D','--database-host',dest='databaseHost',default='localhost',
			  help='Host name of the computer serving the dbx [default: %default]')
    defaultUser = os.getlogin()
    parser.add_option('-u','--database-user',dest='databaseUser',default=defaultUser,
                      help='Host name of the to access the database with [default: %default]')

    parser.add_option('--mmsi-table',dest='mmsiTable',default='shipdata',
                      help='PostgreSQL db table to pull userID (mmsi) list from [default: %default]')

    parser.add_option('-v', '--verbose', dest='verbose', default=False, action='store_true',
                      help='run the tests run in verbose mode')

    (options, args) = parser.parse_args()
    v = options.verbose

    connectStr = "dbname='"+options.databaseName+"' user='"+options.databaseUser+"' host='"+options.databaseHost+"'"
    if v:
        sys.stderr.write( 'CONNECT: %s' % connectStr )
    cx = psycopg.connect(connectStr)
    cu = cx.cursor()

    #vessels = get_vessels(cu,options.mmsi)
    print 'table',options.mmsiTable
    cu.execute('SELECT DISTINCT(userid) FROM '+options.mmsiTable+';')
    vessels=[vessel[0] for vessel in cu.fetchall()]
    print vessels

    workbook = excel.Workbook()
    ws = workbook.add_sheet('Vessel Stats')
    ws_row = 0

    col = 0
    for colname in ('mmsi/userid','imonumber','callsign','name','shipandcargo','shipandcargo text','length','width','min_draught','max_draught'):
        ws.write(ws_row,col,colname); col += 1
    ws_row += 1
        
    vesselcount=0
    for vessel in vessels:
        vesselcount+=1
        if vesselcount%10==0: print 'vessel count',vesselcount

        shipdata=set()
        min_draught=None
        max_draught=None
        cu.execute('SELECT imonumber,callsign,name,shipandcargo,dimA,dimB,dimC,dimD,draught FROM shipdata WHERE userid=%s',(vessel,))
        for row in cu.fetchall():
            imonumber,callsign,name,shipandcargo,dimA,dimB,dimC,dimD,draught = row
            callsign=callsign.strip('@ ')
            name=name.strip('@ ')
            length = dimA + dimB
            width = dimC + dimD

            draught=float(draught)
            if min_draught==None or draught<min_draught:
                min_draught=draught
            if max_draught==None or draught>max_draught:
                max_draught=draught

            entry = (imonumber,callsign,name,shipandcargo,length,width)

            shipdata.add(entry)

        if len(shipdata)==0:
            ws.write(ws_row,0,str(vessel))
            ws_row+=1
            continue
        for entry in shipdata:
            imonumber,callsign,name,shipandcargo,length,width = entry
            col=0
            ws.write(ws_row,col,str(vessel));  col += 1
            ws.write(ws_row,col,str(imonumber));  col += 1
            ws.write(ws_row,col,callsign);  col += 1
            ws.write(ws_row,col,name);  col += 1
            ws.write(ws_row,col,shipandcargo);  col += 1
            try:
                cargo_text = shipandcargo_lut[str(shipandcargo)]
                print 'cargo_text:',cargo_text
            except:
                print 'cargo_text UNKNOWN:',shipandcargo
                cargo_text = 'unknown'
            ws.write(ws_row,col,cargo_text);  col += 1

            ws.write(ws_row,col,length);  col += 1
            ws.write(ws_row,col,width);  col += 1
            ws.write(ws_row,col,min_draught);  col += 1
            ws.write(ws_row,col,max_draught);  col += 1

            ws_row += 1
        
    now = datetime.datetime.now()
    workbook.save('vessels-'+now.strftime('%Y-%m-%dT%H%M')+'.xls') # FIX - command line option


######################################################################
# Code that runs when this is this file is executed directly
######################################################################
if __name__ == '__main__':
    main()
