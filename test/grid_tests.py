#!/usr/bin/env python

__version__ = '$Revision: 4791 $'.split()[1]
__date__ = '$Date: 2007-01-04 $'.split()[1]
__author__ = 'Kurt Schwehr'

__doc__="""
Unit tests for the grid class

@requires: U{epydoc<http://epydoc.sourceforge.net/>} > 3.0alpha3

@author: """+__author__+"""
@version: """ + __version__ +"""
@var __date__: Date of last svn commit
@undocumented: __version__ __author__ __doc__ parser
@status: under development
@license: GPL v2
@since: 2007-Jul-29


@todo: allow for non-square grid cells
"""

from grid import Grid

import unittest
#import unittest as bogus_unittest
import bogus_unittest
#import unittest as bogus_unittest  # if you want to quick turn them back on

######################################################################
# UNIT TESTING
######################################################################

    

class TestGrid(bogus_unittest.TestCase):
#class TestGrid(unittest.TestCase):
    def testInit10(self):
        'init with unit grid'
        g = Grid(0,0, 1,1, 1)
        self.failUnlessEqual(g.xNumCells,1)
        self.failUnlessEqual(g.yNumCells,1)
        self.failUnlessAlmostEqual(g.maxx,1)
        self.failUnlessAlmostEqual(g.maxy,1)

    def testInit20(self):
        'init with 1.1x1 grid'
        g = Grid(0,0, 1.1,1, 1)
        self.failUnlessEqual(g.xNumCells,2)
        self.failUnlessEqual(g.yNumCells,1)
        self.failUnlessAlmostEqual(g.maxx,2)
        self.failUnlessAlmostEqual(g.maxy,1)

    def testInit21(self):
        'init with 1x1.1 grid'
        #g = Grid(0,1,0,1.1,1)
        g = Grid(0,0, 1,1.1, 1)
        self.failUnlessEqual(g.xNumCells,1)
        self.failUnlessEqual(g.yNumCells,2)
        self.failUnlessAlmostEqual(g.maxx,1)
        self.failUnlessAlmostEqual(g.maxy,2)

    def testInit30(self):
        'init with offset from unit boundaries'
        #g = Grid(.5,2.5,1.5,4.5,1)
        g = Grid(.5,1.5,   2.5,4.5,   1)
        self.failUnlessEqual(g.xNumCells,2)
        self.failUnlessEqual(g.yNumCells,3)
        self.failUnlessAlmostEqual(g.minx,.5)
        self.failUnlessAlmostEqual(g.maxx,2.5)
        self.failUnlessAlmostEqual(g.miny,1.5)
        self.failUnlessAlmostEqual(g.maxy,4.5)
        g.writeLayoutGnuplot('tmp_.5_2.5_1.5_4.5_step1.dat')

    def testInit40(self):
        'init with crossing the origin'
        g = Grid(-.5,-1.5,  .5,4.5,  1)
        self.failUnlessEqual(g.xNumCells,1)
        self.failUnlessEqual(g.yNumCells,6)
        self.failUnlessAlmostEqual(g.minx,-.5)
        self.failUnlessAlmostEqual(g.maxx,.5)
        self.failUnlessAlmostEqual(g.miny,-1.5)
        self.failUnlessAlmostEqual(g.maxy,4.5)

    def testInit50(self):
        'init with non unit step sizes'
        g = Grid(0,0,1,1,.1)
        self.failUnlessEqual(g.xNumCells,10)
        self.failUnlessEqual(g.yNumCells,10)
        self.failUnlessAlmostEqual(g.maxx,1)
        self.failUnlessAlmostEqual(g.maxy,1)

    def testInit50(self):
        'init with non unit step sizes, non-square'
        g = Grid(0,0.1,   1.01,1,  .1)
        self.failUnlessEqual(g.xNumCells,11)
        self.failUnlessEqual(g.yNumCells,9)
        self.failUnlessAlmostEqual(g.maxx,1.1)
        self.failUnlessAlmostEqual(g.miny,.1)
        self.failUnlessAlmostEqual(g.maxy,1)

    def testInit51(self):
        'init with non unit step sizes, non-square'
        g = Grid(0.1,0,  1,1.01, .1)
        self.failUnlessEqual(g.xNumCells,9)
        self.failUnlessEqual(g.yNumCells,11)
        self.failUnlessAlmostEqual(g.minx,.1)
        self.failUnlessAlmostEqual(g.maxx,1)
        self.failUnlessAlmostEqual(g.maxy,1.1)

    def testJ_GetCell10(self):
        'getCell 1x1'
        g = Grid(0,0, 1,1,  1);
        i,j = g.getCell(.1,.1)
        self.failUnlessEqual(i,0)
        self.failUnlessEqual(j,0)

    def testJ_GetCell20(self):
        'getCell 1x10'
        g = Grid(0,0,  1,10,  1);
        i,j = g.getCell(.1,.1)
        self.failUnlessEqual(i,0)
        self.failUnlessEqual(j,0)
        i,j = g.getCell(.1,1.1)
        self.failUnlessEqual(i,0)
        self.failUnlessEqual(j,1)
        i,j = g.getCell(.1,9.1)
        self.failUnlessEqual(i,0)
        self.failUnlessEqual(j,9)

    def testJ_GetCell30(self):
        'getCell 10x1'
        g = Grid(0,0,  10,1,  1);
        i,j = g.getCell(.1,.1)
        self.failUnlessEqual(i,0)
        self.failUnlessEqual(j,0)
        i,j = g.getCell(1.1,.1)
        self.failUnlessEqual(i,1)
        self.failUnlessEqual(j,0)
        i,j = g.getCell(9.1,.1)
        self.failUnlessEqual(i,9)
        self.failUnlessEqual(j,0)


    def testJ_GetCell40(self):
        'getCell -10 to 10 x1 '
        g = Grid(-10,0,  10,1,  1);
        i,j = g.getCell(-9.1,.1)
        self.failUnlessEqual(i,0)
        self.failUnlessEqual(j,0)
        i,j = g.getCell(-.1,.1)
        self.failUnlessEqual(i,9)
        self.failUnlessEqual(j,0)
        i,j = g.getCell(9.1,.1)
        self.failUnlessEqual(i,19)
        self.failUnlessEqual(j,0)


    def testJ_GetCell50(self):
        'getCell 1x -10 to 0 '
        g = Grid(0,-10,  1,0,  1);
        i,j = g.getCell(.1,-9.1,)
        self.failUnlessEqual(i,0)
        self.failUnlessEqual(j,0)
        i,j = g.getCell(.1,-.1)
        self.failUnlessEqual(i,0)
        self.failUnlessEqual(j,9)
        i,j = g.getCell(.1,9.1)   # yeah... this is out of the grid
        self.failUnlessEqual(i,0)
        self.failUnlessEqual(j,19)


    def testK_GetCellCenter10(self):
        'getCellCenter 1x1'
        g = Grid(0,0,  1,1,  1)
        x,y = g.getCellCenter(0,0)
        self.failUnlessAlmostEqual(x,.5)
        self.failUnlessAlmostEqual(y,.5)

    def testK_GetCellCenter20(self):
        'getCellCenter 10x1'
        g = Grid(0,0,  10,1,  1)
        x,y = g.getCellCenter(0,0)
        self.failUnlessAlmostEqual(x,.5)
        self.failUnlessAlmostEqual(y,.5)
        x,y = g.getCellCenter(5,0)
        self.failUnlessAlmostEqual(x,5.5)
        self.failUnlessAlmostEqual(y,.5)
        x,y = g.getCellCenter(9,0)
        self.failUnlessAlmostEqual(x,9.5)
        self.failUnlessAlmostEqual(y,.5)

    def testK_GetCellCenter30(self):
        'getCellCenter 1x10'
        g = Grid(0,0,  1,10,  1)
        x,y = g.getCellCenter(0,0)
        self.failUnlessAlmostEqual(x,.5)
        self.failUnlessAlmostEqual(y,.5)
        x,y = g.getCellCenter(0,5)
        self.failUnlessAlmostEqual(x,.5)
        self.failUnlessAlmostEqual(y,5.5)
        x,y = g.getCellCenter(0,9)
        self.failUnlessAlmostEqual(x,.5)
        self.failUnlessAlmostEqual(y,9.5)

    def testK_GetCellCenter20(self):
        'getCellCenter 10 (-10 to 0) x1 '
        g = Grid(-10,0,  0,1,  1)
        x,y = g.getCellCenter(0,0)
        self.failUnlessAlmostEqual(x,-9.5)
        self.failUnlessAlmostEqual(y,.5)
        x,y = g.getCellCenter(5,0)
        self.failUnlessAlmostEqual(x,-4.5)
        self.failUnlessAlmostEqual(y,.5)
        x,y = g.getCellCenter(9,0)
        self.failUnlessAlmostEqual(x,-.5)
        self.failUnlessAlmostEqual(y,.5)


    ##############################
    # 1x1 getLineCells
    ##############################
    def testL_GetLineCells010(self):
        'getLineCells 1x1 vertical'
        g = Grid(0,0, 1,1, 1)
        cells = g.getLineCells(.1,.1, .1,.2)
        self.failUnlessEqual(len(cells),1)
        self.failUnlessEqual(cells[0][0],0)
        self.failUnlessEqual(cells[0][1],0)

    def testL_GetLineCells020(self):
        'getLineCells 1x1 horizontal'
        g = Grid(0,0,  1,1, 1)
        cells = g.getLineCells(.1,.1, .2,.1)
        self.failUnlessEqual(len(cells),1)
        self.failUnlessEqual(cells[0][0],0)
        self.failUnlessEqual(cells[0][1],0)

    def testL_GetLineCells030(self):
        'getLineCells 1x1 slope up, gentle'
        g = Grid(0,0,  1,1, 1)
        cells = g.getLineCells(.1,.1, .2,.11)
        self.failUnlessEqual(len(cells),1)
        self.failUnlessEqual(cells[0][0],0)
        self.failUnlessEqual(cells[0][1],0)

    def testL_GetLineCells030(self):
        'getLineCells 1x1 slope up, steep'
        g = Grid(0,0,  1,1, 1)
        cells = g.getLineCells(.1,.1, .2,.3)
        self.failUnlessEqual(len(cells),1)
        self.failUnlessEqual(cells[0][0],0)
        self.failUnlessEqual(cells[0][1],0)

    def testL_GetLineCells040(self):
        'getLineCells 1x1 slope down, gentle'
        g = Grid(0,0,  1,1, 1)
        cells = g.getLineCells(.1,.1, .2,.09)
        self.failUnlessEqual(len(cells),1)
        self.failUnlessEqual(cells[0][0],0)
        self.failUnlessEqual(cells[0][1],0)

    def testL_GetLineCells050(self):
        'getLineCells 1x1 slope down, steep'
        g = Grid(0,0,  1,1, 1)
        cells = g.getLineCells(.1,.4, .2,.09)
        self.failUnlessEqual(len(cells),1)
        self.failUnlessEqual(cells[0][0],0)
        self.failUnlessEqual(cells[0][1],0)

