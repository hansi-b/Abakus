import unittest
from datetime import date
from decimal import Decimal

from abakus import laufend
from abakus.model import Stelle, AllGuS


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


lCalc = laufend.calcSonderzahlung


class CalcSonderzahlungTest(unittest.TestCase):

    def testNotNovember(self):
        for m in range(1, 13):
            if m == 11:
                continue
            self.assertIsNone(lCalc(date(2019, m, 1), date(2022, 12, 1), None))

    def testNovemberButNoDezember(self):
        self.assertEqual(Decimal(0.), lCalc(date(2019, 11, 1), date(2019, 11, 30), None))

    def testNovemberAndDezember(self):
        self.assertEqual(Decimal(1.), lCalc(date(2019, 11, 1), date(2020, 1, 1), None))


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
