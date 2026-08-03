#!/usr/bin/env python

__version__ = "$Revision: 4791 $".split()[1]
__date__ = "$Date: 2007-01-04 $".split()[1]
__author__ = "Kurt Schwehr"

__doc__ = """
Unit tests for the grid class

@license: Apache 2.0
@since: 2007-Jul-29

@todo: allow for non-square grid cells
"""

from aisutils.grid import Grid

import unittest

######################################################################
# UNIT TESTING
######################################################################


class TestGrid(unittest.TestCase):
    # class TestGrid(unittest.TestCase):
    def testInit10(self):
        "init with unit grid"
        g = Grid(0, 0, 1, 1, 1)
        self.assertEqual(g.xNumCells, 1)
        self.assertEqual(g.yNumCells, 1)
        self.assertAlmostEqual(g.maxx, 1)
        self.assertAlmostEqual(g.maxy, 1)

    def testInit20(self):
        "init with 1.1x1 grid"
        g = Grid(0, 0, 1.1, 1, 1)
        self.assertEqual(g.xNumCells, 2)
        self.assertEqual(g.yNumCells, 1)
        self.assertAlmostEqual(g.maxx, 2)
        self.assertAlmostEqual(g.maxy, 1)

    def testInit21(self):
        "init with 1x1.1 grid"
        # g = Grid(0,1,0,1.1,1)
        g = Grid(0, 0, 1, 1.1, 1)
        self.assertEqual(g.xNumCells, 1)
        self.assertEqual(g.yNumCells, 2)
        self.assertAlmostEqual(g.maxx, 1)
        self.assertAlmostEqual(g.maxy, 2)

    def testInit30(self):
        "init with offset from unit boundaries"
        # g = Grid(.5,2.5,1.5,4.5,1)
        g = Grid(0.5, 1.5, 2.5, 4.5, 1)
        self.assertEqual(g.xNumCells, 2)
        self.assertEqual(g.yNumCells, 3)
        self.assertAlmostEqual(g.minx, 0.5)
        self.assertAlmostEqual(g.maxx, 2.5)
        self.assertAlmostEqual(g.miny, 1.5)
        self.assertAlmostEqual(g.maxy, 4.5)
        g.writeLayoutGnuplot("tmp_.5_2.5_1.5_4.5_step1.dat")

    def testInit40(self):
        "init with crossing the origin"
        g = Grid(-0.5, -1.5, 0.5, 4.5, 1)
        self.assertEqual(g.xNumCells, 1)
        self.assertEqual(g.yNumCells, 6)
        self.assertAlmostEqual(g.minx, -0.5)
        self.assertAlmostEqual(g.maxx, 0.5)
        self.assertAlmostEqual(g.miny, -1.5)
        self.assertAlmostEqual(g.maxy, 4.5)

    def testInit50(self):
        "init with non unit step sizes"
        g = Grid(0, 0, 1, 1, 0.1)
        self.assertEqual(g.xNumCells, 10)
        self.assertEqual(g.yNumCells, 10)
        self.assertAlmostEqual(g.maxx, 1)
        self.assertAlmostEqual(g.maxy, 1)

    def testInit50(self):
        "init with non unit step sizes, non-square"
        g = Grid(0, 0.1, 1.01, 1, 0.1)
        self.assertEqual(g.xNumCells, 11)
        self.assertEqual(g.yNumCells, 9)
        self.assertAlmostEqual(g.maxx, 1.1)
        self.assertAlmostEqual(g.miny, 0.1)
        self.assertAlmostEqual(g.maxy, 1)

    def testInit51(self):
        "init with non unit step sizes, non-square"
        g = Grid(0.1, 0, 1, 1.01, 0.1)
        self.assertEqual(g.xNumCells, 9)
        self.assertEqual(g.yNumCells, 11)
        self.assertAlmostEqual(g.minx, 0.1)
        self.assertAlmostEqual(g.maxx, 1)
        self.assertAlmostEqual(g.maxy, 1.1)

    def testJ_GetCell10(self):
        "getCell 1x1"
        g = Grid(0, 0, 1, 1, 1)
        i, j = g.getCell(0.1, 0.1)
        self.assertEqual(i, 0)
        self.assertEqual(j, 0)

    def testJ_GetCell20(self):
        "getCell 1x10"
        g = Grid(0, 0, 1, 10, 1)
        i, j = g.getCell(0.1, 0.1)
        self.assertEqual(i, 0)
        self.assertEqual(j, 0)
        i, j = g.getCell(0.1, 1.1)
        self.assertEqual(i, 0)
        self.assertEqual(j, 1)
        i, j = g.getCell(0.1, 9.1)
        self.assertEqual(i, 0)
        self.assertEqual(j, 9)

    def testJ_GetCell30(self):
        "getCell 10x1"
        g = Grid(0, 0, 10, 1, 1)
        i, j = g.getCell(0.1, 0.1)
        self.assertEqual(i, 0)
        self.assertEqual(j, 0)
        i, j = g.getCell(1.1, 0.1)
        self.assertEqual(i, 1)
        self.assertEqual(j, 0)
        i, j = g.getCell(9.1, 0.1)
        self.assertEqual(i, 9)
        self.assertEqual(j, 0)

    def testJ_GetCell40(self):
        "getCell -10 to 10 x1"
        g = Grid(-10, 0, 10, 1, 1)
        i, j = g.getCell(-9.1, 0.1)
        self.assertEqual(i, 0)
        self.assertEqual(j, 0)
        i, j = g.getCell(-0.1, 0.1)
        self.assertEqual(i, 9)
        self.assertEqual(j, 0)
        i, j = g.getCell(9.1, 0.1)
        self.assertEqual(i, 19)
        self.assertEqual(j, 0)

    def testJ_GetCell50(self):
        "getCell 1x -10 to 0"
        g = Grid(0, -10, 1, 0, 1)
        i, j = g.getCell(
            0.1,
            -9.1,
        )
        self.assertEqual(i, 0)
        self.assertEqual(j, 0)
        i, j = g.getCell(0.1, -0.1)
        self.assertEqual(i, 0)
        self.assertEqual(j, 9)
        i, j = g.getCell(0.1, 9.1)  # yeah... this is out of the grid
        self.assertEqual(i, 0)
        self.assertEqual(j, 19)

    def testK_GetCellCenter10(self):
        "getCellCenter 1x1"
        g = Grid(0, 0, 1, 1, 1)
        x, y = g.getCellCenter(0, 0)
        self.assertAlmostEqual(x, 0.5)
        self.assertAlmostEqual(y, 0.5)

    def testK_GetCellCenter20(self):
        "getCellCenter 10x1"
        g = Grid(0, 0, 10, 1, 1)
        x, y = g.getCellCenter(0, 0)
        self.assertAlmostEqual(x, 0.5)
        self.assertAlmostEqual(y, 0.5)
        x, y = g.getCellCenter(5, 0)
        self.assertAlmostEqual(x, 5.5)
        self.assertAlmostEqual(y, 0.5)
        x, y = g.getCellCenter(9, 0)
        self.assertAlmostEqual(x, 9.5)
        self.assertAlmostEqual(y, 0.5)

    def testK_GetCellCenter30(self):
        "getCellCenter 1x10"
        g = Grid(0, 0, 1, 10, 1)
        x, y = g.getCellCenter(0, 0)
        self.assertAlmostEqual(x, 0.5)
        self.assertAlmostEqual(y, 0.5)
        x, y = g.getCellCenter(0, 5)
        self.assertAlmostEqual(x, 0.5)
        self.assertAlmostEqual(y, 5.5)
        x, y = g.getCellCenter(0, 9)
        self.assertAlmostEqual(x, 0.5)
        self.assertAlmostEqual(y, 9.5)

    def testK_GetCellCenter20(self):
        "getCellCenter 10 (-10 to 0) x1"
        g = Grid(-10, 0, 0, 1, 1)
        x, y = g.getCellCenter(0, 0)
        self.assertAlmostEqual(x, -9.5)
        self.assertAlmostEqual(y, 0.5)
        x, y = g.getCellCenter(5, 0)
        self.assertAlmostEqual(x, -4.5)
        self.assertAlmostEqual(y, 0.5)
        x, y = g.getCellCenter(9, 0)
        self.assertAlmostEqual(x, -0.5)
        self.assertAlmostEqual(y, 0.5)

    ##############################
    # 1x1 getLineCells
    ##############################
    def testL_GetLineCells010(self):
        "getLineCells 1x1 vertical"
        g = Grid(0, 0, 1, 1, 1)
        cells = g.getLineCells(0.1, 0.1, 0.1, 0.2)
        self.assertEqual(len(cells), 1)
        self.assertEqual(cells[0][0], 0)
        self.assertEqual(cells[0][1], 0)

    def testL_GetLineCells020(self):
        "getLineCells 1x1 horizontal"
        g = Grid(0, 0, 1, 1, 1)
        cells = g.getLineCells(0.1, 0.1, 0.2, 0.1)
        self.assertEqual(len(cells), 1)
        self.assertEqual(cells[0][0], 0)
        self.assertEqual(cells[0][1], 0)

    def testL_GetLineCells030(self):
        "getLineCells 1x1 slope up, gentle"
        g = Grid(0, 0, 1, 1, 1)
        cells = g.getLineCells(0.1, 0.1, 0.2, 0.11)
        self.assertEqual(len(cells), 1)
        self.assertEqual(cells[0][0], 0)
        self.assertEqual(cells[0][1], 0)

    def testL_GetLineCells030(self):
        "getLineCells 1x1 slope up, steep"
        g = Grid(0, 0, 1, 1, 1)
        cells = g.getLineCells(0.1, 0.1, 0.2, 0.3)
        self.assertEqual(len(cells), 1)
        self.assertEqual(cells[0][0], 0)
        self.assertEqual(cells[0][1], 0)

    def testL_GetLineCells040(self):
        "getLineCells 1x1 slope down, gentle"
        g = Grid(0, 0, 1, 1, 1)
        cells = g.getLineCells(0.1, 0.1, 0.2, 0.09)
        self.assertEqual(len(cells), 1)
        self.assertEqual(cells[0][0], 0)
        self.assertEqual(cells[0][1], 0)

    def testL_GetLineCells050(self):
        "getLineCells 1x1 slope down, steep"
        g = Grid(0, 0, 1, 1, 1)
        cells = g.getLineCells(0.1, 0.4, 0.2, 0.09)
        self.assertEqual(len(cells), 1)
        self.assertEqual(cells[0][0], 0)
        self.assertEqual(cells[0][1], 0)