######################################################################
class TestGrid_GetLineCells(bogus_unittest.TestCase):
#class TestGrid_GetLineCells(unittest.TestCase):
    'horiz and vertical runs'
    def testGetLineCells100(self):
        'getLineCells 10x1 horizontal'
        g = Grid(0,0,  10,1, 1)
        cells = g.getLineCells(.1,.1, 9.2,.1)
        self.failUnlessEqual(len(cells),10)
        self.failUnlessEqual(cells[0][0],0)
        self.failUnlessEqual(cells[0][1],0)
        self.failUnlessEqual(cells[-1][0],9)
        self.failUnlessEqual(cells[-1][1],0)


    def testGetLineCells110(self):
        'getLineCells 10x1 horizontal, slight slope up'
        g = Grid(0,0,  10,1, 1)
        cells = g.getLineCells(.1,.5, 9.2,.9)
        self.failUnlessEqual(len(cells),10)
        self.failUnlessEqual(cells[0][0],0)
        self.failUnlessEqual(cells[0][1],0)
        self.failUnlessEqual(cells[-1][0],9)
        self.failUnlessEqual(cells[-1][1],0)

    def testGetLineCells120(self):
        'getLineCells 10x1 horizontal, slight slope down'
        g = Grid(0,0,  10,1, 1)
        cells = g.getLineCells(.1,.5, 9.2,.1)
        self.failUnlessEqual(len(cells),10)
        self.failUnlessEqual(cells[0][0],0)
        self.failUnlessEqual(cells[0][1],0)
        self.failUnlessEqual(cells[-1][0],9)
        self.failUnlessEqual(cells[-1][1],0)

    def testGetLineCells150(self):
        'getLineCells 1x10 vertical'
        g = Grid(0,0,  1,10, 1)
        cells = g.getLineCells(.5,.5, .5,9.1)
        self.failUnlessEqual(len(cells),10)
        self.failUnlessEqual(cells[0][0],0)
        self.failUnlessEqual(cells[0][1],0)
        self.failUnlessEqual(cells[-1][0],0)
        self.failUnlessEqual(cells[-1][1],9)

    def testGetLineCells150(self):
        'getLineCells 1x10 vertical, reverse'
        g = Grid(0,0,  1,10, 1)
        cells = g.getLineCells(.5,9.1, .5,.5)
        self.failUnlessEqual(len(cells),10)
        self.failUnlessEqual(cells[0][0],0)
        self.failUnlessEqual(cells[0][1],9)
        self.failUnlessEqual(cells[-1][0],0)
        self.failUnlessEqual(cells[-1][1],0)

    def testGetLineCells200(self):
        'getLineCells 4x4 len 3 - left-to-right - simple up slope'
        g = Grid(0,0,  4,4, 1)
        cells = g.getLineCells(.9,.1, 1.5,1.1)
        #print 'cells',cells
        self.failUnlessEqual(cells,[(0,0),(1,0),(1,1)])

    def testGetLineCells210(self):
        'getLineCells 4x4 len 3 - left-to-right - simple up slope 2'
        g = Grid(0,0,  4,4, 1)
        cells = g.getLineCells(.5,.9, 1.1,1.5)
        #print 'cells',cells
        self.failUnlessEqual(cells,[(0,0),(0,1),(1,1)])

    def testGetLineCells250(self):
        'getLineCells 4x4 len 3 - left-to-right - simple down slope'
        g = Grid(0,0,  4,4, 1)
        cells = g.getLineCells(.1,1.1, 1.1,.1)
        #print 'cells',cells
        self.failUnlessEqual(cells,[(0,1),(0,0),(1,0)])

    # What happens when we hit a vertex?
    def testGetLineCells260(self):
        'getLineCells 4x4 len 3 - left-to-right - diagonal up'
        g = Grid(0,0,  4,4, 1)
        cells = g.getLineCells(.5,.5, 1.5,1.5)
        self.failUnlessEqual(cells,[(0,0),(1,1)])
        
    # What happens when we hit a vertex?
    def testGetLineCells261(self):
        'getLineCells 4x4 len 3 - left-to-right - diagonal up - end on vertex'
        g = Grid(0,0,  4,4, 1)
        cells = g.getLineCells(.5,.5, 2,2)
        self.failUnlessEqual(cells,[(0,0),(1,1),(2,2)])

    ##############################
    # Right to left tests
    def testGetLineCells300(self):
        'getLineCells 4x4 len 2 - right-to-left - horiz'
        g = Grid(0,0,  4,4, 1)
        cells = g.getLineCells(1.5,.5,  .5,.5)
        self.failUnlessEqual(cells,[(1,0),(0,0)])

    def testGetLineCells310(self):
        'getLineCells 4x4 len 2 - right-to-left - slope down'
        g = Grid(0,0,  4,4, 1)
        cell = g.getCell(1.9,1.1)
        self.failUnlessEqual(cell,(1,1))
        cells = g.getLineCells(1.9,1.1,  .9,.1) # ,verbose=True)
        self.failUnlessEqual(cells,[(1,1),(1,0),(0,0)])

    def testGetLineCells310(self):
        'getLineCells 4x4 len 2 - right-to-left - slope up shallow'
        g = Grid(0,0,  4,4, 1)
        cells = g.getLineCells(1.1,.8,  .1,1.1) # ,verbose=True)
        self.failUnlessEqual(cells,[(1,0),(0,0),(0,1)])

    def testGetLineCells311(self):
        'getLineCells 4x4 len 2 - right-to-left - slope steep'
        g = Grid(0,0,  4,4, 1)
        cells = g.getLineCells(1.1,.1,  .7,1.9) # ,verbose=True)
        self.failUnlessEqual(cells,[(1,0),(0,0),(0,1)])

    def testGetLineCells320(self):
        'getLineCells 4x4 len 2 - right-to-left - diagonal down'
        g = Grid(0,0,  4,4, 1)
        cells = g.getLineCells(1.4,1.4,  .7,.7) # ,verbose=True)
        self.failUnlessEqual(cells,[(1,1),(0,0)])

    def testGetLineCells321(self):
        'getLineCells 4x4 len 2 - right-to-left - diagonal up'
        g = Grid(0,0,  4,4, 1)
        cells = g.getLineCells(1.5,0.5,  .5,1.5) # ,verbose=True)
        self.failUnlessEqual(cells,[(1,0),(0,1)])


