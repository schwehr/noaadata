#!/usr/bin/env python
#!/usr/bin/env python

__version__ = '$Revision: 12483 $'.split()[1]
__date__ = '$Date: 2009-08-19 16:55:51 -0400 (Wed, 19 Aug 2009) $'.split()[1]
__author__ = 'Kurt Schwehr'

__doc__='''

Filter position messages (1,2,3) that are within a polygon.

egrep 'AIVDM,1,1,[0-9]?,[AB],[1-3]' >  short.ais

another box in the Great South Channel.  This is to support a NOAA proposal for an ATBA in that area.

Bounds are::

   * Eastern  N-S line - 68.50 W
   * Western  N-S line - 69.30 W
   * Southern E-W line - 41.00 N
   * Northern E-W line - 42.15 N

WTK ... "Well known something"... FIX: add a ref to definition of OpenGIS/WTK whatever

POLYGON (( -69.30 42.15, -68.50 42.15, -68.50 41, -69.30 41, -69.30 42.15))


The Hampton Roads area for the US Hydro 2007 conference:

-77 -75.75 36.6 37.25


egrep '!AIVDM,1,1,[0-9]?,[AB],[1-3]' biglog.ais > pos_msgs.ais

@requires: U{epydoc<http://epydoc.sourceforge.net/>} > 3.0alpha3
@requires: U{pcl-core<http://trac.gispython.org/projects/PCL>} 

@author: U{'''+__author__+'''<http://schwehr.org/>}
@version: ''' + __version__ +'''
@copyright: 2006
@var __date__: Date of last svn commit
@undocumented: __version__ __author__ __doc__ parser
@since: 2006-Sep-24
@status: under development
@organization: U{CCOM<http://ccom.unh.edu/>}
@license: GPL v2

@todo: add a link to generated doc string to bring up the html for the pretty version
@todo: allow for buffering.  poly._transform into more a better projection, buffer and then convert back
'''

import sys, os

stellwagen=(
    (-70.502624517077535,42.651229858376865),
    (-70.216651917737892,42.766723627364335),
    (-70.035064690795366,42.093299872372249),
    (-70.054344171734087,42.1051712037602),
    (-70.067070010211893,42.108303073944938),
    (-70.086586000518764,42.117519381620241),
    (-70.106071466728224,42.120601658877817),
    (-70.123886112296802,42.126754758125287),
    (-70.140045164348635,42.128528592356282),
    (-70.154968262866575,42.133419041708223),
    (-70.172912604417078,42.13481140155551),
    (-70.196044924942854,42.132099157383799),
    (-70.217071529781094,42.133392331376747),
    (-70.238891607484177,42.129699711869044),
    (-70.2558517459629  ,42.124347685078639),
    (-70.277999877386733,42.115261073385255),
    (-70.470436094985956,42.12923813443058),
    (-70.597366328254395,42.551074986184581),
    (-70.586975101270227,42.558498376829306),
    (-70.58387756894885 ,42.563468929236009),
    (-70.572532649020488,42.575222019909717),
    (-70.555580138073651,42.580753321639378),
    (-70.541786193673204,42.587898251490522),
    (-70.528427130349584,42.595039367575716),
    (-70.51586913948303 ,42.606506341984264),
    (-70.50587462797651 ,42.621070862684029),
    (-70.501319887816891,42.633117669215117),
    (-70.501304632753104,42.642444604042602),
    (-70.502624517077535,42.651229858376865)
    )