######################################################################
class TestGrid_GetLineCells(unittest.TestCase):
    # class TestGrid_GetLineCells(unittest.TestCase):
    "horiz and vertical runs"

    def testGetLineCells100(self):
        "getLineCells 10x1 horizontal"
        g = Grid(0, 0, 10, 1, 1)
        cells = g.getLineCells(0.1, 0.1, 9.2, 0.1)
        self.assertEqual(len(cells), 10)
        self.assertEqual(cells[0][0], 0)
        self.assertEqual(cells[0][1], 0)
        self.assertEqual(cells[-1][0], 9)
        self.assertEqual(cells[-1][1], 0)

    def testGetLineCells110(self):
        "getLineCells 10x1 horizontal, slight slope up"
        g = Grid(0, 0, 10, 1, 1)
        cells = g.getLineCells(0.1, 0.5, 9.2, 0.9)
        self.assertEqual(len(cells), 10)
        self.assertEqual(cells[0][0], 0)
        self.assertEqual(cells[0][1], 0)
        self.assertEqual(cells[-1][0], 9)
        self.assertEqual(cells[-1][1], 0)

    def testGetLineCells120(self):
        "getLineCells 10x1 horizontal, slight slope down"
        g = Grid(0, 0, 10, 1, 1)
        cells = g.getLineCells(0.1, 0.5, 9.2, 0.1)
        self.assertEqual(len(cells), 10)
        self.assertEqual(cells[0][0], 0)
        self.assertEqual(cells[0][1], 0)
        self.assertEqual(cells[-1][0], 9)
        self.assertEqual(cells[-1][1], 0)

    def testGetLineCells150(self):
        "getLineCells 1x10 vertical"
        g = Grid(0, 0, 1, 10, 1)
        cells = g.getLineCells(0.5, 0.5, 0.5, 9.1)
        self.assertEqual(len(cells), 10)
        self.assertEqual(cells[0][0], 0)
        self.assertEqual(cells[0][1], 0)
        self.assertEqual(cells[-1][0], 0)
        self.assertEqual(cells[-1][1], 9)

    def testGetLineCells150(self):
        "getLineCells 1x10 vertical, reverse"
        g = Grid(0, 0, 1, 10, 1)
        cells = g.getLineCells(0.5, 9.1, 0.5, 0.5)
        self.assertEqual(len(cells), 10)
        self.assertEqual(cells[0][0], 0)
        self.assertEqual(cells[0][1], 9)
        self.assertEqual(cells[-1][0], 0)
        self.assertEqual(cells[-1][1], 0)

    def testGetLineCells200(self):
        "getLineCells 4x4 len 3 - left-to-right - simple up slope"
        g = Grid(0, 0, 4, 4, 1)
        cells = g.getLineCells(0.9, 0.1, 1.5, 1.1)
        # print 'cells',cells
        self.assertEqual(cells, [(0, 0), (1, 0), (1, 1)])

    def testGetLineCells210(self):
        "getLineCells 4x4 len 3 - left-to-right - simple up slope 2"
        g = Grid(0, 0, 4, 4, 1)
        cells = g.getLineCells(0.5, 0.9, 1.1, 1.5)
        # print 'cells',cells
        self.assertEqual(cells, [(0, 0), (0, 1), (1, 1)])

    def testGetLineCells250(self):
        "getLineCells 4x4 len 3 - left-to-right - simple down slope"
        g = Grid(0, 0, 4, 4, 1)
        cells = g.getLineCells(0.1, 1.1, 1.1, 0.1)
        # print 'cells',cells
        self.assertEqual(cells, [(0, 1), (0, 0), (1, 0)])

    # What happens when we hit a vertex?
    def testGetLineCells260(self):
        "getLineCells 4x4 len 3 - left-to-right - diagonal up"
        g = Grid(0, 0, 4, 4, 1)
        cells = g.getLineCells(0.5, 0.5, 1.5, 1.5)
        self.assertEqual(cells, [(0, 0), (1, 1)])

    # What happens when we hit a vertex?
    def testGetLineCells261(self):
        "getLineCells 4x4 len 3 - left-to-right - diagonal up - end on vertex"
        g = Grid(0, 0, 4, 4, 1)
        cells = g.getLineCells(0.5, 0.5, 2, 2)
        self.assertEqual(cells, [(0, 0), (1, 1), (2, 2)])

    ##############################
    # Right to left tests
    def testGetLineCells300(self):
        "getLineCells 4x4 len 2 - right-to-left - horiz"
        g = Grid(0, 0, 4, 4, 1)
        cells = g.getLineCells(1.5, 0.5, 0.5, 0.5)
        self.assertEqual(cells, [(1, 0), (0, 0)])

    def testGetLineCells310(self):
        "getLineCells 4x4 len 2 - right-to-left - slope down"
        g = Grid(0, 0, 4, 4, 1)
        cell = g.getCell(1.9, 1.1)
        self.assertEqual(cell, (1, 1))
        cells = g.getLineCells(1.9, 1.1, 0.9, 0.1)  # ,verbose=True)
        self.assertEqual(cells, [(1, 1), (1, 0), (0, 0)])

    def testGetLineCells310(self):
        "getLineCells 4x4 len 2 - right-to-left - slope up shallow"
        g = Grid(0, 0, 4, 4, 1)
        cells = g.getLineCells(1.1, 0.8, 0.1, 1.1)  # ,verbose=True)
        self.assertEqual(cells, [(1, 0), (0, 0), (0, 1)])

    def testGetLineCells311(self):
        "getLineCells 4x4 len 2 - right-to-left - slope steep"
        g = Grid(0, 0, 4, 4, 1)
        cells = g.getLineCells(1.1, 0.1, 0.7, 1.9)  # ,verbose=True)
        self.assertEqual(cells, [(1, 0), (0, 0), (0, 1)])

    def testGetLineCells320(self):
        "getLineCells 4x4 len 2 - right-to-left - diagonal down"
        g = Grid(0, 0, 4, 4, 1)
        cells = g.getLineCells(1.4, 1.4, 0.7, 0.7)  # ,verbose=True)
        self.assertEqual(cells, [(1, 1), (0, 0)])

    def testGetLineCells321(self):
        "getLineCells 4x4 len 2 - right-to-left - diagonal up"
        g = Grid(0, 0, 4, 4, 1)
        cells = g.getLineCells(1.5, 0.5, 0.5, 1.5)  # ,verbose=True)
        self.assertEqual(cells, [(1, 0), (0, 1)])


