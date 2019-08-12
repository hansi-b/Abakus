import unittest
from abakus.model import Gehalt, GuS, Entgeltgruppe, \
    Stufe, ÖtvKosten
from datetime import date


class StufenTest(unittest.TestCase):
    
    def testNächsterAufstieg(self):
        self.assertEquals(date(2020, 3, 12),
            Stufe.eins.nächsterAufstieg(date(2019, 3, 12)))  # @UndefinedVariable
        self.assertEquals(date(2022, 12, 22),
            Stufe.drei.nächsterAufstieg(date(2019, 12, 22)))  # @UndefinedVariable

    def testNächste(self):
        self.assertEquals(Stufe.eins.nächste(), Stufe.zwei)  # @UndefinedVariable
        self.assertEquals(Stufe.sechs.nächste(), Stufe.sechs)  # @UndefinedVariable

        
class GuSTest(unittest.TestCase):

    def testAmEinfach(self):
        start = GuS(Entgeltgruppe.E_10, Stufe.eins, date(2019, 1, 1))
        self.assertEquals(start, start.am(date(2019, 2, 1)))

    def testAmAufstieg(self):
        start = GuS(Entgeltgruppe.E_10, Stufe.eins, date(2019, 1, 1))
        self.assertEquals(GuS(Entgeltgruppe.E_10, Stufe.zwei, date(2020, 1, 1)),
                          start.am(date(2020, 2, 17)))

    def testAmRandfall(self):
        start = GuS(Entgeltgruppe.E_10, Stufe.eins, date(2019, 1, 1))
        self.assertEquals(GuS(Entgeltgruppe.E_10, Stufe.zwei, date(2020, 1, 1)),
                          start.am(date(2020, 1, 1)))

    def testAmÜbersprung(self):
        start = GuS(Entgeltgruppe.E_10, Stufe.eins, date(2019, 1, 1))
        self.assertEquals(GuS(Entgeltgruppe.E_10, Stufe.drei, date(2022, 1, 1)),
                          start.am(date(2023, 3, 4)))

    def testAmEndstufe(self):
        start = GuS(Entgeltgruppe.E_10, Stufe.sechs, date(2019, 1, 1))
        self.assertEquals(start, start.am(date(2043, 3, 4)))


class KostenBerechnungTest(unittest.TestCase):

    def setUp(self):
        self.gehälter = {}

    def tearDown(self):
        self.gehälter = {}
    
    def testSummeMonatlich(self):
        self.givenGehalt(2012, GuS(Entgeltgruppe.E_10, Stufe.drei),  #
                         Gehalt(4., 7.))
        ötv = ÖtvKosten(self.gehälter)
        self.assertEquals(4. * 1.3,
                          ötv.summeMonatlich(2012, GuS(Entgeltgruppe.E_10, Stufe.drei)))

    def testSonderzahlung(self):
        self.givenGehalt(2012, GuS(Entgeltgruppe.E_10, Stufe.drei),  #
                         Gehalt(4., 7.2))
        ötv = ÖtvKosten(self.gehälter)
        
        self.assertEquals(7.2,
                          ötv.sonderzahlung(2012, GuS(Entgeltgruppe.E_10, Stufe.drei)))

    def givenGehalt(self, jahr : int, gus : GuS, gehalt: Gehalt):
        self.gehälter[(jahr, gus)] = gehalt
        

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