######################################################################
# Non zero origin

class TestGrid_GetLineCells_Non0Origin(bogus_unittest.TestCase):
#class TestGrid_GetLineCells_Non0Origin(unittest.TestCase):
    'Use -4,-4 as the origin'
    def testGetLineCells100(self):
        'getLineCells Non 0 Origin - 10x1 horizontal'
        g = Grid(-4,-4,  6,-3, 1)
        cells = g.getLineCells(-3.9,-3.9, 4.2,-3.9)#, verbose=True)
        self.failUnlessEqual(g.xNumCells,10)
        self.failUnlessEqual(g.yNumCells,1)
        self.failUnlessEqual(len(cells),9)
        self.failUnlessEqual(cells[0][0],0)
        self.failUnlessEqual(cells[0][1],0)
        self.failUnlessEqual(cells[-1][0],8)
        self.failUnlessEqual(cells[-1][1],0)

    def testGetLineCells110(self):
        'getLineCells Non 0 Origin - 10x1 horizontal, slight slope up'
        g = Grid(-4,-4,  6,-3, 1)
        cells = g.getLineCells(-3.9,-3.5, 4.2,-3.1)
        self.failUnlessEqual(g.xNumCells,10)
        self.failUnlessEqual(g.yNumCells,1)
        self.failUnlessEqual(len(cells),9)
        self.failUnlessEqual(cells[0][0],0)
        self.failUnlessEqual(cells[0][1],0)
        self.failUnlessEqual(cells[-1][0],8)
        self.failUnlessEqual(cells[-1][1],0)

    def testGetLineCells120(self):
        'getLineCells Non 0 Origin - 10x1 horizontal, slight slope down'
        g = Grid(-4,-4,  6,-3, 1)
        cells = g.getLineCells(-3.9,-3.5, 4.2,-3.9)
        self.failUnlessEqual(g.xNumCells,10)
        self.failUnlessEqual(g.yNumCells,1)
        self.failUnlessEqual(len(cells),9)
        self.failUnlessEqual(cells[0][0],0)
        self.failUnlessEqual(cells[0][1],0)
        self.failUnlessEqual(cells[-1][0],8)
        self.failUnlessEqual(cells[-1][1],0)

    def testGetLineCells150(self):
        'getLineCells Non 0 Origin - 1x10 vertical'
        g = Grid(-4,-4,  -3,6, 1)
        cells = g.getLineCells(-3.5,-3.5, -3.5,5.1)
        self.failUnlessEqual(g.xNumCells,1)
        self.failUnlessEqual(g.yNumCells,10)
        self.failUnlessEqual(len(cells),10)
        self.failUnlessEqual(cells[0][0],0)
        self.failUnlessEqual(cells[0][1],0)
        self.failUnlessEqual(cells[-1][0],0)
        self.failUnlessEqual(cells[-1][1],9)

    def testGetLineCells200(self):
        'getLineCells Non 0 Origin - 4x4 len 3 - left-to-right - simple up slope'
        g = Grid(-4,-4,  0,0, 1)
        cells = g.getLineCells(-3.1,-3.9, -2.5,-2.9)#,verbose=True)
        self.failUnlessEqual(g.xNumCells,4)
        self.failUnlessEqual(g.yNumCells,4)
        self.failUnlessEqual(cells,[(0,0),(1,0),(1,1)])

    def testGetLineCells210(self):
        'getLineCells Non 0 Origin - 4x4 len 3 - left-to-right - simple up slope 2'
        g = Grid(-4,-4,  4,4, 1)
        cells = g.getLineCells(-3.5,-3.1, -2.9,-2.5)
        self.failUnlessEqual(cells,[(0,0),(0,1),(1,1)])

    def testGetLineCells250(self):
        'getLineCells Non 0 Origin - 4x4 len 3 - left-to-right - simple down slope'
        g = Grid(-4,-4,  4,4, 1)
        cells = g.getLineCells(-3.9,-2.9, -2.9,-3.9)
        self.failUnlessEqual(cells,[(0,1),(0,0),(1,0)])

    # What happens when we hit a vertex?
    def testGetLineCells260(self):
        'getLineCells Non 0 Origin - 4x4 len 3 - left-to-right - diagonal up'
        g = Grid(-4,-4,  4,4, 1)
        cells = g.getLineCells(-3.5,-3.5, -2.5,-2.5)
        self.failUnlessEqual(cells,[(0,0),(1,1)])
        
    # What happens when we hit a vertex?
    def testGetLineCells261(self):
        'getLineCells Non 0 Origin - 4x4 len 3 - left-to-right - diagonal up - end on vertex'
        g = Grid(-4,-4,  4,4, 1)
        cells = g.getLineCells(-3.5,-3.5, -2,-2)
        self.failUnlessEqual(cells,[(0,0),(1,1),(2,2)])

    ##############################
    # Right to left tests
    def testGetLineCells300(self):
        'getLineCells Non 0 Origin - 4x4 len 2 - right-to-left - horiz'
        g = Grid(-4,-4,  4,4, 1)
        cells = g.getLineCells(-2.5,-3.5,  -3.5,-3.5)
        self.failUnlessEqual(cells,[(1,0),(0,0)])

    def testGetLineCells310(self):
        'getLineCells Non 0 Origin - 4x4 len 2 - right-to-left - slope down'
        g = Grid(-4,-4,  4,4, 1)
        cell = g.getCell(1.9,1.1)
        self.failUnlessEqual(cell,(1,1))
        cells = g.getLineCells(1.9,1.1,  .9,.1) # ,verbose=True)
        self.failUnlessEqual(cells,[(1,1),(1,0),(0,0)])

    def testGetLineCells310(self):
        'getLineCells Non 0 Origin - 4x4 len 2 - right-to-left - slope up shallow'
        g = Grid(-4,-4,  4,4, 1)
        cells = g.getLineCells(-2.9,-3.2,  -3.9,-2.9) # ,verbose=True)
        self.failUnlessEqual(cells,[(1,0),(0,0),(0,1)])

    def testGetLineCells311(self):
        'getLineCells Non 0 Origin - 4x4 len 2 - right-to-left - slope steep'
        g = Grid(-4,-4,  4,4, 1)
        cells = g.getLineCells(-2.9,-3.9,  -3.3,-2.1) # ,verbose=True)
        self.failUnlessEqual(cells,[(1,0),(0,0),(0,1)])

    # right-to-left - diagonal down
    def testGetLineCells320(self):
        'getLineCells Non 0 Origin - 4x4 len 2 - right-to-left - diagonal down'
        g = Grid(-4,-4,  4,4, 1)
        cells = g.getLineCells(-2.6,-2.6,  -3.3,-3.3) # ,verbose=True)
        self.failUnlessEqual(cells,[(1,1),(0,0)])

    def testGetLineCells321(self):
        'getLineCells Non 0 Origin - 4x4 len 2 - right-to-left - diagonal up'
        g = Grid(-4,-4,  4,4, 1)
        cells = g.getLineCells(-2.5,-3.5,  -3.5,-2.5) # ,verbose=True)
        self.failUnlessEqual(cells,[(1,0),(0,1)])