######################################################################
# Non zero origin


class TestGrid_GetLineCells_Non0Origin(unittest.TestCase):
    # class TestGrid_GetLineCells_Non0Origin(unittest.TestCase):
    "Use -4,-4 as the origin"

    def testGetLineCells100(self):
        "getLineCells Non 0 Origin - 10x1 horizontal"
        g = Grid(-4, -4, 6, -3, 1)
        cells = g.getLineCells(-3.9, -3.9, 4.2, -3.9)  # , verbose=True)
        self.assertEqual(g.xNumCells, 10)
        self.assertEqual(g.yNumCells, 1)
        self.assertEqual(len(cells), 9)
        self.assertEqual(cells[0][0], 0)
        self.assertEqual(cells[0][1], 0)
        self.assertEqual(cells[-1][0], 8)
        self.assertEqual(cells[-1][1], 0)

    def testGetLineCells110(self):
        "getLineCells Non 0 Origin - 10x1 horizontal, slight slope up"
        g = Grid(-4, -4, 6, -3, 1)
        cells = g.getLineCells(-3.9, -3.5, 4.2, -3.1)
        self.assertEqual(g.xNumCells, 10)
        self.assertEqual(g.yNumCells, 1)
        self.assertEqual(len(cells), 9)
        self.assertEqual(cells[0][0], 0)
        self.assertEqual(cells[0][1], 0)
        self.assertEqual(cells[-1][0], 8)
        self.assertEqual(cells[-1][1], 0)

    def testGetLineCells120(self):
        "getLineCells Non 0 Origin - 10x1 horizontal, slight slope down"
        g = Grid(-4, -4, 6, -3, 1)
        cells = g.getLineCells(-3.9, -3.5, 4.2, -3.9)
        self.assertEqual(g.xNumCells, 10)
        self.assertEqual(g.yNumCells, 1)
        self.assertEqual(len(cells), 9)
        self.assertEqual(cells[0][0], 0)
        self.assertEqual(cells[0][1], 0)
        self.assertEqual(cells[-1][0], 8)
        self.assertEqual(cells[-1][1], 0)

    def testGetLineCells150(self):
        "getLineCells Non 0 Origin - 1x10 vertical"
        g = Grid(-4, -4, -3, 6, 1)
        cells = g.getLineCells(-3.5, -3.5, -3.5, 5.1)
        self.assertEqual(g.xNumCells, 1)
        self.assertEqual(g.yNumCells, 10)
        self.assertEqual(len(cells), 10)
        self.assertEqual(cells[0][0], 0)
        self.assertEqual(cells[0][1], 0)
        self.assertEqual(cells[-1][0], 0)
        self.assertEqual(cells[-1][1], 9)

    def testGetLineCells200(self):
        "getLineCells Non 0 Origin - 4x4 len 3 - left-to-right - simple up slope"
        g = Grid(-4, -4, 0, 0, 1)
        cells = g.getLineCells(-3.1, -3.9, -2.5, -2.9)  # ,verbose=True)
        self.assertEqual(g.xNumCells, 4)
        self.assertEqual(g.yNumCells, 4)
        self.assertEqual(cells, [(0, 0), (1, 0), (1, 1)])

    def testGetLineCells210(self):
        "getLineCells Non 0 Origin - 4x4 len 3 - left-to-right - simple up slope 2"
        g = Grid(-4, -4, 4, 4, 1)
        cells = g.getLineCells(-3.5, -3.1, -2.9, -2.5)
        self.assertEqual(cells, [(0, 0), (0, 1), (1, 1)])

    def testGetLineCells250(self):
        "getLineCells Non 0 Origin - 4x4 len 3 - left-to-right - simple down slope"
        g = Grid(-4, -4, 4, 4, 1)
        cells = g.getLineCells(-3.9, -2.9, -2.9, -3.9)
        self.assertEqual(cells, [(0, 1), (0, 0), (1, 0)])

    # What happens when we hit a vertex?
    def testGetLineCells260(self):
        "getLineCells Non 0 Origin - 4x4 len 3 - left-to-right - diagonal up"
        g = Grid(-4, -4, 4, 4, 1)
        cells = g.getLineCells(-3.5, -3.5, -2.5, -2.5)
        self.assertEqual(cells, [(0, 0), (1, 1)])

    # What happens when we hit a vertex?
    def testGetLineCells261(self):
        "getLineCells Non 0 Origin - 4x4 len 3 - left-to-right - diagonal up - end on vertex"
        g = Grid(-4, -4, 4, 4, 1)
        cells = g.getLineCells(-3.5, -3.5, -2, -2)
        self.assertEqual(cells, [(0, 0), (1, 1), (2, 2)])

    ##############################
    # Right to left tests
    def testGetLineCells300(self):
        "getLineCells Non 0 Origin - 4x4 len 2 - right-to-left - horiz"
        g = Grid(-4, -4, 4, 4, 1)
        cells = g.getLineCells(-2.5, -3.5, -3.5, -3.5)
        self.assertEqual(cells, [(1, 0), (0, 0)])

    def testGetLineCells310(self):
        "getLineCells Non 0 Origin - 4x4 len 2 - right-to-left - slope down"
        g = Grid(-4, -4, 4, 4, 1)
        cell = g.getCell(1.9, 1.1)
        self.assertEqual(cell, (1, 1))
        cells = g.getLineCells(1.9, 1.1, 0.9, 0.1)  # ,verbose=True)
        self.assertEqual(cells, [(1, 1), (1, 0), (0, 0)])

    def testGetLineCells310(self):
        "getLineCells Non 0 Origin - 4x4 len 2 - right-to-left - slope up shallow"
        g = Grid(-4, -4, 4, 4, 1)
        cells = g.getLineCells(-2.9, -3.2, -3.9, -2.9)  # ,verbose=True)
        self.assertEqual(cells, [(1, 0), (0, 0), (0, 1)])

    def testGetLineCells311(self):
        "getLineCells Non 0 Origin - 4x4 len 2 - right-to-left - slope steep"
        g = Grid(-4, -4, 4, 4, 1)
        cells = g.getLineCells(-2.9, -3.9, -3.3, -2.1)  # ,verbose=True)
        self.assertEqual(cells, [(1, 0), (0, 0), (0, 1)])

    # right-to-left - diagonal down
    def testGetLineCells320(self):
        "getLineCells Non 0 Origin - 4x4 len 2 - right-to-left - diagonal down"
        g = Grid(-4, -4, 4, 4, 1)
        cells = g.getLineCells(-2.6, -2.6, -3.3, -3.3)  # ,verbose=True)
        self.assertEqual(cells, [(1, 1), (0, 0)])

    def testGetLineCells321(self):
        "getLineCells Non 0 Origin - 4x4 len 2 - right-to-left - diagonal up"
        g = Grid(-4, -4, 4, 4, 1)
        cells = g.getLineCells(-2.5, -3.5, -3.5, -2.5)  # ,verbose=True)
        self.assertEqual(cells, [(1, 0), (0, 1)])