stellwagen_5nm=(
    (-70.680700637727298,42.551074957881227),
    (-70.680522212160241,42.556525283590652),
    (-70.679987700694582,42.561952270232844),
    (-70.679099391643305,42.567332678553903),
    (-70.677861089003258,42.572643468926564),
    (-70.676278095614265,42.577861899109813),
    (-70.674357189746075,42.582965624062147),
    (-70.672106596756336,42.587932787950621),
    (-70.669535954587218,42.592742121088854),
    (-70.666656271046918,42.597373029070781),
    (-70.663479877394451,42.601805681493587),
    (-70.660020374941595,42.606021097394638),
    (-70.656292578368664,42.610001225348597),
    (-70.652312450414712,42.613729021921522),
    (-70.648097034513654,42.617188524374384),
    (-70.64666308460518,42.61826452602363),
    (-70.646531660025573,42.618414749601655),
    (-70.643842821623565,42.621337269490155),
    (-70.632501028562885,42.633089972665942),
    (-70.631462070391976,42.634147580731401),
    (-70.627481942438024,42.637875377304326),
    (-70.623266526947717,42.641334879757189),
    (-70.618833874114159,42.644511273820399),
    (-70.614202966132225,42.647390957360699),
    (-70.609393632993999,42.649961599529824),
    (-70.604426469105533,42.652212192108813),
    (-70.599322744563949,42.654133097976995),
    (-70.598385305995706,42.654445130461994),
    (-70.587877223273978,42.657873754860653),
    (-70.585586744795933,42.659060037915502),
    (-70.585242552292129,42.662106508706586),
    (-70.584354243240838,42.667486917027638),
    (-70.583115940600791,42.672797707400306),
    (-70.581532946801048,42.678016137994305),
    (-70.579612040932858,42.683119862535882),
    (-70.577361448353884,42.688087026424355),
    (-70.574790806184751,42.692896359562589),
    (-70.571911122644451,42.697527267544515),
    (-70.568734728581248,42.70195992037808),
    (-70.565275226128378,42.706175335868373),
    (-70.561547429555461,42.710155463822332),
    (-70.557567301601495,42.713883260395257),
    (-70.553351886111201,42.717342762848119),
    (-70.548919233277644,42.72051915691133),
    (-70.54428832529571,42.72339884045163),
    (-70.53947899215747,42.725969482620762),
    (-70.534511828269004,42.728220075199744),
    (-70.533825329856512,42.72850085954078),
    (-70.247844384481382,42.843986886993811),
    (-70.24342715835229,42.845627008520957),
    (-70.238208727758291,42.847210002320701),
    (-70.232897937385616,42.848448304960748),
    (-70.227517529064571,42.849336614012024),
    (-70.222090542422379,42.849871125477691),
    (-70.216640216712946,42.850049550633997),
    (-70.211189891003514,42.849871125477691),
    (-70.205762904361322,42.849336614012024),
    (-70.200382496040277,42.848448304960748),
    (-70.195071705667601,42.847210002320701),
    (-70.189853275073602,42.845627008520957),
    (-70.184749550532018,42.843706102652767),
    (-70.179782386643552,42.841455510073786),
    (-70.174973053505326,42.83888486790466),
    (-70.174973053094561,42.83888486790466),
    (-70.170342145523392,42.83600518436436),
    (-70.165909492689835,42.83282879030115),
    (-70.161694077199527,42.82936928784828),
    (-70.157713949245576,42.825641491275363),
    (-70.153986152672658,42.821661363321404),
    (-70.150526650219788,42.817445947831104),
    (-70.147350256156571,42.813013294997546),
    (-70.144470572616271,42.80838238742637),
    (-70.144470572616271,42.808382387015612),
    (-70.141899930447153,42.803573053877379),
    (-70.139649337868164,42.798605889988913),
    (-70.137728431999975,42.793502165447329),
    (-70.136179450721571,42.788410273098123),
    (-69.954602954319014,42.114994697971269),
    (-69.954568941797675,42.114868159726477),
    (-69.953330639157628,42.109557369353809),
    (-69.952442330106351,42.104176961032756),
    (-69.951907818640692,42.098749974390564),
    (-69.951729393484385,42.093299648681139),
    (-69.951907818640692,42.087849322971707),
    (-69.952442330106351,42.082422336329515),
    (-69.953330639157628,42.077041928008462),
    (-69.954568941386924,42.071731137635794),
    (-69.956151935186668,42.066512707041795),
    (-69.958072841054857,42.061408982500211),
    (-69.960323434044582,42.056441818611745),
    (-69.960323434044582,42.056441818200987),
    (-69.962894076213715,42.051632485062754),
    (-69.965773759754015,42.047001577491585),
    (-69.965773759754015,42.047001577080827),
    (-69.968950153406468,42.042568924658021),
    (-69.972409655859337,42.03835350875697),
    (-69.976137452432255,42.034373380803011),
    (-69.980117580386221,42.030645584230086),
    (-69.984332996287264,42.027186081777224),
    (-69.988765648710071,42.024009688124764),
    (-69.988765649120836,42.024009688124764),
    (-69.993396556692005,42.021130004584464),
    (-69.998205889830245,42.018559362415338),
    (-69.998205890240996,42.018559362415338),
    (-70.003173054129462,42.016308769425599),
    (-70.008276778671046,42.014387863557417),
    (-70.013495209265045,42.012804869757666),
    (-70.018805999637706,42.011566567528384),
    (-70.024186407958766,42.0106782584771),
    (-70.029613394600958,42.010143747011433),
    (-70.03506372031039,42.009965321444376),
    (-70.040514046019808,42.010143747011433),
    (-70.045941032662,42.0106782584771),
    (-70.05132144098306,42.011566567528384),
    (-70.056632231355721,42.012804869757666),
    (-70.061850661949734,42.014387863557417),
    (-70.066954386491304,42.016308769425599),
    (-70.071921550379784,42.018559362415338),
    (-70.071921550790535,42.018559362415338),
    (-70.07673088351801,42.021130004584464),
    (-70.076730883928761,42.021130004584464),
    (-70.078756704695806,42.022338157848672),
    (-70.086927639841619,42.027369232252596),
    (-70.08698759931012,42.027383990659594),
    (-70.088638625956875,42.027808331212604),
    (-70.093857056140109,42.029391325012348),
    (-70.098960781092458,42.031312230880538),
    (-70.102656443934848,42.032949123877792),
    (-70.110958995893327,42.03687004938368),
    (-70.118175240373688,42.037929711632088),
    (-70.122325651920221,42.038646755387695),
    (-70.127636442292882,42.039885058027735),
    (-70.132854872886881,42.041468051416729),
    (-70.134141955491856,42.041916729170254),
    (-70.14272130911634,42.044986413748468),
    (-70.149129966829321,42.045689159963551),
    (-70.150923638223929,42.045905547866639),
    (-70.156304046544989,42.046793856917922),
    (-70.16161483691765,42.048032159557962),
    (-70.166008641417875,42.049340018533222),
    (-70.171344911709909,42.051089574490319),
    (-70.186346233544967,42.049331314646658),
    (-70.190596867531639,42.048943168953329),
    (-70.196047193241057,42.048764743797022),
    (-70.2011576636028,42.048921590790371),
    (-70.212616909430835,42.049625653062684),
    (-70.219311412390297,42.048493163641453),
    (-70.227404124282216,42.045939723046729),
    (-70.246293466495786,42.038167275980285),
    (-70.251216498927306,42.036320956135427),
    (-70.251216806171627,42.036320840302672),
    (-70.25643523676564,42.034737846913679),
    (-70.261746027138301,42.033499544273639),
    (-70.26712643545936,42.032611235222355),
    (-70.272553422101552,42.032076723756688),
    (-70.27800374781097,42.031898298600382),
    (-70.283454073520403,42.032076723756688),
    (-70.284053204874439,42.032118161486025),
    (-70.476481799056614,42.046124009258129),
    (-70.48130965434477,42.046617082994459),
    (-70.486690062665829,42.047505392045743),
    (-70.492000853038491,42.048743694685783),
    (-70.497219283632489,42.050326688074776),
    (-70.502323008174073,42.052247594353716),
    (-70.507290172473304,42.054498186932697),
    (-70.512099505611531,42.05706882910183),
    (-70.516730413593464,42.05994851264213),
    (-70.521163066016271,42.06312490670534),
    (-70.525378481917315,42.066584408747453),
    (-70.529358609871281,42.07031220532037),
    (-70.533086406444198,42.074292333274329),
    (-70.536545908486318,42.07850774917538),
    (-70.539722302549521,42.082940401598186),
    (-70.542601986089821,42.087571309580113),
    (-70.545172628258953,42.092380642718354),
    (-70.547423220837928,42.097347807017577),
    (-70.549344127116868,42.102451531559154),
    (-70.55023218067889,42.105226064016797),
    (-70.677166149587038,42.527062548699526),
    (-70.677861089414009,42.529506446835882),
    (-70.679099392054056,42.53481723720855),
    (-70.679987701105333,42.540197645529609),
    (-70.680522212570992,42.545624632171801),
    (-70.680700637727298,42.551074957881227)
    )


