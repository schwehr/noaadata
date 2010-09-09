#!/usr/bin/env python

__author__    = 'Kurt Schwehr'
__version__   = '$Revision: 4799 $'.split()[1]
__revision__  = __version__ # For pylint
__date__ = '$Date: 2006-09-25 11:09:02 -0400 (Mon, 25 Sep 2006) $'.split()[1]
__copyright__ = '2008'
__license__   = 'GPL v3'
__contact__   = 'kurt at ccom.unh.edu'
__deprecated__ = 'what goes here?'

__doc__ ='''
Convert a sequence of geotagged jpeg images to kml

@requires: U{Python<http://python.org/>} >= 2.5
@requires: U{epydoc<http://epydoc.sourceforge.net/>} >= 3.0.1
@requires: U{psycopg2<http://http://initd.org/projects/psycopg2/>} >= 2.0.6

@undocumented: __doc__
@since: 2008-Aug-24
@status: under development
@organization: U{CCOM<http://ccom.unh.edu/>} 

'''

import sys
import os

import time
import datetime

import exceptions # For KeyboardInterupt pychecker complaint
import traceback

import pyexiv2
import Image # PIL

def rational2deg(r):
    ''' convert a pyexiv2 rational gps lat or lon to decimal degrees'''

    deg = r[0].numerator / float(r[0].denominator)
    min = r[1].numerator / float(r[1].denominator)
    sec = r[2].numerator / float(r[2].denominator)

    return deg + min / 60 + sec / 3600

def xml_start(file):
    file.write('<?xml version="1.0" encoding="UTF-8"?>\n')

def kml_start(file):
    file.write('<kml xmlns="http://earth.google.com/kml/2.0">\n')

def kml_end(file):
    file.write('</kml>\n')
    

def kml_placemark(x, y, z=10, description='No description', name='unknown',indent='\t\t'):
    ''' Try to handle writing kml placemarks
    '''
    out = []
    out.append(indent+'<Placemark>')
    out.append(indent+'\t<description>'+str(description)+'</description>')
    out.append(indent+'\t<name>'+str(name)+'</name>')
    out.append(indent+'\t<Point>')
    out.append(indent+'\t\t<coordinates>'+str(x)+','+str(y)+','+str(z)+'</coordinates>')
    out.append(indent+'\t</Point>')
    out.append(indent+'</Placemark>')
    return '\n'.join(out)


def process_image(filename):
    image = pyexiv2.Image(filename)
    image.readMetadata()
    lon =  rational2deg(image['Exif.GPSInfo.GPSLongitude'])
    if 'W' ==  image['Exif.GPSInfo.GPSLongitudeRef']:
        lon = -lon
    lat =  rational2deg(image['Exif.GPSInfo.GPSLatitude'])
    if 'S' ==  image['Exif.GPSInfo.GPSLatitudeRef']:
        lat = -lat
    dt = image['Exif.Image.DateTime']

    thumbname = filename.split('.')[0]+'-thumbnail.jpg'
    im = Image.open(filename)
    im.thumbnail((150,150))
    im.save(thumbname,'JPEG')

    indent='\t\t  '
    description = [
        indent + filename,
        indent + str(dt),
        indent + 'Longitude %s' % lon,
        indent + 'Latitude %s' % lat,
        indent + '<img src="'+thumbname+'"/>',
        ]
    description = '<br/>\n'.join(description)

    placemark = kml_placemark(lon, lat, name=dt.strftime('%H%M%S'), description=description)
    return placemark

def main(options,args):
    xml_start(sys.stdout)
    kml_start(sys.stdout)
    print '\t<Folder>'
    for filename in args:
        print process_image(filename)
    print '\t</Folder>'
    #process_image('IMG_6829.JPG')
    kml_end(sys.stdout)

if __name__=='__main__':
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options]",
                          version="%prog "+__version__+' ('+__date__+')')
    parser.add_option('-v', '--verbose', dest='verbose', default=False, action='store_true',
                      help='run the tests run in verbose mode')

    (options, args) = parser.parse_args()
    main(options,args)