######################################################################
# 1.4,.6 Origin


class TestGrid_GetLineCells_PlusPoint5Origin(unittest.TestCase):
    # class TestGrid_GetLineCells_PlusPoint5Origin(unittest.TestCase):
    "Use .5,.5 as the origin"

    xmin = 1000.4
    ymin = 3231.6

    def testGetLineCells100(self):
        "getLineCells 10x1 horizontal"
        g = Grid(0 + self.xmin, 0 + self.ymin, 10 + self.xmin, 1 + self.ymin, 1)
        self.assertEqual(g.xNumCells, 10)
        self.assertEqual(g.yNumCells, 1)
        cells = g.getLineCells(
            0.1 + self.xmin, 0.1 + self.ymin, 9.2 + self.xmin, 0.1 + self.ymin
        )
        self.assertEqual(len(cells), 10)
        self.assertEqual(cells[0][0], 0)
        self.assertEqual(cells[0][1], 0)
        self.assertEqual(cells[-1][0], 9)
        self.assertEqual(cells[-1][1], 0)

    def testGetLineCells110(self):
        "getLineCells 10x1 horizontal, slight slope up"
        g = Grid(0 + self.xmin, 0 + self.ymin, 10 + self.xmin, 1 + self.ymin, 1)
        cells = g.getLineCells(
            0.1 + self.xmin, 0.5 + self.ymin, 9.2 + self.xmin, 0.9 + self.ymin
        )
        self.assertEqual(len(cells), 10)
        self.assertEqual(cells[0][0], 0)
        self.assertEqual(cells[0][1], 0)
        self.assertEqual(cells[-1][0], 9)
        self.assertEqual(cells[-1][1], 0)

    def testGetLineCells120(self):
        "getLineCells 10x1 horizontal, slight slope down"
        g = Grid(0 + self.xmin, 0 + self.ymin, 10 + self.xmin, 1 + self.ymin, 1)
        cells = g.getLineCells(
            0.1 + self.xmin, 0.5 + self.ymin, 9.2 + self.xmin, 0.1 + self.ymin
        )
        self.assertEqual(len(cells), 10)
        self.assertEqual(cells[0][0], 0)
        self.assertEqual(cells[0][1], 0)
        self.assertEqual(cells[-1][0], 9)
        self.assertEqual(cells[-1][1], 0)

    def testGetLineCells150(self):
        "getLineCells 1x10 vertical"
        g = Grid(0 + self.xmin, 0 + self.ymin, 1 + self.xmin, 10 + self.ymin, 1)
        cells = g.getLineCells(
            0.5 + self.xmin, 0.5 + self.ymin, 0.5 + self.xmin, 9.1 + self.ymin
        )
        self.assertEqual(len(cells), 10)
        self.assertEqual(cells[0][0], 0)
        self.assertEqual(cells[0][1], 0)
        self.assertEqual(cells[-1][0], 0)
        self.assertEqual(cells[-1][1], 9)

    def testGetLineCells200(self):
        "getLineCells 4x4 len 3 - left-to-right - simple up slope"
        g = Grid(0 + self.xmin, 0 + self.ymin, 4 + self.xmin, 4 + self.ymin, 1)
        cells = g.getLineCells(
            0.9 + self.xmin, 0.1 + self.ymin, 1.5 + self.xmin, 1.1 + self.ymin
        )
        self.assertEqual(cells, [(0, 0), (1, 0), (1, 1)])

    def testGetLineCells210(self):
        "getLineCells 4x4 len 3 - left-to-right - simple up slope 2"
        g = Grid(0 + self.xmin, 0 + self.ymin, 4 + self.xmin, 4 + self.ymin, 1)
        cells = g.getLineCells(
            0.5 + self.xmin, 0.9 + self.ymin, 1.1 + self.xmin, 1.5 + self.ymin
        )
        self.assertEqual(cells, [(0, 0), (0, 1), (1, 1)])

    def testGetLineCells250(self):
        "getLineCells 4x4 len 3 - left-to-right - simple down slope"
        g = Grid(0 + self.xmin, 0 + self.ymin, 4 + self.xmin, 4 + self.ymin, 1)
        cells = g.getLineCells(
            0.1 + self.xmin, 1.1 + self.ymin, 1.1 + self.xmin, 0.1 + self.ymin
        )
        self.assertEqual(cells, [(0, 1), (0, 0), (1, 0)])

    # What happens when we hit a vertex?
    def testGetLineCells260(self):
        "getLineCells 4x4 len 3 - left-to-right - diagonal up"
        g = Grid(0 + self.xmin, 0 + self.ymin, 4 + self.xmin, 4 + self.ymin, 1)
        cells = g.getLineCells(
            0.5 + self.xmin, 0.5 + self.ymin, 1.5 + self.xmin, 1.5 + self.ymin
        )
        self.assertEqual(cells, [(0, 0), (1, 1)])

    # What happens when we hit a vertex?
    def testGetLineCells261(self):
        "getLineCells 4x4 len 3 - left-to-right - diagonal up - end on vertex"
        g = Grid(0 + self.xmin, 0 + self.ymin, 4 + self.xmin, 4 + self.ymin, 1)
        cells = g.getLineCells(
            0.5 + self.xmin, 0.5 + self.ymin, 2 + self.xmin, 2 + self.ymin
        )  # ,verbose=True)
        self.assertEqual(cells, [(0, 0), (1, 1), (2, 2)])

    ##############################
    # Right to left tests
    def testGetLineCells300(self):
        "getLineCells 4x4 len 2 - right-to-left - horiz"
        g = Grid(0 + self.xmin, 0 + self.ymin, 4 + self.xmin, 4 + self.ymin, 1)
        cells = g.getLineCells(
            1.5 + self.xmin, 0.5 + self.ymin, 0.5 + self.xmin, 0.5 + self.ymin
        )
        self.assertEqual(cells, [(1, 0), (0, 0)])

    def testGetLineCells310(self):
        "getLineCells 4x4 len 2 - right-to-left - slope down"
        g = Grid(0 + self.xmin, 0 + self.ymin, 4 + self.xmin, 4, 1 + self.ymin)
        cell = g.getCell(1.9 + self.xmin, 1.1 + self.ymin)
        self.assertEqual(cell, (1, 1))
        cells = g.getLineCells(
            1.9 + self.xmin, 1.1 + self.ymin, 0.9 + self.xmin, 0.1 + self.ymin
        )  # ,verbose=True)
        self.assertEqual(cells, [(1, 1), (1, 0), (0, 0)])

    def testGetLineCells310(self):
        "getLineCells 4x4 len 2 - right-to-left - slope up shallow"
        g = Grid(0 + self.xmin, 0 + self.ymin, 4 + self.xmin, 4 + self.ymin, 1)
        cells = g.getLineCells(
            1.1 + self.xmin, 0.8 + self.ymin, 0.1 + self.xmin, 1.1 + self.ymin
        )  # ,verbose=True)
        self.assertEqual(cells, [(1, 0), (0, 0), (0, 1)])

    def testGetLineCells311(self):
        "getLineCells 4x4 len 2 - right-to-left - slope steep"
        g = Grid(0 + self.xmin, 0 + self.ymin, 4 + self.xmin, 4 + self.ymin, 1)
        cells = g.getLineCells(
            1.1 + self.xmin, 0.1 + self.ymin, 0.7 + self.xmin, 1.9 + self.ymin
        )  # ,verbose=True)
        self.assertEqual(cells, [(1, 0), (0, 0), (0, 1)])

    def testGetLineCells320(self):
        "getLineCells 4x4 len 2 - right-to-left - diagonal down"
        g = Grid(0 + self.xmin, 0 + self.ymin, 4 + self.xmin, 4 + self.ymin, 1)
        cells = g.getLineCells(
            1.4 + self.xmin, 1.4 + self.ymin, 0.7 + self.xmin, 0.7 + self.ymin
        )  # ,verbose=True)
        self.assertEqual(cells, [(1, 1), (0, 0)])

    def testGetLineCells321(self):
        "getLineCells 4x4 len 2 - right-to-left - diagonal up"
        g = Grid(0 + self.xmin, 0 + self.ymin, 4 + self.xmin, 4 + self.ymin, 1)
        cells = g.getLineCells(
            1.5 + self.xmin, 0.5 + self.ymin, 0.5 + self.xmin, 1.5 + self.ymin
        )  # ,verbose=True)
        self.assertEqual(cells, [(1, 0), (0, 1)])


