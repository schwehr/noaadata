#!/usr/bin/env python
__version__ = '$Revision: 13270 $'.split()[1]
__date__ = '$Date: 2010-03-11 14:50:30 -0500 (Thu, 11 Mar 2010) $'.split()[1]
__author__ = 'Kurt Schwehr'
__doc__="""
Privide a class to allow laying ship tracks down into a grid.

@requires: U{epydoc<http://epydoc.sourceforge.net/>} > 3.0alpha3
@requires: U{numpy<http://numpy.scipy.org/>}

@author: """+__author__+"""
@version: """ + __version__ +"""
@var __date__: Date of last svn commit
@undocumented: __version__ __author__ __doc__ parser
@status: under development
@license: GPL v2
@since: 2007-Jul-29
@todo: allow for non-square grid cells
@see: U{Tentative numpy tutorial<http://www.scipy.org/Tentative_NumPy_Tutorial>}
"""

from math import *
import sys
import traceback
import numpy

def distance(x1,y1,x2,y2):
    return sqrt( (x2-x1)*(x2-x1) + (y2-y1)*(y2-y1) )

def distancePt(p1,p2):
    return sqrt( (p2[0]-p1[0])*(p2[0]-p1[0]) + (p2[1]-p1[1])*(p2[1]-p1[1]) )

def almostEqual(a,b,epsilon=0.000001):
    if (a<b+epsilon) and (a>b-epsilon): return True
    return False

def inRange(value,a,b):
    assert a<b
    if value<a: return False
    if value>b: return False
    return True

def inBoundingBox(x,y,x0,y0,x1,y1):
    '''
    x,y in within or on the bounding box
    '''
    assert x0<=x1
    assert y0<=y1
    if x<x0 or x>x1: return False
    if y<y0 or y>y1: return False
    return True

def wktLine2list(track):
    '''
    convert a well know text line to a list of points where
    each point is a tuple


    SELECT AsText(Transform(track,32619)) FROM tpath WHERE id=33;

    >>> wktLine2list("LINESTRING(376596 4674402,378419 4668775,376569 4668059)")
    [(376596.0, 4674402.0), (378419.0, 4668775.0), (376569.0, 4668059.0)]
    '''
    start=track.find('(')
    end  =track.rfind(')')
    pointStrings = track[start+1:end].split(',')
    list = [ (float(pt.split()[0]),float(pt.split()[1])) for pt in pointStrings ]
    return list


def writeMultisegline2Gnuplot(outfile,multisegLine,name=None):
    '''
    Convert a multisegment line data structure to gnuplot usable line
    '''
    o = outfile
    if name is not None: o.write('# '+name+'\n')
    for seg in multisegLine:
        for axis in seg:
            o.write(str(seg[0])+' '+str(seg[1])+' 0.\n')
        o.write('\n')
    #o.write('\n')

def writeMultiseglineWithCrossings2Gnuplot(outfile,multisegLine,name=None,field=3):
    '''
    lens [((0, 0), 0.0, 0.24874371859296396, 0.99001249960545123), ((0, 1), 0.24874371859296396, 0.5, 1.0000126258640831), ((1, 2), 0.5, 0.75125628140703049, 1.0000126258640547), ((1, 3), 0.75125628140703049, 1.0, 0.99001249960547977)]
    @param field: 1..3 where 3 is the distance, 1 and 2 are the fractions
    '''

    o = outfile
    if name is not None: o.write('# '+name+'\n')
    for seg in multisegLine:
        o.write(str(seg[0][0])+' '+str(seg[0][1])+' '+str(seg[field])+'\n\n')
    o.write('\n')


######################################################################

gridTypes = [
    'occurrence'
    ,'distance'
    ,'distanceWeightedSpeed'
    ]

