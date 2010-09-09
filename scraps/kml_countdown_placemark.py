#!/usr/bin/env python
__author__    = 'Kurt Schwehr'
__version__   = '$Revision: 8283 $'.split()[1]
__date__      = '$Date: 2008-01-17 16:20:22 -0500 (Thu, 17 Jan 2008) $'.split()[1]
__copyright__ = '2008'
__license__   = 'GPL v2'
__contact__   = 'kurt at ccom.unh.edu'
__doc__="""
Make a series of placemarks that are a count down sequence

@requires: U{epydoc<http://epydoc.sourceforge.net/>} > 3.0
@requires: U{pyproj<>}
@requires: U{magicdate<http://cheeseshop.python.org/pypi/magicdate>}
@undocumented: __version__ __author__ __doc__ parser
@status: under development
@since: 2007-Sep-19
@organization: U{CCOM<http://ccom.unh.edu/>}

"""
#@var __date__: Date of last svn commit

import math,sys,os
import sys
import time

def addStyle(out,color='ffffff',opacity=.4,scale=1,indent='    ',styleName='style'):
    '''
    @param polyOpacity: 0..1 where 1 is opaque, and 0 is not visible
    '''
    o=out
    oVal = (int(opacity*255)).__hex__()
    oVal = oVal[oVal.find('x')+1:]
    if len(oVal)==1: oVal='0'+oVal

    o.write(indent+'<Style id="'+styleName+'">\n')
    o.write(indent+'\t<IconStyle>\n')
    o.write(indent+'\t	<color>66ffffff</color>\n')
    o.write(indent+'\t	<scale>1.3</scale>\n')
    o.write(indent+'\t	<Icon>\n')
    o.write(indent+'\t		<href>http://maps.google.com/mapfiles/kml/paddle/ylw-stars.png</href>\n')
    o.write(indent+'\t	</Icon>\n')
    o.write(indent+'\t</IconStyle>\n')
    o.write(indent+'\t<LabelStyle>\n')
    o.write(indent+'\t	<color>ff4c4c4c</color>\n')
    o.write(indent+'\t</LabelStyle>\n')
    o.write(indent+'\t<ListStyle>\n')
    o.write(indent+'\t	<ItemIcon>\n')
    o.write(indent+'\t		<href>http://maps.google.com/mapfiles/kml/paddle/ylw-stars-lv.png</href>\n')
    o.write(indent+'\t	</ItemIcon>\n')
    o.write(indent+'\t</ListStyle>\n')
    o.write(indent+'\t</Style>\n')

def timeSec2KmlTime(timeSec):
    try:
        t = time.gmtime(float(timeSec))
    except:
        sys.exit('ERROR: this is not a valid time:'+str(timeSec))
    s = "%4d-%02d-%02dT%02d:%02d:%02dZ" % (t[0],t[1],t[2],t[3],t[4],t[5])
    return s
    

if __name__ == '__main__':
    from optparse import OptionParser
    import magicdate
    
    parser = OptionParser(usage="%prog [options] [file1] [file2] ...",
                          version="%prog "+__version__+' ('+__date__+')',option_class=magicdate.MagicDateOption)
 
    parser.add_option('--start-time',dest='start',type='magicdate',default=None,help='magicdate')
    #parser.add_option('--end-time'  ,dest='end'  ,type='magicdate',default=None,help='magicdate')

    parser.add_option('--style-name',dest='styleName',default='style',help='Name of the style for the polygon')

    parser.add_option('-S','--with-style',dest='withStyle'
                      ,default=False
                      , action='store_true'
                      ,help='Include a style reference')

    parser.add_option('--color'  ,dest='color'  ,type='string',default='ffffff',help=' [default: %default (gray)]')
    parser.add_option('--opacity',dest='opacity',type='float' ,default=0.7     ,help=' 0..1 [default: %default]')
    parser.add_option('-z','--height',dest='z'
                      ,default=150
                      , type='float'
                      ,help='Height above the surface'
                      +' [default: %default m ]')
    parser.add_option('-x','--lon',dest='x',default=-70.52368399114937
                      , type='float'
                      ,help=' [default: %default m ]')

    parser.add_option('-y','--lat',dest='y',default=42.42635642910747
                      , type='float'
                      ,help=' [default: %default m ]')

    parser.add_option('-t','--time-step',dest='timeStep',default=20
                      , type='int'
                      ,help=' [default: %default m ]')

    parser.add_option('--time-offset',dest='timeOffset',default=0
                      , type='int'
                      ,help=' Move from a date to a time within a day [default: %default min ]')

    (options,args) = parser.parse_args()

    x = options.x
    y = options.y

    import datetime

    z = options.z
    start =  datetime.datetime(options.start.year,options.start.month,options.start.day)+datetime.timedelta(seconds=60*options.timeOffset)
    #print options.start, type(options.start)
    #print start, type(start)
    #print options.end
    print '''<?xml version="1.0" encoding="UTF-8"?>
<!-- Produced with noaadata/xy2kml.py (code by Kurt Schwehr) -->
<kml xmlns="http://earth.google.com/kml/2.2">
  <Document>'''

    if options.withStyle:
        addStyle(sys.stdout
                 ,color=options.color
                 ,opacity=options.opacity
                 ,styleName=options.styleName
                 )

    print '''    <Folder>
'''

    for minutes in range(0,24*60,options.timeStep):
        remaining = 24*60 - minutes
        remainStr = '%02d:%02d' % (remaining/60, remaining % 60 )
        now = start+datetime.timedelta(seconds=minutes*60)
        #print now, '-->' , remainStr #, type (now)
        nowStr = '%4d-%02d-%02dT%02d:%02d:00Z' % (now.year,now.month,now.day,now.hour,now.minute)
        nowStr_plus1 = '%4d-%02d-%02dT%02d:%02d:00Z' % (now.year,now.month,now.day,now.hour,now.minute+options.timeStep)

        print '<Placemark>'
        if options.withStyle: print '        <styleUrl>#'+options.styleName+'</styleUrl>'

        # FIX: make the expiration be selectable

        print '<name>'+remainStr+' (hh:mm) REMAINING</name>'
        print '''<description><center><font size="+2">Right Whale Detected</font></center><br/>
        <center>LNG vessels required to stay <font color="red"><b> below 10 knots</b></font></center>
<pre>  Restriction ends: <b>'''+str(start+datetime.timedelta(days=1))+'''z</b>
  Whale detected:   '''+str(start)+'''z

<a href="http://vislab-ccom.unh.edu/~schwehr/sampletext.html">Additional Information</a>
</pre>
  
        </description>'''
                         
                                 

        print '<Point><coordinates>'+str(x)+','+str(y)+','+str(z)+'</coordinates></Point>'
        print '<TimeSpan><begin>'+nowStr+'</begin><end>'+nowStr_plus1+'</end></TimeSpan>'

        print '</Placemark>'


    print '''
    </Folder>
  </Document>
</kml>
'''
