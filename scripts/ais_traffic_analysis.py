#!/usr/bin/env python

__version__ = '$Revision: 7470 $'.split()[1]
__date__ = '$Date: 2007-11-06 10:31:44 -0500 (Tue, 06 Nov 2007) $'.split()[1]
__author__ = 'Kurt Schwehr'

__doc__='''
Basic traffic analysis by counting message types.

@requires: U{epydoc<http://epydoc.sourceforge.net/>} > 3.0alpha3
@requires: U{BitVector<http://cheeseshop.python.org/pypi/BitVector>}

@author: '''+__author__+'''
@version: ''' + __version__ +'''
@var __date__: Date of last svn commit
@undocumented: __version__ __author__ __doc__ parser
@status: under development
@license: GPL v2
@since: 2007-Sep-01


@todo: make option to parse the station if present and present by station stats
@todo: optionally split to A and B counts
'''

import sys


#AIS NMEA tables
encode = {0: '0',
 1: '1',
 2: '2',
 3: '3',
 4: '4',
 5: '5',
 6: '6',
 7: '7',
 8: '8',
 9: '9',
 10: ':',
 11: ';',
 12: '<',
 13: '=',
 14: '>',
 15: '?',
 16: '@',
 17: 'A',
 18: 'B',
 19: 'C',
 20: 'D',
 21: 'E',
 22: 'F',
 23: 'G',
 24: 'H',
 25: 'I',
 26: 'J',
 27: 'K',
 28: 'L',
 29: 'M',
 30: 'N',
 31: 'O',
 32: 'X',
 33: 'Y',
 34: 'Z',
 35: '[',
 36: '\\',
 37: ']',
 38: '^',
 39: '_',
 40: '`',
 41: 'a',
 42: 'b',
 43: 'c',
 44: 'd',
 45: 'e',
 46: 'f',
 47: 'g',
 48: 'h',
 49: 'i',
 50: 'j',
 51: 'k',
 52: 'l',
 53: 'm',
 54: 'n',
 55: 'o',
 56: 'p',
 57: 'q',
 58: 'r',
 59: 's',
 60: 't',
 61: 'u',
 62: 'v',
 63: 'w'}

decode={}
for key in encode.keys():
    decode[encode[key]]=key
#print decode


############################################################
if __name__=='__main__':
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options] file1.ais [file2.ais ...]",version="%prog "+__version__)
    parser.add_option('-d','--with-date',dest='withDateFilename',default=False, action='store_true',
                      help='Assume a filename of YYYY-MM-DDxxxxx')
    (options,args) = parser.parse_args()

#    if options.columnDef:
#        print '#'
#        for i in range(1,64):
#            print ' '+str(i)

    for filename in args:
        counts = [ 0 for i in range(64) ]
        for line in file(filename):
            # FIX: switch to regex
            "!AIVDM,2,1,9,A,55MwkdP09`"
            "01234567890123"
            if line[0]=='#': continue
            if line[1:7] != 'AIVDM,': continue

            fields=line.split(',')

            try:
                if fields[2]!='1': continue
            except:
                sys.stderr.write('skipping too few fields\n')
                sys.stderr.write('  '+line)
                print '  ',line,
                continue
            try:
                index=decode[fields[5][0]]
            except:
                sys.stderr.write('What index is this? '+fields[5][0]+'\n')
                sys.stderr.write('  '+line)
                continue
                
                
            #print index,line,
            counts[index]+=1
        #print counts
        for i in range(1,len(counts)):
            #print i, counts[i]
            print counts[i],' ',
        if options.withDateFilename:
            date=filename[:10]
            print date+'\t'+'1200',
        else:
            print filename,' ',
        print
        
            
            
