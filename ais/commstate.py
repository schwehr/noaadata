__author__    = 'Kurt Schwehr'
__version__   = '$Revision: 4799 $'.split()[1]
__revision__  = __version__ # For pylint
__date__ = '$Date: 2006-09-25 11:09:02 -0400 (Mon, 25 Sep 2006) $'.split()[1]
__copyright__ = '2009'
__license__   = 'GPL v3'
__contact__   = 'kurt at ccom.unh.edu'
__deprecated__ = 'what goes here?'

__doc__ ='''
Handle communication state as described in Annex 2 - 3.3.7.2.1 of ITU 1371.3

@undocumented: __doc__
@since: 2009-Jul-21
@status: under development
@organization: U{CCOM<http://ccom.unh.edu/>} 
'''

sotdma_fields = (
    'sync_state',
    'slot_timeout',
    'received_stations',
    'slot_number',
    'commstate_utc_hour',
    'commstate_utc_min',
    'commstate_utc_spare',
    'slot_offset'
)

def sotdma_sql_fields(c):
    'sqlhelp fields for commstate'
    for field in sotdma_fields:
        c.addInt(field)


def sotdma_parse_bits(bv):
    assert(len(bv)==19)
    r = {}
    r['sync_state'] = int(bv[:2])
    r['slot_timeout'] = slottimeout = int(bv[2:5])
    submessage = bv[-14:]

    if slottimeout in (3,5,7):
        r['received_stations'] = int(submessage)
    elif slottimeout in (2,4,6):
        r['slot_number'] = int(submessage)
    elif slottimeout == 1:
        r['commstate_utc_hour'] = int(submessage[0:5])
        r['commstate_utc_min'] = int(submessage[5:12])
        r['commstate_utc_spare'] = int(submessage[-2:])
    elif slottimeout == 0:
        r['slot_offset'] = int(submessage)
    else:
        assert False

    return r

itdma_fields = (
    'sync_state',
    'slot_increment',
    'slots_to_allocate',
    'keep_flag',
)

def itdma_sql_fields(c):
    'sqlhelp fields for commstate'
    for field in itdma_fields:
        c.addInt(field)


def itdma_parse_bits(bv):
    assert( len(bv) == 19 )
    r = {}
    r['sync_state'] = int(bv[:2])
    r['slot_increment'] = int( bv[2:15] )
    r['slots_to_allocate'] = int( bv[15:18] )
    r['keep_flag'] = int( bv[18] )
    return r



def sql_fields(c):
    'sqlhelp fields for commstate - both SOTDMA and ITDMA'
    for field in set(sotdma_fields + itdma_fields):
        c.addInt(field)