######################################################################
# 1.4,.6 Origin

class TestGrid_GetLineCells_PlusPoint5Origin(bogus_unittest.TestCase):
#class TestGrid_GetLineCells_PlusPoint5Origin(unittest.TestCase):
    'Use .5,.5 as the origin'
    xmin=1000.4
    ymin=3231.6
    def testGetLineCells100(self):
        'getLineCells 10x1 horizontal'
        g = Grid(0+self.xmin,0+self.ymin,  10+self.xmin,1+self.ymin, 1)
        self.failUnlessEqual(g.xNumCells,10); self.failUnlessEqual(g.yNumCells,1)
        cells = g.getLineCells(.1+self.xmin,.1+self.ymin, 9.2+self.xmin,.1+self.ymin)
        self.failUnlessEqual(len(cells),10)
        self.failUnlessEqual(cells[0][0],0)
        self.failUnlessEqual(cells[0][1],0)
        self.failUnlessEqual(cells[-1][0],9)
        self.failUnlessEqual(cells[-1][1],0)

    def testGetLineCells110(self):
        'getLineCells 10x1 horizontal, slight slope up'
        g = Grid(0+self.xmin,0+self.ymin,  10+self.xmin,1+self.ymin, 1)
        cells = g.getLineCells(.1+self.xmin,.5+self.ymin, 9.2+self.xmin,.9+self.ymin)
        self.failUnlessEqual(len(cells),10)
        self.failUnlessEqual(cells[0][0],0)
        self.failUnlessEqual(cells[0][1],0)
        self.failUnlessEqual(cells[-1][0],9)
        self.failUnlessEqual(cells[-1][1],0)

    def testGetLineCells120(self):
        'getLineCells 10x1 horizontal, slight slope down'
        g = Grid(0+self.xmin,0+self.ymin,  10+self.xmin,1+self.ymin, 1)
        cells = g.getLineCells(.1+self.xmin,.5+self.ymin, 9.2+self.xmin,.1+self.ymin)
        self.failUnlessEqual(len(cells),10)
        self.failUnlessEqual(cells[0][0],0)
        self.failUnlessEqual(cells[0][1],0)
        self.failUnlessEqual(cells[-1][0],9)
        self.failUnlessEqual(cells[-1][1],0)

    def testGetLineCells150(self):
        'getLineCells 1x10 vertical'
        g = Grid(0+self.xmin,0+self.ymin,  1+self.xmin,10+self.ymin, 1)
        cells = g.getLineCells(.5+self.xmin,.5+self.ymin, .5+self.xmin,9.1+self.ymin)
        self.failUnlessEqual(len(cells),10)
        self.failUnlessEqual(cells[0][0],0)
        self.failUnlessEqual(cells[0][1],0)
        self.failUnlessEqual(cells[-1][0],0)
        self.failUnlessEqual(cells[-1][1],9)

    def testGetLineCells200(self):
        'getLineCells 4x4 len 3 - left-to-right - simple up slope'
        g = Grid(0+self.xmin,0+self.ymin,  4+self.xmin,4+self.ymin, 1)
        cells = g.getLineCells(.9+self.xmin,.1+self.ymin, 1.5+self.xmin,1.1+self.ymin)
        self.failUnlessEqual(cells,[(0,0),(1,0),(1,1)])

    def testGetLineCells210(self):
        'getLineCells 4x4 len 3 - left-to-right - simple up slope 2'
        g = Grid(0+self.xmin,0+self.ymin,  4+self.xmin,4+self.ymin, 1)
        cells = g.getLineCells(.5+self.xmin,.9+self.ymin, 1.1+self.xmin,1.5+self.ymin)
        self.failUnlessEqual(cells,[(0,0),(0,1),(1,1)])

    def testGetLineCells250(self):
        'getLineCells 4x4 len 3 - left-to-right - simple down slope'
        g = Grid(0+self.xmin,0+self.ymin,  4+self.xmin,4+self.ymin, 1)
        cells = g.getLineCells(.1+self.xmin,1.1+self.ymin, 1.1+self.xmin,.1+self.ymin)
        self.failUnlessEqual(cells,[(0,1),(0,0),(1,0)])

    # What happens when we hit a vertex?
    def testGetLineCells260(self):
        'getLineCells 4x4 len 3 - left-to-right - diagonal up'
        g = Grid(0+self.xmin,0+self.ymin,  4+self.xmin,4+self.ymin, 1)
        cells = g.getLineCells(.5+self.xmin,.5+self.ymin, 1.5+self.xmin,1.5+self.ymin)
        self.failUnlessEqual(cells,[(0,0),(1,1)])
        
    # What happens when we hit a vertex?
    def testGetLineCells261(self):
        'getLineCells 4x4 len 3 - left-to-right - diagonal up - end on vertex'
        g = Grid(0+self.xmin,0+self.ymin,  4+self.xmin,4+self.ymin, 1)
        cells = g.getLineCells(.5+self.xmin,.5+self.ymin, 2+self.xmin,2+self.ymin) #,verbose=True)
        self.failUnlessEqual(cells,[(0,0),(1,1),(2,2)])

    ##############################
    # Right to left tests
    def testGetLineCells300(self):
        'getLineCells 4x4 len 2 - right-to-left - horiz'
        g = Grid(0+self.xmin,0+self.ymin,  4+self.xmin,4+self.ymin, 1)
        cells = g.getLineCells(1.5+self.xmin,.5+self.ymin,  .5+self.xmin,.5+self.ymin)
        self.failUnlessEqual(cells,[(1,0),(0,0)])

    def testGetLineCells310(self):
        'getLineCells 4x4 len 2 - right-to-left - slope down'
        g = Grid(0+self.xmin,0+self.ymin,  4+self.xmin,4, 1+self.ymin)
        cell = g.getCell(1.9+self.xmin,1.1+self.ymin)
        self.failUnlessEqual(cell,(1,1))
        cells = g.getLineCells(1.9+self.xmin,1.1+self.ymin,  .9+self.xmin,.1+self.ymin) # ,verbose=True)
        self.failUnlessEqual(cells,[(1,1),(1,0),(0,0)])

    def testGetLineCells310(self):
        'getLineCells 4x4 len 2 - right-to-left - slope up shallow'
        g = Grid(0+self.xmin,0+self.ymin,  4+self.xmin,4+self.ymin, 1)
        cells = g.getLineCells(1.1+self.xmin,.8+self.ymin,  .1+self.xmin,1.1+self.ymin) # ,verbose=True)
        self.failUnlessEqual(cells,[(1,0),(0,0),(0,1)])

    def testGetLineCells311(self):
        'getLineCells 4x4 len 2 - right-to-left - slope steep'
        g = Grid(0+self.xmin,0+self.ymin,  4+self.xmin,4+self.ymin, 1)
        cells = g.getLineCells(1.1+self.xmin,.1+self.ymin,  .7+self.xmin,1.9+self.ymin) # ,verbose=True)
        self.failUnlessEqual(cells,[(1,0),(0,0),(0,1)])

    def testGetLineCells320(self):
        'getLineCells 4x4 len 2 - right-to-left - diagonal down'
        g = Grid(0+self.xmin,0+self.ymin,  4+self.xmin,4+self.ymin, 1)
        cells = g.getLineCells(1.4+self.xmin,1.4+self.ymin,  .7+self.xmin,.7+self.ymin) # ,verbose=True)
        self.failUnlessEqual(cells,[(1,1),(0,0)])

    def testGetLineCells321(self):
        'getLineCells 4x4 len 2 - right-to-left - diagonal up'
        g = Grid(0+self.xmin,0+self.ymin,  4+self.xmin,4+self.ymin, 1)
        cells = g.getLineCells(1.5+self.xmin,0.5+self.ymin,  .5+self.xmin,1.5+self.ymin) # ,verbose=True)
        self.failUnlessEqual(cells,[(1,0),(0,1)])



