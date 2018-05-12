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

    # @mongo_exception_manager
    # def get_coverage_by_sample_and_genes(self, sample, gene_list):
    #     """
    #
    #     :param sample: the sample of interest
    #     :param gene_list: the list of genes of interst. If empty all genes will be returned
    #     :return: a cursor with the search results
    #     """
    #     query = {'sample': sample}
    #     if gene_list:
    #         query['name'] = {"$in": gene_list}
    #     projection = {'union_tr.stats.avg': 1, 'name': 1, 'sample': 1, '_id': 0}
    #     cursor = self.coverage_collection.find(
    #         query,
    #         projection
    #     ).sort('name', ASCENDING)
    #     return cursor

    @mongo_exception_manager
    def get_groups_by_samples(self, samples):
        """

        :param samples: the list of samples to query
        :return: a list of documents where _id is the sample and group is the field gcol without repetitions
        """
        query = {"$match": {"sample": {"$in": samples}}}
        projection = {"$project": {"gcol": 1, "sample": 1, "_id": 0}}
        group = {"$group": {"_id": "$sample", "group": {"$first": "$gcol"}}}
        results = self.coverage_collection.aggregate([query, projection, group])
        return results

    @mongo_exception_manager
    def get_genes_by_group(self, group):
        """

        :param group: a group (ie: gcol) of interest
        :return: a list of genes for which there is coverage data in the group
        """
        group_genes = self.coverage_collection.distinct("name", {"gcol": group})
        return group_genes

    @mongo_exception_manager
    def get_genes_by_groups(self, groups):
        """

        :param groups: the list of groups (ie: gcol) of interest
        :return: a list of genes for which there is coverage data in all groups
        """
        genes = []
        for group in groups:
            group_genes = self.get_genes_by_group(group)
            if not genes:
                genes = group_genes
            else:
                genes = list(set(genes).intersection(set(group_genes)))
        return genes

    @mongo_exception_manager
    def get_samples_by_group(self, group):
        """

        :param group: a group (ie: gcol) of interest
        :return: a list of samples belonging to the group
        """
        group_samples = self.coverage_collection.distinct("sample", {"gcol": group})
        return group_samples

    @mongo_exception_manager
    def get_samples_by_groups(self, groups):
        """

        :param groups: a list of groups (ie: gcol) of interest
        :return: a list of samples belonging to the groups
        """
        samples = []
        for group in groups:
            samples += self.get_samples_by_group(group)
        return samples

    @mongo_exception_manager
    def get_coverage_by_sample_and_genes(self, samples=None, experiment=None, gene_list=None):
        """

        :param sample: the sample of interest
        :param gene_list: the list of genes of interst. If empty all genes will be returned
        :return: a cursor with the search results
        """
        query = {}
        if experiment:
            query['gcol'] = experiment
        if samples:
            query['sample'] = {"$in": samples}
        if gene_list:
            query['name'] = {"$in": gene_list}
        projection = {'union_tr.stats': 1, 'gcol': 1,
                      'name': 1, 'sample': 1, '_id': 0}
        cursor = self.coverage_collection.find(
            query,
            projection
        ).sort('name', ASCENDING)
        return cursor