######################################################################
# Test cases for non unit cell size...


class TestGrid_GetLineCells_stepsizes(unittest.TestCase):
    # class TestGrid_GetLineCells_stepsizes(unittest.TestCase):
    "Use .5,.5 as the origin"

    xmin = 1000.4
    ymin = 3231.6
    stepSize = 10.14

    def testGetLineCells100(self):
        "getLineCells 10x1 horizontal"
        ss = self.stepSize
        g = Grid(
            0 + self.xmin,
            0 + self.ymin,
            (10 * ss) + self.xmin,
            (1 * ss) + self.ymin,
            ss,
        )
        self.assertEqual(g.xNumCells, 10)
        self.assertEqual(g.yNumCells, 1)
        cells = g.getLineCells(
            0.1 + self.xmin,
            0.1 + self.ymin,
            (9.2 * ss) + self.xmin,
            (0.1 * ss) + self.ymin,
        )
        self.assertEqual(len(cells), 10)
        self.assertEqual(cells[0][0], 0)
        self.assertEqual(cells[0][1], 0)
        self.assertEqual(cells[-1][0], 9)
        self.assertEqual(cells[-1][1], 0)

    def testGetLineCells100(self):
        "getLineCells 10x2"
        ss = self.stepSize
        g = Grid(
            0 + self.xmin,
            0 + self.ymin,
            (10 * ss) + self.xmin,
            (2 * ss) + self.ymin,
            ss,
        )
        self.assertTrue(g.xNumCells in (10, 11))
        self.assertTrue(g.yNumCells in (2, 3))

    def testGetLineCells110(self):
        "getLineCells 10x1 horizontal, slight slope up"
        ss = self.stepSize
        g = Grid(
            0 + self.xmin,
            0 + self.ymin,
            (10 * ss) + self.xmin,
            (1 * ss) + self.ymin,
            ss,
        )  # , verbose=True)
        cells = g.getLineCells(
            (0.1 * ss) + self.xmin,
            (0.5 * ss) + self.ymin,
            (9.2 * ss) + self.xmin,
            (0.9 * ss) + self.ymin,
        )
        self.assertTrue(g.xNumCells in (10, 11))
        self.assertTrue(g.yNumCells in (1, 2))
        self.assertEqual(len(cells), 10)
        self.assertEqual(cells[0][0], 0)
        self.assertEqual(cells[0][1], 0)
        self.assertEqual(cells[-1][0], 9)
        self.assertEqual(cells[-1][1], 0)

    def testGetLineCells120(self):
        "getLineCells 10x1 horizontal, slight slope down"
        ss = self.stepSize
        g = Grid(
            0 + self.xmin,
            0 + self.ymin,
            (10 * ss) + self.xmin,
            (1 * ss) + self.ymin,
            ss,
        )
        cells = g.getLineCells(
            (0.1 * ss) + self.xmin,
            (0.5 * ss) + self.ymin,
            (9.2 * ss) + self.xmin,
            (0.1 * ss) + self.ymin,
        )
        self.assertEqual(len(cells), 10)
        self.assertEqual(cells[0][0], 0)
        self.assertEqual(cells[0][1], 0)
        self.assertEqual(cells[-1][0], 9)
        self.assertEqual(cells[-1][1], 0)

    def testGetLineCells150(self):
        "getLineCells 1x10 vertical"
        ss = self.stepSize
        g = Grid(
            0 + self.xmin,
            0 + self.ymin,
            (1 * ss) + self.xmin,
            (10 * ss) + self.ymin,
            ss,
        )
        cells = g.getLineCells(
            (0.5 * ss) + self.xmin,
            (0.5 * ss) + self.ymin,
            (0.5 * ss) + self.xmin,
            (9.1 * ss) + self.ymin,
        )
        self.assertEqual(len(cells), 10)
        self.assertEqual(cells[0][0], 0)
        self.assertEqual(cells[0][1], 0)
        self.assertEqual(cells[-1][0], 0)
        self.assertEqual(cells[-1][1], 9)

    def testGetLineCells200(self):
        "getLineCells 4x4 len 3 - left-to-right - simple up slope"
        ss = self.stepSize
        g = Grid(
            0 + self.xmin, 0 + self.ymin, (4 * ss) + self.xmin, (4 * ss) + self.ymin, ss
        )
        self.assertTrue(g.xNumCells in (4, 5))
        self.assertTrue(g.yNumCells in (4, 5))
        cells = g.getLineCells(
            (ss * 0.9) + self.xmin,
            (0.1 * ss) + self.ymin,
            (1.5 * ss) + self.xmin,
            (1.1 * ss) + self.ymin,
        )
        self.assertEqual(cells, [(0, 0), (1, 0), (1, 1)])

    def testGetLineCells210(self):
        "getLineCells 4x4 len 3 - left-to-right - simple up slope 2"
        ss = self.stepSize
        g = Grid(
            0 + self.xmin, 0 + self.ymin, (4 * ss) + self.xmin, (4 * ss) + self.ymin, ss
        )
        cells = g.getLineCells(
            (0.5 * ss) + self.xmin,
            (0.9 * ss) + self.ymin,
            (1.1 * ss) + self.xmin,
            (1.5 * ss) + self.ymin,
        )
        self.assertEqual(cells, [(0, 0), (0, 1), (1, 1)])

    def testGetLineCells250(self):
        "getLineCells 4x4 len 3 - left-to-right - simple down slope"
        ss = self.stepSize
        g = Grid(
            0 + self.xmin, 0 + self.ymin, (4 * ss) + self.xmin, (4 * ss) + self.ymin, ss
        )
        cells = g.getLineCells(
            (0.1 * ss) + self.xmin,
            (1.1 * ss) + self.ymin,
            (1.1 * ss) + self.xmin,
            (0.1 * ss) + self.ymin,
        )
        self.assertEqual(cells, [(0, 1), (0, 0), (1, 0)])

    # What happens when we hit a vertex?
    def testGetLineCells260(self):
        "getLineCells 4x4 len 3 - left-to-right - diagonal up"
        ss = self.stepSize
        g = Grid(
            0 + self.xmin, 0 + self.ymin, (4 * ss) + self.xmin, (4 * ss) + self.ymin, ss
        )
        cells = g.getLineCells(
            (0.5 * ss) + self.xmin,
            (0.5 * ss) + self.ymin,
            (1.5 * ss) + self.xmin,
            (1.5 * ss) + self.ymin,
        )
        self.assertEqual(cells, [(0, 0), (1, 1)])

    # What happens when we hit a vertex?
    def testGetLineCells261(self):
        "getLineCells 4x4 len 3 - left-to-right - diagonal up - end on vertex"
        ss = self.stepSize
        g = Grid(
            0 + self.xmin, 0 + self.ymin, (4 * ss) + self.xmin, (4 * ss) + self.ymin, ss
        )
        x0, y0 = (0.5 * ss) + self.xmin, (0.5 * ss) + self.ymin
        x1, y1 = (2.01 * ss) + self.xmin, (2.01 * ss) + self.ymin
        cells = g.getLineCells(x0, y0, x1, y1)  # ,verbose=True)
        self.assertEqual(cells, [(0, 0), (1, 1), (2, 2)])

    ##############################
    # Right to left tests
    def testGetLineCells300(self):
        "getLineCells 4x4 len 2 - right-to-left - horiz"
        ss = self.stepSize
        g = Grid(
            0 + self.xmin, 0 + self.ymin, (4 * ss) + self.xmin, (4 * ss) + self.ymin, ss
        )
        cells = g.getLineCells(
            (1.5 * ss) + self.xmin,
            (0.5 * ss) + self.ymin,
            (0.5 * ss) + self.xmin,
            (0.5 * ss) + self.ymin,
        )
        self.assertEqual(cells, [(1, 0), (0, 0)])

    def testGetLineCells310(self):
        "getLineCells 4x4 len 2 - right-to-left - slope down"
        ss = self.stepSize
        g = Grid(0 + self.xmin, 0 + self.ymin, (4 * ss) + self.xmin, 4, 1 + self.ymin)
        cell = g.getCell(1.9 + self.xmin, 1.1 + self.ymin)
        self.assertEqual(cell, (1, 1))
        cells = g.getLineCells(
            1.9 + self.xmin, 1.1 + self.ymin, 0.9 + self.xmin, 0.1 + self.ymin
        )  # ,verbose=True)
        self.assertEqual(cells, [(1, 1), (1, 0), (0, 0)])

    def testGetLineCells310(self):
        "getLineCells 4x4 len 2 - right-to-left - slope up shallow"
        ss = self.stepSize
        g = Grid(
            0 + self.xmin, 0 + self.ymin, (4 * ss) + self.xmin, (4 * ss) + self.ymin, ss
        )
        cells = g.getLineCells(
            (1.1 * ss) + self.xmin,
            (0.8 * ss) + self.ymin,
            (0.1 * ss) + self.xmin,
            (1.1 * ss) + self.ymin,
        )  # ,verbose=True)
        self.assertEqual(cells, [(1, 0), (0, 0), (0, 1)])

    def testGetLineCells311(self):
        "getLineCells 4x4 len 2 - right-to-left - slope steep"
        ss = self.stepSize
        g = Grid(
            0 + self.xmin, 0 + self.ymin, (4 * ss) + self.xmin, (4 * ss) + self.ymin, ss
        )
        cells = g.getLineCells(
            (1.1 * ss) + self.xmin,
            (0.1 * ss) + self.ymin,
            (0.7 * ss) + self.xmin,
            (1.9 * ss) + self.ymin,
        )  # ,verbose=True)
        self.assertEqual(cells, [(1, 0), (0, 0), (0, 1)])

    def testGetLineCells320(self):
        "getLineCells 4x4 len 2 - right-to-left - diagonal down"
        ss = self.stepSize
        g = Grid(
            0 + self.xmin, 0 + self.ymin, (4 * ss) + self.xmin, (4 * ss) + self.ymin, ss
        )
        cells = g.getLineCells(
            (1.4 * ss) + self.xmin,
            (1.4 * ss) + self.ymin,
            (0.7 * ss) + self.xmin,
            (0.7 * ss) + self.ymin,
        )  # ,verbose=True)
        self.assertEqual(cells, [(1, 1), (0, 0)])

    def testGetLineCells321(self):
        "getLineCells 4x4 len 2 - right-to-left - diagonal up"
        ss = self.stepSize
        g = Grid(
            0 + self.xmin, 0 + self.ymin, (4 * ss) + self.xmin, (4 * ss) + self.ymin, ss
        )
        x0, y0 = (ss * 1.5) + self.xmin, (ss * 0.5) + self.ymin
        x1, y1 = (ss * 0.5) + self.xmin, (ss * 1.5) + self.ymin

        cells = g.getLineCells(x0, y0, x1, y1)  # ,verbose=True)
        self.assertEqual(cells, [(1, 0), (0, 1)])

    def testGetLineCells321(self):
        "getLineCells 4x4 len 2 - right-to-left - diagonal up"
        ss = self.stepSize
        g = Grid(
            0 + self.xmin, 0 + self.ymin, (4 * ss) + self.xmin, (4 * ss) + self.ymin, ss
        )
        x0, y0 = (ss * 1.95) + self.xmin, (ss * 0.05) + self.ymin
        x1, y1 = (ss * 0.05) + self.xmin, (ss * 1.95) + self.ymin

        cells = g.getLineCells(x0, y0, x1, y1)  # ,verbose=True)
        self.assertEqual(cells, [(1, 0), (0, 1)])