######################################################################
# Test cases for non unit cell size...

class TestGrid_GetLineCells_stepsizes(bogus_unittest.TestCase):
#class TestGrid_GetLineCells_stepsizes(unittest.TestCase):
    'Use .5,.5 as the origin'
    xmin=1000.4
    ymin=3231.6
    stepSize = 10.14
    def testGetLineCells100(self):
        'getLineCells 10x1 horizontal'
        ss = self.stepSize
        g = Grid(0+self.xmin,0+self.ymin,  (10*ss)+self.xmin,(1*ss)+self.ymin, ss)
        self.failUnlessEqual(g.xNumCells,10);
        self.failUnlessEqual(g.yNumCells,1)
        cells = g.getLineCells(.1+self.xmin,.1+self.ymin, (9.2*ss)+self.xmin,(.1*ss)+self.ymin)
        self.failUnlessEqual(len(cells),10)
        self.failUnlessEqual(cells[0][0],0)
        self.failUnlessEqual(cells[0][1],0)
        self.failUnlessEqual(cells[-1][0],9)
        self.failUnlessEqual(cells[-1][1],0)

    def testGetLineCells100(self):
        'getLineCells 10x2'
        ss = self.stepSize
        g = Grid(0+self.xmin,0+self.ymin,  (10*ss)+self.xmin,(2*ss)+self.ymin, ss)
        self.failUnless(g.xNumCells in (10,11));
        self.failUnless(g.yNumCells in (2,3))

    def testGetLineCells110(self):
        'getLineCells 10x1 horizontal, slight slope up'
        ss = self.stepSize
        g = Grid(0+self.xmin,0+self.ymin,  (10*ss)+self.xmin,(1*ss)+self.ymin, ss)#, verbose=True)
        cells = g.getLineCells((.1*ss)+self.xmin,(.5*ss)+self.ymin, (9.2*ss)+self.xmin,(.9*ss)+self.ymin)
        self.failUnless(g.xNumCells in (10,11));
        self.failUnless(g.yNumCells in (1,2))
        self.failUnlessEqual(len(cells),10)
        self.failUnlessEqual(cells[0][0],0)
        self.failUnlessEqual(cells[0][1],0)
        self.failUnlessEqual(cells[-1][0],9)
        self.failUnlessEqual(cells[-1][1],0)

    def testGetLineCells120(self):
        'getLineCells 10x1 horizontal, slight slope down'
        ss = self.stepSize
        g = Grid(0+self.xmin,0+self.ymin,  (10*ss)+self.xmin,(1*ss)+self.ymin, ss)
        cells = g.getLineCells((.1*ss)+self.xmin,(.5*ss)+self.ymin, (9.2*ss)+self.xmin,(.1*ss)+self.ymin)
        self.failUnlessEqual(len(cells),10)
        self.failUnlessEqual(cells[0][0],0)
        self.failUnlessEqual(cells[0][1],0)
        self.failUnlessEqual(cells[-1][0],9)
        self.failUnlessEqual(cells[-1][1],0)

    def testGetLineCells150(self):
        'getLineCells 1x10 vertical'
        ss = self.stepSize
        g = Grid(0+self.xmin,0+self.ymin,  (1*ss)+self.xmin,(10*ss)+self.ymin, ss)
        cells = g.getLineCells((.5*ss)+self.xmin,(.5*ss)+self.ymin, (.5*ss)+self.xmin,(9.1*ss)+self.ymin)
        self.failUnlessEqual(len(cells),10)
        self.failUnlessEqual(cells[0][0],0)
        self.failUnlessEqual(cells[0][1],0)
        self.failUnlessEqual(cells[-1][0],0)
        self.failUnlessEqual(cells[-1][1],9)

    def testGetLineCells200(self):
        'getLineCells 4x4 len 3 - left-to-right - simple up slope'
        ss = self.stepSize
        g = Grid(0+self.xmin,0+self.ymin,  (4*ss)+self.xmin,(4*ss)+self.ymin, ss)
        self.failUnless(g.xNumCells in (4,5));
        self.failUnless(g.yNumCells in (4,5))
        cells = g.getLineCells((ss*.9)+self.xmin,(.1*ss)+self.ymin, (1.5*ss)+self.xmin,(1.1*ss)+self.ymin)
        self.failUnlessEqual(cells,[(0,0),(1,0),(1,1)])

    def testGetLineCells210(self):
        'getLineCells 4x4 len 3 - left-to-right - simple up slope 2'
        ss = self.stepSize
        g = Grid(0+self.xmin,0+self.ymin,  (4*ss)+self.xmin,(4*ss)+self.ymin, ss)
        cells = g.getLineCells((.5*ss)+self.xmin,(.9*ss)+self.ymin, (1.1*ss)+self.xmin,(1.5*ss)+self.ymin)
        self.failUnlessEqual(cells,[(0,0),(0,1),(1,1)])

    def testGetLineCells250(self):
        'getLineCells 4x4 len 3 - left-to-right - simple down slope'
        ss = self.stepSize
        g = Grid(0+self.xmin,0+self.ymin,  (4*ss)+self.xmin,(4*ss)+self.ymin, ss)
        cells = g.getLineCells((.1*ss)+self.xmin,(1.1*ss)+self.ymin, (1.1*ss)+self.xmin,(.1*ss)+self.ymin)
        self.failUnlessEqual(cells,[(0,1),(0,0),(1,0)])

    # What happens when we hit a vertex?
    def testGetLineCells260(self):
        'getLineCells 4x4 len 3 - left-to-right - diagonal up'
        ss = self.stepSize
        g = Grid(0+self.xmin,0+self.ymin,  (4*ss)+self.xmin,(4*ss)+self.ymin, ss)
        cells = g.getLineCells((.5*ss)+self.xmin,(.5*ss)+self.ymin, (1.5*ss)+self.xmin,(1.5*ss)+self.ymin)
        self.failUnlessEqual(cells,[(0,0),(1,1)])
        
    # What happens when we hit a vertex?
    def testGetLineCells261(self):
        'getLineCells 4x4 len 3 - left-to-right - diagonal up - end on vertex'
        ss = self.stepSize
        g = Grid(0+self.xmin,0+self.ymin,  (4*ss)+self.xmin,(4*ss)+self.ymin, ss)
        x0,y0=(.5*ss)+self.xmin,(.5*ss)+self.ymin
        x1,y1=(2.01*ss)+self.xmin,(2.01*ss)+self.ymin
        cells = g.getLineCells(x0,y0, x1,y1) #,verbose=True)
        self.failUnlessEqual(cells,[(0,0),(1,1),(2,2)])

    ##############################
    # Right to left tests
    def testGetLineCells300(self):
        'getLineCells 4x4 len 2 - right-to-left - horiz'
        ss = self.stepSize
        g = Grid(0+self.xmin,0+self.ymin,  (4*ss)+self.xmin,(4*ss)+self.ymin, ss)
        cells = g.getLineCells((1.5*ss)+self.xmin,(.5*ss)+self.ymin,  (.5*ss)+self.xmin,(.5*ss)+self.ymin)
        self.failUnlessEqual(cells,[(1,0),(0,0)])

    def testGetLineCells310(self):
        'getLineCells 4x4 len 2 - right-to-left - slope down'
        ss = self.stepSize
        g = Grid(0+self.xmin,0+self.ymin,  (4*ss)+self.xmin,4, 1+self.ymin)
        cell = g.getCell(1.9+self.xmin,1.1+self.ymin)
        self.failUnlessEqual(cell,(1,1))
        cells = g.getLineCells(1.9+self.xmin,1.1+self.ymin,  .9+self.xmin,.1+self.ymin) # ,verbose=True)
        self.failUnlessEqual(cells,[(1,1),(1,0),(0,0)])

    def testGetLineCells310(self):
        'getLineCells 4x4 len 2 - right-to-left - slope up shallow'
        ss = self.stepSize
        g = Grid(0+self.xmin,0+self.ymin,  (4*ss)+self.xmin,(4*ss)+self.ymin, ss)
        cells = g.getLineCells((1.1*ss)+self.xmin,(.8*ss)+self.ymin,  (.1*ss)+self.xmin,(1.1*ss)+self.ymin) # ,verbose=True)
        self.failUnlessEqual(cells,[(1,0),(0,0),(0,1)])

    def testGetLineCells311(self):
        'getLineCells 4x4 len 2 - right-to-left - slope steep'
        ss = self.stepSize
        g = Grid(0+self.xmin,0+self.ymin,  (4*ss)+self.xmin,(4*ss)+self.ymin, ss)
        cells = g.getLineCells((1.1*ss)+self.xmin,(.1*ss)+self.ymin,  (.7*ss)+self.xmin,(1.9*ss)+self.ymin) # ,verbose=True)
        self.failUnlessEqual(cells,[(1,0),(0,0),(0,1)])

    def testGetLineCells320(self):
        'getLineCells 4x4 len 2 - right-to-left - diagonal down'
        ss = self.stepSize
        g = Grid(0+self.xmin,0+self.ymin,  (4*ss)+self.xmin,(4*ss)+self.ymin, ss)
        cells = g.getLineCells((1.4*ss)+self.xmin,(1.4*ss)+self.ymin,  (.7*ss)+self.xmin,(.7*ss)+self.ymin) # ,verbose=True)
        self.failUnlessEqual(cells,[(1,1),(0,0)])

    def testGetLineCells321(self):
        'getLineCells 4x4 len 2 - right-to-left - diagonal up'
        ss = self.stepSize
        g = Grid(0+self.xmin,0+self.ymin,  (4*ss)+self.xmin,(4*ss)+self.ymin, ss)
        x0,y0=(ss*1.5)+self.xmin,(ss*0.5)+self.ymin
        x1,y1=(ss*.5)+self.xmin,(ss*1.5)+self.ymin
        
        cells = g.getLineCells(x0,y0,  x1,y1)#,verbose=True)
        self.failUnlessEqual(cells,[(1,0),(0,1)])


    def testGetLineCells321(self):
        'getLineCells 4x4 len 2 - right-to-left - diagonal up'
        ss = self.stepSize
        g = Grid(0+self.xmin,0+self.ymin,  (4*ss)+self.xmin,(4*ss)+self.ymin, ss)
        x0,y0=(ss*1.95)+self.xmin,(ss*0.05)+self.ymin
        x1,y1=(ss*.05)+self.xmin,(ss*1.95)+self.ymin
        
        cells = g.getLineCells(x0,y0,  x1,y1)#,verbose=True)
        self.failUnlessEqual(cells,[(1,0),(0,1)])