gsc_and_gsctss= (
    (-69.56000000000, 41.74000000000),
    (-68.51666667000, 42.16666667000),
    (-68.21666667000, 41.63333333000),
    (-69.07000000000, 41.02000000000),
    (-69.07000000000, 41.02000000000),
    (-69.16407331100, 40.95597788560),
    (-69.66570385450, 41.69306766380),
    (-69.56000000000, 41.74000000000)
)
'''Great South Channel and TSS'''

gsc=(
    (-69.56000000000, 41.74000000000),
    (-68.51666667000, 42.16666667000),
    (-68.21666667000, 41.63333333000),
    (-69.07000000000, 41.02000000000),
    (-69.56000000000, 41.74000000000)
)
''' Great South Channel'''

gsctss=(
    (-69.56000000000, 41.74000000000),
    (-69.07000000000, 41.02000000000),
    (-69.16407331100, 40.95597788560),
    (-69.66570385450, 41.69306766380),
    (-69.56000000000, 41.74000000000)
)
''' TSS for Great South Channel '''

# FIX: this hard coding is not going to work in the long run!



def listofpoints2PolygonWKT(aList):
    import StringIO
    buf = StringIO.StringIO()

    buf.write('POLYGON ((')
    for pt in aList[:-1]:
	buf.write(str(pt[0])+' '+str(pt[1])+', ')

    pt = aList[-1]
    buf.write(str(pt[0])+' '+str(pt[1]))

    buf.write('))')
    #print buf.getvalue()

    return buf.getvalue()
    
