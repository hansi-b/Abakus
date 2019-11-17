import unittest
from datetime import date
from decimal import Decimal

from abakus.model import Gehalt, GuS, \
    Stufe, ÖtvKosten, Stelle, AllGuS, Entgeltgruppe


class StufenTest(unittest.TestCase):

    def testNächsterAufstieg(self):
        self.assertEqual(date(2020, 3, 12),
                         Stufe.eins.nächsterAufstieg(date(2019, 3, 12)))  # @UndefinedVariable
        self.assertEqual(date(2022, 12, 22),
                         Stufe.drei.nächsterAufstieg(date(2019, 12, 22)))  # @UndefinedVariable

    def testNächste(self):
        self.assertEqual(Stufe.eins.nächste(), Stufe.zwei)  # @UndefinedVariable
        self.assertEqual(Stufe.sechs.nächste(), Stufe.sechs)  # @UndefinedVariable


class DatierteGuSTest(unittest.TestCase):

    def testAmEinfach(self):
        start = Stelle(AllGuS.E10_2, date(2019, 1, 1))
        self.assertEqual(start, start.am(date(2019, 2, 1)))

    def testAmAufstieg(self):
        start = Stelle(AllGuS.E10_1, date(2019, 1, 1))
        self.assertEqual(Stelle(AllGuS.E10_2, date(2020, 1, 1)),
                         start.am(date(2020, 2, 17)))

    def testAmRandfall(self):
        start = Stelle(AllGuS.E10_1, date(2019, 1, 1))
        self.assertEqual(Stelle(AllGuS.E10_2, date(2020, 1, 1)),
                         start.am(date(2020, 1, 1)))

    def testAmÜbersprung(self):
        start = Stelle(AllGuS.E10_1, date(2019, 1, 1))
        self.assertEqual(Stelle(AllGuS.E10_3, date(2022, 1, 1)),
                         start.am(date(2023, 3, 4)))

    def testAmEndstufe(self):
        start = Stelle(AllGuS.E10_6, date(2019, 1, 1))
        self.assertEqual(start, start.am(date(2043, 3, 4)))


class TestMitGehältern(unittest.TestCase):

    def setUp(self):
        self.gehälter = {}

    def tearDown(self):
        del self.gehälter

    def givenGehalt(self, jahr: int, gus: GuS, gehalt: Gehalt):
        self.gehälter[(jahr, gus)] = gehalt

    def ötv(self):
        return ÖtvKosten(self.gehälter)


class EntgeltGruppenTest(unittest.TestCase):

    def testAnteilig(self):
        self.assertAlmostEqual(Decimal(8.), Entgeltgruppe.E_10.anteilig(Decimal(10.)))
        self.assertAlmostEqual(Decimal(5.), Entgeltgruppe.E_13.anteilig(Decimal(10.)))


class KostenBerechnungTest(TestMitGehältern):

    def testSummeMonatlich(self):
        self.givenGehalt(2012, AllGuS.E10_3, Gehalt.by(4., 7.))
        self.assertAlmostEqual(Decimal(4. * 1.3),
                               self.ötv().summeMonatlich(2012, AllGuS.E10_3))

    def testSonderzahlung(self):
        self.givenGehalt(2012, AllGuS.E10_3, Gehalt(4., 7.2))

        self.assertEqual(7.2, self.ötv().sonderzahlung(2012, AllGuS.E10_3))


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
