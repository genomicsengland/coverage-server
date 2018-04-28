from django.test import TestCase
from mock import patch
import coveragedbingestion.ingest_data as ingest_data
from coveragedata.coverage_manager import CoverageManager
from coveragedata.sample_manager import SampleManager


class TestDataIngestion(TestCase):

    def setUp(self):
        self.input_file = "../resources/test/mocked_coverage_1520552294_0.json"

    @patch.object(CoverageManager, 'add_coverage_data', lambda self, x: None)
    @patch.object(SampleManager, 'add_sample',
                  lambda self, sample_name, number_of_genes, parameters, coding_region, whole_genome, gene_collection: None)
    def test1(self):
        try:
            ingest_data.ingest_data(self.input_file, "test_sample", "test_gene_collection")
        except Exception as e:
            self.assertTrue(False, "Ingestion returned an error: {}".format(str(e)))