######################################################################
# Test cases for non unit cell size...


class TestGrid_GetMultiSegLineCells(unittest.TestCase):
    # class TestGrid_GetMultiSegLineCells(unittest.TestCase):
    "Make sure that lines with multiple vertices scan convert"

    stepSize = 1
    xmin = 0
    xmax = 4
    ymin = 0
    ymax = 4

    def testASeg1(self):
        "Single line segment - one cell"
        ss = self.stepSize
        xmin = self.xmin
        xmax = self.xmax
        ymin = self.ymin
        ymax = self.ymax
        g = Grid(0 * ss + xmin, 0 * ss + ymin, 4 * ss + xmin, 4 * ss + ymin, ss)
        cells = g.getMultiSegLineCells(((0.1, 0.5), (0.3, 0.5)))
        self.assertEqual(cells, [(0, 0)])

    def testASeg2(self):
        "Single line segment - two cells horizontal"
        ss = self.stepSize
        xmin = self.xmin
        xmax = self.xmax
        ymin = self.ymin
        ymax = self.ymax
        g = Grid(0 * ss + xmin, 0 * ss + ymin, 4 * ss + xmin, 4 * ss + ymin, ss)
        cells = g.getMultiSegLineCells(
            ((xmin + ss * 0.1, ymin + ss * 0.5), (xmin + ss * 1.3, ymin + ss * 0.5))
        )
        self.assertEqual(cells, [(0, 0), (1, 0)])

    def testTwoSegs1(self):
        "L shape - 3 cells"
        ss = self.stepSize
        xmin = self.xmin
        xmax = self.xmax
        ymin = self.ymin
        ymax = self.ymax
        g = Grid(0 * ss + xmin, 0 * ss + ymin, 4 * ss + xmin, 4 * ss + ymin, ss)
        cells = g.getMultiSegLineCells(
            (
                (xmin + ss * 0.1, ymin + ss * 0.5),
                (xmin + ss * 1.3, ymin + ss * 0.5),
                (xmin + ss * 1.3, ymin + ss * 1.5),
            )
        )
        self.assertEqual(cells, [(0, 0), (1, 0), (1, 1)])

    def testSegs3(self):
        "Single line segment - two cells horizontal"
        ss = self.stepSize
        xmin = self.xmin
        xmax = self.xmax
        ymin = self.ymin
        ymax = self.ymax
        g = Grid(0 * ss + xmin, 0 * ss + ymin, 4 * ss + xmin, 4 * ss + ymin, ss)
        cells = g.getMultiSegLineCells(
            (
                (xmin + ss * 0.1, ymin + ss * 0.5),
                (xmin + ss * 1.3, ymin + ss * 0.5),
                (xmin + ss * 1.3, ymin + ss * 1.5),
                (xmin + ss * 0.3, ymin + ss * 1.5),
            )
        )
        self.assertEqual(cells, [(0, 0), (1, 0), (1, 1), (0, 1)])

    def testSegs4(self):
        "Single line segment - two cells horizontal"
        ss = self.stepSize
        xmin = self.xmin
        xmax = self.xmax
        ymin = self.ymin
        ymax = self.ymax
        g = Grid(0 * ss + xmin, 0 * ss + ymin, 4 * ss + xmin, 4 * ss + ymin, ss)
        cells = g.getMultiSegLineCells(
            (
                (xmin + ss * 0.1, ymin + ss * 0.5),
                (xmin + ss * 1.3, ymin + ss * 0.5),
                (xmin + ss * 1.3, ymin + ss * 1.5),
                (xmin + ss * 0.3, ymin + ss * 1.5),
                (xmin + ss * 0.1, ymin + ss * 0.5),
            )
        )
        self.assertEqual(cells, [(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)])

    def testSegs4_1(self):
        "Single line segment - two cells horizontal"
        ss = self.stepSize
        xmin = self.xmin
        xmax = self.xmax
        ymin = self.ymin
        ymax = self.ymax
        g = Grid(0 * ss + xmin, 0 * ss + ymin, 4 * ss + xmin, 4 * ss + ymin, ss)
        cells = g.getMultiSegLineCells(
            (
                (xmin + ss * 0.1, ymin + ss * 0.5),
                (xmin + ss * 3.3, ymin + ss * 0.5),
                (xmin + ss * 3.3, ymin + ss * 3.5),
            )
        )
        self.assertEqual(
            cells, [(0, 0), (1, 0), (2, 0), (3, 0), (3, 1), (3, 2), (3, 3)]
        )

    def testSegs4_2(self):
        "Single line segment - two cells horizontal"
        ss = self.stepSize
        xmin = self.xmin
        xmax = self.xmax
        ymin = self.ymin
        ymax = self.ymax
        g = Grid(0 * ss + xmin, 0 * ss + ymin, 4 * ss + xmin, 4 * ss + ymin, ss)
        cells = g.getMultiSegLineCells(
            (
                (xmin + ss * 0.1, ymin + ss * 0.5),
                (xmin + ss * 3.3, ymin + ss * 0.5),
                (xmin + ss * 3.3, ymin + ss * 3.5),
                (xmin + ss * 0.3, ymin + ss * 3.5),
            )
        )
        self.assertEqual(
            cells,
            [
                (0, 0),
                (1, 0),
                (2, 0),
                (3, 0),
                (3, 1),
                (3, 2),
                (3, 3),
                (2, 3),
                (1, 3),
                (0, 3),
            ],
        )

    def testSegs4_3(self):
        "Single line segment - two cells horizontal"
        ss = self.stepSize
        xmin = self.xmin
        xmax = self.xmax
        ymin = self.ymin
        ymax = self.ymax
        g = Grid(0 * ss + xmin, 0 * ss + ymin, 4 * ss + xmin, 4 * ss + ymin, ss)
        cells = g.getMultiSegLineCells(
            (
                (xmin + ss * 0.1, ymin + ss * 0.5),
                (xmin + ss * 3.3, ymin + ss * 0.5),
                (xmin + ss * 3.3, ymin + ss * 3.5),
                (xmin + ss * 0.3, ymin + ss * 3.5),
                (xmin + ss * 0.1, ymin + ss * 0.5),
            )
        )
        self.assertEqual(
            cells,
            [
                (0, 0),
                (1, 0),
                (2, 0),
                (3, 0),
                (3, 1),
                (3, 2),
                (3, 3),
                (2, 3),
                (1, 3),
                (0, 3),
                (0, 0),
                (0, 1),
                (0, 2),
            ],
        )
        # FIX: this is a case where the cells do not come back in the expected order?!?!
        # FIX: would be better if the cells actually came in the right order!


