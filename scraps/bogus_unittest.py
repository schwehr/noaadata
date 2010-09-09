'''
Dummy standin for unittest so that some groups of test do not get run
when they inherit this module instead of the normal unittest.
'''
class TestCase:
    def failUnlessEqual():
        pass
    def failUnlessAlmostEqual():
        pass
