from django.test import TestCase
from calypso_dca.differential_coverage_analyser import DifferentialCoverageAnalyser


class TestDifferentialCoverageAnalysis(TestCase):

    def setUp(self):
        pass

    def test1(self):
        try:
            dca = DifferentialCoverageAnalyser(["groupA", "groupB"])
            pvalues = dca.run()
        except Exception as e:
            self.assertTrue(False, "Ingestion returned an error: {}".format(str(e)))
        pass

    def test2(self):
        try:
            dca = DifferentialCoverageAnalyser(["groupA", "groupB"])
            dca.save_raw_data("../resources/test")
        except Exception as e:
            self.assertTrue(False, "Ingestion returned an error: {}".format(str(e)))
        pass