######################################################################


class TestGrid_GetMultiSegLineCells(unittest.TestCase):
    # class TestGrid_addMultiSegLine(unittest.TestCase):
    "Make sure that lines with multiple vertices scan convert"

    stepSize = 1
    xmin = 0
    xmax = 4
    ymin = 0
    ymax = 4

    def testSegs4_0(self):
        "Single line segment - single cell"
        ss = self.stepSize
        xmin = self.xmin
        xmax = self.xmax
        ymin = self.ymin
        ymax = self.ymax
        g = Grid(0 * ss + xmin, 0 * ss + ymin, 4 * ss + xmin, 4 * ss + ymin, ss)
        line = ((xmin + ss * 0.1, ymin + ss * 0.5), (xmin + ss * 0.12, ymin + ss * 0.5))
        g.addMultiSegLine(line)  # ,verbose=True)
        # g.writeLayoutGnuplot('0-grid.dat')
        # g.writeCellsGnuplot('0.dat')
        self.assertEqual(g.grid[0, 0], 1)

    def testSegs4_1(self):
        "Single line segment - two cells horizontal"
        ss = self.stepSize
        xmin = self.xmin
        xmax = self.xmax
        ymin = self.ymin
        ymax = self.ymax
        g = Grid(0 * ss + xmin, 0 * ss + ymin, 4 * ss + xmin, 4 * ss + ymin, ss)
        line = ((xmin + ss * 0.1, ymin + ss * 0.5), (xmin + ss * 3.3, ymin + ss * 0.5))
        g.addMultiSegLine(line)
        g.writeLayoutGnuplot("1-grid.dat")
        g.writeCellsGnuplot("1.dat")
        self.assertEqual(g.grid[0, 0], 1)

    def testSegs4_3(self):
        "Single line segment - two cells horizontal"
        ss = self.stepSize
        xmin = self.xmin
        xmax = self.xmax
        ymin = self.ymin
        ymax = self.ymax
        g = Grid(0 * ss + xmin, 0 * ss + ymin, 4 * ss + xmin, 4 * ss + ymin, ss)
        line = (
            (xmin + ss * 0.1, ymin + ss * 0.5),
            (xmin + ss * 3.3, ymin + ss * 0.5),
            (xmin + ss * 3.3, ymin + ss * 3.5),
            (xmin + ss * 0.3, ymin + ss * 3.5),
        )
        cells = g.getMultiSegLineCells(line)
        self.assertEqual(
            cells,
            [
                (0, 0),
                (1, 0),
                (2, 0),
                (3, 0),
                (3, 1),
                (3, 2),
                (3, 3),
                (2, 3),
                (1, 3),
                (0, 3),
            ],
        )

        g.addMultiSegLine(line)
        g.writeLayoutGnuplot("3-grid.dat")
        g.writeCellsGnuplot("3.dat")
        self.assertEqual(g.grid[0, 0], 1)
        self.assertEqual(g.grid[3, 0], 1)
        self.assertEqual(g.grid[3, 3], 1)
        self.assertEqual(g.grid[0, 3], 1)
        self.assertEqual(g.grid[2, 2], 0)

    def testSegs4_4(self):
        "Four line segments - box"
        ss = self.stepSize
        xmin = self.xmin
        xmax = self.xmax
        ymin = self.ymin
        ymax = self.ymax
        g = Grid(0 * ss + xmin, 0 * ss + ymin, 4 * ss + xmin, 4 * ss + ymin, ss)
        line = (
            (xmin + ss * 0.1, ymin + ss * 0.5),
            (xmin + ss * 3.3, ymin + ss * 0.5),
            (xmin + ss * 3.3, ymin + ss * 3.5),
            (xmin + ss * 0.3, ymin + ss * 3.5),
            (xmin + ss * 0.1, ymin + ss * 0.5),
        )
        cells = g.getMultiSegLineCells(line)
        g.addMultiSegLine(line)
        g.writeLayoutGnuplot("4-grid.dat")
        g.writeCellsGnuplot("4.dat")
        self.assertEqual(g.grid[0, 0], 2)
        self.assertEqual(g.grid[3, 0], 1)
        self.assertEqual(g.grid[3, 3], 1)
        self.assertEqual(g.grid[0, 3], 1)
        self.assertEqual(g.grid[2, 2], 0)


