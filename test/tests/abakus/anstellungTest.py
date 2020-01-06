import unittest
from datetime import date

from abakus.model import Stelle, AllGuS
from abakus.laufend import Anstellung


class AnstellungTest(unittest.TestCase):

    def testLaufendSimple(self):

        s = Stelle(AllGuS.E10_3, date(2019, 7, 1))
        # NB: Enddatum ist nicht der letzte Tag im Monat, daher ist Sep nicht dabei
        anst = Anstellung(s, date(2019, 7, 1), date(2019, 9, 13))
        expected = [(date(2019, 7, 31), s), (date(2019, 8, 31), s)]
        self.assertEqual(expected, anst.monatsListe)

    def testLetzterTagImMonat(self):

        s = Stelle(AllGuS.E10_3, date(2019, 7, 1))
        anst = Anstellung(s, date(2019, 7, 1), date(2019, 8, 31))
        expected = [(date(2019, 7, 31), s), (date(2019, 8, 31), s)]
        self.assertEqual(expected, anst.monatsListe)

    def testLaufendJahresWechsel(self):

        s = Stelle(AllGuS.E10_3, date(2019, 7, 1))
        anst = Anstellung(s, date(2019, 12, 1), date(2020, 2, 29))
        expected = [(date(2019, 12, 31), s), (date(2020, 1, 31), s),
                    (date(2020, 2, 29), s)]
        self.assertEqual(expected, anst.monatsListe)

    def testFalscheArgumente(self):

        s = Stelle(AllGuS.E10_3, date(2019, 7, 1))
        try:
            Anstellung(s, date(2019, 5, 1), date(2019, 8, 1))
        except AssertionError as e:
            assert "liegt nach dem Anfangsdatum" in str(e), "Got: {}".format(e)
        else:
            self.fail("Expected AssertionError")
        try:
            Anstellung(s, date(2019, 8, 1), date(2019, 7, 1))
        except AssertionError as e:
            assert "liegt nach dem Enddatum" in str(e), "Got: {}".format(e)
        else:
            self.fail("Expected AssertionError")

    def testFindBaseStellenEinfachesGanzesJahr(self):

        s = Stelle(AllGuS.E10_3, date(2019, 1, 1))
        anst = Anstellung(s, date(2019, 1, 1), date(2020, 3, 31))
        self.assertEqual([s, s, s], anst.findBaseStellen(2019))

    def testFindBaseStellenNurNovember(self):

        s = Stelle(AllGuS.E10_3, date(2019, 11, 1))
        anst = Anstellung(s, date(2019, 11, 1), date(2020, 3, 31))
        self.assertEqual([s], anst.findBaseStellen(2019))

    def testFindBaseStellenSprungImAugust(self):

        s1 = Stelle(AllGuS.E10_1, date(2019, 8, 1))
        s2 = Stelle(AllGuS.E10_2, date(2020, 8, 1))
        anst = Anstellung(s1, date(2019, 8, 1), date(2021, 3, 31))
        self.assertEqual([s1, s2, s2], anst.findBaseStellen(2020))


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