stellwagenWKT = listofpoints2PolygonWKT(stellwagen)
stellwagen_5nm_WKT = listofpoints2PolygonWKT(stellwagen_5nm)

gscWKT = listofpoints2PolygonWKT(gsc)
gsc_and_tssWKT = listofpoints2PolygonWKT(gsc_and_gsctss)
gsctssWKT = listofpoints2PolygonWKT(gsctss)

def filter_file(infile, outfile, polygonWKT, verbose=False):
    '''
    For messages 1,2, and 3, see if the message is within the bounding box and send it to outfile if it is.

    Polygon should look something like this... 'POLYGON ((-1.0 50.5, -0.5 51.2, 0.3 50.9, -1 50.5))'

    param polygon: bounding region for the query
    type polygon: WKT polygon string
    '''
    import ais.ais_msg_1 as ais_msg_1
    import ais.binary as binary
    try:
        from cartography.geometry import Geometry
    except:
        sys.exit('ERROR: need to install pcl-core for cartography.geometry.Geometry')
    
    poly = Geometry.fromWKT(polygonWKT)
    bbox = poly.envelope()
    minx = bbox.minx  # for speed, throw out points as soon as possible
    maxx = bbox.maxx
    miny = bbox.miny
    maxy = bbox.maxy

    if verbose:
        print 'minLon maxLon minLat maxLat filename'
        print minx, maxx, miny, maxy 

    count = 0
    linenum=0
    for line in infile:
	linenum += 1
	if linenum%1000==0: 
            sys.stderr.write('line '+str(linenum)+' -- count='+str(count)+'\n')
	# Trick: Only handle the first 19 characters since that contains the lon/lat
	txt = line.split(',')[5][:25]
	#print txt
	bv = binary.ais6tobitvec(txt) #line[5][:19]

        # Try to throw out points as soon as possible.  Use float rather than decimal.  faster??  Maybe not
	#lon = ais_msg_1.decodelongitude(bv)
        lon = binary.signedIntFromBV(bv[61:89])/600000.0
        if lon<minx or lon>maxx: continue
        #print 'close1:',lon
	#lat = ais_msg_1.decodelatitude(bv)
        lat = binary.signedIntFromBV(bv[89:116])/600000.0
        if lat<miny or lat>maxy: continue

        #print 'close2: POINT ('+str(lon)+' '+str(lat)+')'

	point = Geometry.fromWKT('POINT ('+str(lon)+' '+str(lat)+')')
	inside = point.within(poly)
	if 1==inside:
	    outfile.write(line)
	    count+= 1

    return count

