import logging
from pymongo import MongoClient, ASCENDING

from coveragedb.settings import COVERAGE_DB_HOST, COVERAGE_DB
from coveragedata.error_management import mongo_exception_manager


class CoverageManager(object):
    c = MongoClient(host=COVERAGE_DB_HOST)
    coverage_db = c[COVERAGE_DB]
    coverage_collection = coverage_db['coverage']

    @mongo_exception_manager
    def add_coverage_data(self, coverage_data):
        result = self.coverage_collection.insert_many(coverage_data)
        logging.info('{} gene coverage metrics inserted'.format(len(result.inserted_ids)))

    @mongo_exception_manager
    def remove_coverage_data(self, sample_name, gene_collection):
        result = self.coverage_collection.delete_many({'sample': sample_name, 'gcol': gene_collection})
        logging.info('{} gene coverage metrics for gene collection {} were removed'.format(result.deleted_count,
                                                                                           gene_collection)
                     )

    @mongo_exception_manager
    def get_sample_info(self, sample, gene_collection, list_of_genes, last_gene, limit=100):
        gene_search = {"$in": list_of_genes}
        if last_gene:
            gene_search['$gt'] = last_gene

        result = self.coverage_collection.find({'sample': sample, 'gcol': gene_collection,
                                                'name': gene_search}
                                               ).sort('name', ASCENDING).limit(limit)
        return result

    @mongo_exception_manager
    def get_gene_info(self, sample_list, gene_collection, gene):
        result = self.coverage_collection.find({'sample': {"$in": sample_list}, 'gcol': gene_collection, 'name': gene})
        return result

    @mongo_exception_manager
    def get_aggregated_by_gene(self, gene_list):
        query = [
            {'$match': {'name': {'$in': gene_list}}},
            {'$group': {
                '_id': '$name',
                'avg_med': {'$avg': '$union_tr.stats.med'},
                'avg_gte15x': {'$avg': '$union_tr.stats.gte15x'},
                'avg_gte50x': {'$avg': '$union_tr.stats.gte50x'},
                'avg_avg': {'$avg': '$union_tr.stats.avg'},
                'avg_pct75': {'$avg': '$union_tr.stats.pct75'},
                'avg_gte30x': {'$avg': '$union_tr.stats.gte30x'},
                'avg_pct25': {'$avg': '$union_tr.stats.pct25'},
                # 'avg_lt15x': {'$avg': '$union_tr.stats.lt15x'},
            }}

        ]

        return self.coverage_collection.aggregate(query)