######################################################################
# Test cases for non unit cell size...

class TestGrid_GetMultiSegLineCells(bogus_unittest.TestCase):
#class TestGrid_GetMultiSegLineCells(unittest.TestCase):
    'Make sure that lines with multiple vertices scan convert'
    stepSize = 1
    xmin=0
    xmax=4
    ymin=0
    ymax=4
    def testASeg1(self):
        'Single line segment - one cell'
        ss=self.stepSize;xmin=self.xmin;xmax=self.xmax;ymin=self.ymin;ymax=self.ymax
        g = Grid(0*ss+xmin,0*ss+ymin,  4*ss+xmin,4*ss+ymin, ss)
        cells = g.getMultiSegLineCells(((0.1,0.5),(0.3,0.5)))
        self.failUnlessEqual(cells,[(0,0)])

    def testASeg2(self):
        'Single line segment - two cells horizontal'
        ss=self.stepSize;xmin=self.xmin;xmax=self.xmax;ymin=self.ymin;ymax=self.ymax
        g = Grid(0*ss+xmin,0*ss+ymin,  4*ss+xmin,4*ss+ymin, ss)
        cells = g.getMultiSegLineCells(((xmin+ss*0.1,ymin+ss*0.5),(xmin+ss*1.3,ymin+ss*0.5)))
        self.failUnlessEqual(cells,[(0,0),(1,0)])

    def testTwoSegs1(self):
        'L shape - 3 cells'
        ss=self.stepSize;xmin=self.xmin;xmax=self.xmax;ymin=self.ymin;ymax=self.ymax
        g = Grid(0*ss+xmin,0*ss+ymin,  4*ss+xmin,4*ss+ymin, ss)
        cells = g.getMultiSegLineCells((
            (xmin+ss*0.1,ymin+ss*0.5)
            ,(xmin+ss*1.3,ymin+ss*0.5)
            ,(xmin+ss*1.3,ymin+ss*1.5)
            ))
        self.failUnlessEqual(cells,[(0,0),(1,0),(1,1)])

    def testSegs3(self):
        'Single line segment - two cells horizontal'
        ss=self.stepSize;xmin=self.xmin;xmax=self.xmax;ymin=self.ymin;ymax=self.ymax
        g = Grid(0*ss+xmin,0*ss+ymin,  4*ss+xmin,4*ss+ymin, ss)
        cells = g.getMultiSegLineCells((
            (xmin+ss*0.1,ymin+ss*0.5)
            ,(xmin+ss*1.3,ymin+ss*0.5)
            ,(xmin+ss*1.3,ymin+ss*1.5)
            ,(xmin+ss*0.3,ymin+ss*1.5)
            ))
        self.failUnlessEqual(cells,[(0,0),(1,0),(1,1),(0,1)])

    def testSegs4(self):
        'Single line segment - two cells horizontal'
        ss=self.stepSize;xmin=self.xmin;xmax=self.xmax;ymin=self.ymin;ymax=self.ymax
        g = Grid(0*ss+xmin,0*ss+ymin,  4*ss+xmin,4*ss+ymin, ss)
        cells = g.getMultiSegLineCells((
            (xmin+ss*0.1,ymin+ss*0.5)
            ,(xmin+ss*1.3,ymin+ss*0.5)
            ,(xmin+ss*1.3,ymin+ss*1.5)
            ,(xmin+ss*0.3,ymin+ss*1.5)
            ,(xmin+ss*0.1,ymin+ss*0.5)
            ))
        self.failUnlessEqual(cells,[(0,0),(1,0),(1,1),(0,1),(0,0)])


    def testSegs4_1(self):
        'Single line segment - two cells horizontal'
        ss=self.stepSize;xmin=self.xmin;xmax=self.xmax;ymin=self.ymin;ymax=self.ymax
        g = Grid(0*ss+xmin,0*ss+ymin,  4*ss+xmin,4*ss+ymin, ss)
        cells = g.getMultiSegLineCells((
            (xmin+ss*0.1,ymin+ss*0.5)
            ,(xmin+ss*3.3,ymin+ss*0.5)
            ,(xmin+ss*3.3,ymin+ss*3.5)
            ))
        self.failUnlessEqual(cells,[(0,0),(1,0),(2,0)
                                    ,(3,0),(3,1),(3,2)
                                    ,(3,3)
                                    ])

    def testSegs4_2(self):
        'Single line segment - two cells horizontal'
        ss=self.stepSize;xmin=self.xmin;xmax=self.xmax;ymin=self.ymin;ymax=self.ymax
        g = Grid(0*ss+xmin,0*ss+ymin,  4*ss+xmin,4*ss+ymin, ss)
        cells = g.getMultiSegLineCells((
            (xmin+ss*0.1,ymin+ss*0.5)
            ,(xmin+ss*3.3,ymin+ss*0.5)
            ,(xmin+ss*3.3,ymin+ss*3.5)
            ,(xmin+ss*0.3,ymin+ss*3.5)
            ))
        self.failUnlessEqual(cells,[(0,0)
                                    ,(1,0),(2,0),(3,0)
                                    ,(3,1),(3,2),(3,3)
                                    ,(2,3),(1,3),(0,3)
                                    ])

    def testSegs4_3(self):
        'Single line segment - two cells horizontal'
        ss=self.stepSize;xmin=self.xmin;xmax=self.xmax;ymin=self.ymin;ymax=self.ymax
        g = Grid(0*ss+xmin,0*ss+ymin,  4*ss+xmin,4*ss+ymin, ss)
        cells = g.getMultiSegLineCells((
            (xmin+ss*0.1,ymin+ss*0.5)
            ,(xmin+ss*3.3,ymin+ss*0.5)
            ,(xmin+ss*3.3,ymin+ss*3.5)
            ,(xmin+ss*0.3,ymin+ss*3.5)
            ,(xmin+ss*0.1,ymin+ss*0.5)
            ))
        self.failUnlessEqual(cells,[(0,0)
                                    ,(1,0),(2,0),(3,0)
                                    ,(3,1),(3,2),(3,3)
                                    ,(2,3),(1,3),(0,3)
                                    ,(0,0),(0,1),(0,2)
                                    ])
        # FIX: this is a case where the cells do not come back in the expected order?!?!
        # FIX: would be better if the cells actually came in the right order!




