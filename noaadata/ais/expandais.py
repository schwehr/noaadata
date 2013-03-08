#!/usr/bin/env python

__version__ = '$Revision: 4820 $'.split()[1]
__date__ = '$Date: 2006-09-28 12:11:51 -0400 (Thu, 28 Sep 2006) $'.split()[1]
__author__ = 'Kurt Schwehr'

__doc__='''
Expand structs in ais xml to include-struct elements while applying name mangling

@requires: U{lxml<http://codespeak.net/lxml/>}
@requires: U{epydoc<http://epydoc.sourceforge.net/>} > 3.0alpha3

@author: '''+__author__+'''
@version: ''' + __version__ +'''
@copyright: 2006
@var __date__: Date of last svn commit
@undocumented: __version__ __author__ __doc__ parser
@since: 2006-Sep-26
@status: under development
@organization: U{CCOM<http://ccom.unh.edu/>}

@bug: WHY IS THE IMO message screwing up the day field?
@license: GPL v2
'''

import sys
from lxml import etree

def getPos(parent,child):
    '''
    Return the position number of the child node.  It seems like this
    really should be a part of the element tree interface.  Perhaps
    I overlooked it.
    '''
    for i in range(len(parent)):
	if parent[i]==child: return i
    return None


def expandAis(inET,verbose=False):
    '''
    Replace each include-struct with the structure.  This code is not
    pretty, but it seems to work.  The include-struct name is
    prepended to each field name within the struct.  The
    include-struct description is also added to before the fields
    description.

    @param inET: lxml element tree to expand
    @return: lxml element tree with expanded structures
    '''
    inET.xinclude()
    import copy
    outET = copy.deepcopy(inET)
    #outET.xinclude()

    root = outET.getroot()
    includeStructs = root.xpath('message/include-struct')
    for inc in includeStructs:

	if verbose: print 'inc:',inc.attrib['name'], 'parent:',inc.getparent().tag
	parent = inc.getparent()
	nodePosition = getPos(parent,inc)
	#if verbose: print 'pos:',nodePosition

	structName = inc.attrib['struct']
	baseName = inc.attrib['name']+'_'

        if len(inc.xpath('do_not_mangle_name'))>0:
            if verbose: print 'Not mangling',structName,baseName[:-1]
            baseName = ''
	#if verbose: print 'baseName:',baseName, 'structName=',structName

        # // means find all struct tags at all levels
	structDef = root.xpath("//struct[@name='"+structName+"']")

	# Put in a comment where the include-struct was.
	inc.getparent().replace(inc,etree.Comment('Struct include of '+inc.attrib['name']+' was here'))

	replacement=copy.deepcopy(structDef[0])

        postgis=False # Does this structure have an associated postgis data structure?
        postgisName=None
        postgisType=None
        if 'postgis_type' in replacement.attrib:
            postgis=True
            postgisType=replacement.attrib['postgis_type']
            postgisName=inc.attrib['name'] #baseName
            if verbose: print 'Found PostGIS datatype for structure:',postgisName,postgisType

	# FIX: what happens when the include is at the beginning or end of the list?

	for subfield in replacement.xpath('field'):
	    subfield.attrib['name']=baseName+subfield.attrib['name']
            desc = subfield.xpath('description')

            if postgis:
                if verbose: print 'Annotating',subfield.attrib['name'], 'with postgis info'
                subfield.attrib['postgisType']=postgisType
                subfield.attrib['postgisName']=postgisName

	    if len(desc)==1:
                txt = inc.xpath('description')[0].text
                if None == txt:
                    if verbose: 'WARNING: are you sure you want no text in this description?'
                    txt = ''
                else: txt +='  '  # FIX: was \n\t which cause trouble with word export
		desc[0].text=  txt+desc[0].text
	    else:
		print 'WARNING: no description for subfield!!!!  Must have exactly one description field'
	    # Now that the node is ready, jam it in there after the replaced comment

	    #print "FIX: make sure these end up in the right place!!!!"

	    newPos = nodePosition+getPos(replacement,subfield) #+1
	    nodePosition+=1
	    parent.insert(newPos,subfield)
	#if verbose: print 'New parent:',etree.tostring(parent)

    return outET

def nukeStructs(inET,verbose=False):
    '''
    Replace each include-struct with the structure.  This code is not
    pretty, but it seems to work.  The include-struct name is
    prepended to each field name within the struct.  The
    include-struct description is also added to before the fields
    description.

    @param inET: lxml element tree to expand
    @return: lxml element tree with expanded structures
    '''
    import copy
    outET = copy.deepcopy(inET)

    root = outET.getroot()
    structs = root.xpath('struct')
    for struct in structs:
	if verbose: print 'nuking struct:',struct.attrib['name']
	struct.getparent().replace(struct,etree.Comment('Struct '+struct.attrib['name']+' was here'))

    return outET

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options]",
			    version="%prog "+__version__)
    parser.add_option('-i','--input-file',dest='inFilename',default=None,
                        help='AIS to read from')
    parser.add_option('-o','--output-file',dest='outFilename',default='out-ais.xml',
                        help='New AIS file that has structures expanded')
    parser.add_option('-v','--verbose',dest='verbose',default=False,action='store_true',
                        help='Verbose mode')

    parser.add_option('-k','--keep-structs',dest='keepStructs',default=False,action='store_true',
                        help='Keep the structure definitions at the beginning of the file')
    (options,args) = parser.parse_args()

    tree = etree.parse(options.inFilename)
    #tree.xinclude()
    newET = expandAis(tree,options.verbose)
    if not options.keepStructs:
	newET = nukeStructs(newET,options.verbose)
    newET.write(options.outFilename)

    #if options.verbose: print etree.tostring(newET)