class Grid:
    '''
    Provide a grid data structure.  Will resize up to include the full
    range on the max size if not an interger size of stepSize.  Units are
    whatever you desire.  It is up to you to project them.

    0,0 is at the lower left and (xNumCells-1,yNumCells-1) is the upper right cell
    '''
    epsilon = .000001
    def __init__(self,minx,miny,maxx,maxy,stepSize,gridType='occurrence',verbose=False):
        ''' Prepare a grid.
        Readjust the grid such that the stepSize divides evenly into the ranges.
        Compute and cache the number of cells.
        '''
        self.minx=minx
        self.miny=miny
        self.maxx=maxx
        self.maxy=maxy
        self.verbose = verbose
        stepSize=float(stepSize)

        print >> sys.stderr, 'gridtype:',gridType
        assert gridType in gridTypes
        self.gridType = gridType

        if verbose:
            print '     == IN Params =='
            print '     x:',minx,maxx
            print '     y:',miny,maxy
            print '  step:',stepSize

        assert(minx<maxx)
        assert(miny<maxy)
        assert(stepSize>0)
        self.stepSize = stepSize
        if (maxx-minx)/stepSize > floor((maxx-minx)/stepSize)+self.epsilon:
            self.maxx = minx + stepSize*floor((maxx-minx)/stepSize) + stepSize
        #self.maxx=maxx

        if (maxy-miny)/stepSize > floor((maxy-miny)/stepSize)+self.epsilon:
            self.maxy = miny + stepSize*floor((maxy-miny)/stepSize) + stepSize
        #self.maxy=maxy

        if verbose:
            print ' Range changes:'
            print '   maxx:',maxx,'->',self.maxx
            print '   maxy:',maxy,'->',self.maxy

        self.xNumCells = int(ceil((self.maxx-self.minx)/self.stepSize))
        self.yNumCells = int(ceil((self.maxy-self.miny)/self.stepSize))

        if verbose:
            print '       step size   num cells     deltaMeters'
            print '   x: ',self.stepSize,'    ->',self.xNumCells, '       ', self.maxx - self.minx
            print '   y: ',self.stepSize,'    ->',self.yNumCells, '       ', self.maxy - self.miny

        # FIX: why should I have to do add +1?  Rounding/edge error?
        # Will this cause errors down the road in other functions?

        if gridType=='occurrence':
            self.grid=numpy.zeros((self.xNumCells+1,self.yNumCells+1),dtype=int)
        else:
            self.grid=numpy.zeros((self.xNumCells+1,self.yNumCells+1),dtype=float)

    def describe(self):
        print ' === GRID === '
        print '   Bounds   ... (%.2f,%.2f) -> (%.2f,%.2f)'%(self.minx,self.miny,self.maxx,self.maxy)
        print '   Width    ...',self.xNumCells
        print '   Height   ...',self.yNumCells
        print '   CellSize ...',self.stepSize

    def getCell(self,x,y,verbose=False):
        '@return: the i,j of the cell containing this coordinate'
        i = int(floor( (x-self.minx)/self.stepSize ))
        j = int(floor( (y-self.miny)/self.stepSize ))
        if verbose: print x,y,'->',i,j, (x-self.miny), self.stepSize
        return i,j

    def getCellCenter(self,i,j):
        '''@param i: the horizonal cell count from the left starting at 0
        @return the x,y of the center of specified cell'''
        x = self.minx + self.stepSize * i + 0.5*self.stepSize
        y = self.miny + self.stepSize * j + 0.5*self.stepSize
        return x,y

    def getLineCells2pt(self, p1, p2, verbose=False):
        return self.getLineCells(p1[0],p1[1],p2[0],p2[1],verbose)


    def getLineCellsWithCrossingsPts(self, p1, p2, verbose=False):
        return self.getLineCellsWithCrossings(p1[0],p1[1],p2[0],p2[1])

    def getLineCellsWithCrossings(self, x0,y0, x1,y1,verbose=False):
        '''
        Scan convert a single line segment with two vertices.

        Used for when we need to calculated paraeters off the line to
        add a value to the cell.  e.g. distance or speed wieghted by
        distance.

        A line inside a cell returns the cell, 0., 1., and the distance

        @return: a list of (cell(an i,j), startFrac, endFrac, distance) for a line
        @todo: make this actually be fast
        @todo: switch to delta Y for N-S lines
        '''
        if verbose: print '\n\n===============\n   getLineCells',x0,y0, x1,y1
        #from IPython.Shell import IPShellEmbed
        #ipshell = IPShellEmbed(argv=[])
        #ipshell()

        # only scan left to right direction
        flippedX = False
        if x0>x1:
            if verbose: print 'flipping X'
            x0,y0,x1,y1=x1,y1,x0,y0
            flippedX = True

        startCell = self.getCell(x0,y0,verbose)
        endCell   = self.getCell(x1,y1,verbose)
        if verbose: print 'cellrange',startCell,endCell,x0,y0,'->',x1,y1

        # just one cell
        if startCell==endCell:
            dist = distance(x0,y0, x1,y1)
            return ( (startCell,0.,1.,dist),)

        dx = x1-x0
        dy = y1-y0
        m = slope = (dy/float(dx))
        b = y0 - slope * x0
        # Else, we have have to cross diagonally

        stepSize = self.stepSize
        minx=self.minx; maxx=self.maxx
        miny=self.miny; maxy=self.maxy

        flippedY = False
        if y0>y1:
            if verbose: print 'flipping Y'
            flippedY = True
            y0,y1=y1,y0
        y_first_ycrossing = miny + ceil ((y0 - miny)/stepSize) * stepSize
        y_last_ycrossing  = miny + floor((y1 - miny)/stepSize) * stepSize
        steps = int( ceil((y_last_ycrossing - y_first_ycrossing)/stepSize + 1))

        if verbose:
            print 'steps y',y_first_ycrossing,y_last_ycrossing ,'->',steps

        x_ycrossings = [   ]
        for step in range(steps):
            y = step*stepSize + y_first_ycrossing
            x = (y-b)/m
            x_ycrossings.append(x)
        del y_first_ycrossing
        del y_last_ycrossing

        if verbose: print 'x_ycrossings',x_ycrossings

        x_first_xcrossing = minx + ceil((x0 - minx)/stepSize) * stepSize
        if verbose:
            print '  x_xcross params:', x0,minx, stepSize, ceil((x0 - minx)/stepSize),
            print '--->', x_first_xcrossing
        x_last_xcrossing  = minx + floor((x1 - minx)/stepSize) * stepSize

        steps = int( ceil((x_last_xcrossing - x_first_xcrossing)/float(stepSize) +1)  )
        if verbose:
            print 'steps2',x_first_xcrossing,x_last_xcrossing ,'->',steps
            print 'steps2',x_last_xcrossing - x_first_xcrossing, (x_last_xcrossing - x_first_xcrossing)/stepSize
        x_xcrossings = [   ]
        for step in range(steps):
            x = step*stepSize + x_first_xcrossing
            if verbose: print '  X:', step,stepSize,x_first_xcrossing
            x_xcrossings.append(x)
        if verbose: print 'x_xcrossings',x_xcrossings

        crossings = x_ycrossings+x_xcrossings
        if flippedX:
            if verbose: print 'reverse sort crossings'
            crossings.sort(reverse=True)
        else:
            crossings.sort()
        if verbose: print '\ncrossings',crossings

        # remove duplicates
        cnew=[crossings[0],]
        for i in range(1,len(crossings)):
            #if crossings[i]==crossings[i-1]: continue # Faster... first?
            if almostEqual(crossings[i],crossings[i-1]): continue
            cnew.append(crossings[i])
        #print crossings,'->',cnew
        if verbose:
            print 'orig crossings:',crossings
            print ' new crossings:',cnew
        crossings=cnew

        # Be careful which side to add that start cell
        cells=[]
        if not flippedX:
            cells = [startCell,]

        fractions = [0.,]

        totXRange = x1 - x0
        print 'xrange',totXRange , x1,x0
        for x in crossings:
            fractions.append( (x-x0) / totXRange )
            x = x+0.0001
            y = m * x + b
            cells.append(self.getCell(x,y))
        if flippedX:
            cells.append(startCell)

        fractions.append(1.)
        print 'fractions',fractions
        distances = []
        for i in range(0,len(fractions)-1):
            x = x0 + totXRange * fractions[i]
            y = m * x + b
            p1 = (x,y)
            x = x0 + totXRange * fractions[i+1]
            y = m * x + b
            p2 = (x,y)

            distances.append(distancePt(p1,p2))
        print 'dists',distances


        assert(len(cells)>1)
        # Make sure the line does not extend beyond the cell range
        minCellX = min(startCell[0],endCell[0])
        maxCellX = max(startCell[0],endCell[0])
        minCellY = min(startCell[1],endCell[1])
        maxCellY = max(startCell[1],endCell[1])

        print 'minmaxX',minCellX,maxCellX
        print 'minmaxY',minCellY,maxCellY


        # if rounding errors happen to push us out, then toss a cell

        if not inBoundingBox(cells[0][0],cells[0][1],minCellX,minCellY,maxCellX,maxCellY):
            if verbose: print 'chomp front'
            assert False # need to also remove from the fractions
            cells=cells[1:]
        if not inBoundingBox(cells[-1][0],cells[-1][1],minCellX,minCellY,maxCellX,maxCellY):
            if verbose: print 'chomp tail'
            assert False # need to also remove from the fractions
            cells=cells[:-1]

        #c = cells[0]
        #if not inRange(c[0],minCellX,maxCellX) or not inRange(c[1],minCellY,maxCellY):
        #    if verbose: print 'chomp front'
        #    cells=cells[1:]
        #c = cells[-1]
        #if not inRange(c[0],minCellX,maxCellX) or not inRange(c[1],minCellY,maxCellY):
        # 
        #    cells=cells[:-1]

        assert(len(cells)>1)
        if verbose: print cells
        #return cells
        r = []
        print 'lens',
        assert len(fractions)==len(cells)+1
        assert len(cells)==len(distances)
        for i in range(len(cells)):
            r.append((cells[i],fractions[i],fractions[i+1],distances[i]))
        return r

    ######################################################################
    def getLineCells(self, x0,y0, x1,y1,verbose=False):
        '''
        Scan convert a single line segment with two vertices.
        @return: a list of cells for a line
        @todo: make this actually be fast
        '''
        if verbose: print '\n\n===============\n   getLineCells',x0,y0, x1,y1
        #from IPython.Shell import IPShellEmbed
        #ipshell = IPShellEmbed(argv=[])
        #ipshell()

        # only scan left to right direction
        flippedX = False
        if x0>x1:
            if verbose: print 'flipping X'
            x0,y0,x1,y1=x1,y1,x0,y0
            flippedX = True

        startCell = self.getCell(x0,y0,verbose)
        endCell   = self.getCell(x1,y1,verbose)
        if verbose: print 'cellrange',startCell,endCell,x0,y0,'->',x1,y1

        # Vertical Line or just one cell?
        if startCell[0]==endCell[0]:
            yFlipped=False
            if startCell[1]>endCell[1]:
                startCell,endCell=endCell,startCell
                yFlipped=True
            if verbose:
                print 'CASE vert or single cell', startCell[1],endCell[1]+1
            i = startCell[0]
            cells = [ (i,j) for j in range(startCell[1],endCell[1]+1) ]
            if yFlipped:
                cells.reverse()
            return cells

        # Horizontal Line?  Do this fast
        if startCell[1]==endCell[1]:
            if verbose: print 'CASE horiz'
            j = startCell[1]
            #print range(startCell[0],endCell[0]+1)
            cells = [ (i,j) for i in range(startCell[0],endCell[0]+1) ]
            if flippedX:
                # Line goes from right to left
                if verbose: print 'reversing based on x (horiz line)'
                cells.reverse()
            #print 'going to return',cells
            return cells

        if verbose: print 'CASE not easy... must calculate'

        dx = x1-x0
        dy = y1-y0
        m = slope = (dy/float(dx))
        b = y0 - slope * x0
        # Else, we have have to cross diagonally

        stepSize = self.stepSize
        minx=self.minx; maxx=self.maxx
        miny=self.miny; maxy=self.maxy

        flippedY = False
        if y0>y1:
            if verbose: print 'flipping Y'
            flippedY = True
            y0,y1=y1,y0
        y_first_ycrossing = miny + ceil ((y0 - miny)/stepSize) * stepSize
        y_last_ycrossing  = miny + floor((y1 - miny)/stepSize) * stepSize
        steps = int( ceil((y_last_ycrossing - y_first_ycrossing)/stepSize + 1))

        if verbose:
            print 'steps y',y_first_ycrossing,y_last_ycrossing ,'->',steps

        x_ycrossings = [   ]
        for step in range(steps):
            y = step*stepSize + y_first_ycrossing
            x = (y-b)/m
            x_ycrossings.append(x)
        del y_first_ycrossing
        del y_last_ycrossing

        if verbose: print 'x_ycrossings',x_ycrossings

        x_first_xcrossing = minx + ceil((x0 - minx)/stepSize) * stepSize
        if verbose:
            print '  x_xcross params:', x0,minx, stepSize, ceil((x0 - minx)/stepSize),
            print '--->', x_first_xcrossing
        x_last_xcrossing  = minx + floor((x1 - minx)/stepSize) * stepSize

        steps = int( ceil((x_last_xcrossing - x_first_xcrossing)/float(stepSize) +1)  )
        if verbose:
            print 'steps2',x_first_xcrossing,x_last_xcrossing ,'->',steps
            print 'steps2',x_last_xcrossing - x_first_xcrossing, (x_last_xcrossing - x_first_xcrossing)/stepSize
        x_xcrossings = [   ]
        for step in range(steps):
            x = step*stepSize + x_first_xcrossing
            if verbose: print '  X:', step,stepSize,x_first_xcrossing
            x_xcrossings.append(x)
        if verbose: print 'x_xcrossings',x_xcrossings

        crossings = x_ycrossings+x_xcrossings
        if flippedX:
            if verbose: print 'reverse sort crossings'
            crossings.sort(reverse=True)
        else:
            crossings.sort()
        if verbose: print '\ncrossings',crossings

        # remove duplicates
        cnew=[crossings[0],]
        for i in range(1,len(crossings)):
            #if crossings[i]==crossings[i-1]: continue # Faster... first?
            if almostEqual(crossings[i],crossings[i-1]): continue
            cnew.append(crossings[i])
        #print crossings,'->',cnew
        if verbose:
            print 'orig crossings:',crossings
            print ' new crossings:',cnew
        crossings=cnew

        # Be careful which side to add that start cell
        cells=[]
        if not flippedX:
            cells = [startCell,]
        for x in crossings:
            x = x+0.0001
            y = m * x + b
            cells.append(self.getCell(x,y))
        if flippedX:
            cells.append(startCell)

        assert(len(cells)>1)
        # Make sure the line does not extend beyond the cell range
        minCellX = min(startCell[0],endCell[0])
        maxCellX = max(startCell[0],endCell[0])
        minCellY = min(startCell[1],endCell[1])
        maxCellY = max(startCell[1],endCell[1])

        c = cells[0]
        if not inRange(c[0],minCellX,maxCellX) or not inRange(c[1],minCellY,maxCellY):
            if verbose: print 'chomp front'
            cells=cells[1:]
        c = cells[-1]
        if not inRange(c[0],minCellX,maxCellX) or not inRange(c[1],minCellY,maxCellY):
            if verbose: print 'chomp tail'
            cells=cells[:-1]

        assert(len(cells)>1)
        if verbose: print cells
        return cells

    def getMultiSegLineCells(self,multiSegLine,verbose=False):
        '''
        Return the cells for a multi vertex line.  Handles the doubling that will happen at each endpoint
        @param multiSegLine: ((x1,y1),(x2,y2),(x3,y3),(x4,y4)...)
        '''
        assert len(multiSegLine)>1

        cells = self.getLineCells2pt(multiSegLine[0],multiSegLine[1])
        if len(multiSegLine)==2:
            return cells
        for i in range(1,len(multiSegLine)-1):
            # Make sure to skip the first cell on each additional segment
            newCells = self.getLineCells2pt(multiSegLine[i],multiSegLine[i+1])
            if len(newCells)<1:
                print 'ACK... must have at least one cell!!! ERROR fail death'
                print '     ',i,multiSegLine[i],multiSegLine[i+1]
                print '     ',newCells
                assert False
            if newCells[0] == cells[-1]:
                cells+=newCells[1:]
            else:
                cells+=newCells[:-1]
        return cells


    def getMultiSegLineCellsWithCrossings(self,multiSegLine,verbose=False):
        '''
        Return the cells for a multi vertex line.  Returns distances
        within cells, so that doubling is not an issue

        @param multiSegLine: ((x1,y1),(x2,y2),(x3,y3),(x4,y4)...)
        @return: list of (cell, startFrac, endFrac, distance)
        '''
        assert len(multiSegLine)>1

        #cells = getLineCellsWithCrossingsPts(multiSegLine[0],multiSegLine[1])
        cells=[]
        for i in range(len(multiSegLine)-1):
            newCells = self.getLineCellsWithCrossingsPts(multiSegLine[i],multiSegLine[i+1])
            cells+=newCells
        return cells


    def writeLayoutGnuplot(self,filename):
        'Write out the grid lines as gnuplot dat file'
        o = file(filename,'w')
        # Horizonal lines
        minxStr = str(self.minx)+' '
        maxxStr = str(self.maxx)+' '
        for yCell in range(self.yNumCells+1):
            yStr = str(self.miny + yCell*self.stepSize)+' 0\n'
            o.write(minxStr+yStr)
            o.write(maxxStr+yStr+'\n')
        # Vertical Lines
        minyStr = ' '+str(self.miny)+' 0\n'
        maxyStr = ' '+str(self.maxy)+' 0\n'
        for xCell in range(self.xNumCells+1):
            xStr = str(self.minx + xCell*self.stepSize)
            o.write(xStr+minyStr)
            o.write(xStr+maxyStr+'\n')


    def addMultiSegLine(self,multiSegLine,verbose=False):
        grid=self.grid
        #print '\naddMultiSegLine line ',multiSegLine
        if verbose: sys.stderr.write('addMultiSegLine cell inserts: (using type '+self.gridType+')\n')

        if 'occurrence' == self.gridType:
            cells = self.getMultiSegLineCells(multiSegLine)
            for cell in cells:
                try:
                    grid[cell[0],cell[1]]+=1
                    if verbose:
                        print '  ',cell[0],cell[1],grid[cell[0],cell[1]]
                except Exception, e:
                    sys.stderr.write('    Exception:' + str(type(Exception))+'\n')
                    sys.stderr.write('    Exception args:'+ str(e)+'\n')
                    traceback.print_exc(file=sys.stderr)

                    print 'error on grid cell inc:',str(multiSegLine)[:40],'...'
                    print 'CRAP... grid failure'
                    print '  ',cell, self.xNumCells, self.yNumCells
                    assert False
        elif 'distance' == self.gridType:
            result = self.getMultiSegLineCellsWithCrossings(multiSegLine)
            if verbose: sys.stderr.write(str(result)+'\n')
            for seg in result:
                # (0, 0), 0.0, 0.24874371859296465, 0.99124918032832443)
                cell = seg[0]
                dist = seg[3]
                print 'adding:', cell, dist
                grid[cell[0],cell[1]] += dist
            print grid
        elif 'distanceWeightedSpeed' == self.gridType:
            assert False
        else:
            assert False

    def writeCellsGnuplot(self,filename,useSquares=False):
        '''
        @param useSquares: if true then write out the height of each cell as a square.  False then it writes a point
        '''
        assert useSquares==False # FIX: implement this feature
        grid = self.grid
        o = file(filename,'w')
        for i in range(grid.shape[0]):
            for j in range(grid.shape[1]):
                x,y = self.getCellCenter(i,j)
                o.write('%f %f %f\n' % (x,y,grid[i,j]))


    def writeArcAsciiGrid(self,filename):
        g = self.grid
        o = file(filename,'w')
        o.write('ncols        '+str(self.xNumCells)+'\n')
        o.write('nrows        '+str(self.yNumCells)+'\n')
        o.write('xllcorner    '+str(self.minx)+'\n')
        o.write('yllcorner    '+str(self.miny)+'\n')
        o.write('cellsize     '+str(self.stepSize)+'\n')
        for j in range(self.yNumCells-1,-1,-1):
            #print j
            zPoints=[]
            for i in range(self.xNumCells):
                zPoints.append('%3d' % (g[i,j]))
            o.write(' '.join(zPoints))
            o.write('\n')

############################################################
if __name__=='__main__':
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options]",version="%prog "+__version__)
    parser.add_option('--doc-test',dest='doctest',default=False,action='store_true',
                      help='run the documentation tests')
    parser.add_option('--unit-test',dest='unittest',default=False,action='store_true',
                      help='run the unit tests')
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
    if not success: sys.exit('Something Failed')
    del success # Hide success from epydoc

    if options.unittest:
        sys.argv = [sys.argv[0]]
        if options.verbose: sys.argv.append('-v')
        import unittest
        from grid_tests import *
        unittest.main()
