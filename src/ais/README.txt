
Kurt Schwehr's try 3 at an AIS parsing and generation package.  This
one really is a compiler.

BitVector.py is by Avi Kak at Purdue and is included with permission.

TODO:
* expandais sometimes inserts structs in the wrong place.  Can be hacked into place with comment nodes.
* Put in "Do not mangle name" for all strcture includes where there are no conflicts.  Simpler.
* Conditional sections
* AIS Messages 24 A and B are defined in 80_405e_CDV.pdf.  What to do about case statements?
* msg 17 - IALA A-124 Page 136 Table B1  - Also in the ITU spec - DGNSS
* other IMO messages
* Other RIS/EU / UN waterway messages
