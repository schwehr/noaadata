#!/usr/bin/env python
__author__ = "Kurt Schwehr"
__version__ = ["$Revision:", "8545", "$"][1]
__revision__ = __version__  # For pylint
__date__ = [
    "$Date:",
    "2008-02-06",
    "17:37:24",
    "-0500",
    "(Wed,",
    "06",
    "Feb",
    "2008)",
    "$",
][1]
__copyright__ = "2008"
__license__ = "Apache 2.0"

__doc__ = """
AIS database utilities.

@status: under development
@since: 2008-Feb-07
@undocumented: __doc__ parser

@requires: U{GeoTypes<http://www.initd.org/tracker/psycopg/wiki/GeoTypes>} >= 0.7.0

@todo: Switch to GeoDjango so that this becomes irrelevant
"""

# @requires: U{psycopg2<http://http://initd.org/projects/psycopg2/>} >= 2.0.6
# import psycopg2
# import psycopg2.extensions
try:
    import GeoTypes
except ImportError:
    GeoTypes = None


class convert:
    """Simple wrapper to make decoding WKB Hex a lot simpler."""

    def __init__(self):
        if GeoTypes is None:
            raise ImportError("GeoTypes module is not available")
        self.factory = GeoTypes.OGGeoTypeFactory()
        self.parser = GeoTypes.HEXEWKBParser(self.factory)

    def decode(self, wkbhex):
        """Convert a WKB Hex string to an object.

        Args:
            wkbhex: HEX geometry string.

        Returns:
            Geometry object parsed from WKB Hex string.
        """
        if GeoTypes is None:
            raise ImportError("GeoTypes module is not available")
        self.parser.parseGeometry(wkbhex)
        geom = self.factory.getGeometry()
        return geom
