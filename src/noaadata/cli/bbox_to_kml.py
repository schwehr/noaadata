#!/usr/bin/env python

__version__ = "$Revision$"[11:-2]
__date__ = "$Date$"[7:-2]
__author__ = "Kurt Schwehr"

from optparse import OptionParser


def main():
    parser = OptionParser(
        usage="%prog [options] [file1.txt file2.txt ...]",
        version="%prog " + __version__ + " (" + __date__ + ")",
    )

    parser.add_option(
        "-v",
        "--verbose",
        dest="verbose",
        default=False,
        action="store_true",
        help="run the tests run in verbose mode",
    )

    (_options, args) = parser.parse_args()

    print("""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://earth.google.com/kml/2.1">
  <Document>
    <Folder id="bounding boxes">
""")
    for filename in args:
        for line in open(filename):
            station, x1, x2, y1, y2 = line.split()
            print(
                f"""<Placemark><name>{station}</name><Polygon>
  <!-- specific to Polygon -->
  <extrude>0</extrude>                       <!-- boolean -->
  <tessellate>1</tessellate>                 <!-- boolean -->
  <altitudeMode>clampToGround</altitudeMode>
  <outerBoundaryIs>
    <LinearRing>
      <coordinates>{x1},{y1},1000 {x1},{y2},1000 {x2},{y2},1000 {x2},{y1},1000 {x1},{y1},1000</coordinates>         <!-- lon,lat[,alt] -->
    </LinearRing>
  </outerBoundaryIs>
</Polygon></Placemark>
"""
            )
            x = (float(x1) + float(x2)) / 2.0
            y = (float(y1) + float(y2)) / 2.0

            print(
                f"""<Placemark><name>{station}</name><Point><coordinates>{x:f},{y:f}</coordinates></Point></Placemark>"""
            )

    print("</Folder></Document></kml>")


if __name__ == "__main__":
    main()
