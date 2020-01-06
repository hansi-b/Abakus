import unittest
from datetime import date
from decimal import Decimal

from abakus.laufend import Summierer, Anstellung
from abakus.model import Stelle, AllGuS
from tests.abakus.modelTest import TestMitGehältern

trivialCalc = Summierer(None).calcSonderzahlung


class SummiererCalcSonderzahlungTest(TestMitGehältern):

    def testNotNovember(self):

        for m in range(1, 13):
            if m == 11:
                continue
            self.assertIsNone(trivialCalc(date(2019, m, 1), None))

    def testNovemberButNoDezember(self):
        anst = Anstellung(Stelle(AllGuS.E10_3, date(2019, 1, 1)), date(2019, 1, 1), date(2019, 11, 30))
        self.assertEqual(Decimal(0.), trivialCalc(date(2019, 11, 1), anst))

    def testNovemberAndDezember(self):
        self.givenGehalt(2019, AllGuS.E10_3, 12., 75.)
        lCalc = Summierer(self.ötv).calcSonderzahlung

        anst = Anstellung(Stelle(AllGuS.E10_3, date(2019, 1, 1)), date(2019, 1, 1), date(2019, 12, 31))

        self.assertAlmostEqual(Decimal(1.3 * 9.), lCalc(date(2019, 11, 1), anst))

    def testE10MitVorgeschichte(self):
        self.givenGehalt(2019, AllGuS.E10_3, 6., 50.)
        lCalc = Summierer(self.ötv).calcSonderzahlung

        anst = Anstellung(Stelle(AllGuS.E10_3, date(2019, 1, 1)), date(2019, 1, 1), date(2020, 1, 1))
        self.assertAlmostEqual(Decimal(1.3 * 3.), lCalc(date(2019, 11, 1), anst))


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
