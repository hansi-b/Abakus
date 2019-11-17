import unittest
from datetime import date
from decimal import Decimal

from abakus import laufend
from abakus.laufend import Summierer
from abakus.model import Stelle, AllGuS, Gehalt
from tests.abakus.modelTest import TestMitGehältern


class MonatsListeTest(unittest.TestCase):

    def testLaufendSimple(self):

        s = Stelle(AllGuS.E10_3, date(2019, 7, 1))
        # NB: Enddatum ist nicht der letzte Tag im Monat
        actual = laufend.monatsListe(s, date(2019, 7, 1), date(2019, 9, 13))
        expected = [(date(2019, 7, 31), s), (date(2019, 8, 31), s)]
        self.assertEqual(expected, actual)

    def testLetzterTagImMonat(self):

        s = Stelle(AllGuS.E10_3, date(2019, 7, 1))
        actual = laufend.monatsListe(s, date(2019, 7, 1), date(2019, 8, 31))
        expected = [(date(2019, 7, 31), s), (date(2019, 8, 31), s)]
        self.assertEqual(expected, actual)

    def testLaufendJahresWechsel(self):

        s = Stelle(AllGuS.E10_3, date(2019, 7, 1))
        actual = laufend.monatsListe(s, date(2019, 12, 1), date(2020, 2, 29))
        expected = [(date(2019, 12, 31), s), (date(2020, 1, 31), s),
                    (date(2020, 2, 29), s)]
        self.assertEqual(expected, actual)

    def testFalscheArgumente(self):

        s = Stelle(AllGuS.E10_3, date(2019, 7, 1))
        try:
            laufend.monatsListe(s, date(2019, 5, 1), date(2019, 8, 1))
        except AssertionError as e:
            assert "liegt nach dem Anfangsdatum" in str(e), "Got: {}".format(e)
        else:
            self.fail("Expected AssertionError")
        try:
            laufend.monatsListe(s, date(2019, 8, 1), date(2019, 7, 1))
        except AssertionError as e:
            assert "liegt nach dem Enddatum" in str(e), "Got: {}".format(e)
        else:
            self.fail("Expected AssertionError")


trivialCalc = Summierer(None).calcSonderzahlung


class SummiererCalcSonderzahlungTest(TestMitGehältern):

    def testNotNovember(self):

        for m in range(1, 13):
            if m == 11:
                continue
            self.assertIsNone(trivialCalc(date(2019, m, 1), date(2022, 12, 1), None))

    def testNovemberButNoDezember(self):
        self.assertEqual(Decimal(0.), trivialCalc(date(2019, 11, 1), date(2019, 11, 30), None))

    def testNovemberAndDezember(self):
        self.givenGehalt(2019, AllGuS.E10_3, Gehalt.by(4., 7.))
        lCalc = Summierer(self.ötv()).calcSonderzahlung

        vorgeschichte = [(date(2019, 10, 1), Stelle(AllGuS.E10_3, date(2019, 1, 1)))]

        self.assertEqual(Decimal(7.), lCalc(date(2019, 11, 1), date(2020, 1, 1), vorgeschichte))

    def testE10MitVorgeschichte(self):
        self.givenGehalt(2019, AllGuS.E10_3, Gehalt.by(4., 6.))
        lCalc = Summierer(self.ötv()).calcSonderzahlung

        vorgeschichte = [(date(2019, 10, 1), Stelle(AllGuS.E10_3, date(2019, 1, 1)))]

        self.assertEqual(Decimal(6.), lCalc(date(2019, 11, 1), date(2020, 1, 1), vorgeschichte))


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