######################################################################

class TestGrid_GetMultiSegLineCells(bogus_unittest.TestCase):
#class TestGrid_addMultiSegLine(unittest.TestCase):
    'Make sure that lines with multiple vertices scan convert'
    stepSize = 1
    xmin=0
    xmax=4
    ymin=0
    ymax=4
    def testSegs4_0(self):
        'Single line segment - single cell'
        ss=self.stepSize;xmin=self.xmin;xmax=self.xmax;ymin=self.ymin;ymax=self.ymax
        g = Grid(0*ss+xmin,0*ss+ymin,  4*ss+xmin,4*ss+ymin, ss)
        line = (
            (xmin+ss*0.1,ymin+ss*0.5)
            ,(xmin+ss*0.12,ymin+ss*0.5)
            )
        g.addMultiSegLine(line)#,verbose=True)
        #g.writeLayoutGnuplot('0-grid.dat')
        #g.writeCellsGnuplot('0.dat')
        self.failUnlessEqual(g.grid[0,0],1)
        

    def testSegs4_1(self):
        'Single line segment - two cells horizontal'
        ss=self.stepSize;xmin=self.xmin;xmax=self.xmax;ymin=self.ymin;ymax=self.ymax
        g = Grid(0*ss+xmin,0*ss+ymin,  4*ss+xmin,4*ss+ymin, ss)
        line = (
            (xmin+ss*0.1,ymin+ss*0.5)
            ,(xmin+ss*3.3,ymin+ss*0.5)
            )
        g.addMultiSegLine(line)
        g.writeLayoutGnuplot('1-grid.dat')
        g.writeCellsGnuplot('1.dat')
        self.failUnlessEqual(g.grid[0,0],1)
        

    def testSegs4_3(self):
        'Single line segment - two cells horizontal'
        ss=self.stepSize;xmin=self.xmin;xmax=self.xmax;ymin=self.ymin;ymax=self.ymax
        g = Grid(0*ss+xmin,0*ss+ymin,  4*ss+xmin,4*ss+ymin, ss)
        line = (
            (xmin+ss*0.1,ymin+ss*0.5)
            ,(xmin+ss*3.3,ymin+ss*0.5)
            ,(xmin+ss*3.3,ymin+ss*3.5)
            ,(xmin+ss*0.3,ymin+ss*3.5)
            )
        cells = g.getMultiSegLineCells(line)
        self.failUnlessEqual(cells,[(0,0)
                                    ,(1,0),(2,0),(3,0)
                                    ,(3,1),(3,2),(3,3)
                                    ,(2,3),(1,3),(0,3)
                                    ])

        g.addMultiSegLine(line)
        g.writeLayoutGnuplot('3-grid.dat')
        g.writeCellsGnuplot('3.dat')
        self.failUnlessEqual(g.grid[0,0],1)
        self.failUnlessEqual(g.grid[3,0],1)
        self.failUnlessEqual(g.grid[3,3],1)
        self.failUnlessEqual(g.grid[0,3],1)
        self.failUnlessEqual(g.grid[2,2],0)
        
    def testSegs4_4(self):
        'Four line segments - box'
        ss=self.stepSize;xmin=self.xmin;xmax=self.xmax;ymin=self.ymin;ymax=self.ymax
        g = Grid(0*ss+xmin,0*ss+ymin,  4*ss+xmin,4*ss+ymin, ss)
        line = (
            (xmin+ss*0.1,ymin+ss*0.5)
            ,(xmin+ss*3.3,ymin+ss*0.5)
            ,(xmin+ss*3.3,ymin+ss*3.5)
            ,(xmin+ss*0.3,ymin+ss*3.5)
            ,(xmin+ss*0.1,ymin+ss*0.5)
            )
        cells = g.getMultiSegLineCells(line)
        g.addMultiSegLine(line)
        g.writeLayoutGnuplot('4-grid.dat')
        g.writeCellsGnuplot('4.dat')
        self.failUnlessEqual(g.grid[0,0],2)
        self.failUnlessEqual(g.grid[3,0],1)
        self.failUnlessEqual(g.grid[3,3],1)
        self.failUnlessEqual(g.grid[0,3],1)
        self.failUnlessEqual(g.grid[2,2],0)


