import unittest
from excel.data import Gehalt

class GehälterTest(unittest.TestCase):

    def testStufen(self):
        g = Gehalt(2400, 200)
        print(g)



if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
