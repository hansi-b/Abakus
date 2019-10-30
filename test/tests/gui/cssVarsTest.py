__author__ = "Hans Bering"
__copyright__ = "Copyright 2019, Hans Bering"
__license__ = "GPL3"
__status__ = "Development"

import unittest
from gui.cssVars import varredCss2Css


class Test(unittest.TestCase):

    def testNoVariables(self):
        varred = "abc\nxyz".split()
        self.assertEquals(varred,
                          list(varredCss2Css(varred)))

    def testSimpleVariables(self):
        varred = [
            "/** {Variables}",
            "x=1",
            "*/",
            "a:'{x}';"
            ]
        result = [
            "/** {Variables}",
            "x=1",
            "*/",
            "a:1;"
            ]
        
        self.assertEquals(result,
                          list(varredCss2Css(varred)))


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testSimple']
    unittest.main()
