
import unittest
import datetime
from gui import Abakus


class Test(unittest.TestCase):

    def testOffsetVonDate(self):

        d = Abakus.offsetVonDate(datetime.date(2019, 1, 1))       
        self.assertEqual(datetime.date(2019, 3, 1), d)

        d = Abakus.offsetVonDate(datetime.date(2019, 8, 23))       
        self.assertEqual(datetime.date(2019, 10, 1), d)

        d = Abakus.offsetVonDate(datetime.date(2019, 10, 31))       
        self.assertEqual(datetime.date(2019, 12, 1), d)

    def testOffsetVonDateOverflow(self):

        d = Abakus.offsetVonDate(datetime.date(2019, 11, 2))       
        self.assertEqual(datetime.date(2020, 1, 1), d)

        d = Abakus.offsetVonDate(datetime.date(2019, 12, 12))       
        self.assertEqual(datetime.date(2020, 2, 1), d)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