class TestWhyDidThisFail(bogus_unittest.TestCase):
    def test1(self):
        'Vertical line in reverse direction'
        ss   =    1852.0
        xmin =  359207.844601
        xmax =  426523.405265
        ymin = 4651174.05098
        ymax = 4750102.91341
        g = Grid(xmin,ymin,  xmax,ymax, ss, verbose=True)
        cells=g.getLineCells ( 415216.29984943097, 4671534.0646001603,
                               415182.051535215,   4671547.4328312902
                              ,verbose=True
                              )
        print cells
        self.failUnless(len(cells)>0)

class TestArcAsciiGrid(bogus_unittest.TestCase):
    def test001(self):
        g = Grid(0,0, 4,4, 1)
        g.writeArcAsciiGrid('tmp_4x4.asc')
        print 'FIX: how do I validate writing to a file with unittest?'

    def test010(self):
        g = Grid(0,0, 4,4, 1)
        g.grid[0,0]=1 # LL corner
        g.writeArcAsciiGrid('tmp_4x4_ll.asc')
        print 'FIX: how do I validate writing to a file with unittest?'

    def test020(self):
        g = Grid(0,0, 4,4, 1)
        g.grid[0,3]=1 # UL corner
        g.writeArcAsciiGrid('tmp_4x4_ul.asc')
        #print 'FIX: how do I validate writing to a file with unittest?'

    def test030(self):
        g = Grid(0,0, 4,4, 1)
        g.grid[3,0]=1 # lr corner
        g.writeArcAsciiGrid('tmp_4x4_lr.asc')
        #print 'FIX: how do I validate writing to a file with unittest?'

    def test040(self):
        g = Grid(0,0, 4,4, 1)
        g.grid[3,3]=1 # ur corner
        g.writeArcAsciiGrid('tmp_4x4_ur.asc')
        #print 'FIX: how do I validate writing to a file with unittest?'

class TestGridLength(unittest.TestCase):
    stepSize=1
    xmin=0
    xmax=4
    ymin=0
    ymax=4

    def testSingleCell(self):
        ss=self.stepSize;xmin=self.xmin;xmax=self.xmax;ymin=self.ymin;ymax=self.ymax
        g = Grid(0*ss+xmin,0*ss+ymin,  4*ss+xmin,4*ss+ymin, ss,gridType='distance')
        line = ( (0,1.5),(1,1.5))

        # Single cell - vert
        r = g.getLineCellsWithCrossings(.25,0, .75,0.,verbose=True)
        #print 'r',r
        cell,frac1,frac2,dist = r[0]
        self.failUnlessEqual((0,0),cell)
        self.failUnlessAlmostEqual(0.,frac1)
        self.failUnlessAlmostEqual(1.,frac2)
        self.failUnlessAlmostEqual(0.5,dist)

        # Single cell - horz
        r = g.getLineCellsWithCrossings(0,.25, 0.,.75,verbose=True)
        self.failUnlessEqual((0,0),cell)
        self.failUnlessEqual(0.,frac1)
        self.failUnlessEqual(1.,frac2)
        self.failUnlessAlmostEqual(0.5,dist)

    def testHorizontal1(self):
        ss=self.stepSize;xmin=self.xmin;xmax=self.xmax;ymin=self.ymin;ymax=self.ymax
        g = Grid(0*ss+xmin,0*ss+ymin,  4*ss+xmin,4*ss+ymin, ss,gridType='distance')
        line = ( (0,1.5),(1,1.5))

        # Horizontal
        r = g.getLineCellsWithCrossings(0.5,1.5, 1.5,1.5) #,verbose=True)
        self.failUnlessEqual(len(r),2)

        cell,frac1,frac2,dist = r[0]
        self.failUnlessEqual((0,1),cell)
        self.failUnlessEqual(0.,frac1)
        self.failUnlessEqual(.5,frac2)
        self.failUnlessAlmostEqual(0.5,dist)

        cell,frac1,frac2,dist = r[1]
        self.failUnlessEqual((1,1),cell)
        self.failUnlessEqual(0.5,frac1)
        self.failUnlessEqual(1.,frac2)
        self.failUnlessAlmostEqual(0.5,dist)

        r = g.getLineCellsWithCrossings(0.5,1.5, 4.5,1.5) #,verbose=True)
        print r
        self.failUnlessEqual(len(r),5)

        cell,frac1,frac2,dist = r[0]
        self.failUnlessEqual((0,1),cell)
        self.failUnlessEqual(0.,frac1)
        self.failUnlessAlmostEqual(.25/2.,frac2)
        self.failUnlessAlmostEqual(0.5,dist)

        cell,frac1,frac2,dist = r[-1]
        self.failUnlessEqual((4,1),cell)
        self.failUnlessAlmostEqual(1 - (0.25/2.),frac1)
        self.failUnlessEqual(1.,frac2)
        self.failUnlessAlmostEqual(0.5,dist)


        

        print 'r', r

############################################################
if __name__=='__main__':
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options]",version="%prog "+__version__)
    parser.add_option('--unit-test',dest='unittest',default=False,action='store_true',
                      help='run the unit tests')
    parser.add_option('-v','--verbose',dest='verbose',default=False,action='store_true',
                      help='Make the test output verbose')

    (options,args) = parser.parse_args()

    if options.unittest:
        import sys
        sys.argv = [sys.argv[0]]
        if options.verbose: sys.argv.append('-v')
        unittest.main()