class TestWhyDidThisFail(unittest.TestCase):
    def test1(self):
        "Vertical line in reverse direction"
        ss = 1852.0
        xmin = 359207.844601
        xmax = 426523.405265
        ymin = 4651174.05098
        ymax = 4750102.91341
        g = Grid(xmin, ymin, xmax, ymax, ss, verbose=True)
        cells = g.getLineCells(
            415216.29984943097,
            4671534.0646001603,
            415182.051535215,
            4671547.4328312902,
            verbose=True,
        )
        print(cells)
        self.assertTrue(len(cells) > 0)


class TestArcAsciiGrid(unittest.TestCase):
    def test001(self):
        g = Grid(0, 0, 4, 4, 1)
        g.writeArcAsciiGrid("tmp_4x4.asc")
        print("FIX: how do I validate writing to a file with unittest?")

    def test010(self):
        g = Grid(0, 0, 4, 4, 1)
        g.grid[0, 0] = 1  # LL corner
        g.writeArcAsciiGrid("tmp_4x4_ll.asc")
        print("FIX: how do I validate writing to a file with unittest?")

    def test020(self):
        g = Grid(0, 0, 4, 4, 1)
        g.grid[0, 3] = 1  # UL corner
        g.writeArcAsciiGrid("tmp_4x4_ul.asc")
        # print 'FIX: how do I validate writing to a file with unittest?'

    def test030(self):
        g = Grid(0, 0, 4, 4, 1)
        g.grid[3, 0] = 1  # lr corner
        g.writeArcAsciiGrid("tmp_4x4_lr.asc")
        # print 'FIX: how do I validate writing to a file with unittest?'

    def test040(self):
        g = Grid(0, 0, 4, 4, 1)
        g.grid[3, 3] = 1  # ur corner
        g.writeArcAsciiGrid("tmp_4x4_ur.asc")
        # print 'FIX: how do I validate writing to a file with unittest?'


class TestGridLength(unittest.TestCase):
    stepSize = 1
    xmin = 0
    xmax = 4
    ymin = 0
    ymax = 4

    def testSingleCell(self):
        ss = self.stepSize
        xmin = self.xmin
        xmax = self.xmax
        ymin = self.ymin
        ymax = self.ymax
        g = Grid(
            0 * ss + xmin,
            0 * ss + ymin,
            4 * ss + xmin,
            4 * ss + ymin,
            ss,
            gridType="distance",
        )
        line = ((0, 1.5), (1, 1.5))

        # Single cell - vert
        r = g.getLineCellsWithCrossings(0.25, 0, 0.75, 0.0, verbose=True)
        # print 'r',r
        cell, frac1, frac2, dist = r[0]
        self.assertEqual((0, 0), cell)
        self.assertAlmostEqual(0.0, frac1)
        self.assertAlmostEqual(1.0, frac2)
        self.assertAlmostEqual(0.5, dist)

        # Single cell - horz
        r = g.getLineCellsWithCrossings(0, 0.25, 0.0, 0.75, verbose=True)
        self.assertEqual((0, 0), cell)
        self.assertEqual(0.0, frac1)
        self.assertEqual(1.0, frac2)
        self.assertAlmostEqual(0.5, dist)

    def testHorizontal1(self):
        ss = self.stepSize
        xmin = self.xmin
        xmax = self.xmax
        ymin = self.ymin
        ymax = self.ymax
        g = Grid(
            0 * ss + xmin,
            0 * ss + ymin,
            4 * ss + xmin,
            4 * ss + ymin,
            ss,
            gridType="distance",
        )
        line = ((0, 1.5), (1, 1.5))

        # Horizontal
        r = g.getLineCellsWithCrossings(0.5, 1.5, 1.5, 1.5)  # ,verbose=True)
        self.assertEqual(len(r), 2)

        cell, frac1, frac2, dist = r[0]
        self.assertEqual((0, 1), cell)
        self.assertEqual(0.0, frac1)
        self.assertEqual(0.5, frac2)
        self.assertAlmostEqual(0.5, dist)

        cell, frac1, frac2, dist = r[1]
        self.assertEqual((1, 1), cell)
        self.assertEqual(0.5, frac1)
        self.assertEqual(1.0, frac2)
        self.assertAlmostEqual(0.5, dist)

        r = g.getLineCellsWithCrossings(0.5, 1.5, 4.5, 1.5)  # ,verbose=True)
        print(r)
        self.assertEqual(len(r), 5)

        cell, frac1, frac2, dist = r[0]
        self.assertEqual((0, 1), cell)
        self.assertEqual(0.0, frac1)
        self.assertAlmostEqual(0.25 / 2.0, frac2)
        self.assertAlmostEqual(0.5, dist)

        cell, frac1, frac2, dist = r[-1]
        self.assertEqual((4, 1), cell)
        self.assertAlmostEqual(1 - (0.25 / 2.0), frac1)
        self.assertEqual(1.0, frac2)
        self.assertAlmostEqual(0.5, dist)

        print("r", r)


############################################################
if __name__ == "__main__":
    from optparse import OptionParser

    parser = OptionParser(usage="%prog [options]", version="%prog " + __version__)
    parser.add_option(
        "--unit-test",
        dest="unittest",
        default=False,
        action="store_true",
        help="run the unit tests",
    )
    parser.add_option(
        "-v",
        "--verbose",
        dest="verbose",
        default=False,
        action="store_true",
        help="Make the test output verbose",
    )

    (options, args) = parser.parse_args()

    if options.unittest:
        import sys

        sys.argv = [sys.argv[0]]
        if options.verbose:
            sys.argv.append("-v")
        unittest.main()
