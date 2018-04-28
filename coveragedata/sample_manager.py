import logging
from pymongo import MongoClient, ASCENDING

from coveragedb.settings import COVERAGE_DB_HOST, COVERAGE_DB
from coveragedata.error_management import mongo_exception_manager


class SampleManager(object):
    c = MongoClient(host=COVERAGE_DB_HOST)
    coverage_db = c[COVERAGE_DB]
    sample_collection = coverage_db['samples']

    def check(self):
        print("".join([s for s in self.sample_collection.list_indexes()]))

    @mongo_exception_manager
    def add_sample(self, sample_name, number_of_genes, parameters, coding_region, whole_genome, gene_collection):
        self.sample_collection.insert_one({'name': sample_name,
                                           'nog': number_of_genes,
                                           'parameters': parameters,
                                           'coding_region': coding_region,
                                           'whole_genome': whole_genome,
                                           'gene_collection': gene_collection
                                           })
        logging.info('Sample {} for collection {} was added'.format(sample_name, gene_collection))

    @mongo_exception_manager
    def remove_sample(self, sample_name, gene_collection):
        self.sample_collection.delete_one({'name': sample_name, 'gene_collection': gene_collection})
        logging.info('Sample {} for collection {} was removed'.format(sample_name, gene_collection))

    @mongo_exception_manager
    def get_sample_info(self, sample_list, gene_collection, last_sample=None, limit=100):
        sample_search = {"$in": sample_list}
        if last_sample:
            sample_search['$gt'] = last_sample

        result = self.sample_collection.find({'gene_collection': gene_collection, 'name': sample_search}
                                             ).sort('name', ASCENDING).limit(limit)
        return result