def filter_box(infile, outfile, west, east, lower, upper, verbose=False):
    ''' Do a straight box clip that should be faster than using the WKT.
    Use geographic coordinates what run +/- 180 east west and +/-90
    north south. 

    @bug: Good luck at the +/-180 boundary!

    '''
    assert (upper>lower)
    assert (west<east)
    import ais.ais_msg_1 as ais_msg_1
    import ais.binary as binary

    if verbose:
        print 'xrange:',west,east
        print 'yrange:',lower,upper

    count = 0
    linenum=0
    for line in infile:
	linenum += 1
	if linenum%1000==0: sys.stderr.write('line '+str(linenum)+'\n')
	# Trick: Only handle the first 19 characters since that contains the lon/lat
	txt = line.split(',')[5][:25]
	#print txt
	bv = binary.ais6tobitvec(txt) #line[5][:19]
	lon = float(ais_msg_1.decodelongitude(bv))
	lat = float(ais_msg_1.decodelatitude(bv))

        if west>lon or lon>east:
            #print 'skip on lon',type(west),type(lon),type(east), west>lon,lon>east 
            continue
        if lower>lat or lat>upper:
            continue
        if verbose:
            print 'ACCEPT',lon,lat
        outfile.write(line)
        count+=1

######################################################################
if __name__=='__main__':
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options]",
			    version="%prog "+__version__)

    parser.add_option('-o','--output',dest='outputFilename',default=None,
		      help='Name of the file to write [default: stdout]')

    parser.add_option('-p','--polygon',dest='polygonWKT',default=stellwagenWKT,
		      help='Region to include [default: Stellwagen Bank National Marine Sanctuary]')

    parser.add_option('-5','--stellwagen-5nm',action='store_const'
                      ,dest='polygonWKT'
                      ,const=stellwagen_5nm_WKT,
                      help='Use Stellwagen Bank National Marine Sanctuary, but buffer by 5nm')


    parser.add_option('-g','--gsc-only',action='store_const'
                      ,dest='polygonWKT'
                      ,const=gscWKT,
                      help='Use Great South Channel')

    parser.add_option('-G','--gsc-and-tss',action='store_const'
                      ,dest='polygonWKT'
                      ,const=gsc_and_tssWKT,
                      help='Use Great South Channel and Traffic Separation Zone')

    parser.add_option('--gsc-tss',action='store_const'
                      ,dest='polygonWKT'
                      ,const=gsctssWKT,
                      help='Use Traffic Separation Zone for Great South Channel')



    parser.add_option('-b','--box',dest='useBox',default=False,action='store_true'
                      ,help='Use a faster bounding box search algorithm')

    parser.add_option('-x','--lon-min', dest='lonMin', type='float', default=-77
                      ,help=' [default: %default]')
    parser.add_option('-X','--lon-max', dest='lonMax', type='float', default=-75.75
                      ,help=' [default: %default]')

    parser.add_option('-y','--lat-min', dest='latMin', type='float', default=36.6
                      ,help=' [default: %default]')
    parser.add_option('-Y','--lat-max', dest='latMax', type='float', default=37.25
                      ,help=' [default: %default]')

    parser.add_option('-v','--verbose',dest='verbose',default=False,action='store_true'
                      ,help='Make the program be verbose')

    (options,args) = parser.parse_args()




    outFile = sys.stdout
    if None != options.outputFilename: outFile = open(options.outputFilename,'w')

    if options.useBox:
        x = options.lonMin; X = options.lonMax
        y = options.latMin; Y = options.latMax
        if verbose: print 'using bbox',x,X,'    ',y,Y
        if len(args)==0:
            count = filter_box(sys.stdin,outFile,x,X,y,Y,options.verbose)
            if (options.verbose): sys.stderr.write('Found points inside: '+str(count)+'\n')
        else:
            for filename in args:
                if (options.verbose): sys.stderr.write('Working on file: '+filename+'\n')
                count = filter_box(open(filename),outFile,x,X,y,Y,options.verbose)
                if (options.verbose): sys.stderr.write('Found points inside: '+str(count)+'\n')
        sys.exit(0)

    if options.verbose:
	sys.stderr.write('WKT:\n  '+options.polygonWKT+'\n')


    if len(args)==0:
	count = filter_file(sys.stdin,outFile,options.polygonWKT,options.verbose)
	if (options.verbose): sys.stderr.write('Found points inside: '+str(count)+'\n')
    else:
	for filename in args:
	    if (options.verbose): sys.stderr.write('Working on file: '+filename+'\n')
	    count = filter_file(open(filename),outFile,options.polygonWKT,options.verbose)
	    if (options.verbose): sys.stderr.write('Found points inside: '+str(count)+'\n')

