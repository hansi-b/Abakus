import unittest
from abakus.model import Gehalt, GuS, Entgeltgruppe, \
    Stufe, ÖtvKosten


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
